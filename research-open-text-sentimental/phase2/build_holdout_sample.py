#!/usr/bin/env python3
"""Reserve 200 as-yet-unreviewed new API posts for a blind final test.

The 100/100 API-pool selection is a reproducible source-stratified sample,
not an estimate of class prevalence across Reddit. No answers are assigned.
"""

from __future__ import annotations

import hashlib
import json
import random
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

from build_pilot_sample import ROOT, availability_note, build_candidate_pool, clip

SEED = 2026100615
PER_POOL = 100
MASTER = ROOT / "phase2" / "combined_dataset" / "master_records.json"
OUT = ROOT / "phase2" / "annotation" / "heldout_200"


def main() -> None:
    if OUT.exists() and any(OUT.iterdir()):
        raise SystemExit(f"Refusing to overwrite reserved sample: {OUT}")
    master = json.loads(MASTER.read_text(encoding="utf-8"))
    unreviewed_new = {
        r["reddit_id"]
        for r in master
        if r["source_family"] == "oct5_api"
        and r["phase2_review_status"] == "needs_phase2_review"
    }
    by_pool: dict[str, list[dict]] = {"oct5_query_tps": [], "oct5_query_gds": []}
    for row in build_candidate_pool():
        if row["reddit_id"] in unreviewed_new:
            by_pool[row["source_pool"]].append(row)
    if sum(len(v) for v in by_pool.values()) != 2469 or any(len(v) < PER_POOL for v in by_pool.values()):
        raise ValueError(f"Unexpected eligible pool sizes: { {k:len(v) for k,v in by_pool.items()} }")
    rng = random.Random(SEED)
    selected = []
    for pool, rows in by_pool.items():
        selected += rng.sample(sorted(rows, key=lambda r: r["reddit_id"]), PER_POOL)
    rng.shuffle(selected)
    if len({r["reddit_id"] for r in selected}) != 200:
        raise ValueError("Duplicate post in holdout")

    reviewer_rows, mapping_rows = [], []
    for order, row in enumerate(selected, start=1):
        rid = row["reddit_id"]
        anonymous = "H2-" + hashlib.sha256(f"{SEED}:{rid}".encode()).hexdigest()[:12].upper()
        reviewer_rows.append({
            "review_id": anonymous,
            "sheet_order": order,
            "title": row["title"],
            "post_body": clip(row["post_body"], 2500),
            "discussion_context": clip(row["discussion_context"], 2000),
            "text_availability_note": availability_note(row["text_availability"]),
            "about_software": "",
            "update_related": "",
            "discussion_type": "",
            "confidence": "",
            "reason": "",
        })
        mapping_rows.append({
            "review_id": anonymous,
            "reddit_id": rid,
            "source_pool": row["source_pool"],
            "url": row["url"],
            "subreddit": row["subreddit"],
            "created_utc": row.get("created_utc", ""),
            "text_availability": row["text_availability"],
        })
    OUT.mkdir(parents=True)
    (OUT / "blind_review_rows.json").write_text(json.dumps(reviewer_rows, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (OUT / "ANALYST_ONLY_MAPPING.json").write_text(json.dumps(mapping_rows, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    manifest = {
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "seed": SEED,
        "n": len(selected),
        "eligible_frame_counts": {k: len(v) for k, v in by_pool.items()},
        "sample_counts": dict(Counter(r["source_pool"] for r in selected)),
        "text_availability_counts": dict(Counter(r["text_availability"] for r in selected)),
        "design": "100 simple-random posts from each saved API candidate pool, excluding original posts and all 400 Phase 2 reviewed posts; pool identities hidden from reviewers.",
        "limitation": "Source-stratified candidate sample; cannot estimate prevalence in all Reddit update discussions.",
        "reservation": "Do not train models or generate assistant label suggestions on these post ids before both blind human reviews are complete and final labels frozen.",
    }
    (OUT / "sampling_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
