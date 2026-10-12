"""Validate the submitted qualitative first passes and summarize actions only.

This script does not score a model, decide which reviewer is right, or code themes.
"""
from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter
from pathlib import Path

import openpyxl

HERE = Path(__file__).resolve().parent
SOURCE = {r["study_case_id"]: r for r in json.loads((HERE / "packet_source.json").read_text()) if r["cohort"] == "main"}
FILES = {
    "A": HERE / "main_submissions/Reviewer_A_MAIN_30_COMPLETED.xlsx",
    "B": HERE / "main_submissions/Reviewer_B_MAIN_30_COMPLETED.xlsx",
}
FIELDS = ["case_id", "reviewer_a_action", "reviewer_b_action", "same_action", "reviewer_a_evidence", "reviewer_b_evidence", "reviewer_a_reason", "reviewer_b_reason", "reviewer_a_uncertainty", "reviewer_b_uncertainty", "reviewer_a_question", "reviewer_b_question", "reviewer_a_confidence", "reviewer_b_confidence"]


def load(path: Path) -> dict[str, tuple]:
    wb = openpyxl.load_workbook(path, read_only=True, data_only=True)
    assert wb.sheetnames == ["Review"]
    rows = list(wb.active.values)
    assert len(rows) == 31
    answer = {r[0]: r for r in rows[1:]}
    assert len(answer) == 30 and set(answer) == set(SOURCE)
    for cid, r in answer.items():
        s = SOURCE[cid]
        assert r[1] == s["title"] and r[2] == s["post_body"], f"source text differs: {cid}"
        assert r[3] in {"A", "B", "C", "D", "cannot_assess"}, f"invalid action: {cid}"
        assert r[8] in {"low", "medium", "high"}, f"invalid confidence: {cid}"
        assert all(v is not None and str(v).strip() for v in r[4:9]), f"missing answer: {cid}"
        if r[3] == "cannot_assess":
            assert r[9] is not None and str(r[9]).strip(), f"missing cannot-assess reason: {cid}"
    return answer


def main() -> None:
    a, b = load(FILES["A"]), load(FILES["B"])
    paired = []
    for cid in sorted(SOURCE):
        ra, rb = a[cid], b[cid]
        paired.append({
            "case_id": cid,
            "reviewer_a_action": ra[3], "reviewer_b_action": rb[3],
            "same_action": ra[3] == rb[3],
            "reviewer_a_evidence": ra[4], "reviewer_b_evidence": rb[4],
            "reviewer_a_reason": ra[5], "reviewer_b_reason": rb[5],
            "reviewer_a_uncertainty": ra[6], "reviewer_b_uncertainty": rb[6],
            "reviewer_a_question": ra[7], "reviewer_b_question": rb[7],
            "reviewer_a_confidence": ra[8], "reviewer_b_confidence": rb[8],
        })
    with (HERE / "ANALYST_ONLY_PAIRED_RESPONSES.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(paired)
    table = Counter((r["reviewer_a_action"], r["reviewer_b_action"]) for r in paired)
    result = {
        "status": "descriptive_intake_only_themes_pending",
        "source_sha256": {k: hashlib.sha256(p.read_bytes()).hexdigest() for k, p in FILES.items()},
        "cases": len(paired), "same_action": sum(r["same_action"] for r in paired),
        "different_action": sum(not r["same_action"] for r in paired),
        "reviewer_a_actions": dict(Counter(r["reviewer_a_action"] for r in paired)),
        "reviewer_b_actions": dict(Counter(r["reviewer_b_action"] for r in paired)),
        "action_pairs": {f"{x}|{y}": n for (x, y), n in sorted(table.items())},
        "different_action_case_ids": [r["case_id"] for r in paired if not r["same_action"]],
        "answer_text_identical_across_reviewers": sum(a[i][5] == b[i][5] for i in SOURCE),
        "limitations": ["two_reviewers_purposeful_cases", "no_correct_action_key", "independence_and_outside_lookup_are_user_reported_not_file_verifiable"],
    }
    (HERE / "MAIN_INTAKE.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
