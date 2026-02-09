from __future__ import annotations

import math
from typing import Dict, List

from .text_utils import tokenize


def hashed_tf_vector(text: str, dim: int = 2048) -> List[float]:
    """
    Dependency-free vectorization using a hashing trick:
    - tokenize -> hash(token) % dim
    - store term frequency
    """
    if dim <= 0:
        raise ValueError("dim must be > 0")

    vec = [0.0] * dim
    for tok in tokenize(text):
        idx = hash(tok) % dim
        vec[idx] += 1.0
    return vec


def cosine_sim(a: List[float], b: List[float]) -> float:
    if len(a) != len(b):
        raise ValueError("Vectors must have the same dimension")

    dot = 0.0
    na = 0.0
    nb = 0.0
    for x, y in zip(a, b):
        dot += x * y
        na += x * x
        nb += y * y

    if na == 0.0 or nb == 0.0:
        return 0.0

    return dot / (math.sqrt(na) * math.sqrt(nb))
