import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .models import Base
from urllib.parse import quote_plus

# Use SQLite for development (file-based database)
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./vision_mvp.db")

# SQLAlchemy engine
# For SQLite, we need check_same_thread=False to allow multiple threads
engine = create_engine(
    DATABASE_URL, 
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {},
    pool_pre_ping=True
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    # create tables
    Base.metadata.create_all(bind=engine)

def get_db_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()