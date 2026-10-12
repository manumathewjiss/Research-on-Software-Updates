#!/usr/bin/env python3
"""Archive and validate Manu's final 762-post review plus six revisited cases."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / "phase2/annotation/final_remaining_768"
DEST = ROOT / "phase2/annotation/submissions/2026-10-07-final-remaining-768"
MASTER = ROOT / "phase2/combined_dataset/master_records.json"
FIELDS = ("about_software", "update_related", "discussion_type")
ALLOWED = {
    "about_software": {"yes", "no", "unclear"},
    "update_related": {"yes", "no", "unclear"},
    "discussion_type": {"technical_troubleshooting", "general_dissatisfaction", "other", "na"},
}
CONTROL = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\ufffe\uffff]")
SOURCE_FIELDS = ("subreddit", "title", "post_body", "discussion_context", "text_availability",
                 "proposed_about_software", "proposed_update_related", "proposed_discussion_type",
                 "proposed_confidence", "proposed_reason", "source_url")
UNCERTAIN_SOURCE_FIELDS = ("subreddit", "title", "post_body", "discussion_context",
                           "text_availability", "previous_uncertainty_note", "source_url")


def normalize(value: str) -> str:
    return CONTROL.sub("", str(value)).replace("\r\n", "\n").replace("\r", "\n")


def source_matches(expected: str, submitted: str) -> bool:
    expected = normalize(expected)
    submitted = normalize(submitted)
    return submitted == expected or (expected.startswith(("=", "+", "@")) and submitted == "'" + expected)


def check_labels(labels: dict, review_id: str) -> None:
    for field in FIELDS:
        if labels[field] not in ALLOWED[field]:
            raise ValueError(f"Invalid {field} on {review_id}: {labels[field]!r}")
    if (labels["about_software"] == "yes") == (labels["discussion_type"] == "na"):
        raise ValueError(f"Inconsistent software scope and type on {review_id}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("reviewed_workbook", type=Path)
    args = parser.parse_args()
    workbook = args.reviewed_workbook.resolve()
    if not workbook.is_file():
        raise FileNotFoundError(workbook)
    expected = {r["review_id"]: r for r in json.loads((SOURCE / "workbook_rows.json").read_text(encoding="utf-8"))}
    uncertain_expected = {r["review_id"]: r for r in json.loads((SOURCE / "uncertain_rows.json").read_text(encoding="utf-8"))}
    mapping = {r["review_id"]: r for r in json.loads((SOURCE / "ANALYST_ONLY_MAPPING.json").read_text(encoding="utf-8"))}
    master = {r["phase2_review_ref"]: r for r in json.loads(MASTER.read_text(encoding="utf-8"))
              if r["phase2_review_status"] == "manu_assisted_uncertain"}
    if len(expected) != 762 or set(expected) != set(mapping) or len(uncertain_expected) != 6 or set(uncertain_expected) != set(master):
        raise ValueError("Original review materials or unresolved mapping incomplete")
    xl = pd.ExcelFile(workbook)
    expected_sheets = ["Start here"] + [f"Batch {i}" for i in range(21, 29)] + ["Uncertain 6"]
    if xl.sheet_names != expected_sheets:
        raise ValueError("Unexpected workbook tabs")
    reviewed = []
    for batch in range(21, 29):
        rows = pd.read_excel(workbook, sheet_name=f"Batch {batch}", dtype=str,
                             keep_default_na=False).to_dict("records")
        count = 62 if batch == 28 else 100
        if len(rows) != count:
            raise ValueError(f"Batch {batch} has {len(rows)} posts, expected {count}")
        for row in rows:
            review_id = row["review_id"].strip()
            if review_id not in expected or not review_id.startswith(f"B{batch}-"):
                raise ValueError(f"Unexpected ID {review_id}")
            for field in SOURCE_FIELDS:
                if not source_matches(expected[review_id][field], row[field]):
                    raise ValueError(f"Source or proposal changed: {review_id}/{field}")
            decision = row["decision"].strip().lower()
            if decision not in {"accept", "revise", "uncertain"}:
                raise ValueError(f"Missing or invalid decision: {review_id}")
            labels = {field: row[f"final_{field}"].strip() for field in FIELDS}
            if decision == "accept":
                if any(labels.values()):
                    raise ValueError(f"Unexpected final fields on accepted {review_id}")
                labels = {field: row[f"proposed_{field}"].strip() for field in FIELDS}
            elif decision == "revise":
                if not row["reviewer_note"].strip():
                    raise ValueError(f"Revision lacks note: {review_id}")
            else:
                if any(labels.values()) or not row["reviewer_note"].strip():
                    raise ValueError(f"Uncertain row has final labels or no note: {review_id}")
            if decision != "uncertain":
                check_labels(labels, review_id)
            reviewed.append({"review_id": review_id, "study_id": mapping[review_id]["study_id"],
                             "reddit_id": mapping[review_id]["reddit_id"],
                             "decision": decision, **labels,
                             "reason": row["reviewer_note"].strip(),
                             "reviewed_at": row["reviewed_at"].strip(),
                             "review_method": "Manu verification of automatic proposals"})
    if len(reviewed) != 762 or len({r["review_id"] for r in reviewed}) != 762:
        raise ValueError("Missing or duplicate final batch rows")

    revisited = []
    rows = pd.read_excel(workbook, sheet_name="Uncertain 6", dtype=str,
                         keep_default_na=False).to_dict("records")
    if len(rows) != 6:
        raise ValueError("Expected six revisited uncertain posts")
    for row in rows:
        review_id = row["review_id"].strip()
        if review_id not in uncertain_expected:
            raise ValueError(f"Unexpected uncertain ID {review_id}")
        for field in UNCERTAIN_SOURCE_FIELDS:
            if not source_matches(uncertain_expected[review_id][field], row[field]):
                raise ValueError(f"Uncertain source changed: {review_id}/{field}")
        decision = row["decision"].strip().lower()
        labels = {field: row[f"final_{field}"].strip() for field in FIELDS}
        if decision == "resolved":
            check_labels(labels, review_id)
        elif decision == "still_uncertain":
            if any(labels.values()) or not row["reviewer_note"].strip():
                raise ValueError(f"Uncertain case has final labels or no note: {review_id}")
        else:
            raise ValueError(f"Missing or invalid uncertain decision: {review_id}")
        revisited.append({"review_id": review_id, "study_id": master[review_id]["study_id"],
                          "reddit_id": master[review_id]["reddit_id"],
                          "decision": decision, **labels,
                          "reason": row["reviewer_note"].strip(),
                          "review_method": "Manu revisit of earlier uncertain post"})
    if len({r["review_id"] for r in revisited}) != 6:
        raise ValueError("Duplicate uncertain review ID")

    digest = hashlib.sha256(workbook.read_bytes()).hexdigest()
    DEST.mkdir(parents=True, exist_ok=True)
    copy = DEST / workbook.name
    if copy.exists() and hashlib.sha256(copy.read_bytes()).hexdigest() != digest:
        raise ValueError("A different workbook already exists in the archive")
    if not copy.exists():
        shutil.copy2(workbook, copy)
    (DEST / "FINAL_REVIEW.json").write_text(json.dumps(reviewed, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (DEST / "UNCERTAIN_REVISIT.json").write_text(json.dumps(revisited, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    report = {"imported_utc": datetime.now(timezone.utc).isoformat(),
              "reviewed_workbook": copy.name, "sha256": digest,
              "new_post_decisions": dict(Counter(r["decision"] for r in reviewed)),
              "revisited_decisions": dict(Counter(r["decision"] for r in revisited)),
              "unresolved_ids": [r["review_id"] for r in reviewed + revisited if r["decision"] in {"uncertain", "still_uncertain"}],
              "note": "The completed workbook is preserved. These are assisted review decisions, not independent blinded annotations."}
    (DEST / "INTAKE_REPORT.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
