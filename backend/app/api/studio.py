from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import secrets
from ..db import get_db_session
from ..models import Event
from sqlalchemy.orm import Session
import sqlalchemy

router = APIRouter()

class RegisterRequest(BaseModel):
    storage_path = str

class RegisterResponse(BaseModel):
    event_code: str
    token: str
    qr_link: str

@router.post("/register", response_model = RegisterResponse)
def register_event(payload: RegisterRequest):
    token = secrets.token_urlsafe(16)
    event_code = "EV_" + secrets.token_hex(4)
    # insert into db
    from ..db import SessionLocal
    db: Session = SessionLocal()
    try:
        ev = Event(event_code = event_code, token = token, storage_path = payload.storage_path)
        db.add(ev)
        db.commit()
        db.refresh(ev)
    except sqlalchemy.exc.IntegrityError:
        db.rollback()
        raise HTTPException(status_code = 500, detail = "Failed to create event")
    finally:
        db.close()

    qr_link = f"https://app.example.com/e/{event_code}/{token}"
    return {"event_code": event_code, "token": token, "qr_link": qr_link}