import numpy as np
from PIL import Image
import io

def get_embedding_from_image_bytes(img_bytes):
    # placeholder: replace with insightface model inference
    # return a deterministic pseudo-vector for dev testing

    arr = np.frombuffer(img_bytes, dtype = 'uint8')
    seed = int(arr.sum() % 1000000)
    rng = np.random.default_rng(seed)
    vec = rng.standard_normal(512).astype('float32')

    # normalize
    vec = vec / np.linalg.norm(vec)
    return vec