"""Freeze a simple random 250-post diagnostic sample and reviewer batch 1."""
from __future__ import annotations

import hashlib
import json
import random
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
SOURCE = HERE.parent / "revised_development_v2/development_v2.jsonl"
OUT = HERE / "main_sample_20261007"
SEED = 20261007
N = 250
BATCH_SIZE = 50


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path: Path, data: object) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n")


def main() -> None:
    assert digest(SOURCE) == "287995b6b8b529c145591108d9a77f88f1e515185d38810910066ffba21fa781"
    rows = [json.loads(line) for line in SOURCE.read_text().splitlines() if line]
    frame = [r for r in rows if r["s2_in_scope"] and r["s2_target"] == 1
             and not r["reddit_id"].startswith("so_")
             and r["reddit_id"] not in {"1t0wme9", "1wrqch6"}]
    assert len(frame) == 1658
    assert len({r["reddit_id"] for r in frame}) == len(frame)
    frame.sort(key=lambda r: r["reddit_id"])
    selected = random.Random(SEED).sample(frame, N)
    pilot_ids = {r["reddit_id"] for r in json.loads((HERE / "analyst_mapping.json").read_text())}

    OUT.mkdir(exist_ok=True)
    mapping = []
    reviewer_batches = [[] for _ in range(N // BATCH_SIZE)]
    for index, row in enumerate(selected, 1):
        blind_id = f"M20261007-{index:03d}"
        batch_index = (index - 1) // BATCH_SIZE
        reviewer_batches[batch_index].append({
            "sample_id": blind_id, "title": row["title"], "post_body": row["post_body"]
        })
        mapping.append({
            "sample_id": blind_id, "reddit_id": row["reddit_id"],
            "study_id": row["study_id"], "batch": batch_index + 1,
            "source_pool": row["source_pool_audit_only"],
            "has_body": bool(row["post_body"].strip()),
            "pilot_overlap": row["reddit_id"] in pilot_ids,
        })
    write_json(OUT / "analyst_mapping.json", mapping)
    for index, batch in enumerate(reviewer_batches, 1):
        write_json(OUT / f"review_batch_{index:02d}.json", batch)
    write_json(OUT / "sampling_manifest.json", {
        "purpose": "Simple random sample for diagnostic-field prevalence in the reviewed Reddit-only S2 troubleshooting development corpus",
        "sampling_unit": "unique Reddit post ID",
        "source_snapshot_sha256": digest(SOURCE),
        "seed": SEED,
        "frame_n": len(frame),
        "sample_n": len(selected),
        "inclusion_probability": f"{N}/{len(frame)}",
        "batch_size": BATCH_SIZE,
        "batches": len(reviewer_batches),
        "sampling_method": "Python random.Random(seed).sample after sorting frame by reddit_id",
        "pilot_overlap_n": sum(r["pilot_overlap"] for r in mapping),
        "source_distribution": dict(Counter(r["source_pool"] for r in mapping)),
        "body_missing_n": sum(not r["has_body"] for r in mapping),
        "reserved_test_used": False,
        "stack_overflow_excluded": True,
        "reviewer_files_contain_old_answers_or_source_pool": False,
        "guide": "CODEBOOK_v1.0.md",
        "analyst_mapping_sha256": digest(OUT / "analyst_mapping.json"),
    })
    print(json.dumps({"frame": len(frame), "sample": len(selected),
                      "pilot_overlap": sum(r["pilot_overlap"] for r in mapping),
                      "body_missing": sum(not r["has_body"] for r in mapping)}))


if __name__ == "__main__":
    main()
