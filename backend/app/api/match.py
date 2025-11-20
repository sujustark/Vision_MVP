from fastapi import APIRouter, UploadFile, File, HTTPException, Form
from pydantic import BaseModel
from ..db import get_db_session
from ..models import Event, Face
import io
from ..utils.embeddings import get_embedding_from_image_bytes
from ..faiss_index import EventFaissIndex
import numpy as np

router = APIRouter()

class MatchResponse(BaseModel):
    results: list

@router.post("/match", response_model = MatchResponse)
async def match(token: str = Form(...), file: UploadFile = File(...), k: int = Form(5)):
    # validate token
    from ..db import SessionLocal
    db = SessionLocal()
    ev = db.query(Event).filter(Event.token == token).first()
    
    if not ev:
        db.close()
        raise HTTPException(status_code = 401, detail = "Invalid or expired token")
    
    # read file bytes
    img_bytes = await file.read()
    # convert to embedding
    query_vec = get_embedding_from_image_bytes(img_bytes) # np.array float32

    # check if face detected
    if np.all(query_vec == 0):
         db.close()
         raise HTTPException(status_code = 400, detail = "No face detected in the selfie")

    # load faiss index for event (EventFaissIndex handles lazy loads)
    idx = EventFaissIndex(ev.id, dim = len(query_vec))
    results = idx.search(query_vec.reshape(1, -1), k = k)
    
    # results is list of lists (one per query vector)
    # we only have 1 query vector
    top_matches = results[0] if results else []
    
    # Extract face_db_ids
    face_ids = [m["face_db_id"] for m in top_matches if m.get("face_db_id") is not None]
    
    # Fetch image paths from DB
    final_results = []
    if face_ids:
        faces = db.query(Face).filter(Face.id.in_(face_ids)).all()
        face_map = {f.id: f.image_path for f in faces}
        
        for m in top_matches:
            fid = m.get("face_db_id")
            if fid and fid in face_map:
                final_results.append({
                    "image_path": face_map[fid],
                    "distance": m.get("distance", 0.0),
                    "score": m.get("score", 0.0)
                })
    
    db.close()
    return {"results": final_results}