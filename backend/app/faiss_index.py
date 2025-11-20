import os
import json
import numpy as np
from pathlib import Path

# Try to import faiss; if not available, fallback to numpy search
try:
    import faiss
    FAISS_AVAILABLE = True
except Exception:
    FAISS_AVAILABLE = False

class EventFaissIndex:
    """Unified index interface.
    If faiss is installed, uses a persistetn HNSW index file.
    Otherwise falls back to numpy-based search using saved embeddings (.npy) + meta (.json)."""

    def __init__(self, event_id: int, dim: int = 512, index_dir: str = None): # type: ignore
        self.event_id = int(event_id)
        self.dim = dim
        if index_dir is None:
            # default to backend/app/indices
            root = Path(__file__).resolve().parents[0]
            index_dir = root / "indices"
        self.index_dir = Path(index_dir)
        self.index_dir.mkdir(parents = True, exist_ok = True)
        self.faiss_index_path = self.index_dir / f"event_{self.event_id}.index"
        self.emb_path = self.index_dir / f"event_{self.event_id}_embeddings.npy"
        self.meta_path = self.index_dir / f"event_{self.event_id}_meta.json"

        # state
        self.index = None
        self.id_map = [] # face_db_id_order

        # load whichever is available
        if FAISS_AVAILABLE and self.faiss_index_path.exists():
            try:
                self.index = faiss.read_index(str(self.faiss_index_path)) # type: ignore
                with open(self.meta_path, "r", encoding = "utf-8") as fh:
                    meta = json.load(fh)
                    self.id_map = [int(m["face_db_id"]) for m in meta]
            except Exception:
                # fallback to numpy
                FAISS_AVAILABLE_LOCAL = False
                print(f"Faiss index load failed; falling back to numpy.")

        elif self.emb_path.exists():
            # no faiss, but embeddings exist - use numpy falback
            pass
        else:
            # nothin exists yet - empty index
            pass

    # If faiss is availabale and index is loaded, we can add (only if faiss is installed)
    def add(self, vectors: np.ndarray, face_ids: list):
        vectors = vectors.astype("float32")
        if FAISS_AVAILABLE:
            # create index if not exists
            if self.index is None:
                # HNSW flat index
                self.index = faiss.IndexHNSWFlat(self.dim, 32) # type: ignore
                self.index.hnsw.efSearch = 64
            self.index.add(vectors) # type: ignore
            # append mapping
            self.id_map.extend([int(x) for x in face_ids])
            # save
            faiss.write_index(self.index, str(self.faiss_index_path)) # type: ignore
            with open(self.meta_path, "w", encoding = "utf-8") as fh:
                json.dump([{"face_db_id": fid} for fid in self.id_map], fh)
        else:
            # numpy fallback: load old embeddings if exist, append and save
            if self.emb_path.exists():
                existing = np.load(str(self.emb_path))
                new = np.vstack([existing, vectors])
            else:
                new = vectors
            np.save(str(self.emb_path), new)
            # append meta mapping
            if self.meta_path.exists():
                with open(self.meta_path, "r", encoding = "utf-8") as fh:
                    meta = json.load(fh)
            else:
                meta = []
            for fid in face_ids:
                meta.append({"face_db_id": int(fid)})
            with open(self.meta_path, "w", encoding = 'utf-8') as fh:
                json.dump(meta, fh, indent = 2)
            self.id_map = [int(m["face_db_id"]) for m in meta]
    
    def search(self, query_vec:np.ndarray, k: int = 5):
        """Query_vec: shape (1, dim) or (N, dim)
        Returns: list of rows: each row is list of dicts: {"face_db_id", "score"}
        """
        q = np.asarray(query_vec, dtype = "float32")
        if q.ndim == 1:
            q = q.reshape(1, -1)

        if FAISS_AVAILABLE and self.index is not None:
            D, I = self.index.search(q, k) # type: ignore
            out = []
            for dist_list, idx_list in zip(D, I):
                row = []
                for dist, idx in zip(dist_list, idx_list):
                    if idx < 0:
                        continue
                    face_db_id = self.id_map[idx]
                    row.append({"face_db_id": int(face_db_id), "distance": float(dist)})
                out.append(row)
            return out
        
        # numpy fallback
        if not self.emb_path.exists():
            return[[] for _ in range(q.shape[0])]
        
        emb = np.load(str(self.emb_path))
        # ensure normalized
        def l2norm(a):
            a = a.astype('float32')
            norms = np.linalg.norm(a, axis = 1, keepdims = True)
            norms[norms == 0] = 1.0
            return a / norms
        emb_norm = l2norm(emb)
        q_norm = l2norm(q)
        # cosine similarity = dot product on normalized vectors
        sims = np.dot(q_norm, emb_norm.T)
        results = []
        for row in sims:
            # get top k indices (descending)
            idxs = np.argsort(-row)[:k]
            row_res = []
            for idx in idxs:
                score = float(row[idx])
                face_db_id = None
                if self.meta_path.exists():
                    with open(self.meta_path, "r", encoding = "utf-8") as fh:
                        meta = json.load(fh)
                        if idx < len(meta):
                            face_db_id = int(meta[idx]["face_db_id"])
                row_res.append({"face_db_id": face_db_id, "score": score})
            results.append(row_res)
        return results