#!/usr/bin/env python3
"""Build a provenance-preserving Phase 2 master from saved inputs.

The old 542 labels remain legacy fields. Phase 2 fields are copied only from
the completed 100-post post-discussion sheet or the 300-post joint review.
No labels are inferred for the remaining old posts.
"""

from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

from build_pilot_sample import ROOT, build_candidate_pool, clip

ANN = ROOT / "phase2" / "annotation"
OUT = ROOT / "phase2" / "combined_dataset"
OLD_CSV = ROOT / "tps_gds_classification" / "data" / "updated_labeled_dataset_unique.csv"
PILOT_MAP = ANN / "pilot" / "pilot_id_mapping.csv"
EXPANSION_MAP = ANN / "expansion_300" / "ANALYST_ONLY_ID_MAPPING.csv"
NEW_SUB = ANN / "submissions" / "2026-10-06-second-review"
PILOT_MANU = NEW_SUB / "Manu_Blind_Review_100_Posts.csv"
PILOT_FINAL = NEW_SUB / "Berhe_Blind_Review_100_Posts.csv"
EXP_MANU = NEW_SUB / "Manu_Blind_Review_300_Posts.csv"
EXP_BERHE = NEW_SUB / "Berhe_Blind_Review_300_Posts.csv"
HOLDOUT_MAP = ANN / "heldout_200" / "ANALYST_ONLY_MAPPING.json"
HOLDOUT_FINAL = ANN / "heldout_200" / "final_consensus.json"
ASSISTED_FINAL = ANN / "submissions" / "2026-10-06-assisted-500" / "FINAL_REVIEW.json"
ASSISTED2_FINAL = ANN / "submissions" / "2026-10-07-assisted-500-round2" / "FINAL_REVIEW.json"
ASSISTED3_FINAL = ANN / "submissions" / "2026-10-07-assisted-1000-round3" / "FINAL_REVIEW.json"
ASSISTED4_FINAL = ANN / "submissions" / "2026-10-07-final-remaining-768" / "FINAL_REVIEW.json"
UNCERTAIN_REVISIT = ANN / "submissions" / "2026-10-07-final-remaining-768" / "UNCERTAIN_REVISIT.json"
FIELDS = ("about_software", "update_related", "discussion_type")


def read_csv(path: Path, key: str) -> dict[str, dict]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    result = {row[key].strip(): row for row in rows}
    if len(result) != len(rows) or any(not k for k in result):
        raise ValueError(f"Missing or duplicate {key}: {path}")
    return result


def study_id(reddit_id: str) -> str:
    return "C2-" + hashlib.sha256(f"phase2-combined:{reddit_id}".encode()).hexdigest()[:12].upper()


def main() -> None:
    old = read_csv(OLD_CSV, "reddit_id")
    pilot_map = read_csv(PILOT_MAP, "pilot_id")
    expansion_map = read_csv(EXPANSION_MAP, "review_id")
    pilot_manu = read_csv(PILOT_MANU, "pilot_id")
    pilot_final = read_csv(PILOT_FINAL, "pilot_id")
    expansion_manu = read_csv(EXP_MANU, "review_id")
    expansion_berhe = read_csv(EXP_BERHE, "review_id")

    if len(old) != 542 or len(pilot_map) != 100 or len(expansion_map) != 300:
        raise ValueError("Unexpected source counts")
    if set(pilot_map) != set(pilot_manu) or set(pilot_map) != set(pilot_final):
        raise ValueError("Pilot id mismatch")
    if set(expansion_map) != set(expansion_manu) or set(expansion_map) != set(expansion_berhe):
        raise ValueError("Expansion id mismatch")
    for pid in pilot_map:
        if any(pilot_manu[pid][f] != pilot_final[pid][f] for f in FIELDS):
            raise ValueError(f"Pilot final values still disagree: {pid}")
    for rid in expansion_map:
        if any(expansion_manu[rid][f] != expansion_berhe[rid][f] for f in FIELDS):
            raise ValueError(f"Expansion joint values disagree: {rid}")

    candidates = {row["reddit_id"]: row for row in build_candidate_pool()}
    selected_ids = set(candidates)
    reviewed_ids = set(old)
    reviewed_ids.update(m["reddit_id"] for m in pilot_map.values())
    reviewed_ids.update(m["reddit_id"] for m in expansion_map.values())
    if len(selected_ids) != 3362 or len(reviewed_ids) != 893:
        raise ValueError(f"Unexpected corpus sizes: {len(selected_ids)} total, {len(reviewed_ids)} old-or-reviewed")

    review_by_reddit_id = {}
    for pid, mapping in pilot_map.items():
        rid = mapping["reddit_id"]
        review_by_reddit_id[rid] = ("pilot_post_discussion", pid, pilot_final[pid])
    for review_id, mapping in expansion_map.items():
        rid = mapping["reddit_id"]
        if rid in review_by_reddit_id:
            raise ValueError(f"Expansion overlaps pilot: {rid}")
        review_by_reddit_id[rid] = ("joint_review", review_id, expansion_manu[review_id])
    if len(review_by_reddit_id) != 400:
        raise ValueError("Expected 400 reviewed posts")

    reserved_ids = set()
    holdout_mapping = {}
    if HOLDOUT_MAP.exists():
        holdout_mapping = {r["review_id"]: r["reddit_id"] for r in json.loads(HOLDOUT_MAP.read_text(encoding="utf-8"))}
        reserved_ids = set(holdout_mapping.values())
        if len(reserved_ids) != 200 or reserved_ids & set(review_by_reddit_id) or not reserved_ids <= selected_ids:
            raise ValueError("Invalid reserved test ids")
    if HOLDOUT_FINAL.exists():
        final_rows = json.loads(HOLDOUT_FINAL.read_text(encoding="utf-8"))
        if len(final_rows) != 200 or {r["review_id"] for r in final_rows} != set(holdout_mapping):
            raise ValueError("Invalid final holdout labels")
        for row in final_rows:
            rid = holdout_mapping[row["review_id"]]
            review_by_reddit_id[rid] = ("reserved_test_consensus", row["review_id"], row)

    for assisted_file, expected_rows in ((ASSISTED_FINAL, 500), (ASSISTED2_FINAL, 500),
                                         (ASSISTED3_FINAL, 1000), (ASSISTED4_FINAL, 762)):
        if not assisted_file.exists():
            continue
        assisted_rows = json.loads(assisted_file.read_text(encoding="utf-8"))
        if len(assisted_rows) != expected_rows or len({r["review_id"] for r in assisted_rows}) != expected_rows:
            raise ValueError(f"Expected {expected_rows} distinct assisted-review rows")
        for row in assisted_rows:
            rid = row["reddit_id"]
            if rid not in selected_ids or rid in review_by_reddit_id or rid in reserved_ids:
                raise ValueError(f"Invalid assisted-review overlap: {rid}")
            if row["decision"] not in {"accept", "revise", "uncertain"}:
                raise ValueError(f"Invalid assisted-review decision: {rid}")
            if row["decision"] == "uncertain":
                if any(row.get(field) for field in FIELDS):
                    raise ValueError(f"Uncertain review has labels: {rid}")
                review_by_reddit_id[rid] = ("manu_assisted_uncertain", row["review_id"], row)
            else:
                if any(not row.get(field) for field in FIELDS):
                    raise ValueError(f"Resolved assisted review lacks labels: {rid}")
                review_by_reddit_id[rid] = ("manu_assisted_review", row["review_id"], row)

    if UNCERTAIN_REVISIT.exists():
        revisit_rows = json.loads(UNCERTAIN_REVISIT.read_text(encoding="utf-8"))
        if len(revisit_rows) != 6 or len({r["review_id"] for r in revisit_rows}) != 6:
            raise ValueError("Expected six distinct uncertain revisits")
        for row in revisit_rows:
            rid = row["reddit_id"]
            prior = review_by_reddit_id.get(rid)
            if prior is None or prior[0] != "manu_assisted_uncertain" or prior[1] != row["review_id"]:
                raise ValueError(f"Revisit is not a previously uncertain post: {rid}")
            if row["decision"] == "resolved":
                if any(not row.get(field) for field in FIELDS):
                    raise ValueError(f"Resolved revisit lacks labels: {rid}")
                review_by_reddit_id[rid] = ("manu_assisted_review", row["review_id"], row)
            elif row["decision"] == "still_uncertain":
                if any(row.get(field) for field in FIELDS):
                    raise ValueError(f"Still-uncertain revisit has labels: {rid}")
                review_by_reddit_id[rid] = ("manu_assisted_uncertain", row["review_id"], row)
            else:
                raise ValueError(f"Invalid revisit decision: {rid}")

    master = []
    for rid in sorted(selected_ids):
        source = candidates[rid]
        legacy = old.get(rid)
        status, review_ref, review = review_by_reddit_id.get(rid, ("needs_phase2_review", "", {}))
        if rid in reserved_ids and status == "needs_phase2_review":
            status = "reserved_test_unlabeled"
        master.append({
            "study_id": study_id(rid),
            "reddit_id": rid,
            "url": source.get("url", ""),
            "subreddit": source.get("subreddit", ""),
            "created_utc": source.get("created_utc", ""),
            "source_family": "phase1_542" if legacy else "oct5_api",
            "source_pool": source.get("source_pool", ""),
            "title": source.get("title", ""),
            "post_body": source.get("post_body", ""),
            "discussion_context": source.get("discussion_context", ""),
            "text_availability": source.get("text_availability", ""),
            "n_comments_stored": source.get("n_comments_stored", 0),
            "phase1_legacy_label": legacy.get("corrected_label", "") if legacy else "",
            "phase2_review_status": status,
            "phase2_review_ref": review_ref,
            "phase2_about_software": review.get("about_software", ""),
            "phase2_update_related": review.get("update_related", ""),
            "phase2_discussion_type": review.get("discussion_type", ""),
            "phase2_confidence": review.get("confidence", ""),
            "phase2_reason": review.get("reason", ""),
        })
    master.sort(key=lambda x: (x["source_family"] != "phase1_542", x["study_id"]))
    if len({r["study_id"] for r in master}) != 3362:
        raise ValueError("Study id collision")
    expected_unreviewed = 3362 - len(review_by_reddit_id)
    if sum(r["phase2_review_status"] in {"needs_phase2_review", "reserved_test_unlabeled"} for r in master) != expected_unreviewed:
        raise ValueError(f"Expected {expected_unreviewed} posts awaiting Phase 2 review")

    blind = []
    for r in master:
        if r["phase2_review_status"] != "needs_phase2_review" or r["source_family"] != "phase1_542":
            continue
        blind.append({
            "study_id": r["study_id"],
            "title": r["title"],
            "post_body": clip(r["post_body"], 2500),
            "discussion_context": clip(r["discussion_context"], 2000),
            "text_availability_note": r["text_availability"],
            "about_software": "",
            "update_related": "",
            "discussion_type": "",
            "confidence": "",
            "reason": "",
        })

    counts = {
        "master_posts": len(master),
        "original_posts": sum(r["source_family"] == "phase1_542" for r in master),
        "new_posts": sum(r["source_family"] == "oct5_api" for r in master),
        "review_status": dict(Counter(r["phase2_review_status"] for r in master)),
        "reviewed_discussion_type": dict(Counter(r["phase2_discussion_type"] for r in master if r["phase2_review_status"] in {"pilot_post_discussion", "joint_review", "reserved_test_consensus", "manu_assisted_review"})),
        "blind_review_rows": len(blind),
        "strict_scope_reviewed": sum(r["phase2_about_software"] == "yes" and r["phase2_update_related"] == "yes" for r in master),
    }

    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "master_records.json").write_text(json.dumps(master, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (OUT / "blind_review_old_remaining.json").write_text(json.dumps(blind, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (OUT / "build_manifest.json").write_text(json.dumps({"built_at_utc": datetime.now(timezone.utc).isoformat(), "label_snapshot": str(NEW_SUB), "holdout_consensus": str(HOLDOUT_FINAL) if HOLDOUT_FINAL.exists() else None, "assisted_reviews": [str(path) for path in (ASSISTED_FINAL, ASSISTED2_FINAL, ASSISTED3_FINAL, ASSISTED4_FINAL) if path.exists()], "uncertain_revisit": str(UNCERTAIN_REVISIT) if UNCERTAIN_REVISIT.exists() else None, "counts": counts, "notes": ["Phase 1 labels are stored only as legacy values.", "The 300 new-post labels are joint decisions, not independent agreement.", "The 100 pilot final values are post-discussion decisions; use the original pre-discussion report for agreement.", "The 200 reserved-test labels came from one jointly written draft and do not support an independent agreement statistic.", "The assisted-review submissions have 2,757 resolved labels, while five posts remain uncertain; proposals are not independent human annotations.", "Reserved-test posts must never be used in training or model selection."]}, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(counts, indent=2))


if __name__ == "__main__":
    main()
