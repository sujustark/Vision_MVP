from sqlalchemy import Column, Integer, String, Boolean, Text, TIMESTAMP, JSON, ForeignKey, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
import enum

Base = declarative_base()

class UserRole(str, enum.Enum):
    STUDIO = "studio"
    CUSTOMER = "customer"

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    full_name = Column(String, nullable=False)
    role = Column(Enum(UserRole), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(TIMESTAMP, default=lambda: datetime.now(timezone.utc))
    
    # Relationships
    events = relationship("Event", back_populates="owner")

class Event(Base):
    __tablename__ = "events"
    id = Column(Integer, primary_key=True, index=True)
    event_code = Column(String, unique=True, index=True)
    token = Column(String, unique=True, index=True)
    storage_path = Column(Text)
    indexed = Column(Boolean, default=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # Nullable for backward compatibility
    created_at = Column(TIMESTAMP, default=lambda: datetime.now(timezone.utc))
    
    # Relationships
    owner = relationship("User", back_populates="events")

class Face(Base):
    __tablename__ = "faces"
    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(Integer, index=True)
    face_id = Column(String, unique=True, index=True)
    image_path = Column(Text)
    bbox = Column(JSON)
    created_at = Column(TIMESTAMP, default=lambda: datetime.now(timezone.utc))