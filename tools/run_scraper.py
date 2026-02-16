"""
Manual scraper execution script
Run this to populate the database with fresh deals
"""

import sys
sys.path.insert(0, '.')

from scrapers.amazon_scraper import AmazonScraper
from database import get_db_connection
import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

def main():
    print("=" * 60)
    print("MANUAL SCRAPER EXECUTION")
    print("=" * 60)
    
    # Run Amazon scraper
    print("\n1. Running Amazon scraper...")
    amazon_scraper = AmazonScraper(min_discount=15)
    amazon_deals = amazon_scraper.run()
    print(f"   Found {len(amazon_deals)} Amazon deals")
    
    # Save to database
    if amazon_deals:
        print("\n2. Saving to database...")
        conn = get_db_connection("/data/sooq_deals.db")
        cursor = conn.cursor()
        
        # Import database functions
        from database import upsert_product
        
        saved_count = 0
        for deal in amazon_deals:
            try:
                upsert_product(conn, deal.to_db_dict())
                saved_count += 1
            except Exception as e:
                print(f"   Error saving {deal.external_id}: {e}")
        
        conn.commit()
        conn.close()
        print(f"   Saved {saved_count} deals to database")
    else:
        print("   No deals to save")
    
    print("\n" + "=" * 60)
    print(f"SCRAPING COMPLETE: {len(amazon_deals)} deals saved")
    print("=" * 60)

if __name__ == "__main__":
    main()
