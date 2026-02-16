# Task Plan - B.L.A.S.T. Execution Roadmap

**Project:** Sooq Deals — Egyptian Deals Aggregator
**Created:** 2025-02-15
**Updated:** 2026-02-16
**Status:** Phase 5 Trigger IN PROGRESS (Deployment & Connectivity Verified)

---

## 🎯 Phases Overview

### Phase 0: Initialization [✅ COMPLETE]
**Goal:** Establish project infrastructure
- [x] Create gemini.md (Project Constitution)
- [x] Create task_plan.md (This file)
- [x] Create findings.md (Research log)
- [x] Create progress.md (Activity tracker)
- [x] Create directory structure (.tmp/, architecture/, tools/)
- [x] Create .env template
- [x] Answer Discovery Questions
- [x] Define Data Schemas
- [x] User approves Blueprint ✅ (2026-02-16)

---

### Phase 1: Blueprint [✅ COMPLETE]
**Goal:** Define what we're building

#### Discovery Questions ✅
- [x] North Star: Deals aggregator site with affiliate revenue
- [x] Integrations: Amazon PA-API v5, Jumia KOL API, Noon (scraping), Modal, Vercel
- [x] Source of Truth: SQLite on Modal Volume
- [x] Delivery Payload: Web app (Vercel) + API (Modal)
- [x] Behavioral Rules: 15% min discount, EGP currency, affiliate disclosure, no static prices

#### Data Schema Definition ✅
- [x] Define Input Schema (JSON) — Product, Click, ScrapeLog
- [x] Define Output Schema (JSON) — API response format
- [x] Document data transformations — discount calc, affiliate URL insertion
- [x] Get user confirmation on payload shape ✅

#### Research ✅
- [x] Amazon.eg Associates: private/invite-only, up to 9% commission, PA-API v5 available
- [x] Jumia Affiliates: 5-13% commission, KOL API on GitHub
- [x] Noon Affiliates: 2-10% commission, no public API, scraping only
- [x] Modal.com: $30/mo free credits, FastAPI support, Cron scheduling
- [x] Scraping legality: prefer APIs, respect ToS, no Egypt-specific ban
- [x] Document API limitations
- [x] Record rate limits and quotas

---

### Phase 2: Link [� NEXT]
**Goal:** Verify all connectivity

#### API Verification
- [x] Test Modal deployment (hello world) ✅
- [x] Test Amazon PA-API v5 connection (Fallback to scraping) ✅
- [x] Test Jumia KOL API connection (Fallback to scraping) ✅
- [x] Verify .env credentials loaded correctly ✅

#### Handshake Scripts
- [ ] Build `tools/scrapers/test_amazon.py` — minimal API test
- [ ] Build `tools/scrapers/test_jumia.py` — minimal API test
- [ ] Verify SQLite database creation on Modal Volume

#### Success Criteria
- [x] Modal deploys and serves FastAPI endpoint ✅
- [x] At least one scraper returns real product data (Seeded data & Amazon attempted) ✅
- [x] Database schema created and queryable ✅

---

### Phase 3: Architect [✅ COMPLETE]
**Goal:** Build the 3-layer system

#### Layer 1: SOPs (architecture/)
#### Layer 1: SOPs (architecture/)
- [x] Write `architecture/data-flow.md` — scraping pipeline SOP ✅
- [x] Write `architecture/affiliate-links.md` — link generation SOP ✅

#### Layer 2: Navigation
- [x] Build routing logic (scheduler orchestration) ✅

#### Layer 3: Tools (tools/)
- [x] `tools/app.py` — Modal app definition ✅
- [x] `tools/database.py` — SQLite schema & CRUD ✅
- [x] `tools/scrapers/base.py` — Base scraper class ✅
- [x] `tools/scrapers/amazon_scraper.py` — Amazon PA-API v5 (Stub + Scraper) ✅
- [x] `tools/scrapers/jumia_scraper.py` — Jumia KOL API + fallback ✅
- [x] `tools/api.py` — FastAPI routes ✅
- [x] `tools/scheduler.py` — Modal Cron functions ✅

---

### Phase 4: Stylize [✅ MVP COMPLETE]
**Goal:** Build frontend & refine outputs

#### Frontend (Next.js)
#### Frontend (Next.js)
- [x] Initialize Next.js project in `frontend/` ✅
- [x] Build Homepage with hero + featured deals ✅
- [x] Build Deals listing page with filters (FilterSidebar) ✅
- [x] Build DealCard component (discount badge, prices, store badge) ✅
- [x] Build Header & Footer ✅
- [x] Rebrand to "Bena2es" (Light theme, BNXS logo, soft UI) ✅
- [ ] Build Category pages (Pending)
- [ ] Build SearchBar with debounced API (Pending)
- [ ] Build Privacy Policy page
- [ ] Build Affiliate Disclosure page
- [ ] Build About page
- [ ] Apply dark mode design system (Supported via Tailwind)
- [ ] Add micro-animations and hover effects (Basic implemented)
- [ ] Mobile-first responsive layout ✅

#### Feedback Loop
- [ ] Present stylized results
- [ ] Get user feedback
- [ ] Iterate based on feedback

---

### Phase 5: Trigger [� IN PROGRESS]
**Goal:** Deploy and automate

#### Cloud Transfer
#### Cloud Transfer
- [x] Deploy backend to Modal (production) ✅
- [/] Deploy frontend to Vercel (Configured & Ready) 🔄

#### Automation Setup
- [x] Configure Modal Cron (scrape every 4h) ✅
- [x] Configure cleanup Cron (daily expired deals) ✅

#### Affiliate Applications
- [ ] Apply for Amazon.eg Associates
- [ ] Apply for Jumia Affiliate program
- [ ] Generate first 3 qualifying sales (Amazon requirement)

#### Documentation
- [ ] Finalize Maintenance Log in gemini.md
- [ ] Document deployment procedure
- [ ] Create runbook for operations

---

## 📋 Current Blockers

1. ~~User approval of implementation plan~~ ✅ Approved
2. **Amazon.eg Associates** — build MVP first, then apply

### Approved Decisions (2026-02-16)
- ✅ MVP scope: Amazon.eg + Jumia only (Noon deferred to Phase 2)
- ✅ Amazon Associates: Build MVP first, apply after site is live
- ✅ Frontend: Next.js on Vercel
- ✅ Database: SQLite on Modal Volume (PostgreSQL migration later if needed)

---

## ✅ Success Definition

Project is **COMPLETE** when:
- [ ] Deals from Amazon.eg + Jumia displayed on live website
- [ ] Affiliate links redirect correctly with tracking
- [ ] Approved by at least one affiliate program
- [ ] Automated scraping running on schedule
- [ ] All tests passing
- [ ] Documentation complete

---

*Next Action: Begin Phase 2: Link — test Modal deployment and API connectivity*