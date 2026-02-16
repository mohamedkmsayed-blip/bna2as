"""
Sooq Deals — FastAPI Routes
=============================
REST API endpoints for the frontend to consume.
Deployed as a Modal web endpoint.
"""

import logging
from typing import Optional

from fastapi import FastAPI, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse, JSONResponse

from app import app as modal_app, image, volume, DB_PATH, VOLUME_MOUNT
from database import (
    init_db, get_active_deals, get_product_by_id,
    get_categories, get_stats, log_click,
)

import modal

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# FastAPI App
# ---------------------------------------------------------------------------

web_app = FastAPI(
    title="Sooq Deals API",
    description="Egyptian deals aggregator — Amazon.eg, Jumia, Noon",
    version="1.0.0",
)

# CORS — allow frontend origins
web_app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:3001",
        "https://sooqdeals.com",
        "https://www.sooqdeals.com",
    ],
    allow_credentials=True,
    allow_methods=["GET"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# API Routes
# ---------------------------------------------------------------------------

@web_app.get("/api/deals")
async def list_deals(
    source: Optional[str] = Query(None, description="Filter by source: amazon, jumia, noon"),
    category: Optional[str] = Query(None, description="Filter by category"),
    min_discount: float = Query(15.0, ge=0, le=100, description="Minimum discount %"),
    sort: str = Query("newest", description="Sort: newest, discount, price_low, price_high, popular"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    q: Optional[str] = Query(None, description="Search query"),
):
    """List active deals with filtering, sorting, and pagination."""
    result = get_active_deals(
        db_path=DB_PATH,
        source=source,
        category=category,
        min_discount=min_discount,
        sort=sort,
        page=page,
        limit=limit,
        search=q,
    )
    return result


@web_app.get("/api/deals/{product_id}")
async def get_deal(product_id: str):
    """Get details for a single deal."""
    product = get_product_by_id(DB_PATH, product_id)
    if not product:
        return JSONResponse(status_code=404, content={"error": "Deal not found"})
    return product


@web_app.get("/api/categories")
async def list_categories():
    """Get list of categories with deal counts."""
    categories = get_categories(DB_PATH)
    return {"categories": categories}


@web_app.get("/api/search")
async def search_deals(
    q: str = Query(..., min_length=2, description="Search query"),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
):
    """Search deals by title or brand."""
    result = get_active_deals(
        db_path=DB_PATH,
        search=q,
        page=page,
        limit=limit,
        sort="discount",
    )
    return result


@web_app.get("/api/stats")
async def public_stats():
    """Public stats: total deals, sources, average discount, last updated."""
    stats = get_stats(DB_PATH)
    return stats


@web_app.get("/go/{product_id}")
async def redirect_to_deal(product_id: str, request: Request):
    """
    Track click and redirect user to the affiliate URL.
    This is the monetization endpoint — every deal click goes through here.
    """
    product = get_product_by_id(DB_PATH, product_id)
    if not product:
        return JSONResponse(status_code=404, content={"error": "Deal not found"})

    # Log the click
    log_click(
        db_path=DB_PATH,
        product_id=product_id,
        user_ip=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
        referrer=request.headers.get("referer"),
    )

    # Redirect to affiliate URL (or original URL if no affiliate link)
    target_url = product.get("affiliate_url") or product["url"]
    return RedirectResponse(url=target_url, status_code=302)


@web_app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "ok", "service": "sooq-deals-api"}


# ---------------------------------------------------------------------------
# Modal Web Endpoint
# ---------------------------------------------------------------------------

@modal_app.function(
    image=image,
    volumes={VOLUME_MOUNT: volume},
    secrets=[modal.Secret.from_dotenv()],
)
@modal.asgi_app()
def api():
    """Deploy FastAPI as a Modal ASGI web endpoint."""
    # Initialize database on cold start
    init_db(DB_PATH)
    return web_app

# Expose app for Modal CLI
app = modal_app
