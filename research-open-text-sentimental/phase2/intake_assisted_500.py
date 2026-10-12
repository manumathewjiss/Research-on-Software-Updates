#!/usr/bin/env python3
"""Validate Manu's five completed review batches and preserve their decisions."""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
ANN = ROOT / "phase2/annotation"
FIELDS = ("about_software", "update_related", "discussion_type")
ALLOWED = {
    "about_software": {"yes", "no", "unclear"},
    "update_related": {"yes", "no", "unclear"},
    "discussion_type": {"technical_troubleshooting", "general_dissatisfaction", "other", "na"},
}
UNCHANGED = ("subreddit", "title", "post_body", "discussion_context", "text_availability",
             "proposed_about_software", "proposed_update_related", "proposed_discussion_type",
             "proposed_confidence", "proposed_reason", "source_url")
XML_CONTROL = set(range(0, 9)) | {11, 12} | set(range(14, 32)) | {0xFFFE, 0xFFFF}


def normalized_cell(value: str) -> str:
    value = value.replace("\r\n", "\n").replace("\r", "\n")
    return "".join(ch for ch in value if ord(ch) not in XML_CONTROL)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--round", type=int, choices=(1, 2, 3), default=1)
    parser.add_argument("reviewed_workbook", type=Path)
    args = parser.parse_args()
    source_name = {1: "provisional_500", 2: "provisional_500_round2", 3: "provisional_1000_round3"}[args.round]
    dest_name = {1: "2026-10-06-assisted-500", 2: "2026-10-07-assisted-500-round2", 3: "2026-10-07-assisted-1000-round3"}[args.round]
    source = ANN / source_name
    dest = ANN / "submissions" / dest_name
    first_batch = {1: 1, 2: 6, 3: 11}[args.round]
    batch_count = 10 if args.round == 3 else 5
    expected_count = batch_count * 100
    workbook = args.reviewed_workbook.resolve()
    if not workbook.is_file():
        raise FileNotFoundError(workbook)
    original = {r["review_id"]: r for r in json.loads((source / "workbook_rows.json").read_text(encoding="utf-8"))}
    mapping = {r["review_id"]: r for r in json.loads((source / "ANALYST_ONLY_MAPPING.json").read_text(encoding="utf-8"))}
    if len(original) != expected_count or set(original) != set(mapping):
        raise ValueError("Original sample or mapping is incomplete")
    sheets = pd.ExcelFile(workbook)
    if sheets.sheet_names != ["Start here"] + [f"Batch {i}" for i in range(first_batch, first_batch + batch_count)]:
        raise ValueError("Unexpected workbook tabs")
    submitted = []
    for batch in range(first_batch, first_batch + batch_count):
        rows = pd.read_excel(workbook, sheet_name=f"Batch {batch}", dtype=str,
                             keep_default_na=False).to_dict("records")
        if len(rows) != 100:
            raise ValueError(f"Batch {batch} does not have 100 posts")
        for row in rows:
            review_id = row["review_id"].strip()
            if not review_id.startswith(f"B{batch}-") or review_id not in original:
                raise ValueError(f"Unexpected review id {review_id}")
            for field in UNCHANGED:
                expected = normalized_cell(original[review_id][field])
                allowed = {expected}
                if expected.startswith(("=", "+", "@")):
                    allowed.add("'" + expected)
                if normalized_cell(row[field]) not in allowed:
                    raise ValueError(f"Source text or proposal changed for {review_id}: {field}")
            decision = row["decision"].strip().lower()
            if decision not in {"accept", "revise", "uncertain"}:
                raise ValueError(f"Missing or invalid decision for {review_id}")
            finals = {field: row[f"final_{field}"].strip() for field in FIELDS}
            if decision == "accept":
                if any(finals.values()):
                    raise ValueError(f"Unexpected final fields on accepted {review_id}")
                finals = {field: row[f"proposed_{field}"].strip() for field in FIELDS}
            elif decision == "revise":
                if not row["reviewer_note"].strip():
                    raise ValueError(f"Revision lacks a note: {review_id}")
            else:
                if any(finals.values()) or not row["reviewer_note"].strip():
                    raise ValueError(f"Uncertain row has final fields or no note: {review_id}")
            if decision != "uncertain":
                for field in FIELDS:
                    if finals[field] not in ALLOWED[field]:
                        raise ValueError(f"Invalid {field} on {review_id}")
                if (finals["about_software"] == "yes") == (finals["discussion_type"] == "na"):
                    raise ValueError(f"Inconsistent software scope and type on {review_id}")
            submitted.append({"review_id": review_id, "study_id": mapping[review_id]["study_id"],
                              "reddit_id": mapping[review_id]["reddit_id"],
                              "decision": decision, **finals,
                              "reason": row["reviewer_note"].strip(),
                              "reviewed_at": row["reviewed_at"].strip(),
                              "review_method": "Manu verification of automatic proposals"})
    if len(submitted) != expected_count or len({r["review_id"] for r in submitted}) != expected_count:
        raise ValueError("Missing or duplicate review rows")
    digest = hashlib.sha256(workbook.read_bytes()).hexdigest()
    dest.mkdir(parents=True, exist_ok=True)
    copy = dest / workbook.name
    if copy.exists() and hashlib.sha256(copy.read_bytes()).hexdigest() != digest:
        raise ValueError("A different workbook is already archived under that name")
    if not copy.exists():
        shutil.copy2(workbook, copy)
    (dest / "FINAL_REVIEW.json").write_text(json.dumps(submitted, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    summary = {"imported_utc": datetime.now(timezone.utc).isoformat(),
               "reviewed_workbook": copy.name, "sha256": digest,
               "decisions": dict(Counter(r["decision"] for r in submitted)),
               "resolved": sum(r["decision"] != "uncertain" for r in submitted),
               "unresolved_ids": [r["review_id"] for r in submitted if r["decision"] == "uncertain"],
               "note": "Manu reviewed proposals; no independent blinded agreement is implied. Uncertain posts remain unlabeled. Review dates were blank in the submitted workbook."}
    (dest / "INTAKE_REPORT.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
