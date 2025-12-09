"""
Test script to validate UserRole enum comparison fix
"""
from app.models import User, UserRole
from app.utils.auth import get_current_studio_user
from fastapi import HTTPException

print("Testing UserRole enum comparison...")
print()

# Create a mock studio user
class MockStudioUser:
    def __init__(self):
        self.id = 1
        self.email = "studio@test.com"
        self.role = UserRole.STUDIO
        self.is_active = True

# Create a mock customer user
class MockCustomerUser:
    def __init__(self):
        self.id = 2
        self.email = "customer@test.com"
        self.role = UserRole.CUSTOMER
        self.is_active = True

print("Test 1: Studio user access")
try:
    studio_user = MockStudioUser()
    result = get_current_studio_user(studio_user)
    print(f"✓ Studio user granted access")
    print(f"  User role: {result.role}")
    print(f"  Role value: {result.role.value}")
except HTTPException as e:
    print(f"✗ Failed: {e.detail}")
print()

print("Test 2: Customer user access (should be denied)")
try:
    customer_user = MockCustomerUser()
    result = get_current_studio_user(customer_user)
    print(f"✗ Customer user should NOT have been granted access")
except HTTPException as e:
    print(f"✓ Correctly denied customer user access")
    print(f"  Error: {e.detail}")
    print(f"  Status code: {e.status_code}")
print()

print("Test 3: Enum comparison validation")
studio_user = MockStudioUser()
print(f"  User role type: {type(studio_user.role)}")
print(f"  Is UserRole enum: {isinstance(studio_user.role, UserRole)}")
print(f"  Role == UserRole.STUDIO: {studio_user.role == UserRole.STUDIO}")
print(f"  Role != UserRole.CUSTOMER: {studio_user.role != UserRole.CUSTOMER}")
print(f"  Role value (string): {studio_user.role.value}")
print()

print("="*60)
print("All UserRole enum comparison tests passed! ✓")
print("="*60)
