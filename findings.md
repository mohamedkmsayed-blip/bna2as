# Findings - Research & Discovery Log

**Project:** Sooq Deals — Egyptian Deals Aggregator
**Created:** 2025-02-15
**Updated:** 2026-02-16
**Purpose:** Central repository for research, discoveries, constraints, and learnings

---

## 🔍 Research Findings

### 2026-02-16 — Affiliate Program Research

#### Amazon.eg Associates
- **Status:** Private/invite-only program (as of late 2021, may have changed)
- **Commission:** Up to 9% depending on category
- **Requirements:**
  - Active website with original content (not "under construction")
  - Privacy policy page
  - Affiliate disclosure on every page
  - 3 qualifying sales within first 180 days or account terminated
  - No static prices — must use dynamic pricing from API
  - Product images must come from Amazon API, not self-hosted
  - No link shorteners to disguise affiliate links
  - Affiliate tag format: `tag=yourtag-21`
- **API:** Product Advertising API (PA-API) v5 available for amazon.eg
  - Requires active Associates account + 3 sales for full query limits
  - Operations: `SearchItems`, `GetItems`, `GetBrowseNodes`
  - Region: eu-west-1

#### Jumia Egypt Affiliate Program
- **Status:** Open for applications via jumia.com.eg
- **Commission:** 5-13% depending on product category
  - Electronics: ~6%, Home Supplies: ~13%, Programming: ~11.4%
  - Up to 13% on all orders within 7-day cookie window
  - Minimum commission: 10 EGP
- **API:** Jumia KOL Affiliates API (GitHub: `Jumia-Kol-API`)
  - Retrieves product details and generates affiliate links
  - Uses Key Opinion Leader (KOL) account ID
- **Vendor APIs also available:** GPM (product catalog), GOP (order processing)

#### Noon Egypt Affiliate Program
- **Status:** Available through Noon directly or affiliate networks (Admitad, ArabClicks)
- **Commission:** 2-10% depending on category
- **Payment:** Monthly, ~45 days after month end
- **API:** No public affiliate API
  - Noon has Commercial/Merchant APIs for sellers only
  - Third-party scrapers exist (Apify)
  - Admitad notes: promotion primarily relies on offline promo codes
- **Decision:** Defer to Phase 2 due to lack of API and ToS scraping prohibition

---

### 2026-02-16 — Web Scraping Legality Research

- **Amazon.eg:** ToS explicitly prohibits scraping → Use PA-API v5 (compliant)
- **Jumia:** Has robots.txt, dynamic content → Use KOL API (grey area but common)
- **Noon:** ToS prohibits scraping, no public API → Highest risk
- **Egypt law:** No specific anti-scraping law. IP Law No. 82 of 2002 covers copyright.
  - Factual data (prices, product names) generally not copyrightable
  - Product descriptions and images ARE copyrightable
- **Best practices:** Respect robots.txt, rate limit requests, use official APIs where possible

---

### 2026-02-16 — Modal.com Platform Research

- **Pricing:** Usage-based, no per-request charges
  - CPU: $0.0000131/core/sec
  - Memory: $0.00000222/GiB/sec
  - Starter plan: $0/mo + $30 free compute credits
- **Features:** FastAPI web endpoints, scheduled functions (Cron), persistent Volumes (for SQLite)
- **Ideal for:** Scraper scheduling + API serving in one platform

---

## 📚 Resources Discovered

| Resource | Type | URL | Relevance | Status |
|----------|------|-----|-----------|--------|
| Amazon PA-API v5 Docs | Official API | docs.aws.amazon.com/paapi5 | Core - Amazon scraping | To integrate |
| Jumia-Kol-API | GitHub Repo | github.com/Jumia-Kol-API | Core - Jumia scraping | To integrate |
| Noon Product Scraper | Apify Actor | apify.com/noon-scraper | Optional - Noon data | Phase 2 |
| Modal FastAPI Guide | Docs | modal.com/docs/guide/webhooks | Core - Backend | To implement |

---

## 🔐 API Constraints & Limitations

| Service | Rate Limit | Quota | Special Notes |
|---------|-----------|-------|---------------|
| Amazon PA-API v5 | 1 req/sec (initial) | 8640/day (scales with sales) | Need 3 sales for full limits |
| Jumia KOL API | Unknown | Unknown | Unofficial, may change |
| Noon | N/A (scraping) | N/A | Aggressive anti-bot, CAPTCHAs |
| Modal Starter | 10 containers | $30/mo free credits | Sufficient for MVP |

---

## 🐛 Error Patterns & Solutions

| Error | Cause | Solution | Date Fixed |
|-------|-------|----------|------------|
| [NONE YET] | - | - | - |

---

## 💡 Key Discoveries

### Discovery 1: Amazon.eg is Private Program
- **Date:** 2026-02-16
- **Context:** Researching affiliate program availability
- **Finding:** Amazon.eg Associates is invite-only, unlike most Amazon regional programs
- **Impact:** May need to build MVP first and apply, or contact Amazon directly

### Discovery 2: Jumia Has Unofficial KOL API
- **Date:** 2026-02-16
- **Context:** Looking for API access to Jumia product data
- **Finding:** A GitHub repo `Jumia-Kol-API` provides product fetching and affiliate link generation
- **Impact:** Enables programmatic access without full web scraping

### Discovery 3: Noon Has No Affiliate API
- **Date:** 2026-02-16
- **Context:** Researching Noon integration options
- **Finding:** Noon only offers promo codes through affiliate networks, no product data API
- **Impact:** Noon deferred to Phase 2; would require web scraping or third-party tools

---

## ⚠️ Constraints & Limitations

1. **Amazon.eg Associates approval** — May be difficult to get initially
2. **PA-API rate limits** — Start at 1 req/sec, need sales to increase
3. **Noon anti-bot protection** — CAPTCHA challenges, dynamic content
4. **No Arabic content initially** — MVP in English only
5. **Cookie windows** — Jumia: 7 days, Amazon: 24 hours, Noon: varies

---

## 📝 Notes

- Consider using ArabClicks as an affiliate network that aggregates Amazon, Jumia, and Noon under one dashboard
- Egyptian e-commerce market growing rapidly; Ramadan and Black Friday (White Friday) are peak deal seasons
- EGP currency fluctuations may affect price comparisons

---

*Last Updated: 2026-02-16*
*Next Research Task: Test API connectivity in Phase 2 (Link)*