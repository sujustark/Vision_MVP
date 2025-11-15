import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .models import Base
from urllib.parse import quote_plus

DATABSE_URL = os.getenv("DATABASE_URL", "postgressql://vision:vision@db:5432/visiondb")

# SQLAlchemy engine
engine = create_engine(DATABSE_URL, pool_pre_ping = True)
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