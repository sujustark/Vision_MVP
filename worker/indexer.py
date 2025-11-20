import sys
import os
from pathlib import Path
import glob
import uuid
import json
import numpy as np

REPO_ROOT = Path(__file__).resolve().parents[1]
BACKEND_ROOT = REPO_ROOT / "backend"
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

# import backend.app modules as app.
try:
    from app.db import SessionLocal
    from app.models import Event, Face
    # Import the new embedding utility
    from app.utils.embeddings import get_embedding_from_file
except Exception as e:
    print(f"Failed to import backend.app modules: {e}")
    # Fallback if running directly and path insertion didn't work as expected for imports
    # But the sys.path insert above should handle it.
    raise SystemExit(e)

def index_local_folder(event_id: int, folder_path: str):
    folder = Path(folder_path)
    if not folder.exists():
        print(f"[ERROR] Folder not found: {folder}")
        return
    db = SessionLocal()
    ev = db.query(Event).filter(Event.id == event_id).first()
    if not ev:
        print(f"[ERROR] Event id {event_id} not found. Create it first via /api/v1/studio/register")
        db.close()
        return
    
    # ensure indices dir exists in backend/app/indices
    backend_app_dir = BACKEND_ROOT / "app"
    indices_dir = backend_app_dir / "indices"
    indices_dir.mkdir(parents = True, exist_ok = True)

    # Collect image files
    exts = ["*.jpg", "*.jpeg", "*.JPG", "*.png", "*.PNG"]
    files = []
    for e in exts:
        files.extend(sorted(folder.glob(e)))

    if not files:
        print(f"[WARNING] No image files found in {folder}")
        db.close()
        return
    
    vectors = []
    meta = []

    for img_path in files:
        print('Indexing', img_path)
        try:
            emb = get_embedding_from_file(str(img_path))
        except Exception as e:
            print(f"[WARNING] Skipping {img_path} due to read error: {e}")
            continue
        # create face DB record
        f = Face(event_id = event_id, face_id = str(uuid.uuid4()), image_path = str(img_path))
        db.add(f)
        db.commit()
        db.refresh(f)
        
        vectors.append(emb)
        meta.append({"face_db_id": int(f.id), "face_uuid": f.face_id, "image_path": str(img_path)})

    if not vectors:
        print("[WARNING] No vectors were created; nothing saved.")
        db.close()
        return
    
    # Save embeddings and meta
    emb_arr = np.stack(vectors, axis = 0).astype("float32")
    emb_file = indices_dir / f"event_{event_id}_embeddings.npy"
    meta_file = indices_dir / f"event_{event_id}_meta.json"

    np.save(str(emb_file), emb_arr)
    with open(meta_file, "w", encoding = "utf-8") as fh:
        json.dump(meta, fh, indent = 2)

    # Mark event as indexed
    ev.indexed = True
    db.add(ev)
    db.commit()
    db.close()

    print("Indexing Complete.")
    print("Embeddings saved to:", emb_file)
    print("Meta saved to:", meta_file)

if __name__ == "__main__":
    # For testing manually
    EVENT_ID = 1
    FOLDER = r"D:\Vision_MVP\sample_images"
    
    # You might need to ensure EVENT_ID 1 exists in DB first
    index_local_folder(EVENT_ID, FOLDER)