"""
Run scraper directly using Modal API
"""
import modal
import sys
sys.path.insert(0, '.')

# Import the scheduler function
from scheduler import scrape_all

print("Triggering scraper on Modal...")
print("This will run the Amazon scraper and save deals to the database.")
print()

try:
    # Call the function
    result = scrape_all.remote()
    print(f"Scraper completed successfully!")
    print(f"Result: {result}")
except Exception as e:
    print(f"Error running scraper: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
