#!/usr/bin/env python3
"""Build two identical, blank reviewer sheets for 300 new API candidates.

The selection is a reproducible simple random sample within each saved API
pool. Source information stays in an analyst-only mapping. Existing pilot and
Phase 1 posts are excluded. This script never assigns research labels.
"""

from __future__ import annotations

import csv
import hashlib
import json
import random
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

from build_pilot_sample import (
    API_DIR,
    GOLD_CSV,
    ROOT,
    anonymous_id,
    availability_note,
    clip,
    comment_snippets,
    load_new_api_posts,
    text_available,
)

SEED = 20261006
PER_POOL = 150
OUT_DIR = ROOT / "phase2" / "annotation" / "expansion_300"
PILOT_MAP = ROOT / "phase2" / "annotation" / "pilot" / "pilot_id_mapping.csv"
POOL_FILES = {
    "tps": ["tps_response.json", "tps_page_2.json", "tps_page_3.json", "tps_page_4.json", "tps_page_5.json"],
    "gds": ["gds_response.json"],
}


def ids_from_csv(path: Path, column: str) -> set[str]:
    with path.open(encoding="utf-8", newline="") as handle:
        return {row[column].strip() for row in csv.DictReader(handle) if row.get(column, "").strip()}


def normalize(post: dict, pool: str) -> dict | None:
    rid = str(post.get("redditId") or "").strip()
    title = str(post.get("title") or "").strip()
    body = str(post.get("author_description") or "").strip()
    comments = post.get("comments") or []
    context = comment_snippets(comments)
    available, availability = text_available(title, body, context)
    if not rid or not available:
        return None
    features = post.get("features") or {}
    keywords = features.get("matchedKeywords") if isinstance(features, dict) else None
    return {
        "reddit_id": rid,
        "url": post.get("url") or "",
        "subreddit": post.get("subreddit") or "",
        "source_pool": f"oct5_query_{pool}",
        "api_matched_keywords": keywords if isinstance(keywords, list) else [],
        "created_utc": post.get("created_utc") or "",
        "n_comments_stored": len(comments),
        "title": title,
        "post_body": body,
        "discussion_context": context,
        "text_availability": availability,
    }


def write_csv(path: Path, columns: list[str], rows: list[dict]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    if OUT_DIR.exists() and any(OUT_DIR.iterdir()):
        raise SystemExit(f"Refusing to replace existing review files: {OUT_DIR}")
    old_ids = ids_from_csv(GOLD_CSV, "reddit_id")
    pilot_ids = ids_from_csv(PILOT_MAP, "reddit_id")
    excluded = old_ids | pilot_ids
    tps_raw, gds_raw = load_new_api_posts()
    source_rows = {"tps": tps_raw, "gds": gds_raw}

    # An id present in both endpoints is removed from both sample frames so
    # source strata remain unambiguous. Keep the count in the manifest.
    tps_ids = {str(p.get("redditId") or "").strip() for p in tps_raw}
    gds_ids = {str(p.get("redditId") or "").strip() for p in gds_raw}
    cross_pool_ids = tps_ids & gds_ids
    frames = {}
    for pool, posts in source_rows.items():
        rows = [normalize(p, pool) for p in posts if str(p.get("redditId") or "").strip() not in excluded | cross_pool_ids]
        rows = [r for r in rows if r is not None]
        unique = {r["reddit_id"]: r for r in rows}
        frames[pool] = [unique[rid] for rid in sorted(unique)]
        if len(frames[pool]) < PER_POOL:
            raise SystemExit(f"Only {len(frames[pool])} eligible {pool} posts; need {PER_POOL}")

    rng = random.Random(SEED)
    selected = rng.sample(frames["tps"], PER_POOL) + rng.sample(frames["gds"], PER_POOL)
    rng.shuffle(selected)
    ids = [r["reddit_id"] for r in selected]
    if len(ids) != len(set(ids)) or set(ids) & excluded:
        raise AssertionError("Duplicate or excluded post entered sample")
    for order, row in enumerate(selected, start=1):
        row["review_id"] = anonymous_id(SEED, row["reddit_id"])
        row["sheet_order"] = order
    if len({r["review_id"] for r in selected}) != len(selected):
        raise AssertionError("Anonymous id collision")

    review_columns = [
        "review_id", "sheet_order", "title", "post_body", "discussion_context",
        "text_availability_note", "about_software", "update_related",
        "discussion_type", "confidence", "reason",
    ]
    review_rows = [{
        "review_id": r["review_id"],
        "sheet_order": r["sheet_order"],
        "title": r["title"],
        "post_body": clip(r["post_body"], 2500),
        "discussion_context": clip(r["discussion_context"], 2000),
        "text_availability_note": availability_note(r["text_availability"]),
        "about_software": "", "update_related": "", "discussion_type": "",
        "confidence": "", "reason": "",
    } for r in selected]
    map_columns = [
        "review_id", "sheet_order", "reddit_id", "url", "subreddit", "source_pool",
        "api_matched_keywords", "created_utc", "n_comments_stored",
        "text_availability", "title",
    ]
    map_rows = [{**r, "api_matched_keywords": "|".join(r["api_matched_keywords"])} for r in selected]

    OUT_DIR.mkdir(parents=True)
    write_csv(OUT_DIR / "Manu_Blind_Review_300_Posts.csv", review_columns, review_rows)
    write_csv(OUT_DIR / "Berhe_Blind_Review_300_Posts.csv", review_columns, review_rows)
    write_csv(OUT_DIR / "ANALYST_ONLY_ID_MAPPING.csv", map_columns, map_rows)
    manifest = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "seed": SEED,
        "sample_design": "Simple random sample without replacement within each October 5 API candidate pool; 150 per pool.",
        "sample_counts": dict(Counter(r["source_pool"] for r in selected)),
        "eligible_frame_counts": {pool: len(rows) for pool, rows in frames.items()},
        "excluded_phase1_ids": len(old_ids),
        "excluded_pilot_ids": len(pilot_ids),
        "cross_pool_ids_excluded": len(cross_pool_ids),
        "text_availability_counts": dict(Counter(r["text_availability"] for r in selected)),
        "input_files": {pool: [{"path": str(API_DIR / name), "sha256": hashlib.sha256((API_DIR / name).read_bytes()).hexdigest()} for name in names] for pool, names in POOL_FILES.items()},
        "limitations": [
            "The two API pools are keyword-selected candidates, not human labels.",
            "The 150/150 sample is not a prevalence estimate for Reddit or for all update discussions.",
            "Reviewer sheets show a saved and clipped text snapshot, including up to five short reply snippets.",
            "No human judgments were generated by this script.",
        ],
    }
    (OUT_DIR / "sampling_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(OUT_DIR), "counts": manifest["sample_counts"], "eligible_frames": manifest["eligible_frame_counts"], "cross_pool_excluded": len(cross_pool_ids)}, indent=2))


if __name__ == "__main__":
    main()
