import numpy as np
import cv2
import insightface
from insightface.app import FaceAnalysis

# Initialize FaceAnalysis globally to avoid reloading models on every call
# Using buffalo_l model for high accuracy (512-dimensional embeddings)
app_face = FaceAnalysis(name='buffalo_l', providers=['CPUExecutionProvider'])
app_face.prepare(ctx_id=0, det_size=(640, 640))

def get_embedding_from_image_bytes(image_bytes: bytes) -> np.ndarray:
    """
    Detects the largest face in the image bytes and returns its embedding.
    Returns a zero-vector if no face is found.
    """
    # Convert bytes to numpy array
    nparr = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    
    if img is None:
        # Could not decode image
        return np.zeros(512, dtype=np.float32)

    faces = app_face.get(img)
    if not faces:
        return np.zeros(512, dtype=np.float32)

    # Sort by area (box width * height) to find the largest face
    # face.bbox is [x1, y1, x2, y2]
    faces = sorted(faces, key=lambda x: (x.bbox[2] - x.bbox[0]) * (x.bbox[3] - x.bbox[1]), reverse=True)
    
    # Return the embedding of the largest face
    # embedding is usually 512-d for buffalo_l
    return faces[0].embedding.astype(np.float32)

def get_embedding_from_file(file_path: str) -> np.ndarray:
    """
    Reads an image from disk and returns the embedding of the largest face.
    """
    img = cv2.imread(file_path)
    if img is None:
        return np.zeros(512, dtype=np.float32)
        
    faces = app_face.get(img)
    if not faces:
        return np.zeros(512, dtype=np.float32)

    faces = sorted(faces, key=lambda x: (x.bbox[2] - x.bbox[0]) * (x.bbox[3] - x.bbox[1]), reverse=True)
    return faces[0].embedding.astype(np.float32)