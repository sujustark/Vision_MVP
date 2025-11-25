"""
Test script to verify face matching accuracy with real InsightFace AI.
This script tests the complete flow including indexing and matching.
"""
import requests
import os
import time

# Configuration
BASE_URL = "http://localhost:8000/api/v1"
SAMPLE_IMAGES_DIR = r"D:\Vision_MVP\sample_images"

print("=" * 60)
print("FACE MATCHING ACCURACY TEST")
print("=" * 60)

# Verify sample images exist
if not os.path.exists(SAMPLE_IMAGES_DIR):
    print(f"❌ Sample images directory not found: {SAMPLE_IMAGES_DIR}")
    exit(1)

images = [f for f in os.listdir(SAMPLE_IMAGES_DIR) if f.lower().endswith(('.jpg', '.png', '.jpeg'))]
if not images:
    print(f"❌ No images found in {SAMPLE_IMAGES_DIR}")
    exit(1)

print(f"✓ Found {len(images)} images in sample directory")
print()

# Step 1: Register Event
print("STEP 1: Registering Event")
print("-" * 60)
try:
    resp = requests.post(f"{BASE_URL}/studio/register", json={"storage_path": SAMPLE_IMAGES_DIR})
    if resp.status_code != 200:
        print(f"❌ Failed to register: {resp.text}")
        exit(1)
    data = resp.json()
    TOKEN = data['token']
    EVENT_CODE = data['event_code']
    print(f"✓ Event registered successfully")
    print(f"  Event Code: {EVENT_CODE}")
    print(f"  Token: {TOKEN}")
except Exception as e:
    print(f"❌ Error: {e}")
    exit(1)

print()

# Step 2: Wait for indexing
print("STEP 2: Waiting for Photo Indexing")
print("-" * 60)
print("⏳ Indexing photos with InsightFace (this may take 30-60 seconds)...")
time.sleep(45)  # Give enough time for indexing with real AI
print("✓ Indexing should be complete")
print()

# Step 3: Test matching with different images
print("STEP 3: Testing Face Matching")
print("-" * 60)

test_images = images[:min(3, len(images))]  # Test with first 3 images

for i, test_image in enumerate(test_images, 1):
    print(f"\nTest {i}/{len(test_images)}: Using {test_image}")
    test_image_path = os.path.join(SAMPLE_IMAGES_DIR, test_image)
    
    try:
        with open(test_image_path, "rb") as f:
            files = {"file": f}
            data = {"token": TOKEN, "k": 10, "threshold": 0.3}
            resp = requests.post(f"{BASE_URL}/match", data=data, files=files)
        
        if resp.status_code != 200:
            print(f"  ❌ Match failed: {resp.text}")
            continue
        
        results = resp.json()["results"]
        print(f"  ✓ Found {len(results)} matches")
        
        if results:
            print(f"\n  Top Matches:")
            for j, r in enumerate(results[:5], 1):  # Show top 5
                filename = os.path.basename(r['image_path'])
                score = r['score'] * 100  # Convert to percentage
                print(f"    {j}. {filename:40s} - Score: {score:5.1f}%")
                
                # Check if it's the same image (should have very high score)
                if filename == test_image:
                    if score > 90:
                        print(f"       ✓ EXCELLENT: Same image detected with {score:.1f}% confidence")
                    elif score > 70:
                        print(f"       ✓ GOOD: Same image detected with {score:.1f}% confidence")
                    else:
                        print(f"       ⚠ WARNING: Same image but low score ({score:.1f}%)")
        else:
            print(f"  ⚠ No matches found (threshold may be too high)")
            
    except Exception as e:
        print(f"  ❌ Error: {e}")

print()
print("=" * 60)
print("TEST COMPLETE")
print("=" * 60)
print()
print("INTERPRETATION:")
print("- Score > 90%: Excellent match (same person, similar angle)")
print("- Score 70-90%: Good match (same person, different angle/lighting)")
print("- Score 40-70%: Possible match (same person, significant variation)")
print("- Score < 40%: Likely different person")
print()
print("NOTE: The same image should always score > 95%")
