from __future__ import annotations

import hashlib
import math
from typing import List

from .text_utils import tokenize


def _stable_hash_64(token: str) -> int:
    # Stable across runs/platforms.
    digest = hashlib.blake2b(token.encode("utf-8"), digest_size=8).digest()
    return int.from_bytes(digest, "little", signed=False)


def hashed_tf_vector(text: str, dim: int = 2048) -> List[float]:
    """
    Dependency-free vectorization using a *stable* hashing trick:
    - tokenize -> stable_hash(token) % dim
    - store term frequency
    """
    if dim <= 0:
        raise ValueError("dim must be > 0")

    vec = [0.0] * dim
    for tok in tokenize(text):
        idx = _stable_hash_64(tok) % dim
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
