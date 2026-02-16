# Data Flow SOP — Scraping → Processing → Serving

## Overview
This SOP defines how product data flows through the Sooq Deals system, from scraping external sources to serving deals via the API.

## Pipeline Flow

```
┌─────────────┐     ┌──────────────┐     ┌────────────┐     ┌──────────┐
│  Scrapers   │ ──▶ │ Filter/Norm  │ ──▶ │  Database   │ ──▶ │   API    │
│ (4h cron)   │     │ (≥15% disc)  │     │ (SQLite)    │     │ (FastAPI)│
└─────────────┘     └──────────────┘     └────────────┘     └──────────┘
```

## Steps

### 1. Scrape (scheduler.py → scrapers/)
- **Trigger:** Modal Cron every 4 hours
- **Sources:** Amazon.eg (PA-API / web), Jumia (KOL API / web)
- **Output:** Raw `Product` objects from each scraper

### 2. Filter & Normalize (scrapers/base.py)
- Calculate `discount_pct = ((original - current) / original) * 100`
- Filter out products with `discount_pct < 15%`
- Normalize to `Product` Pydantic model
- Deduplicate by `id` = `{source}_{external_id}`

### 3. Store (database.py)
- `upsert_product()` — insert new or update existing
- If product exists: update price, discount, timestamp
- If new: insert with `first_seen` = now
- Log scrape run to `scrape_logs` table

### 4. Serve (api.py)
- `GET /api/deals` — paginated, filterable list
- `GET /go/{id}` — click tracking + affiliate redirect

### 5. Cleanup (scheduler.py)
- Daily cron deactivates deals not updated in 48 hours
- Sets `is_active = 0` on stale products

## Error Handling
- Each scraper run is logged (success/fail) with duration
- Failed scrapers don't block other scrapers
- Retries with exponential backoff on HTTP errors
- Rate limiting: 1.5s between requests, longer on 429s

## Invariants
- All prices are in EGP
- Product IDs are globally unique: `{source}_{external_id}`
- Never store API keys in code — always from `.env` / Modal secrets
- All intermediate files go to `.tmp/`
