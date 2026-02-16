"""
Sooq Deals — Database Layer
============================
SQLite database schema, initialization, and CRUD operations.
All database access goes through this module.
"""

import sqlite3
import json
from datetime import datetime, timezone
from typing import Optional

# ---------------------------------------------------------------------------
# Schema
# ---------------------------------------------------------------------------

SCHEMA_SQL = """
-- Products: master record per product
CREATE TABLE IF NOT EXISTS products (
    id              TEXT PRIMARY KEY,
    source          TEXT NOT NULL,
    external_id     TEXT NOT NULL,
    title           TEXT NOT NULL,
    title_ar        TEXT,
    description     TEXT,
    image_url       TEXT,
    category        TEXT,
    brand           TEXT,
    url             TEXT NOT NULL,
    affiliate_url   TEXT,
    current_price   REAL NOT NULL,
    original_price  REAL,
    discount_pct    REAL,
    currency        TEXT DEFAULT 'EGP',
    rating          REAL,
    review_count    INTEGER,
    in_stock        INTEGER DEFAULT 1,
    is_active       INTEGER DEFAULT 1,
    first_seen      TEXT NOT NULL,
    last_updated    TEXT NOT NULL,
    created_at      TEXT DEFAULT CURRENT_TIMESTAMP
);

-- Click tracking for analytics
CREATE TABLE IF NOT EXISTS clicks (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id  TEXT NOT NULL,
    user_ip     TEXT,
    user_agent  TEXT,
    referrer    TEXT,
    clicked_at  TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (product_id) REFERENCES products(id)
);

-- Scrape history for monitoring
CREATE TABLE IF NOT EXISTS scrape_logs (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    source          TEXT NOT NULL,
    status          TEXT NOT NULL,
    products_found  INTEGER DEFAULT 0,
    deals_found     INTEGER DEFAULT 0,
    error_message   TEXT,
    duration_sec    REAL,
    scraped_at      TEXT DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for fast queries
CREATE INDEX IF NOT EXISTS idx_products_source ON products(source);
CREATE INDEX IF NOT EXISTS idx_products_category ON products(category);
CREATE INDEX IF NOT EXISTS idx_products_discount ON products(discount_pct);
CREATE INDEX IF NOT EXISTS idx_products_active ON products(is_active);
CREATE INDEX IF NOT EXISTS idx_products_source_active ON products(source, is_active);
CREATE INDEX IF NOT EXISTS idx_clicks_product ON clicks(product_id);
CREATE INDEX IF NOT EXISTS idx_clicks_time ON clicks(clicked_at);
"""


# ---------------------------------------------------------------------------
# Database Connection & Init
# ---------------------------------------------------------------------------

def get_connection(db_path: str) -> sqlite3.Connection:
    """Get a SQLite connection with row factory enabled."""
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def init_db(db_path: str) -> None:
    """Create all tables and indexes if they don't exist."""
    conn = get_connection(db_path)
    conn.executescript(SCHEMA_SQL)
    conn.commit()
    conn.close()


# ---------------------------------------------------------------------------
# Product CRUD
# ---------------------------------------------------------------------------

def upsert_product(db_path: str, product: dict) -> bool:
    """
    Insert or update a product. Returns True if new, False if updated.
    Deduplicates by product['id'] (format: "{source}_{external_id}").
    """
    conn = get_connection(db_path)
    now = datetime.now(timezone.utc).isoformat()

    # Check if product exists
    existing = conn.execute(
        "SELECT id, current_price FROM products WHERE id = ?",
        (product["id"],)
    ).fetchone()

    if existing:
        # Update existing product
        conn.execute("""
            UPDATE products SET
                title = ?, image_url = ?, category = ?, brand = ?,
                url = ?, affiliate_url = ?,
                current_price = ?, original_price = ?, discount_pct = ?,
                rating = ?, review_count = ?,
                in_stock = ?, is_active = 1, last_updated = ?
            WHERE id = ?
        """, (
            product.get("title"), product.get("image_url"),
            product.get("category"), product.get("brand"),
            product.get("url"), product.get("affiliate_url"),
            product["current_price"], product.get("original_price"),
            product.get("discount_pct"),
            product.get("rating"), product.get("review_count"),
            product.get("in_stock", 1), now, product["id"]
        ))
        conn.commit()
        conn.close()
        return False
    else:
        # Insert new product
        conn.execute("""
            INSERT INTO products (
                id, source, external_id, title, title_ar, description,
                image_url, category, brand, url, affiliate_url,
                current_price, original_price, discount_pct, currency,
                rating, review_count, in_stock, is_active,
                first_seen, last_updated
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1, ?, ?)
        """, (
            product["id"], product["source"], product["external_id"],
            product["title"], product.get("title_ar"),
            product.get("description"), product.get("image_url"),
            product.get("category"), product.get("brand"),
            product["url"], product.get("affiliate_url"),
            product["current_price"], product.get("original_price"),
            product.get("discount_pct"), product.get("currency", "EGP"),
            product.get("rating"), product.get("review_count"),
            product.get("in_stock", 1), now, now
        ))
        conn.commit()
        conn.close()
        return True


def get_active_deals(
    db_path: str,
    source: Optional[str] = None,
    category: Optional[str] = None,
    min_discount: float = 15.0,
    sort: str = "newest",
    page: int = 1,
    limit: int = 20,
    search: Optional[str] = None,
) -> dict:
    """
    Fetch active deals with filtering, sorting, and pagination.
    Returns: {"deals": [...], "total": int, "page": int, "pages": int}
    """
    conn = get_connection(db_path)

    where_clauses = ["is_active = 1", "discount_pct >= ?"]
    params: list = [min_discount]

    if source:
        where_clauses.append("source = ?")
        params.append(source)

    if category:
        where_clauses.append("category = ?")
        params.append(category)

    if search:
        where_clauses.append("(title LIKE ? OR brand LIKE ?)")
        search_term = f"%{search}%"
        params.extend([search_term, search_term])

    where_sql = " AND ".join(where_clauses)

    # Sort mapping
    sort_map = {
        "newest": "last_updated DESC",
        "discount": "discount_pct DESC",
        "price_low": "current_price ASC",
        "price_high": "current_price DESC",
        "popular": "review_count DESC",
    }
    order_sql = sort_map.get(sort, "last_updated DESC")

    # Get total count
    count_row = conn.execute(
        f"SELECT COUNT(*) as total FROM products WHERE {where_sql}",
        params
    ).fetchone()
    total = count_row["total"]

    # Get paginated results
    offset = (page - 1) * limit
    rows = conn.execute(
        f"""SELECT * FROM products
            WHERE {where_sql}
            ORDER BY {order_sql}
            LIMIT ? OFFSET ?""",
        params + [limit, offset]
    ).fetchall()

    deals = [dict(row) for row in rows]
    pages = max(1, (total + limit - 1) // limit)

    conn.close()
    return {
        "deals": deals,
        "total": total,
        "page": page,
        "pages": pages,
    }


def get_product_by_id(db_path: str, product_id: str) -> Optional[dict]:
    """Get a single product by ID."""
    conn = get_connection(db_path)
    row = conn.execute(
        "SELECT * FROM products WHERE id = ?", (product_id,)
    ).fetchone()
    conn.close()
    return dict(row) if row else None


def get_categories(db_path: str) -> list[dict]:
    """Get all categories with deal counts."""
    conn = get_connection(db_path)
    rows = conn.execute("""
        SELECT category, COUNT(*) as count
        FROM products
        WHERE is_active = 1 AND category IS NOT NULL
        GROUP BY category
        ORDER BY count DESC
    """).fetchall()
    conn.close()
    return [{"name": row["category"], "count": row["count"]} for row in rows]


def get_stats(db_path: str) -> dict:
    """Get aggregate statistics for the public stats endpoint."""
    conn = get_connection(db_path)

    stats = {}
    row = conn.execute("""
        SELECT
            COUNT(*) as total_deals,
            COUNT(DISTINCT source) as sources,
            AVG(discount_pct) as avg_discount,
            MAX(last_updated) as last_updated
        FROM products WHERE is_active = 1
    """).fetchone()

    stats = {
        "total_deals": row["total_deals"],
        "sources": row["sources"],
        "avg_discount": round(row["avg_discount"] or 0, 1),
        "last_updated": row["last_updated"],
    }

    # Clicks in last 24h
    click_row = conn.execute("""
        SELECT COUNT(*) as clicks_24h FROM clicks
        WHERE clicked_at >= datetime('now', '-1 day')
    """).fetchone()
    stats["clicks_24h"] = click_row["clicks_24h"]

    conn.close()
    return stats


# ---------------------------------------------------------------------------
# Click Tracking
# ---------------------------------------------------------------------------

def log_click(
    db_path: str,
    product_id: str,
    user_ip: Optional[str] = None,
    user_agent: Optional[str] = None,
    referrer: Optional[str] = None,
) -> None:
    """Log a click event for a product."""
    conn = get_connection(db_path)
    conn.execute(
        """INSERT INTO clicks (product_id, user_ip, user_agent, referrer)
           VALUES (?, ?, ?, ?)""",
        (product_id, user_ip, user_agent, referrer)
    )
    conn.commit()
    conn.close()


# ---------------------------------------------------------------------------
# Scrape Logging
# ---------------------------------------------------------------------------

def log_scrape(
    db_path: str,
    source: str,
    status: str,
    products_found: int = 0,
    deals_found: int = 0,
    error_message: Optional[str] = None,
    duration_sec: float = 0.0,
) -> None:
    """Log a scrape run result."""
    conn = get_connection(db_path)
    conn.execute(
        """INSERT INTO scrape_logs
           (source, status, products_found, deals_found, error_message, duration_sec)
           VALUES (?, ?, ?, ?, ?, ?)""",
        (source, status, products_found, deals_found, error_message, duration_sec)
    )
    conn.commit()
    conn.close()


# ---------------------------------------------------------------------------
# Maintenance
# ---------------------------------------------------------------------------

def deactivate_stale_deals(db_path: str, hours: int = 48) -> int:
    """Mark deals not updated in N hours as inactive. Returns count."""
    conn = get_connection(db_path)
    cursor = conn.execute(
        f"""UPDATE products SET is_active = 0
            WHERE is_active = 1
            AND last_updated < datetime('now', '-{hours} hours')"""
    )
    count = cursor.rowcount
    conn.commit()
    conn.close()
    return count
