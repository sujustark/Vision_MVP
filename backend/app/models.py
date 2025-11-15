from sqlalchemy import Column, Integer, String, Boolean, Text, TIMESTAMP, JSON
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime, timezone

Base = declarative_base()

class Event(Base):
    __tablename__ = "events"
    id = Column(Integer, primary_key = True, index = True)
    event_code = Column(String, unique = True, index = True)
    token = Column(String, unique = True, index = True)
    storage_path = Column(Text)
    indexed = Column(Boolean, default = False)
    created_at = Column(TIMESTAMP, default = lambda: datetime.now(timezone.utc))

class Face(Base):
    __tablename__ = "faces"
    id = Column(Integer, primary_key = True, index = True)
    event_id = Column(Integer, index = True)
    face_id = Column(String, unique = True, index = True)
    image_path = Column(Text)
    bbox = Column(JSON)
    created_at = Column(TIMESTAMP, default = lambda: datetime.now(timezone.utc))