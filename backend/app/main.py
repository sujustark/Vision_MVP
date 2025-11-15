import os
from fastapi import FastAPI
from .db import init_db, get_db_session
from .api.studio import router as studio_router
from .api.match import router as match_router

app = FastAPI(title = "Vision Face MVP - backend")

@app.on_event("startup")
def startup_event():
    # create tables (dev only)
    init_db()

app.include_router(studio_router, prefix = "/api/v1/studio")
app.include_router(match_router, prefix = "/api/v1")

@app.get("/")
def root():
    return {"status": "ok"}