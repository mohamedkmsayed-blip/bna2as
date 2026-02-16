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
# Note: Amazon redirects these to seasonal sale pages (e.g., /events/ramadansale)
AMAZON_DEALS_URLS = [
    "https://www.amazon.eg/gp/goldbox",  # Will redirect to current sale
    "https://www.amazon.eg/deals",  # Will redirect to current sale
    "https://www.amazon.eg/events/ramadansale",  # Direct seasonal sale page
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
        # Updated selectors for Amazon.eg current structure (2026)
        # Products use dcl-product-wrapper class on seasonal sale pages
        selectors = [
            '.dcl-product-wrapper',  # Current Amazon deals page structure
            'div[data-component-type="s-search-result"]',  # Search results (legacy)
            'div[data-asin]',  # Generic ASIN container
            '.s-result-item',  # Search result items
        ]
        cards = []
        for selector in selectors:
            found = soup.select(selector)
            if found:
                logger.info(f"[amazon] Found {len(found)} products with selector: {selector}")
                cards.extend(found)
                break
        return cards

    def _parse_product_card(self, card) -> Optional[Product]:
        """Parse a single product card into a Product model."""
        # Extract title - try multiple selectors
        title_selectors = [
            ".dcl-product-title",
            "[data-testid='product-title']",
            "h2 a",
            "a[href*='/dp/']",
            ".a-text-normal"
        ]
        title = None
        link_el = None
        for sel in title_selectors:
            title_el = card.select_one(sel)
            if title_el:
                title = title_el.get_text(strip=True)
                link_el = title_el if title_el.name == 'a' else title_el.select_one('a')
                if title and len(title) >= 5:
                    break
        
        if not title or len(title) < 5:
            return None

        # Extract link
        if not link_el:
            link_el = card.select_one("a[href*='/dp/'], a[href*='/gp/']")
        if not link_el or not link_el.get("href"):
            return None
        
        href = link_el["href"]
        if not href.startswith("http"):
            href = f"https://www.amazon.eg{href}"

        # Extract ASIN from URL or data attributes
        asin = self._extract_asin(href, card)
        if not asin:
            return None

        # Extract prices - updated selectors
        current_price = self._extract_price(card, is_current=True)
        original_price = self._extract_price(card, is_current=False)

        if not current_price or current_price <= 0:
            return None

        # Calculate discount
        discount = self.calculate_discount(original_price, current_price)

        # Extract image - updated selectors
        img_selectors = [
            "img.dcl-product-image",
            "img[data-src]",
            "img.s-image",
            "img[src*='m.media-amazon.com']",
            "img"
        ]
        image_url = None
        for sel in img_selectors:
            img_el = card.select_one(sel)
            if img_el:
                image_url = img_el.get("data-src") or img_el.get("src")
                if image_url:
                    break

        # Extract rating
        rating = None
        rating_el = card.select_one("span.a-icon-alt, i.a-icon-star-small span, .a-star-small")
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

    def _extract_asin(self, url: str, card=None) -> Optional[str]:
        """Extract ASIN from Amazon URL or card data attributes."""
        # First try to get ASIN from data attribute (new structure)
        if card:
            item_id = card.get('data-csa-c-item-id', '')
            if item_id:
                match = re.search(r'amzn1\.asin\.([A-Z0-9]{10})', item_id)
                if match:
                    return match.group(1)
            
            # Also check data-asin attribute
            asin = card.get('data-asin')
            if asin:
                return asin
        
        # Fallback to URL extraction
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
            # Try to find current/sale price
            selectors = [
                ".a-price:not(.a-text-price) .a-offscreen",
                ".a-price-whole",
                ".a-color-price",
                "[data-testid='price-current']",
            ]
            # Also search all text for EGP patterns
            text_content = card.get_text()
            prices_found = []
            for match in re.finditer(r'EGP\s*([\d,]+\.?\d*)', text_content):
                try:
                    price = float(match.group(1).replace(",", ""))
                    prices_found.append(price)
                except ValueError:
                    continue
            
            if prices_found:
                # Return the lowest price as current price
                return min(prices_found)
            
            # Fallback to selectors
            for selector in selectors:
                el = card.select_one(selector)
                if el:
                    text = el.get_text(strip=True)
                    price_match = re.search(r'([\d,]+\.?\d*)', text.replace(",", ""))
                    if price_match:
                        return float(price_match.group(1))
        else:
            # Try to find original/list price (usually higher)
            selectors = [
                ".a-price.a-text-price .a-offscreen",
                ".a-text-strike",
                ".priceBlockStrikePriceString",
                "[data-testid='price-list']",
            ]
            
            # Search for struck-through prices or "List:" text
            text_content = card.get_text()
            list_match = re.search(r'List:\s*EGP\s*([\d,]+\.?\d*)', text_content)
            if list_match:
                try:
                    return float(list_match.group(1).replace(",", ""))
                except ValueError:
                    pass
            
            # Look for prices in strikethrough elements
            strike_els = card.select("s, .a-text-strike, del")
            for el in strike_els:
                text = el.get_text(strip=True)
                price_match = re.search(r'([\d,]+\.?\d*)', text.replace(",", ""))
                if price_match:
                    try:
                        return float(price_match.group(1))
                    except ValueError:
                        continue
            
            # Fallback to selectors
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
