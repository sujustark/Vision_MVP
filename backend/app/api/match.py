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
async def match(token: str = Form(...), file: UploadFile = File(...), k: int = Form(10), threshold: float = Form(0.3)):
    """
    Match a selfie against indexed faces for an event.
    
    Args:
        token: Event access token
        file: Selfie image file
        k: Number of top matches to return (default: 10)
        threshold: Minimum similarity threshold (0-1, default: 0.3)
    
    Returns:
        List of matched photos with similarity scores
    """
    # validate token
    from ..db import SessionLocal
    db = SessionLocal()
    ev = db.query(Event).filter(Event.token == token).first()
    
    if not ev:
        db.close()
        raise HTTPException(status_code = 401, detail = "Invalid or expired token")
    
    # read file bytes
    img_bytes = await file.read()
    # convert to embedding (already normalized in embeddings.py)
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
    
    # Extract face_db_ids and filter by threshold
    # For cosine similarity (used in faiss_index.py numpy fallback):
    # - score ranges from -1 to 1
    # - higher is better
    # For L2 distance (used in FAISS HNSW):
    # - distance ranges from 0 to infinity
    # - lower is better
    # We need to convert distance to similarity score
    
    filtered_matches = []
    for m in top_matches:
        # Check if we have score (cosine similarity) or distance (L2)
        if "score" in m:
            # Cosine similarity: already in [0, 1] range (normalized)
            similarity = m["score"]
        elif "distance" in m:
            # L2 distance: convert to similarity
            # For normalized vectors, L2 distance relates to cosine similarity:
            # similarity = 1 - (distance^2 / 2)
            # But simpler: similarity = 1 / (1 + distance)
            distance = m["distance"]
            similarity = 1.0 / (1.0 + distance)
        else:
            continue
        
        # Filter by threshold
        if similarity >= threshold:
            filtered_matches.append({
                "face_db_id": m.get("face_db_id"),
                "similarity": similarity,
                "distance": m.get("distance", 0.0)
            })
    
    # Sort by similarity (descending)
    filtered_matches = sorted(filtered_matches, key=lambda x: x["similarity"], reverse=True)
    
    # Fetch image paths from DB
    final_results = []
    if filtered_matches:
        face_ids = [m["face_db_id"] for m in filtered_matches if m.get("face_db_id") is not None]
        faces = db.query(Face).filter(Face.id.in_(face_ids)).all()
        face_map = {f.id: f.image_path for f in faces}
        
        for m in filtered_matches:
            fid = m.get("face_db_id")
            if fid and fid in face_map:
                final_results.append({
                    "image_path": face_map[fid],
                    "distance": m.get("distance", 0.0),
                    "score": m.get("similarity", 0.0)  # Use similarity as score
                })
    
    db.close()
    return {"results": final_results}