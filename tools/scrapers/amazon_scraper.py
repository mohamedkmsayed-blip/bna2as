"""
Sooq Deals — Amazon.eg Scraper
================================
Scrapes deals from Amazon.eg using two strategies:
1. Primary: Amazon Product Advertising API v5 (requires Associates credentials)
2. Fallback: Scrape Amazon.eg deals pages directly

Environment variables required:
  AMAZON_ACCESS_KEY, AMAZON_SECRET_KEY, AMAZON_PARTNER_TAG
"""

import os
import re
import logging
import hashlib
import hmac
import json
from datetime import datetime, timezone
from typing import Optional
from urllib.parse import urlencode, urlparse, parse_qs, urljoin

from bs4 import BeautifulSoup

from .base import BaseScraper, Product

logger = logging.getLogger(__name__)

# Amazon.eg deal/sale page URLs
AMAZON_DEALS_URLS = [
    "https://www.amazon.eg/-/en/gp/goldbox",
    "https://www.amazon.eg/-/en/deals",
]

# Category browse nodes for amazon.eg
AMAZON_CATEGORIES = {
    "electronics": "18509126031",
    "computers": "18509130031",
    "mobile-phones": "18509134031",
    "home-kitchen": "18509138031",
    "fashion": "18509142031",
    "beauty": "18509146031",
    "sports": "18509150031",
}


class AmazonScraper(BaseScraper):
    """
    Amazon.eg scraper with PA-API v5 primary and web scraping fallback.
    """

    SOURCE = "amazon"

    def __init__(self, min_discount: float = 15.0):
        super().__init__(min_discount)
        self.partner_tag = os.environ.get("AMAZON_PARTNER_TAG", "")
        self.access_key = os.environ.get("AMAZON_ACCESS_KEY", "")
        self.secret_key = os.environ.get("AMAZON_SECRET_KEY", "")
        self.has_api_keys = bool(self.access_key and self.secret_key and self.partner_tag)

    def scrape(self) -> list[Product]:
        """
        Scrape Amazon.eg for deals.
        Uses PA-API if credentials available, otherwise falls back to web scraping.
        """
        if self.has_api_keys:
            logger.info("[amazon] Using PA-API v5")
            return self._scrape_via_api()
        else:
            logger.info("[amazon] No API keys — falling back to web scraping")
            return self._scrape_via_web()

    def build_affiliate_url(self, original_url: str) -> str:
        """Append Amazon Associates tag to URL."""
        if not self.partner_tag:
            return original_url

        # Parse existing URL
        parsed = urlparse(original_url)
        params = parse_qs(parsed.query)
        params["tag"] = [self.partner_tag]

        # Rebuild URL with tag
        new_query = urlencode(params, doseq=True)
        return f"{parsed.scheme}://{parsed.netloc}{parsed.path}?{new_query}"

    # ----- PA-API v5 Strategy -----

    def _scrape_via_api(self) -> list[Product]:
        """
        Use Amazon PA-API v5 SearchItems to find deals.
        Note: Full PA-API signing is complex — this is a simplified version.
        For production, consider using a library like `python-amazon-paapi`.
        """
        # TODO: Implement full PA-API v5 signing when credentials are ready.
        # For now, fall back to web scraping.
        logger.warning("[amazon] PA-API v5 integration pending credentials — using web fallback")
        return self._scrape_via_web()

    # ----- Web Scraping Fallback -----

    def _scrape_via_web(self) -> list[Product]:
        """Scrape Amazon.eg deals pages for discounted products."""
        products = []

        for url in AMAZON_DEALS_URLS:
            response = self.safe_request(url)
            if not response:
                continue

            soup = BeautifulSoup(response.text, "lxml")
            product_cards = self._find_product_cards(soup)

            for card in product_cards:
                try:
                    product = self._parse_product_card(card)
                    if product:
                        products.append(product)
                except Exception as e:
                    logger.debug(f"[amazon] Failed to parse card: {e}")
                    continue

        logger.info(f"[amazon] Scraped {len(products)} products from deals pages")
        return products

    def _find_product_cards(self, soup: BeautifulSoup) -> list:
        """Find product card elements on Amazon deals pages."""
        # Amazon uses various class patterns for deal cards
        selectors = [
            'div[data-component-type="s-search-result"]',
            'div.DealCard-module__dealCard',
            'div[data-deal-id]',
            'div.a-section.octopus-dlp-asin-section',
        ]
        cards = []
        for selector in selectors:
            found = soup.select(selector)
            if found:
                cards.extend(found)
                break
        return cards

    def _parse_product_card(self, card) -> Optional[Product]:
        """Parse a single product card into a Product model."""
        # Extract title
        title_el = card.select_one("h2 a span, .a-text-normal, .DealCard-module__title")
        if not title_el:
            return None
        title = title_el.get_text(strip=True)
        if not title or len(title) < 5:
            return None

        # Extract link
        link_el = card.select_one("h2 a, a.a-link-normal[href*='/dp/']")
        if not link_el or not link_el.get("href"):
            return None
        href = link_el["href"]
        if not href.startswith("http"):
            href = f"https://www.amazon.eg{href}"

        # Extract ASIN from URL
        asin = self._extract_asin(href)
        if not asin:
            return None

        # Extract prices
        current_price = self._extract_price(card, is_current=True)
        original_price = self._extract_price(card, is_current=False)

        if not current_price or current_price <= 0:
            return None

        # Calculate discount
        discount = self.calculate_discount(original_price, current_price)

        # Extract image
        img_el = card.select_one("img.s-image, img[data-a-hires], img.DealCard-module__image")
        image_url = img_el.get("src") or img_el.get("data-a-hires") if img_el else None

        # Extract rating
        rating = None
        rating_el = card.select_one("span.a-icon-alt, i.a-icon-star-small span")
        if rating_el:
            rating_match = re.search(r'(\d+\.?\d*)', rating_el.get_text())
            if rating_match:
                rating = float(rating_match.group(1))

        # Extract review count
        review_count = None
        review_el = card.select_one("span.a-size-base.s-underline-text, span[data-component-type='s-review']")
        if review_el:
            count_match = re.search(r'([\d,]+)', review_el.get_text())
            if count_match:
                review_count = int(count_match.group(1).replace(",", ""))

        product_url = href.split("?")[0]  # Clean URL
        affiliate_url = self.build_affiliate_url(product_url)

        return Product(
            id=self.make_product_id(asin),
            source=self.SOURCE,
            external_id=asin,
            title=title,
            image_url=image_url,
            category=self._guess_category(title),
            url=product_url,
            affiliate_url=affiliate_url,
            current_price=current_price,
            original_price=original_price,
            discount_pct=discount,
            rating=rating,
            review_count=review_count,
        )

    def _extract_asin(self, url: str) -> Optional[str]:
        """Extract ASIN from Amazon URL (e.g., /dp/B09V3KXJPB)."""
        match = re.search(r'/dp/([A-Z0-9]{10})', url)
        if match:
            return match.group(1)
        match = re.search(r'/product/([A-Z0-9]{10})', url)
        if match:
            return match.group(1)
        return None

    def _extract_price(self, card, is_current: bool = True) -> Optional[float]:
        """Extract current or original price from a product card."""
        if is_current:
            selectors = [
                "span.a-price:not(.a-text-price) span.a-offscreen",
                "span.a-price-whole",
                "span.a-color-price",
            ]
        else:
            selectors = [
                "span.a-price.a-text-price span.a-offscreen",
                "span.a-text-strike",
                "span.priceBlockStrikePriceString",
            ]

        for selector in selectors:
            el = card.select_one(selector)
            if el:
                text = el.get_text(strip=True)
                price_match = re.search(r'([\d,]+\.?\d*)', text.replace(",", ""))
                if price_match:
                    return float(price_match.group(1))
        return None

    def _guess_category(self, title: str) -> Optional[str]:
        """Simple keyword-based category guess."""
        title_lower = title.lower()
        category_keywords = {
            "electronics": ["phone", "samsung", "iphone", "apple", "headphone", "earbuds", "speaker", "tv", "monitor"],
            "computers": ["laptop", "keyboard", "mouse", "ssd", "ram", "usb", "hard drive"],
            "home-kitchen": ["blender", "mixer", "iron", "vacuum", "fan", "air conditioner"],
            "fashion": ["shirt", "dress", "shoes", "sneakers", "watch", "bag", "handbag"],
            "beauty": ["cream", "shampoo", "perfume", "makeup", "skincare", "serum"],
            "sports": ["gym", "fitness", "yoga", "running", "water bottle", "dumbbell"],
            "gaming": ["ps5", "xbox", "controller", "gaming", "console"],
        }
        for category, keywords in category_keywords.items():
            if any(kw in title_lower for kw in keywords):
                return category
        return "other"
