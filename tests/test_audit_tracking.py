"""Tracking auditor: cookie scope, deduplication, linker fail-safe, instrumentation tests."""

from conftest import types_of

TRACKING_MARKERS = "const p = new URLSearchParams(location.search); p.get('utm_source'); p.get('fbclid');\n"

# The anti-pattern: deriving the root domain by slicing hostname labels. On a Public
# Suffix List host this yields domain=.vercel.app and the browser drops the cookie
# with no error, so attribution vanishes on every preview deploy.
GENERIC_DERIVATION = TRACKING_MARKERS + """
function getCookieRootDomain() {
  const hostname = window.location.hostname
  const parts = hostname.split('.')
  return `.${parts.slice(-2).join('.')}`
}
document.cookie = `x=1; domain=${getCookieRootDomain()}`
"""

EXPLICIT_ALLOWLIST = TRACKING_MARKERS + """
const PRODUCT_ROOT_DOMAINS = ['dominio.com.br']
function cookieDomainSuffix() {
  const hostname = window.location.hostname
  const root = PRODUCT_ROOT_DOMAINS.find(d => hostname === d || hostname.endsWith(`.${d}`))
  return root ? `; domain=.${root}` : ''
}
document.cookie = `x=1; path=/${cookieDomainSuffix()}`
"""


def test_generic_root_domain_derivation_is_flagged(audit_tracking, tree):
    findings = audit_tracking.audit_cookie_domain(tree({"src/attribution.js": GENERIC_DERIVATION}))
    assert "Attribution Cookie Scope" in types_of(findings)
    assert any(f["severity"] == "HIGH" for f in findings)
    assert any("Public Suffix List" in f["description"] for f in findings)


def test_explicit_allowlist_passes(audit_tracking, tree):
    """Guards against the original bug, where any occurrence of 'domain=' or
    'rootDomain' was treated as evidence of correctness."""
    assert audit_tracking.audit_cookie_domain(tree({"src/attribution.js": EXPLICIT_ALLOWLIST})) == []


def test_tracking_without_any_cookie_scoping_is_flagged(audit_tracking, tree):
    findings = audit_tracking.audit_cookie_domain(tree({"src/a.js": TRACKING_MARKERS}))
    assert "Attribution Cookie Scope" in types_of(findings)


def test_project_without_tracking_is_not_flagged(audit_tracking, tree):
    assert audit_tracking.audit_cookie_domain(tree({"src/a.js": "export const x = 1\n"})) == []


# --------------------------------------------------------------------------- #
# Deduplication
# --------------------------------------------------------------------------- #

def test_pixel_without_event_id_is_flagged(audit_tracking, tree):
    root = tree({"src/t.js": "fbq('track', 'Purchase', { value: 10 })\n"})
    assert "CAPI Deduplication" in types_of(audit_tracking.audit_event_id_dedup(root))


def test_pixel_with_event_id_passes(audit_tracking, tree):
    root = tree({"src/t.js": "fbq('track', 'Purchase', { value: 10 }, { eventID: txId })\n"})
    assert audit_tracking.audit_event_id_dedup(root) == []


# --------------------------------------------------------------------------- #
# GA4 linker fail-safe
# --------------------------------------------------------------------------- #

LINKER_NO_TIMEOUT = """
export function decorate(url) {
  return new Promise((resolve) => {
    window.gtag('get', gaId, 'linker_param', (linkerParam) => resolve(url + linkerParam))
  })
}
"""

LINKER_WITH_TIMEOUT = LINKER_NO_TIMEOUT + """
const timeoutPromise = new Promise((resolve) => setTimeout(() => resolve(url), 600))
Promise.race([linkerPromise, timeoutPromise])
"""


def test_linker_without_timeout_is_flagged(audit_tracking, tree):
    """Under an adblocker the gtag callback may never fire, hanging the CTA."""
    findings = audit_tracking.audit_ga_linker_timeout(tree({"src/linker.js": LINKER_NO_TIMEOUT}))
    assert "Cross-Domain Linker" in types_of(findings)
    assert findings[0]["severity"] == "HIGH"


def test_linker_with_timeout_passes(audit_tracking, tree):
    assert audit_tracking.audit_ga_linker_timeout(tree({"src/linker.js": LINKER_WITH_TIMEOUT})) == []


def test_code_without_linker_is_not_flagged(audit_tracking, tree):
    assert audit_tracking.audit_ga_linker_timeout(tree({"src/a.js": "const x = 1\n"})) == []


# --------------------------------------------------------------------------- #
# Instrumentation coverage
# --------------------------------------------------------------------------- #

def test_tracking_module_without_spec_is_flagged(audit_tracking, tree):
    """Instrumentation is the only subsystem that fails with no symptom at all."""
    root = tree({"src/tracking.js": "export function trackPurchase() {}\n"})
    assert "Instrumentation Coverage" in types_of(audit_tracking.audit_instrumentation_tests(root))


def test_tracking_module_with_spec_passes(audit_tracking, tree):
    root = tree({
        "src/tracking.js": "export function trackPurchase() {}\n",
        "src/tracking.spec.js": "import { trackPurchase } from './tracking.js'\n",
    })
    assert audit_tracking.audit_instrumentation_tests(root) == []


def test_unrelated_spec_does_not_satisfy_coverage(audit_tracking, tree):
    root = tree({
        "src/tracking.js": "export function trackPurchase() {}\n",
        "src/button.spec.js": "it('renders', () => {})\n",
    })
    assert "Instrumentation Coverage" in types_of(audit_tracking.audit_instrumentation_tests(root))


def test_project_without_tracking_module_is_not_flagged(audit_tracking, tree):
    assert audit_tracking.audit_instrumentation_tests(tree({"src/button.js": "x\n"})) == []


# --------------------------------------------------------------------------- #
# Acquisition persistence
# --------------------------------------------------------------------------- #

def test_migrations_without_acquisition_context_are_flagged(audit_tracking, tree):
    root = tree({"migrations/1_users.sql": "CREATE TABLE users (id uuid);\n"})
    assert "Marketing Data Persistence" in types_of(audit_tracking.audit_acquisition_persistence(root))


def test_acquisition_context_column_passes(audit_tracking, tree):
    root = tree({"migrations/1_users.sql": "ALTER TABLE users ADD COLUMN acquisition_context JSONB;\n"})
    assert audit_tracking.audit_acquisition_persistence(root) == []


def test_clean_tree_scores_100(audit_tracking, tree):
    result = audit_tracking.audit(tree({"README.md": "# hi\n"}))
    assert result["issues_count"] == 0
    assert result["score"] == 100
