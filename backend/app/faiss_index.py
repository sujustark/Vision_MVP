import os
import numpy as np
import faiss
import json

class EventFaissIndex:
    def __init__(self, event_id, dim = 512, index_dir = "/app/indices"):
        self.event_id = event_id
        self.dim = dim
        self.index_dir = index_dir
        os.makedirs(self.index_dir, exist_ok = True)
        self.index_path = os.path.join(self.index_dir, f"event_{event_id}.index")
        self.meta_path = os.path.join(self.index_dir, f"event{event_id}_meta.json")
        self.index = None
        self.id_map = []
        self._load_or_create()

    def _load_or_create(self):
        if os.path.exists(self.index_path):
            self.index = faiss.read_index(self.index_path)
            if os.path.exists(self.meta_path):
                with open(self.meta_path, "r") as f:
                    self.id_map = json.load(f)

        else:
            # HNSW index
            self.index = faiss.IndexHNSWFlat(self.dim, 32)
            self.index.hnsw.efsearch = 64
            self.id_map = []

    def add(self, vectors: np.ndarray, face_ids: list):
        # vectors: (N, dim)
        self.index.add(vectors.astype('float32'))
        self.id_map.extend(face_ids)
        self._save()

    def search(self, query_vec: np.ndarray, k = 5):
        # query_vec: (1, dim) or (N, dim)
        D, I = self.index.search(query_vec.astype('float32'), k)
        out = []
        for dist_list, idx_list in zip(D, I):
            row = []
            for dist, idx in zip(dist_list, idx_list):
                if idx < 0:
                    continue
                face_id = self.id_map[idx]
                row.append({"face_id": face_id, "distance": float(dist)})
            out.append(row)
        return out
    
    def _save(self):
        faiss.write_index(self.index, self.index_path)
        with open(self.meta_path, "w") as f:
            json.dump(self.id_map, f)