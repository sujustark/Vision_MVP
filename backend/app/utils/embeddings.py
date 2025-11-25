import numpy as np
import cv2
import insightface
from insightface.app import FaceAnalysis

# Initialize FaceAnalysis globally to avoid reloading models on every call
# Using buffalo_l model for high accuracy (512-dimensional embeddings)
# Increased det_size for better detection of smaller/distant faces
app_face = FaceAnalysis(name='buffalo_l', providers=['CPUExecutionProvider'])
app_face.prepare(ctx_id=0, det_size=(640, 640))

def normalize_embedding(embedding: np.ndarray) -> np.ndarray:
    """
    Normalize embedding to unit length for better cosine similarity matching.
    """
    norm = np.linalg.norm(embedding)
    if norm == 0:
        return embedding
    return embedding / norm

def get_embedding_from_image_bytes(image_bytes: bytes) -> np.ndarray:
    """
    Detects the largest face in the image bytes and returns its normalized embedding.
    Returns a zero-vector if no face is found.
    
    Improvements:
    - Normalizes embeddings for better cosine similarity
    - Filters faces by quality score
    - Handles multiple faces and selects the best one
    """
    # Convert bytes to numpy array
    nparr = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    
    if img is None:
        # Could not decode image
        return np.zeros(512, dtype=np.float32)

    # Detect faces
    faces = app_face.get(img)
    if not faces:
        return np.zeros(512, dtype=np.float32)

    # Filter faces by detection score (quality threshold)
    # InsightFace provides a det_score for each face
    quality_threshold = 0.5
    quality_faces = [f for f in faces if f.det_score > quality_threshold]
    
    if not quality_faces:
        # If no high-quality faces, fall back to all faces
        quality_faces = faces
    
    # Sort by area (box width * height) to find the largest face
    # face.bbox is [x1, y1, x2, y2]
    quality_faces = sorted(
        quality_faces, 
        key=lambda x: (x.bbox[2] - x.bbox[0]) * (x.bbox[3] - x.bbox[1]), 
        reverse=True
    )
    
    # Get the embedding of the largest, highest-quality face
    embedding = quality_faces[0].embedding.astype(np.float32)
    
    # Normalize for better cosine similarity matching
    return normalize_embedding(embedding)

def get_embedding_from_file(file_path: str) -> np.ndarray:
    """
    Reads an image from disk and returns the normalized embedding of the largest face.
    
    Improvements:
    - Pre-processes image for better detection
    - Normalizes embeddings
    - Filters by face quality
    """
    img = cv2.imread(file_path)
    if img is None:
        return np.zeros(512, dtype=np.float32)
    
    # Optional: Enhance image quality for better detection
    # Resize if image is too large (helps with memory and speed)
    max_dimension = 1920
    height, width = img.shape[:2]
    if max(height, width) > max_dimension:
        scale = max_dimension / max(height, width)
        new_width = int(width * scale)
        new_height = int(height * scale)
        img = cv2.resize(img, (new_width, new_height), interpolation=cv2.INTER_AREA)
    
    # Detect faces
    faces = app_face.get(img)
    if not faces:
        return np.zeros(512, dtype=np.float32)
    
    # Filter by quality
    quality_threshold = 0.5
    quality_faces = [f for f in faces if f.det_score > quality_threshold]
    
    if not quality_faces:
        quality_faces = faces
    
    # Sort by area to find the largest face
    quality_faces = sorted(
        quality_faces,
        key=lambda x: (x.bbox[2] - x.bbox[0]) * (x.bbox[3] - x.bbox[1]),
        reverse=True
    )
    
    # Get embedding and normalize
    embedding = quality_faces[0].embedding.astype(np.float32)
    return normalize_embedding(embedding)