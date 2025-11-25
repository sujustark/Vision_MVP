"""
Database migration script to add users table and update events table.
Run this once to migrate the database schema.
"""
import sys
from pathlib import Path

# Add backend to path
backend_root = Path(__file__).resolve().parent
if str(backend_root) not in sys.path:
    sys.path.insert(0, str(backend_root))

from app.db import SessionLocal, engine
from app.models import Base, User, Event, UserRole
from app.utils.auth import hash_password
from sqlalchemy import inspect

def migrate_database():
    """
    Migrate the database to add users table and user_id to events.
    """
    print("=" * 60)
    print("DATABASE MIGRATION")
    print("=" * 60)
    
    # Check if users table exists
    inspector = inspect(engine)
    existing_tables = inspector.get_table_names()
    
    print(f"\nExisting tables: {existing_tables}")
    
    # Create all tables (will only create missing ones)
    print("\nCreating missing tables...")
    Base.metadata.create_all(bind=engine)
    
    # Check again
    inspector = inspect(engine)
    new_tables = inspector.get_table_names()
    print(f"Tables after migration: {new_tables}")
    
    # Create a default admin user if users table is empty
    db = SessionLocal()
    try:
        user_count = db.query(User).count()
        if user_count == 0:
            print("\nCreating default admin user...")
            admin_user = User(
                email="admin@vision-mvp.com",
                password_hash=hash_password("admin"),  # Shorter password
                full_name="Admin User",
                role=UserRole.STUDIO,
                is_active=True
            )
            db.add(admin_user)
            db.commit()
            db.refresh(admin_user)
            print(f"✓ Created admin user (ID: {admin_user.id})")
            print(f"  Email: admin@vision-mvp.com")
            print(f"  Password: admin")
            print(f"  Role: studio")
            
            # Assign existing events to admin user
            events = db.query(Event).filter(Event.user_id == None).all()
            if events:
                print(f"\nAssigning {len(events)} existing events to admin user...")
                for event in events:
                    event.user_id = admin_user.id
                db.commit()
                print(f"✓ Assigned {len(events)} events to admin user")
        else:
            print(f"\n✓ Users table already has {user_count} user(s)")
    
    except Exception as e:
        print(f"\n❌ Error during migration: {e}")
        db.rollback()
        raise
    finally:
        db.close()
    
    print("\n" + "=" * 60)
    print("MIGRATION COMPLETE")
    print("=" * 60)
    print("\nYou can now:")
    print("1. Login with admin@vision-mvp.com / admin123")
    print("2. Or create a new user via /api/v1/auth/signup")
    print()

if __name__ == "__main__":
    migrate_database()
