import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .models import Base
from urllib.parse import quote_plus

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://vision:vision@localhost:5432/visiondb")

# SQLAlchemy engine
engine = create_engine(DATABASE_URL, pool_pre_ping = True)
SessionLocal = sessionmaker(autocommit = False, autoflush = False, bind = engine)

def init_db():
    # create tables
    Base.metadata.create_all(bind = engine)

def get_db_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()