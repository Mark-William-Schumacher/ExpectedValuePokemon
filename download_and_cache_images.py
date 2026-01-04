"""
Script to download card images and update the cache with local_image fields.
"""
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("=" * 60)
print("Image Download & Cache Update Script")
print("=" * 60)

# Step 1: Refresh the cache with local_image field
print("\n1. Refreshing card cache with local_image field...")
from web.backend.containers import AppContainer

container = AppContainer()
cache_service = container.card_cache_service()
print("   Invalidating old cache...")
cache_service.invalidate_cache()
print("   Generating new cache...")
cards = cache_service.refresh_cache()
print(f"   ✓ Cache refreshed with {len(cards)} cards")

# Check if local_image is now present
if cards and 'local_image' in cards[0]:
    print(f"   ✓ local_image field present: {cards[0]['local_image']}")
else:
    print("   ⚠ Warning: local_image field not found in cache")

# Step 2: Download images to the web backend static folder
print("\n2. Downloading images to web/backend/static/assets/images...")
from core_module.prelaunch.image_downloader import download_images_to_web_root

download_images_to_web_root(cards)
print("   ✓ Image download complete")

print("\n" + "=" * 60)
print("✓ ALL DONE! Images are ready to serve from Flask backend")
print("=" * 60)
print("\nImages location: web/backend/static/assets/images/")
print("Access via: http://127.0.0.1:5000/static/assets/images/<filename>")

