# Affiliate Links SOP — Generation, Tracking & Redirect

## Overview
This SOP defines how affiliate links are generated, how clicks are tracked, and how users are redirected to retailer sites.

## Affiliate URL Patterns

| Platform | Format | Example |
|----------|--------|---------|
| Amazon.eg | `?tag={PARTNER_TAG}` | `amazon.eg/dp/B09V3K?tag=sooqdeals-21` |
| Jumia | `?tag={AFFILIATE_TAG}` | `jumia.com.eg/product.html?tag=sooq123` |
| Noon | `?utm_source=affiliate&utm_medium={CODE}` | Phase 2 |

## Click Flow

```
User clicks "Shop Now"
    │
    ▼
GET /go/{product_id}     ← Frontend calls this
    │
    ├── 1. Look up product in DB
    ├── 2. Log click (IP, user-agent, referrer, timestamp)
    ├── 3. Get affiliate_url (or fallback to url)
    │
    ▼
302 Redirect → affiliate_url    ← User lands on retailer site
```

## Rules

1. **Every external link MUST go through `/go/{id}`** — never link directly to retailers from the frontend
2. **affiliate_url is generated at scrape time** — not at click time (performance)
3. **Click data is anonymized** — store only IP (truncated), user-agent, referrer
4. **No PII is stored** — no cookies, no usernames, no emails in click tracking
5. **Fallback:** If `affiliate_url` is null, redirect to the plain `url`

## Amazon-Specific Rules
- Tag format MUST end in `-21` for .eg
- Product images MUST come from Amazon API (not self-hosted)
- Prices MUST NOT be displayed as static text (dynamic via API)
- Affiliate disclosure MUST be visible on every page

## Commission Tracking
Commissions are tracked by the affiliate programs themselves (not by us):
- Amazon: via PA-API dashboard
- Jumia: via affiliate portal
- Noon: via Admitad/ArabClicks dashboard
