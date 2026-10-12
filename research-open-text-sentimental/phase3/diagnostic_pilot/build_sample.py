"""Build a blind, one-reviewer diagnostic-detail pilot from v2 development only."""

from __future__ import annotations

import hashlib
import json
import random
import re
from collections import Counter
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SOURCE = ROOT / "phase3/revised_development_v2/development_v2.jsonl"
SEED = 20261007
QUOTAS = {
    ("phase1_gold_file", False): 4,
    ("phase1_gold_file", True): 4,
    ("oct5_query_gds", False): 4,
    ("oct5_query_gds", True): 8,
    ("oct5_query_tps", False): 2,
    ("oct5_query_tps", True): 28,
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def text_key(row: dict) -> str:
    text = (row["title"] + "\n" + row["post_body"]).lower()
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9]+", " ", text)).strip()


def main() -> None:
    rows = [json.loads(line) for line in SOURCE.read_text().splitlines() if line]
    pool = [row for row in rows if row["s2_in_scope"] and row["s2_target"] == 1 and not row["reddit_id"].startswith("so_") and row["reddit_id"] not in {"1t0wme9", "1wrqch6"}]
    assert len(pool) == 1658
    rng = random.Random(SEED)
    chosen: list[dict] = []
    seen_text: set[str] = set()
    for (source, has_body), quota in QUOTAS.items():
        candidates = [row for row in pool if row["source_pool_audit_only"] == source and bool(row["post_body"].strip()) == has_body]
        rng.shuffle(candidates)
        count = 0
        for row in candidates:
            key = text_key(row)
            if key in seen_text:
                continue
            chosen.append(row)
            seen_text.add(key)
            count += 1
            if count == quota:
                break
        assert count == quota, (source, has_body, count)
    rng.shuffle(chosen)
    assert len(chosen) == 50 and len({row["reddit_id"] for row in chosen}) == 50

    reviewer = []
    mapping = []
    for i, row in enumerate(chosen, start=1):
        pilot_id = f"D{SEED}-{i:03d}"
        reviewer.append({"pilot_id": pilot_id, "title": row["title"], "post_body": row["post_body"]})
        mapping.append({"pilot_id": pilot_id, "reddit_id": row["reddit_id"], "study_id": row["study_id"], "source_pool": row["source_pool_audit_only"], "has_body": bool(row["post_body"].strip()), "subreddit": row["subreddit"], "created_utc": row["created_utc"]})
    (HERE / "pilot_review_text.json").write_text(json.dumps(reviewer, indent=2, ensure_ascii=False) + "\n")
    (HERE / "analyst_mapping.json").write_text(json.dumps(mapping, indent=2, ensure_ascii=False) + "\n")
    manifest = {
        "purpose": "Codebook feasibility pilot; not a prevalence estimate or independent test set",
        "seed": SEED,
        "source_v2_sha256": sha(SOURCE),
        "eligible_reddit_s2_troubleshooting_development_posts": len(pool),
        "pilot_n": len(chosen),
        "quotas": [{"source_pool": source, "has_body": has_body, "n": count} for (source, has_body), count in QUOTAS.items()],
        "review_text_sha256": sha(HERE / "pilot_review_text.json"),
        "mapping_sha256": sha(HERE / "analyst_mapping.json"),
        "reserved_test_used": False,
        "stack_overflow_excluded": True,
        "labels_filled": False,
    }
    (HERE / "sampling_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(json.dumps({"pilot_n": len(chosen), "eligible_pool": len(pool), "has_body": dict(Counter(str(bool(row['post_body'].strip())) for row in chosen))}, indent=2))


if __name__ == "__main__":
    main()
