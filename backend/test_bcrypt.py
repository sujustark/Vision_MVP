from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Test hashing
password = "test123"
print(f"Hashing password: {password}")
try:
    hashed = pwd_context.hash(password)
    print(f"Success! Hash: {hashed[:50]}...")
    
    # Test verification
    verified = pwd_context.verify(password, hashed)
    print(f"Verification: {verified}")
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
