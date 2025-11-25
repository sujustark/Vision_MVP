"""
Test script to verify backend authentication endpoints.
"""
import requests
import json

BASE_URL = "http://localhost:8000/api/v1"

print("=" * 60)
print("BACKEND AUTHENTICATION TEST")
print("=" * 60)

# Test 1: Signup
print("\n1. Testing Signup (Studio User)")
print("-" * 60)
signup_data = {
    "email": "photographer@test.com",
    "password": "photo123",
    "full_name": "Test Photographer",
    "role": "studio"
}

try:
    resp = requests.post(f"{BASE_URL}/auth/signup", json=signup_data)
    print(f"Status: {resp.status_code}")
    if resp.status_code == 201:
        data = resp.json()
        print(f"✓ Signup successful!")
        print(f"  User ID: {data['user_id']}")
        print(f"  Email: {data['email']}")
        print(f"  Role: {data['role']}")
        print(f"  Token: {data['access_token'][:50]}...")
        studio_token = data['access_token']
    else:
        print(f"✗ Signup failed: {resp.text}")
        studio_token = None
except Exception as e:
    print(f"✗ Error: {e}")
    studio_token = None

# Test 2: Login with admin
print("\n2. Testing Login (Admin User)")
print("-" * 60)
login_data = {
    "email": "admin@vision-mvp.com",
    "password": "admin"
}

try:
    resp = requests.post(f"{BASE_URL}/auth/login", json=login_data)
    print(f"Status: {resp.status_code}")
    if resp.status_code == 200:
        data = resp.json()
        print(f"✓ Login successful!")
        print(f"  User ID: {data['user_id']}")
        print(f"  Email: {data['email']}")
        print(f"  Role: {data['role']}")
        print(f"  Token: {data['access_token'][:50]}...")
        admin_token = data['access_token']
    else:
        print(f"✗ Login failed: {resp.text}")
        admin_token = None
except Exception as e:
    print(f"✗ Error: {e}")
    admin_token = None

# Test 3: Get current user info
print("\n3. Testing /auth/me (Get Current User)")
print("-" * 60)
if admin_token:
    try:
        headers = {"Authorization": f"Bearer {admin_token}"}
        resp = requests.get(f"{BASE_URL}/auth/me", headers=headers)
        print(f"Status: {resp.status_code}")
        if resp.status_code == 200:
            data = resp.json()
            print(f"✓ User info retrieved!")
            print(f"  User ID: {data['user_id']}")
            print(f"  Email: {data['email']}")
            print(f"  Full Name: {data['full_name']}")
            print(f"  Role: {data['role']}")
            print(f"  Active: {data['is_active']}")
        else:
            print(f"✗ Failed: {resp.text}")
    except Exception as e:
        print(f"✗ Error: {e}")
else:
    print("⊘ Skipped (no token)")

# Test 4: Protected Studio endpoint (should require auth)
print("\n4. Testing Protected Studio Endpoint")
print("-" * 60)
if studio_token or admin_token:
    token = studio_token or admin_token
    try:
        headers = {"Authorization": f"Bearer {token}"}
        register_data = {"storage_path": "D:\\Vision_MVP\\sample_images"}
        resp = requests.post(f"{BASE_URL}/studio/register", json=register_data, headers=headers)
        print(f"Status: {resp.status_code}")
        if resp.status_code == 200:
            data = resp.json()
            print(f"✓ Event registered with authentication!")
            print(f"  Event Code: {data['event_code']}")
            print(f"  Token: {data['token'][:20]}...")
        else:
            print(f"✗ Failed: {resp.text}")
    except Exception as e:
        print(f"✗ Error: {e}")
else:
    print("⊘ Skipped (no token)")

# Test 5: Try accessing protected endpoint without auth (should fail)
print("\n5. Testing Protected Endpoint Without Auth (Should Fail)")
print("-" * 60)
try:
    register_data = {"storage_path": "D:\\Vision_MVP\\sample_images"}
    resp = requests.post(f"{BASE_URL}/studio/register", json=register_data)
    print(f"Status: {resp.status_code}")
    if resp.status_code == 401 or resp.status_code == 403:
        print(f"✓ Correctly rejected unauthorized request!")
        print(f"  Message: {resp.json().get('detail', 'N/A')}")
    else:
        print(f"✗ Should have been rejected but got: {resp.status_code}")
except Exception as e:
    print(f"✗ Error: {e}")

# Test 6: Signup as Customer
print("\n6. Testing Signup (Customer User)")
print("-" * 60)
customer_signup = {
    "email": "customer@test.com",
    "password": "customer123",
    "full_name": "Test Customer",
    "role": "customer"
}

try:
    resp = requests.post(f"{BASE_URL}/auth/signup", json=customer_signup)
    print(f"Status: {resp.status_code}")
    if resp.status_code == 201:
        data = resp.json()
        print(f"✓ Customer signup successful!")
        print(f"  User ID: {data['user_id']}")
        print(f"  Email: {data['email']}")
        print(f"  Role: {data['role']}")
        customer_token = data['access_token']
    else:
        print(f"✗ Signup failed: {resp.text}")
        customer_token = None
except Exception as e:
    print(f"✗ Error: {e}")
    customer_token = None

# Test 7: Try to register event as customer (should fail)
print("\n7. Testing Studio Endpoint as Customer (Should Fail)")
print("-" * 60)
if customer_token:
    try:
        headers = {"Authorization": f"Bearer {customer_token}"}
        register_data = {"storage_path": "D:\\Vision_MVP\\sample_images"}
        resp = requests.post(f"{BASE_URL}/studio/register", json=register_data, headers=headers)
        print(f"Status: {resp.status_code}")
        if resp.status_code == 403:
            print(f"✓ Correctly rejected customer from studio endpoint!")
            print(f"  Message: {resp.json().get('detail', 'N/A')}")
        else:
            print(f"✗ Should have been rejected but got: {resp.status_code}")
    except Exception as e:
        print(f"✗ Error: {e}")
else:
    print("⊘ Skipped (no customer token)")

print("\n" + "=" * 60)
print("TEST COMPLETE")
print("=" * 60)
print("\nSummary:")
print("✓ = Test passed")
print("✗ = Test failed")
print("⊘ = Test skipped")
