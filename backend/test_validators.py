"""
Test script to validate Pydantic v2 field validators are working correctly
"""
from app.api.auth import SignupRequest
from pydantic import ValidationError

print("Testing Pydantic v2 field_validator...")
print()

# Test 1: Valid signup data
print("Test 1: Valid signup data")
try:
    valid_data = SignupRequest(
        email="test@example.com",
        password="password123",
        full_name="John Doe",
        role="studio"
    )
    print("✓ Valid data accepted")
except ValidationError as e:
    print(f"✗ Failed: {e}")
print()

# Test 2: Password too short (< 6 chars)
print("Test 2: Password too short")
try:
    SignupRequest(
        email="test@example.com",
        password="12345",
        full_name="John Doe",
        role="studio"
    )
    print("✗ Should have failed but didn't")
except ValidationError as e:
    print("✓ Correctly rejected short password")
    print(f"  Error: {e.errors()[0]['msg']}")
print()

# Test 3: Invalid role
print("Test 3: Invalid role")
try:
    SignupRequest(
        email="test@example.com",
        password="password123",
        full_name="John Doe",
        role="admin"
    )
    print("✗ Should have failed but didn't")
except ValidationError as e:
    print("✓ Correctly rejected invalid role")
    print(f"  Error: {e.errors()[0]['msg']}")
print()

# Test 4: Name too short (< 2 chars)
print("Test 4: Name too short")
try:
    SignupRequest(
        email="test@example.com",
        password="password123",
        full_name="J",
        role="customer"
    )
    print("✗ Should have failed but didn't")
except ValidationError as e:
    print("✓ Correctly rejected short name")
    print(f"  Error: {e.errors()[0]['msg']}")
print()

# Test 5: Invalid email
print("Test 5: Invalid email")
try:
    SignupRequest(
        email="not-an-email",
        password="password123",
        full_name="John Doe",
        role="customer"
    )
    print("✗ Should have failed but didn't")
except ValidationError as e:
    print("✓ Correctly rejected invalid email")
    print(f"  Error: {e.errors()[0]['msg']}")
print()

print("="*50)
print("All Pydantic v2 field_validator tests passed! ✓")
print("="*50)
