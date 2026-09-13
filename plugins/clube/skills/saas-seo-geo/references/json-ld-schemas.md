# Schema.org Structured Data (JSON-LD)

Technical reference and production templates for Schema.org structured data in SaaS applications, landing pages, and documentation.

---

## 1. Mandatory Principles

1. **Exact UI Parity:** Every entity, price, FAQ, or organization property declared in JSON-LD MUST strictly match the visible text on the page. Discrepancies risk search engine manual actions and AI citation hallucination.
2. **Standard Validated Types:** Use standard Schema.org schemas embedded in `<script type="application/ld+json">` tags inside `<head>`.
3. **GEO Optimization via FAQPage:** While traditional Google SERP snippets have reduced visible FAQ dropdowns, LLMs and AI search engines (Perplexity, ChatGPT Search, Claude, Gemini) rely on `FAQPage` JSON-LD as primary grounded context.

---

## 2. Core SaaS Schemas

### A. SoftwareApplication (SaaS Product)

```html
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "SoftwareApplication",
  "name": "SaaSProductName",
  "url": "https://www.domain.com/",
  "applicationCategory": "BusinessApplication",
  "operatingSystem": "Web",
  "description": "Comprehensive description of software capabilities and key features.",
  "offers": {
    "@type": "Offer",
    "price": "49.00",
    "priceCurrency": "USD",
    "priceValidUntil": "2027-12-31",
    "description": "Starting at $49/mo on the annual plan."
  }
}
</script>
```

### B. FAQPage (GEO & Semantic Search)

```html
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "mainEntity": [
    {
      "@type": "Question",
      "name": "What is SaaSProductName?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "SaaSProductName is an automated platform that helps teams streamline operations and increase revenue."
      }
    },
    {
      "@type": "Question",
      "name": "How does pricing work?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "Plans start at $49/month with a 14-day free trial. No credit card required to start."
      }
    }
  ]
}
</script>
```

### C. Organization (Brand Entity & Knowledge Graph)

```html
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "Organization",
  "name": "CompanyName Inc.",
  "url": "https://www.domain.com",
  "logo": "https://www.domain.com/logo.png",
  "sameAs": [
    "https://twitter.com/companyhandle",
    "https://www.linkedin.com/company/companyhandle",
    "https://github.com/companyhandle"
  ],
  "contactPoint": {
    "@type": "ContactPoint",
    "contactType": "customer support",
    "telephone": "+1-800-555-0199",
    "email": "support@domain.com",
    "availableLanguage": ["English", "Portuguese"]
  }
}
</script>
```

### D. BreadcrumbList (Subpages & Docs)

```html
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "BreadcrumbList",
  "itemListElement": [
    {
      "@type": "ListItem",
      "position": 1,
      "name": "Home",
      "item": "https://www.domain.com/"
    },
    {
      "@type": "ListItem",
      "position": 2,
      "name": "Features",
      "item": "https://www.domain.com/features"
    },
    {
      "@type": "ListItem",
      "position": 3,
      "name": "Integrations",
      "item": "https://www.domain.com/features/integrations"
    }
  ]
}
</script>
```

---

## 3. Edge Cases & Validation

- ⚠️ **JSON Syntax Escaping:** Unescaped quotes (`"`) or invalid trailing commas in JSON-LD break the entire script block without warning. Always validate schemas with the Google Rich Results Test or Schema.org Validator.
- ⚠️ **Dynamic Pricing Drift:** If your marketing page updates plan prices dynamically (e.g. from an API or currency selector), ensure the JSON-LD updates synchronously or reflects the default canonical USD pricing.

---

## 4. Cross-References

- [Meta & Social Metadata](meta-social.md) — Base head tags and Open Graph.
- [GEO & llms.txt](geo-llmstxt.md) — Generative Engine Optimization patterns.
- [Back to SaaS SEO Skill](../SKILL.md)
