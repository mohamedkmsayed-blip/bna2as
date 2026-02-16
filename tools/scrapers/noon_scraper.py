"""
Sooq Deals — Noon Egypt Scraper (Phase 2)
===========================================
Placeholder for Noon scraper — deferred due to lack of public API.
Will be implemented in Phase 2 using web scraping.

Environment variables required:
  NOON_AFFILIATE_CODE
"""

import os
import logging
from typing import Optional

from .base import BaseScraper, Product

logger = logging.getLogger(__name__)


class NoonScraper(BaseScraper):
    """
    Noon Egypt scraper — Phase 2 implementation.
    Currently a placeholder; will scrape noon.com/egypt-en/deals/.
    """

    SOURCE = "noon"

    def __init__(self, min_discount: float = 15.0):
        super().__init__(min_discount)
        self.affiliate_code = os.environ.get("NOON_AFFILIATE_CODE", "")

    def scrape(self) -> list[Product]:
        """Noon scraping is not yet implemented (Phase 2)."""
        logger.info("[noon] Scraper not yet implemented — deferred to Phase 2")
        return []

    def build_affiliate_url(self, original_url: str) -> str:
        """Append Noon affiliate code to URL."""
        if not self.affiliate_code:
            return original_url
        separator = "&" if "?" in original_url else "?"
        return f"{original_url}{separator}utm_source=affiliate&utm_medium={self.affiliate_code}"
