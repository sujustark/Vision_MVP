import requests
import os
import time
import sys

# Configuration
BASE_URL = "http://localhost:8000/api/v1"
SAMPLE_IMAGES_DIR = r"D:\Vision_MVP\sample_images"
# Ensure sample images exist
if not os.path.exists(SAMPLE_IMAGES_DIR):
    print(f"Sample images dir not found: {SAMPLE_IMAGES_DIR}")
    sys.exit(1)

# 1. Register Event
print("1. Registering Event...")
try:
    resp = requests.post(f"{BASE_URL}/studio/register", json={"storage_path": SAMPLE_IMAGES_DIR})
    if resp.status_code != 200:
        print(f"Failed to register: {resp.text}")
        sys.exit(1)
    data = resp.json()
    print(f"   Success! Event Code: {data['event_code']}, Token: {data['token']}")
    TOKEN = data['token']
    EVENT_ID = data.get('id') # We added ID to response in studio.py
except Exception as e:
    print(f"Error registering: {e}")
    sys.exit(1)

# 2. Wait for Indexing (Mock wait since it's background)
print("2. Waiting for indexing (5s)...")
time.sleep(5)

# 3. Match Face
# We need a selfie. Let's pick one from the sample images itself to ensure a match.
# Assuming there's at least one image in sample_images
images = [f for f in os.listdir(SAMPLE_IMAGES_DIR) if f.lower().endswith(('.jpg', '.png'))]
if not images:
    print("No images in sample dir to test match.")
    sys.exit(1)

test_image_path = os.path.join(SAMPLE_IMAGES_DIR, images[0])
print(f"3. Matching using {images[0]}...")

try:
    with open(test_image_path, "rb") as f:
        files = {"file": f}
        data = {"token": TOKEN, "k": 5}
        resp = requests.post(f"{BASE_URL}/match", data=data, files=files)
        
    if resp.status_code != 200:
        print(f"Match failed: {resp.text}")
    else:
        results = resp.json()["results"]
        print(f"   Success! Found {len(results)} matches.")
        for r in results:
            print(f"   - {r['image_path']} (Score: {r['score']})")
            
            # 4. Test Image Serving
            print(f"4. Testing Image Serving for {r['image_path']}...")
            img_resp = requests.get(f"{BASE_URL}/images", params={"path": r['image_path']})
            if img_resp.status_code == 200:
                print("   Image served successfully.")
            else:
                print(f"   Failed to serve image: {img_resp.status_code}")

except Exception as e:
    print(f"Error matching: {e}")

print("\nVerification Complete.")
