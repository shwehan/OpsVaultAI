from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from .vector_utils import cosine_sim, hashed_tf_vector


@dataclass
class RetrievalResult:
    source_id: str
    snippet: str
    score: float


class Index:
    def __init__(self, rows: List[dict], dim: int = 2048):
        self.rows = rows
        self.dim = dim

    def retrieve(self, query: str, k: int = 5) -> List[RetrievalResult]:
        if not self.rows:
            return []

        qv = hashed_tf_vector(query, dim=self.dim)

        scored: List[RetrievalResult] = []
        for r in self.rows:
            vec = r.get("vector", [])
            if not vec:
                continue
            score = float(cosine_sim(qv, vec))

            text = r.get("text", "") or ""
            snippet = text[:240] + ("..." if len(text) > 240 else "")
            source_id = r.get("source_id", "") or ""

            scored.append(RetrievalResult(source_id=source_id, snippet=snippet, score=score))

        # scored.sort(key=lambda x: x.score, reverse=True)
        # return scored[: max(1, k)]
        scored.sort(key=lambda x: x.score, reverse=True)
        top = scored[: max(1, k)]

        # If we found at least one meaningful match, drop pure-zero noise.
        if any(r.score > 0.0 for r in top):
            top = [r for r in top if r.score > 0.0]

        return top


_index_cache: Dict[str, Tuple[float, Index]] = {}


def _load_rows(index_path: str) -> List[dict]:
    p = Path(index_path)
    if not p.exists():
        return []
    rows: List[dict] = []
    with p.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            rows.append(json.loads(line))
    return rows


def get_index(index_path: str, dim: int = 2048) -> Index:
    """
    Loads and caches the index by file mtime so you don't reload on every request.
    """
    p = Path(index_path)
    mtime = p.stat().st_mtime if p.exists() else -1.0

    cached = _index_cache.get(index_path)
    if cached and cached[0] == mtime:
        return cached[1]

    rows = _load_rows(index_path)
    idx = Index(rows=rows, dim=dim)
    _index_cache[index_path] = (mtime, idx)
    return idx
