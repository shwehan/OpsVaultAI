from __future__ import annotations

import re
from typing import List


_WORD_RE = re.compile(r"[a-zA-Z0-9_]+")


def normalize_text(s: str) -> str:
    # Light cleanup: keep it simple and predictable.
    s = s.replace("\r\n", "\n").replace("\r", "\n")
    return s.strip()


def tokenize(s: str) -> List[str]:
    s = s.lower()
    return _WORD_RE.findall(s)


def chunk_text(text: str, chunk_chars: int = 800, overlap_chars: int = 150) -> List[str]:
    """
    Chunk by character length (fast + dependency-free).
    Overlap helps preserve context across boundaries.
    """
    text = normalize_text(text)
    if not text:
        return []

    if chunk_chars <= 0:
        return [text]

    chunks: List[str] = []
    start = 0
    n = len(text)

    while start < n:
        end = min(start + chunk_chars, n)
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)

        if end >= n:
            break

        # overlap
        start = max(0, end - overlap_chars)

        # avoid infinite loops if overlap >= chunk
        if start >= end:
            start = end

    return chunks
