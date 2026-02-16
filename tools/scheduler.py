"""
Sooq Deals — Scheduler (Modal Cron Jobs)
==========================================
Scheduled functions that run scrapers and maintain the database.
"""

import time
import logging

import modal

from app import app, image, volume, DB_PATH, VOLUME_MOUNT
from database import init_db, upsert_product, log_scrape, deactivate_stale_deals

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


# ---------------------------------------------------------------------------
# Scrape All Sources (Every 4 Hours)
# ---------------------------------------------------------------------------

@app.function(
    image=image,
    volumes={VOLUME_MOUNT: volume},
    schedule=modal.Period(hours=4),
    timeout=600,  # 10 minute timeout
    secrets=[modal.Secret.from_dotenv()],
)
def scrape_all():
    """
    Run all active scrapers, filter for deals, and upsert into the database.
    Runs every 4 hours via Modal Cron.
    """
    return _run_extraction()


def _run_extraction():
    """Shared scraping logic."""
    from scrapers.amazon_scraper import AmazonScraper
    from scrapers.jumia_scraper import JumiaScraper

    init_db(DB_PATH)

    scrapers = [
        ("amazon", AmazonScraper),
        ("jumia", JumiaScraper),
    ]

    total_new = 0
    total_updated = 0

    for source_name, ScraperClass in scrapers:
        start_time = time.time()
        try:
            with ScraperClass() as scraper:
                deals = scraper.run()

            new_count = 0
            update_count = 0

            for deal in deals:
                is_new = upsert_product(DB_PATH, deal.to_db_dict())
                if is_new:
                    new_count += 1
                else:
                    update_count += 1

            elapsed = time.time() - start_time
            log_scrape(
                db_path=DB_PATH,
                source=source_name,
                status="success",
                products_found=len(deals),
                deals_found=new_count + update_count,
                duration_sec=elapsed,
            )

            total_new += new_count
            total_updated += update_count

            logger.info(
                f"[{source_name}] Done in {elapsed:.1f}s — "
                f"{new_count} new, {update_count} updated"
            )

        except Exception as e:
            elapsed = time.time() - start_time
            logger.error(f"[{source_name}] Scraper failed: {e}")
            log_scrape(
                db_path=DB_PATH,
                source=source_name,
                status="failed",
                error_message=str(e),
                duration_sec=elapsed,
            )

    # Commit volume changes
    volume.commit()

    logger.info(
        f"[scheduler] Scrape complete — {total_new} new deals, "
        f"{total_updated} updated deals"
    )
    return {"new": total_new, "updated": total_updated}


# ---------------------------------------------------------------------------
# Cleanup Expired Deals (Daily)
# ---------------------------------------------------------------------------

@app.function(
    image=image,
    volumes={VOLUME_MOUNT: volume},
    schedule=modal.Period(hours=24),
    timeout=120,
)
def cleanup_expired():
    """
    Mark deals not updated in 48 hours as inactive.
    Runs daily via Modal Cron.
    """
    init_db(DB_PATH)

    deactivated = deactivate_stale_deals(DB_PATH, hours=48)
    volume.commit()

    logger.info(f"[cleanup] Deactivated {deactivated} stale deals")
    return {"deactivated": deactivated}


# ---------------------------------------------------------------------------
# Manual Scrape Trigger (On-Demand)
# ---------------------------------------------------------------------------

@app.function(
    image=image,
    volumes={VOLUME_MOUNT: volume},
    timeout=600,
    secrets=[modal.Secret.from_dotenv()],
)
def manual_scrape():
    """
    Manually trigger a scrape run (for testing or on-demand refresh).
    Call via: modal run scheduler.py::manual_scrape
    """
    return _run_extraction()


# ---------------------------------------------------------------------------
# Clear Database (On-Demand)
# ---------------------------------------------------------------------------

@app.function(
    image=image,
    volumes={VOLUME_MOUNT: volume},
    timeout=60,
)
def clear_database():
    """
    Clear all products and logs from database (fresh start).
    Call via: modal run scheduler.py::clear_database
    """
    import sqlite3
    
    init_db(DB_PATH)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Count before deletion
    cursor.execute("SELECT COUNT(*) FROM products")
    product_count = cursor.fetchone()[0]
    
    # Delete all data
    cursor.execute("DELETE FROM products")
    cursor.execute("DELETE FROM clicks")
    cursor.execute("DELETE FROM scrape_logs")
    
    conn.commit()
    conn.close()
    volume.commit()
    
    logger.info(f"[clear_database] Removed {product_count} products")
    return {"cleared": product_count}
