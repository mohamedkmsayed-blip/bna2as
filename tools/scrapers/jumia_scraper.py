"""
Sooq Deals — Jumia Egypt Scraper
==================================
Scrapes deals from jumia.com.eg using two strategies:
1. Primary: Jumia KOL Affiliates API (unofficial, via KOL account)
2. Fallback: Scrape Jumia deals/sale pages directly

Environment variables required:
  JUMIA_KOL_ID, JUMIA_AFFILIATE_TAG
"""

import os
import re
import logging
import time
from typing import Optional
from urllib.parse import urlencode, urlparse, parse_qs

from bs4 import BeautifulSoup

from .base import BaseScraper, Product

logger = logging.getLogger(__name__)

# Jumia Egypt deals page URLs
JUMIA_DEALS_URLS = [
    "https://www.jumia.com.eg/mlp-deals/",
    "https://www.jumia.com.eg/flash-sales/",
    "https://www.jumia.com.eg/sp-mega-deals/",
]

# Category pages to scrape (sorted by popularity in Egypt)
JUMIA_CATEGORY_URLS = {
    "phones-tablets": "https://www.jumia.com.eg/phones-tablets/",
    "electronics": "https://www.jumia.com.eg/electronics/",
    "computing": "https://www.jumia.com.eg/computing/",
    "home-office": "https://www.jumia.com.eg/home-office/",
    "health-beauty": "https://www.jumia.com.eg/health-beauty/",
    "fashion": "https://www.jumia.com.eg/category-fashion-by-jumia/",
    "appliances": "https://www.jumia.com.eg/appliances/",
    "gaming": "https://www.jumia.com.eg/gaming/",
    "sporting-goods": "https://www.jumia.com.eg/sporting-goods/",
}


class JumiaScraper(BaseScraper):
    """
    Jumia Egypt scraper with KOL API primary and web scraping fallback.
    Enhanced with realistic browser headers and session handling to bypass bot detection.
    """

    SOURCE = "jumia"

    def __init__(self, min_discount: float = 15.0):
        super().__init__(min_discount)
        self.kol_id = os.environ.get("JUMIA_KOL_ID", "")
        self.affiliate_tag = os.environ.get("JUMIA_AFFILIATE_TAG", "")
        self.has_kol_keys = bool(self.kol_id)
        
        # Enhanced headers to bypass Jumia bot detection
        self.client.headers.update({
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "en-US,en;q=0.9,ar;q=0.8",
            "Cache-Control": "max-age=0",
            "DNT": "1",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-User": "?1",
        })
        
        # Session cookie storage
        self.session_initialized = False

    def scrape(self) -> list[Product]:
        """
        Scrape Jumia Egypt for deals.
        Uses KOL API if credentials are available, otherwise web scraping.
        """
        if self.has_kol_keys:
            logger.info("[jumia] Using KOL Affiliates API")
            return self._scrape_via_kol_api()
        else:
            logger.info("[jumia] No KOL ID — using web scraping")
            return self._scrape_via_web()

    def build_affiliate_url(self, original_url: str) -> str:
        """Append Jumia affiliate tracking to URL."""
        if not self.affiliate_tag:
            return original_url

        # Jumia affiliate links typically use a query param
        separator = "&" if "?" in original_url else "?"
        return f"{original_url}{separator}tag={self.affiliate_tag}"

    # ----- KOL API Strategy -----

    def _scrape_via_kol_api(self) -> list[Product]:
        """
        Use Jumia KOL API to fetch products and generate affiliate links.
        API endpoint pattern: varies by implementation.
        """
        # TODO: Integrate with Jumia KOL API when credentials are ready.
        # The API provides product details and affiliate link generation.
        logger.warning("[jumia] KOL API integration pending — using web fallback")
        return self._scrape_via_web()

    # ----- Session Management -----

    def _init_session(self) -> bool:
        """
        Initialize session by visiting Jumia homepage to get cookies.
        This helps bypass bot detection.
        """
        if self.session_initialized:
            return True
        
        try:
            logger.info("[jumia] Initializing session...")
            
            # Visit homepage first to get session cookies
            home_url = "https://www.jumia.com.eg/"
            response = self.client.get(home_url, timeout=30)
            
            if response.status_code == 200:
                # Set referer for subsequent requests
                self.client.headers.update({
                    "Referer": "https://www.jumia.com.eg/"
                })
                self.session_initialized = True
                logger.info("[jumia] Session initialized successfully")
                return True
            else:
                logger.warning(f"[jumia] Failed to initialize session: HTTP {response.status_code}")
                return False
                
        except Exception as e:
            logger.warning(f"[jumia] Session initialization failed: {e}")
            return False

    # ----- Web Scraping Strategy -----

    def _scrape_via_web(self) -> list[Product]:
        """Scrape Jumia Egypt deals and category pages."""
        products = []
        seen_ids = set()
        
        # Try to initialize session first
        session_ok = self._init_session()
        if not session_ok:
            logger.warning("[jumia] Proceeding without session initialization")
        
        # Add random delay to look more human
        import random

        # Scrape deals pages first
        for url in JUMIA_DEALS_URLS:
            page_products = self._scrape_page(url)
            for p in page_products:
                if p.id not in seen_ids:
                    seen_ids.add(p.id)
                    products.append(p)
            # Random delay between 2-4 seconds
            time.sleep(random.uniform(2.0, 4.0))

        # Then scrape top category pages (page 1 only)
        for cat_name, cat_url in JUMIA_CATEGORY_URLS.items():
            # Add discount filter to category URLs
            filtered_url = f"{cat_url}?shipped_from=country_local&rating=4-5#catalog-listing"
            page_products = self._scrape_page(filtered_url, category=cat_name)
            for p in page_products:
                if p.id not in seen_ids:
                    seen_ids.add(p.id)
                    products.append(p)
            # Random delay between 2-4 seconds
            time.sleep(random.uniform(2.0, 4.0))

        logger.info(f"[jumia] Scraped {len(products)} total products")
        return products

    def _scrape_page(self, url: str, category: Optional[str] = None) -> list[Product]:
        """Scrape a single Jumia page for products."""
        # Try with current headers first
        response = self.safe_request(url)
        
        # If 403, try with mobile user agent
        if not response or response.status_code == 403:
            logger.info("[jumia] Trying mobile user agent...")
            original_ua = self.client.headers.get("User-Agent")
            self.client.headers.update({
                "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1"
            })
            response = self.safe_request(url)
            # Restore original UA
            if original_ua:
                self.client.headers.update({"User-Agent": original_ua})
        
        if not response:
            return []

        soup = BeautifulSoup(response.text, "lxml")
        products = []

        # Jumia product cards are in article tags or specific div classes
        cards = soup.select("article.prd, div.sku, a.core[href*='/mlp']")
        if not cards:
            # Try alternative selectors
            cards = soup.select("div[data-sku], div.sku.-gallery, section.card-b")

        for card in cards:
            try:
                product = self._parse_product_card(card, category)
                if product:
                    products.append(product)
            except Exception as e:
                logger.debug(f"[jumia] Failed to parse card: {e}")
                continue

        return products

    def _parse_product_card(self, card, category: Optional[str] = None) -> Optional[Product]:
        """Parse a Jumia product card into a Product model."""
        # Extract title
        title_el = card.select_one("h3.name, h3.title, div.name, span.name")
        if not title_el:
            return None
        title = title_el.get_text(strip=True)
        if not title or len(title) < 5:
            return None

        # Extract link and SKU
        link_el = card if card.name == "a" else card.select_one("a[href*='jumia.com.eg']")
        if not link_el:
            link_el = card.select_one("a.core, a[href]")
        if not link_el or not link_el.get("href"):
            return None

        href = link_el["href"]
        if not href.startswith("http"):
            href = f"https://www.jumia.com.eg{href}"

        # Extract SKU from URL or data attribute
        sku = card.get("data-sku") or self._extract_sku(href)
        if not sku:
            # Generate from URL hash
            sku = href.split("/")[-1].split(".")[0][:20]
        if not sku:
            return None

        # Extract prices
        current_price = self._extract_price(card, is_current=True)
        original_price = self._extract_price(card, is_current=False)

        if not current_price or current_price <= 0:
            return None

        # Calculate discount
        discount = self.calculate_discount(original_price, current_price)

        # Check for Jumia's own discount badge
        if discount is None:
            badge_el = card.select_one("span.bdg._dsct, div.bdg._dsct, span.tag._dsct")
            if badge_el:
                badge_match = re.search(r'(\d+)%', badge_el.get_text())
                if badge_match:
                    discount = float(badge_match.group(1))

        # Extract image
        img_el = card.select_one("img.img, img[data-src]")
        image_url = None
        if img_el:
            image_url = img_el.get("data-src") or img_el.get("src")

        # Extract rating
        rating = None
        rating_el = card.select_one("div.stars._s, div.rev")
        if rating_el:
            rating_match = re.search(r'(\d+\.?\d*)', rating_el.get_text())
            if rating_match:
                rating = float(rating_match.group(1))

        # Extract review count
        review_count = None
        review_el = card.select_one("div.rev, span.rev")
        if review_el:
            review_text = review_el.get_text()
            count_match = re.search(r'\((\d+)\)', review_text)
            if count_match:
                review_count = int(count_match.group(1))

        # Build affiliate URL
        clean_url = href.split("?")[0]
        affiliate_url = self.build_affiliate_url(clean_url)

        # Use provided category or guess from title
        final_category = category or self._guess_category(title)

        return Product(
            id=self.make_product_id(sku),
            source=self.SOURCE,
            external_id=sku,
            title=title,
            image_url=image_url,
            category=final_category,
            url=clean_url,
            affiliate_url=affiliate_url,
            current_price=current_price,
            original_price=original_price,
            discount_pct=discount,
            rating=rating,
            review_count=review_count,
        )

    def _extract_sku(self, url: str) -> Optional[str]:
        """Extract product SKU from Jumia URL."""
        # Jumia URLs often end with -PRODUCTSKU.html
        match = re.search(r'-([A-Z0-9]+)\.html', url, re.IGNORECASE)
        if match:
            return match.group(1)
        return None

    def _extract_price(self, card, is_current: bool = True) -> Optional[float]:
        """Extract current or original price from a Jumia product card."""
        if is_current:
            selectors = [
                "span.prc",
                "div.prc",
                "span.price",
                "span.new",
            ]
        else:
            selectors = [
                "span.old",
                "div.old",
                "span.s-prc-w span",
                "del",
            ]

        for selector in selectors:
            el = card.select_one(selector)
            if el:
                text = el.get_text(strip=True)
                # Extract numeric value (EGP prices can have commas)
                price_match = re.search(r'([\d,]+\.?\d*)', text.replace(",", ""))
                if price_match:
                    return float(price_match.group(1))
        return None

    def _guess_category(self, title: str) -> Optional[str]:
        """Simple keyword-based category classification."""
        title_lower = title.lower()
        category_map = {
            "phones-tablets": ["phone", "samsung", "iphone", "redmi", "oppo", "realme", "tablet", "ipad"],
            "electronics": ["headphone", "earbuds", "speaker", "tv", "camera", "charger", "cable", "power bank"],
            "computing": ["laptop", "keyboard", "mouse", "monitor", "ssd", "ram", "printer"],
            "home-office": ["desk", "chair", "shelf", "organizer", "lamp"],
            "health-beauty": ["cream", "shampoo", "perfume", "serum", "lotion", "sunscreen"],
            "fashion": ["shirt", "dress", "shoes", "sneakers", "bag", "watch", "sunglasses"],
            "appliances": ["blender", "mixer", "iron", "fan", "heater", "washing", "refrigerator"],
            "gaming": ["ps5", "xbox", "controller", "gaming", "console", "joystick"],
        }
        for category, keywords in category_map.items():
            if any(kw in title_lower for kw in keywords):
                return category
        return "other"
