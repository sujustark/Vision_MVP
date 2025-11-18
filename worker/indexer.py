import os
import glob
import uuid
import json
import numpy as np
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
BACKEND_APP = REPO_ROOT / "backend" / "app"

if str(BACKEND_APP) not in sys.path:
    sys.path.insert(0, str(BACKEND_APP))

# DB imports
from app.db import SessionLocal, engine
from app.models import Event, Face

# Simple deterministic embedding
def get_embedding_from_file(path, dim = 512):
    data = open(path, "rb").read()
    seed = int(sum(data) % 2**32)
    rng = np.random.default_rng(seed)
    v = rng.standard_normal(dim).astype("float32")
    v = v / np.linalg.norm(v)
    return v

def index_local_folder(event_id: int, folder_path: str):
    folder = Path(folder_path)
    if not folder.exists():
        print("Folder not Found:", folder)
        return
    
    db = SessionLocal()
    ev = db.query(Event).filter(Event.id == event_id).first()
    if not ev:
        print(f"Event id {event_id} not found. Create it first via /register.")
        db.close()
        return
    
    # prepare indices directory
    indices_dir = BACKEND_APP / "indices"
    indices_dir.mkdir(parents = True, exist_ok = True)

    # collect image files
    exts = ["*.jpg", "*.jpeg", "*.png", "*.heic", "*.heif"]
    files = []
    for e in exts:
        files.extend(sorted(folder.glob(e)))

    if not files:
        print(f"No image files found in", folder)
        db.close()
        return
    
    vectors = []
    face_id_order = []
    meta = []

    for img_path in files:
        print("Indexing:", img_path)
        # in MVP assuming full image is the face (no detector)
        emb = get_embedding_from_file(str(img_path))

        # Create DB face record
        f = Face(event_id = event_id, face_id = str(uuid.uuid4()), image_path = str(img_path))
        db.add(f)
        db.commit()
        db.refresh(f)
        vectors.append(emb)
        face_id_order.append(int(f.id)) # type: ignore
        meta.append({"face_db_id": int(f.id), "face_uuid": f.face_id, "image_path": str(img_path)}) # type: ignore

        # save embeddings array and meta mapping
        emb_arr = np.stack(vectors, axis = 0).astype("float32")
        emb_file = indices_dir / f"event_{event_id}_embeddngs.npy"
        meta_file = indices_dir / f"event_{event_id}_meta.json"
        np.save(str(emb_file), emb_arr)
        with open(meta_file, "W", encoding = "utf-8") as fh:
            json.dump(meta, fh, indent = 2)

        # mark event indexed
        ev.indexed = True # type: ignore
        db.add(ev)
        db.commit()
        db.refresh(ev)
        db.close()

        print("Indexing Complete.")
        print("Embeddings saved to:", emb_file)
        print("Meta saved to:", meta_file)

if __name__ == "__main__":
    # EDIT IF NEEDED:
    EVENT_ID = 1
    FOLDER = r"D:\Vision_MVP\sample_images"

    index_local_folder(EVENT_ID, FOLDER)