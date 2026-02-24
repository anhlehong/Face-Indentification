import numpy as np


def generate_fake_embedding(dim: int = 512) -> np.ndarray:
    vector = np.random.rand(dim) - 0.5
    return vector / np.linalg.norm(vector)
