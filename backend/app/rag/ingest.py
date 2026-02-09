from __future__ import annotations

import argparse
import json
import os
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable, List, Optional

from .text_utils import chunk_text, normalize_text
from .vector_utils import hashed_tf_vector


@dataclass
class ChunkRecord:
    source_id: str
    title: str
    chunk_id: str
    text: str
    vector: List[float]


def iter_doc_paths(docs_dir: Path, exts: List[str]) -> Iterable[Path]:
    for p in docs_dir.rglob("*"):
        if p.is_file() and p.suffix.lower() in exts:
            yield p


def read_text_file(path: Path) -> str:
    # Robust-ish for mixed encodings
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return path.read_text(encoding="latin-1")


def build_index(
    docs_dir: Path,
    out_path: Path,
    chunk_chars: int,
    overlap_chars: int,
    dim: int,
    exts: List[str],
) -> int:
    out_path.parent.mkdir(parents=True, exist_ok=True)

    n_chunks = 0
    with out_path.open("w", encoding="utf-8") as f:
        for doc_path in iter_doc_paths(docs_dir, exts):
            rel = doc_path.relative_to(docs_dir).as_posix()
            title = doc_path.stem

            raw = read_text_file(doc_path)
            raw = normalize_text(raw)

            chunks = chunk_text(raw, chunk_chars=chunk_chars, overlap_chars=overlap_chars)
            for i, chunk in enumerate(chunks):
                rec = ChunkRecord(
                    source_id=rel,
                    title=title,
                    chunk_id=f"{rel}::chunk_{i}",
                    text=chunk,
                    vector=hashed_tf_vector(chunk, dim=dim),
                )
                f.write(json.dumps(asdict(rec), ensure_ascii=False) + "\n")
                n_chunks += 1

    return n_chunks


def main() -> None:
    parser = argparse.ArgumentParser(description="Build a simple JSONL chunk index from docs.")
    parser.add_argument("--docs", required=True, help="Path to docs directory to index")
    parser.add_argument("--out", required=True, help="Output JSONL path (e.g., data/index.jsonl)")
    parser.add_argument("--chunk-chars", type=int, default=800)
    parser.add_argument("--overlap-chars", type=int, default=150)
    parser.add_argument("--dim", type=int, default=2048)
    parser.add_argument(
        "--exts",
        default=".md,.txt",
        help="Comma-separated extensions to include (default: .md,.txt)",
    )
    args = parser.parse_args()

    docs_dir = Path(args.docs).resolve()
    out_path = Path(args.out).resolve()
    exts = [e.strip().lower() for e in args.exts.split(",") if e.strip()]
    if not docs_dir.exists() or not docs_dir.is_dir():
        raise SystemExit(f"--docs path does not exist or is not a directory: {docs_dir}")

    n = build_index(
        docs_dir=docs_dir,
        out_path=out_path,
        chunk_chars=args.chunk_chars,
        overlap_chars=args.overlap_chars,
        dim=args.dim,
        exts=exts,
    )
    print(f"✅ Wrote {n} chunks to {out_path}")


if __name__ == "__main__":
    main()
