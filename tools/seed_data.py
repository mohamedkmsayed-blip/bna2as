import asyncio
import modal
from app import app, image, volume, DB_PATH, VOLUME_MOUNT
from database import upsert_product, init_db

@app.function(image=image, volumes={VOLUME_MOUNT: volume})
def seed_remote():
    print("Seeding database with test product...")
    
    # Ensure DB is initialized
    init_db(DB_PATH)
    
    # Create test product
    test_product = {
        "id": "test_seed_001",
        "source": "amazon",
        "external_id": "TEST001",
        "title": "Test Product - Xiaomi Redmi Note 13 (Seeded)",
        "url": "https://www.amazon.eg/dp/TEST001",
        # Use a real image URL that works
        "image": "https://m.media-amazon.com/images/I/71WDCOkEc0L._AC_SX679_.jpg",
        "current_price": 9999.0,
        "original_price": 12000.0,
        "discount_pct": 16.7,
        "rating": 4.5,
        "review_count": 100,
        "is_active": 1,
        "category": "electronics"
    }
    
    upsert_product(DB_PATH, test_product)
    print("Seeded test product: test_seed_001")

@app.local_entrypoint()
def main():
    seed_remote.remote()
