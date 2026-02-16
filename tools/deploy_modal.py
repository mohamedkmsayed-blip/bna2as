"""
Deploy script using Modal Python API directly
"""
import modal
import sys
sys.path.insert(0, '.')

# Import the app
from app import app

print("Deploying to Modal...")
try:
    # This will trigger deployment
    app.deploy()
    print("✓ Deployment complete!")
except Exception as e:
    print(f"Error: {e}")
    sys.exit(1)
