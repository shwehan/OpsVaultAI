from pathlib import Path

from backend.app.rag.ingest import build_index
from backend.app.rag.retrieve import get_index


def test_retrieval_smoke_builds_and_finds_expected_doc(tmp_path):
    # Build an index from repo's KB docs into a temp file
    docs_dir = Path("data/kb")
    assert docs_dir.exists(), "Expected data/kb to exist"

    out_path = tmp_path / "index.jsonl"
    n = build_index(
        docs_dir=docs_dir,
        out_path=out_path,
        chunk_chars=800,
        overlap_chars=150,
        dim=2048,
        exts=[".md", ".txt"],
    )
    assert n > 0

    idx = get_index(str(out_path))
    results = idx.retrieve("What is the return policy?", k=3)
    assert len(results) > 0

    # Expect the return policy doc to appear near the top
    top_sources = [r.source_id for r in results]
    assert any("return_policy" in s for s in top_sources)
