from fastapi import APIRouter, UploadFile, File, HTTPException, Form
from pydantic import BaseModel
from ..db import get_db_session
from ..models import Event
import io
from ..utils.embeddings import get_embedding_from_image_bytes
from ..faiss_index import EventFaissIndex

router = APIRouter()

class MatchResponse(BaseModel):
    results: list

@router.post("/match", response_model = MatchResponse)
async def match(token: str = Form(...), file: UploadFile = File(...), k: int = Form(5)):
    # validate token
    from ..db import SessionLocal
    db = SessionLocal()
    ev = db.query(Event).filter(Event.token == token).first()
    db.close()
    if not ev:
        raise HTTPException(status_code = 401, detail = "Invalid or expired token")
    
    # read file bytes
    img_bytes = await file.read()
    # convert to embedding (placeholder)
    query_vec = get_embedding_from_image_bytes(img_bytes) # np.array float32

    # load faiss index for event (EventFaissIndex handles lazy loads)
    idx = EventFaissIndex(ev.id, dim = len(query_vec))
    results = idx.search(query_vec.reshape(1, -1), k = k)

    # results format: list of dicts with face id, distance -> we return as - is
    return {"results": results}