"""
Sooq Deals — Base Scraper
==========================
Abstract base class for all platform scrapers.
Handles discount calculation, filtering, normalization, and retry logic.
"""

import time
import httpx
import logging
from abc import ABC, abstractmethod
from datetime import datetime, timezone
from typing import Optional
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Data Models
# ---------------------------------------------------------------------------

class Product(BaseModel):
    """Normalized product model — all scrapers output this."""
    id: str                             # "{source}_{external_id}"
    source: str                         # "amazon", "jumia", "noon"
    external_id: str                    # Platform-specific ID
    title: str
    title_ar: Optional[str] = None
    description: Optional[str] = None
    image_url: Optional[str] = None
    category: Optional[str] = None
    brand: Optional[str] = None
    url: str                            # Original product URL
    affiliate_url: Optional[str] = None # URL with affiliate tag
    current_price: float                # In EGP
    original_price: Optional[float] = None
    discount_pct: Optional[float] = None
    currency: str = "EGP"
    rating: Optional[float] = None
    review_count: Optional[int] = None
    in_stock: int = 1
    is_active: int = 1

    def to_db_dict(self) -> dict:
        """Convert to dict for database insertion."""
        return self.model_dump()


# ---------------------------------------------------------------------------
# Base Scraper
# ---------------------------------------------------------------------------

class BaseScraper(ABC):
    """
    Abstract base class for all scrapers.
    Subclasses must implement: scrape() and build_affiliate_url().
    """

    SOURCE: str = ""  # Override in subclass: "amazon", "jumia", "noon"
    MIN_DISCOUNT: float = 15.0

    def __init__(self, min_discount: float = 15.0):
        self.MIN_DISCOUNT = min_discount
        self.client = httpx.Client(
            timeout=30.0,
            follow_redirects=True,
            headers={
                "User-Agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/131.0.0.0 Safari/537.36"
                ),
                "Accept-Language": "en-US,en;q=0.9,ar;q=0.8",
            },
        )
        self.results: list[Product] = []

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.client.close()

    # ----- Abstract methods -----

    @abstractmethod
    def scrape(self) -> list[Product]:
        """
        Fetch products and return normalized Product list.
        Must be implemented by each platform scraper.
        """
        ...

    @abstractmethod
    def build_affiliate_url(self, original_url: str) -> str:
        """
        Attach affiliate tag to the original product URL.
        Must be implemented by each platform scraper.
        """
        ...

    # ----- Shared helpers -----

    @staticmethod
    def calculate_discount(original_price: Optional[float], current_price: float) -> Optional[float]:
        """Calculate discount percentage. Returns None if not calculable."""
        if not original_price or original_price <= 0 or current_price <= 0:
            return None
        if current_price >= original_price:
            return None
        return round(((original_price - current_price) / original_price) * 100, 1)

    def filter_by_discount(self, products: list[Product]) -> list[Product]:
        """Keep only products with discount >= MIN_DISCOUNT."""
        filtered = []
        for p in products:
            if p.discount_pct is not None and p.discount_pct >= self.MIN_DISCOUNT:
                filtered.append(p)
        logger.info(
            f"[{self.SOURCE}] Filtered: {len(filtered)}/{len(products)} "
            f"products have >= {self.MIN_DISCOUNT}% discount"
        )
        return filtered

    def make_product_id(self, external_id: str) -> str:
        """Generate a unique product ID: '{source}_{external_id}'."""
        return f"{self.SOURCE}_{external_id}"

    def safe_request(self, url: str, retries: int = 3, delay: float = 2.0) -> Optional[httpx.Response]:
        """Make an HTTP GET request with retries."""
        for attempt in range(retries):
            try:
                response = self.client.get(url)
                response.raise_for_status()
                return response
            except httpx.HTTPStatusError as e:
                logger.warning(
                    f"[{self.SOURCE}] HTTP {e.response.status_code} on attempt "
                    f"{attempt + 1}/{retries}: {url}"
                )
                if e.response.status_code == 429:
                    time.sleep(delay * (attempt + 1) * 2)  # Longer backoff for rate limits
                else:
                    time.sleep(delay * (attempt + 1))
            except httpx.RequestError as e:
                logger.warning(
                    f"[{self.SOURCE}] Request error on attempt "
                    f"{attempt + 1}/{retries}: {e}"
                )
                time.sleep(delay * (attempt + 1))
        logger.error(f"[{self.SOURCE}] Failed after {retries} retries: {url}")
        return None

    def run(self) -> list[Product]:
        """
        Execute the scraper: scrape → calculate discounts → filter.
        Returns list of qualifying deals.
        """
        logger.info(f"[{self.SOURCE}] Starting scrape...")
        start_time = time.time()

        try:
            products = self.scrape()
            deals = self.filter_by_discount(products)
            elapsed = time.time() - start_time
            logger.info(
                f"[{self.SOURCE}] Complete in {elapsed:.1f}s — "
                f"{len(products)} products, {len(deals)} deals"
            )
            return deals
        except Exception as e:
            elapsed = time.time() - start_time
            logger.error(f"[{self.SOURCE}] Scrape failed after {elapsed:.1f}s: {e}")
            raise
