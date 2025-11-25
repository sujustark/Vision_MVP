from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends
from pydantic import BaseModel
import secrets
from ..db import get_db_session
from ..models import Event, User
from ..utils.auth import get_current_studio_user
from sqlalchemy.orm import Session
import sqlalchemy
import sys
from pathlib import Path
import subprocess
import os

router = APIRouter()

class RegisterRequest(BaseModel):
    storage_path: str

class RegisterResponse(BaseModel):
    event_code: str
    token: str
    qr_link: str
    id: int

@router.post("/register", response_model = RegisterResponse)
def register_event(
    payload: RegisterRequest, 
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_studio_user)
):
    """
    Register a new event. Requires studio user authentication.
    """
    token = secrets.token_urlsafe(16)
    event_code = "EV_" + secrets.token_hex(4)
    # insert into db
    from ..db import SessionLocal
    db: Session = SessionLocal()
    try:
        ev = Event(
            event_code=event_code, 
            token=token, 
            storage_path=payload.storage_path,
            user_id=current_user.id  # Associate event with authenticated user
        )
        db.add(ev)
        db.commit()
        db.refresh(ev)
    except sqlalchemy.exc.IntegrityError:
        db.rollback()
        raise HTTPException(status_code = 500, detail = "Failed to create event")
    finally:
        db.close()

    qr_link = f"http://localhost:5173/e/{event_code}/{token}"
    
    # Trigger background indexing
    background_tasks.add_task(run_indexer, ev.id, payload.storage_path)

    return {"event_code": event_code, "token": token, "qr_link": qr_link, "id": ev.id}

def run_indexer(event_id: int, folder_path: str):
    # This runs in background
    
    worker_script = Path(__file__).resolve().parents[3] / "worker" / "indexer.py"
    
    # We can also just import the function if we add worker to sys.path
    worker_dir = Path(__file__).resolve().parents[3] / "worker"
    if str(worker_dir) not in sys.path:
        sys.path.insert(0, str(worker_dir))
        
    try:
        from indexer import index_local_folder
        index_local_folder(event_id, folder_path)
    except ImportError:
        print("Could not import indexer. Running as subprocess...")
        subprocess.Popen([sys.executable, str(worker_script)], env={**os.environ, "EVENT_ID": str(event_id), "FOLDER": folder_path})