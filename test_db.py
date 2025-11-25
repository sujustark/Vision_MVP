"""
Simple test to check if the database is accessible
"""
import sys
from pathlib import Path

backend_root = Path(__file__).resolve().parent / "backend"
sys.path.insert(0, str(backend_root))

try:
    from app.db import engine, SessionLocal
    from app.models import User
    
    print("Testing database connection...")
    print(f"Database URL: {engine.url}")
    
    # Try to create a session
    db = SessionLocal()
    print("✓ Database session created")
    
    # Try to query users
    try:
        count = db.query(User).count()
        print(f"✓ Users table exists with {count} users")
    except Exception as e:
        print(f"✗ Error querying users: {e}")
    
    db.close()
    
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()
