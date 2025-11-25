import requests

# Test signup with proper Python
url = "http://localhost:8000/api/v1/auth/signup"
data = {
    "email": "newuser@test.com",
    "password": "test123",
    "full_name": "New User",
    "role": "studio"
}

print("Testing signup...")
try:
    response = requests.post(url, json=data)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
except Exception as e:
    print(f"Error: {e}")
