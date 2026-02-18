import sys
from pathlib import Path

# Ensure repo root is on PYTHONPATH so `import backend...` works when running as a script
REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

# from __future__ import annotations

import json
import statistics
import time
from pathlib import Path
from typing import Dict, List

from backend.app.rag.ingest import build_index
from backend.app.rag.retrieve import get_index

STOPWORDS = {
    "what","is","the","a","an","your","our","do","does","we","are",
    "to","of","and","or","in","on","for","with","how"
}
GENERIC = {"policy","process","help","support"}

def extract_keywords(q: str) -> List[str]:
    tokens = [t.strip(".,?!:;()[]{}\"'").lower() for t in (q or "").split()]
    tokens = [t for t in tokens if len(t) >= 4 and t not in STOPWORDS and t not in GENERIC]
    return tokens


def load_golden(path: Path) -> List[Dict]:
    rows = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def recall_at_k(found_sources: List[str], expected_sources: List[str]) -> float:
    expected = set(expected_sources)
    found = set(found_sources)
    return 1.0 if len(expected.intersection(found)) > 0 else 0.0


def main():
    # Build an index from KB docs so eval is reproducible
    docs_dir = Path("data/kb")
    assert docs_dir.exists(), "Expected data/kb to exist"

    index_path = Path("data/index.jsonl")
    n = build_index(
        docs_dir=docs_dir,
        out_path=index_path,
        chunk_chars=800,
        overlap_chars=150,
        dim=2048,
        exts=[".md", ".txt"],
    )
    print(f"Index built: {n} chunks -> {index_path}")

    idx = get_index(str(index_path))

    golden_path = Path("eval/golden_questions.jsonl")
    golden = load_golden(golden_path)

    ks = [1, 3, 5]

    MIN_SCORE = 0.12
    abstained_flags: List[bool] = []
    abstain_correct: List[bool] = []


    recalls = {k: [] for k in ks}
    latencies_ms: List[float] = []

    # answerable = len(expected) > 0

    for row in golden:
        q = row["q"]
        expected = row.get("expected_sources", [])
        t0 = time.time()
        results = idx.retrieve(q, k=max(ks))
        
        # top_score = results[0].score if results else 0.0
        # abstained = top_score < MIN_SCORE
        # abstained_flags.append(abstained)

        # should_abstain = (len(expected) == 0)
        # abstain_correct.append(abstained == should_abstain)



        ms = (time.time() - t0) * 1000.0
        latencies_ms.append(ms)

        # found_sources = [r.source_id for r in results]

        # # for k in ks:
        # #     recalls[k].append(recall_at_k(found_sources[:k], expected))
        # if answerable:
        #     for k in ks:
        #         topk = [r.source_id for r in results[:k]]
        #         recalls[k].append(any(src in topk for src in expected))
            
        found_sources = [r.source_id for r in results]

        # score-based abstain
        top_score = results[0].score if results else 0.0
        low_score = top_score < MIN_SCORE

        # keyword-missing abstain (matches API guardrail)
        keywords = extract_keywords(q)
        joined = " ".join([getattr(r, "snippet", "") for r in results]).lower()
        missing = [kw for kw in keywords if kw not in joined]
        missing_keywords = (len(keywords) > 0 and len(missing) == len(keywords))

        abstained = low_score or missing_keywords
        abstained_flags.append(abstained)

        expected = row.get("expected_sources", [])
        answerable = len(expected) > 0
        should_abstain = not answerable
        abstain_correct.append(abstained == should_abstain)

        if answerable:
            for k in ks:
                topk = [r.source_id for r in results[:k]]
                recalls[k].append(any(src in topk for src in expected))


        print(f"\nQ: {q}")
        print(f"Expected: {expected}")
        print("Top sources:", found_sources[:5])
        print(f"Latency: {ms:.1f} ms")

        print(f"Top score: {top_score:.3f} | Abstained: {abstained}")

        print(f"Should abstain: {should_abstain}")

    # print("\n=== Summary ===")
    # for k in ks:
    #     print(f"Recall@{k}: {sum(recalls[k]) / len(recalls[k]):.2f}")

    # abstain_rate = sum(1 for a in abstained_flags if a) / len(abstained_flags)
    # print(f"Abstain rate: {abstain_rate:.2f} (MIN_SCORE={MIN_SCORE:.2f})")
    
    # abstain_acc = sum(abstain_correct) / len(abstain_correct) if abstain_correct else 0.0
    # print(f"Abstain accuracy: {abstain_acc:.2f}")
    print("\n=== Summary ===")
    for k in ks:
        denom = len(recalls[k])
        print(f"Recall@{k} (answerable only): {(sum(recalls[k]) / denom):.2f}" if denom else f"Recall@{k}: n/a")

    abstain_rate = sum(1 for a in abstained_flags if a) / len(abstained_flags)
    print(f"Abstain rate (all): {abstain_rate:.2f} (MIN_SCORE={MIN_SCORE:.2f})")

    abstain_acc = sum(abstain_correct) / len(abstain_correct) if abstain_correct else 0.0
    print(f"Abstain accuracy (all): {abstain_acc:.2f}")

    p50 = statistics.median(latencies_ms)
    p95 = sorted(latencies_ms)[max(0, int(0.95 * len(latencies_ms)) - 1)]
    print(f"Latency p50: {p50:.1f} ms")
    print(f"Latency p95: {p95:.1f} ms")


if __name__ == "__main__":
    main()
