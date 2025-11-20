import os
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from .db import init_db, get_db_session, SessionLocal
from .models import Event
from .api.studio import router as studio_router
from .api.match import router as match_router

app = FastAPI(title="Vision Face MVP - backend")

# Add CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def startup_event():
    # create tables (dev only)
    init_db()

app.include_router(studio_router, prefix="/api/v1/studio")
app.include_router(match_router, prefix="/api/v1")

@app.get("/")
def root():
    return {"status": "ok"}

@app.get("/api/v1/images")
def get_image(path: str = Query(...)):
    # Security check: ensure path belongs to a registered event
    db = SessionLocal()
    events = db.query(Event).all()
    allowed = False
    for ev in events:
        # normalize paths for comparison
        if os.path.commonpath([os.path.abspath(path), os.path.abspath(ev.storage_path)]) == os.path.abspath(ev.storage_path):
            allowed = True
            break
    db.close()
    
    if not allowed:
        # In a real app, strictly enforce this. 
        # For MVP/Demo, if the path exists and is an image, we might be lenient, 
        # but let's stick to security best practices even for MVP.
        # If the path is not in a registered folder, deny it.
        raise HTTPException(status_code=403, detail="Access denied to this path")

    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="Image not found")
    
    return FileResponse(path)