"""SEO/GEO auditor: indexing boundary, canonical rules, llms.txt discovery."""

import pytest

from conftest import types_of

NOINDEX_APP = """<!doctype html>
<html lang="pt-BR"><head>
<meta name="robots" content="noindex, nofollow" />
<link rel="canonical" href="https://app.dominio.com/" />
<title>App</title>
</head></html>
"""

NOINDEX_APP_CLEAN = """<!doctype html>
<html lang="pt-BR"><head>
<meta name="robots" content="noindex, nofollow" />
<title>App</title>
</head></html>
"""

PUBLIC_LP = """<!doctype html>
<html lang="pt-BR"><head>
<link rel="canonical" href="https://www.dominio.com.br/" />
<script type="application/ld+json">{"@type":"SoftwareApplication"}</script>
<title>LP</title>
</head></html>
"""


def test_noindex_page_with_canonical_is_flagged(audit_seo, tree):
    """The two signals contradict each other and the canonical is ignored anyway."""
    root = tree({"web/index.html": NOINDEX_APP})
    findings = audit_seo.audit_html_metadata(root)
    assert "Technical SEO" in types_of(findings)
    assert any("noindex" in f["description"] for f in findings)


def test_noindex_page_without_canonical_is_not_flagged_for_canonical(audit_seo, tree):
    """A private entrypoint is not expected to carry a canonical — the earlier
    version demanded one and pushed exactly the wrong fix."""
    root = tree({"web/index.html": NOINDEX_APP_CLEAN})
    findings = audit_seo.audit_html_metadata(root)
    assert not any("canonical" in f["description"].lower() for f in findings)


def test_indexable_page_without_canonical_is_flagged(audit_seo, tree):
    root = tree({"lp/index.html": "<html><head><title>x</title></head></html>"})
    findings = audit_seo.audit_html_metadata(root)
    assert any("canonical" in f["description"].lower() for f in findings)


def test_complete_public_page_passes(audit_seo, tree):
    assert audit_seo.audit_html_metadata(tree({"lp/index.html": PUBLIC_LP})) == []


def test_mixed_tree_flags_only_the_contradiction(audit_seo, tree):
    """A repo with a proper LP and a noindex app: the LP satisfies the canonical
    requirement, so only the app's contradictory pair should surface."""
    root = tree({"lp/index.html": PUBLIC_LP, "web/index.html": NOINDEX_APP})
    findings = audit_seo.audit_html_metadata(root)
    assert len(findings) == 1
    assert "noindex" in findings[0]["description"]


# --------------------------------------------------------------------------- #
# llms.txt discovery
# --------------------------------------------------------------------------- #

def test_llms_txt_found_in_monorepo_subdirectory(audit_seo, tree):
    """Probing only the target root misses sites living in subdirectories."""
    root = tree({
        "code/site-lp/public/llms.txt": "# Product\n",
        "code/site-lp/public/llms-full.txt": "# Product full\n",
        "code/site-lp/index.html": PUBLIC_LP,
    })
    assert audit_seo.audit_llms_txt(root) == []


def test_missing_llms_txt_is_flagged(audit_seo, tree):
    root = tree({"lp/index.html": PUBLIC_LP})
    assert "GEO (AI Engine Optimization)" in types_of(audit_seo.audit_llms_txt(root))


def test_llms_full_missing_is_flagged_only_when_llms_exists(audit_seo, tree):
    """llms-full.txt is the deep companion — it only makes sense once the index exists."""
    root = tree({"lp/index.html": PUBLIC_LP, "lp/public/llms.txt": "# Product\n"})
    findings = audit_seo.audit_llms_txt(root)
    assert len(findings) == 1
    assert "llms-full.txt" in findings[0]["description"]
    assert findings[0]["severity"] == "LOW"


def test_no_landing_page_means_no_geo_findings(audit_seo, tree):
    """A backend-only repository should not be asked for llms.txt."""
    assert audit_seo.audit_llms_txt(tree({"api/main.go": "package main\n"})) == []


def test_find_public_file_rejects_non_public_location(audit_seo, tree):
    """A llms.txt buried in src/ is not served at the URL root."""
    root = tree({"lp/src/docs/llms.txt": "# nope\n"})
    assert audit_seo.find_public_file(root, "llms.txt") is None


def test_clean_tree_scores_100(audit_seo, tree):
    result = audit_seo.audit(tree({"README.md": "# hi\n"}))
    assert result["issues_count"] == 0
    assert result["score"] == 100
