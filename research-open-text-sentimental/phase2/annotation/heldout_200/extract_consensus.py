#!/usr/bin/env python3
"""Extract jointly agreed 200-post answers from the preserved XLSX files.

Run with Python and openpyxl. The authors reported one jointly written draft,
so these files do not provide an independent agreement measure.
"""

from __future__ import annotations

import json
from pathlib import Path

from openpyxl import load_workbook

ROOT = Path(__file__).resolve().parents[3]
ANN = ROOT / "phase2" / "annotation"
SOURCE = ANN / "submissions" / "2026-10-06-holdout200"
OUT = ANN / "heldout_200" / "final_consensus.json"
PREPARED = ANN / "heldout_200" / "blind_review_rows.json"
FIELDS = ("about_software", "update_related", "discussion_type", "confidence")
TEXT_FIELDS = ("sheet_order", "title", "post_body", "discussion_context", "text_availability_note")


def read_workbook(path: Path) -> dict[str, dict]:
    wb = load_workbook(path, read_only=True, data_only=True)
    rows = list(wb["Review"].values)
    head = rows[0]
    data = [dict(zip(head, row)) for row in rows[1:]]
    result = {r["review_id"]: r for r in data}
    if len(data) != len(result) or len(data) != 200:
        raise ValueError(f"Missing or duplicate review id: {path}")
    return result


def main() -> None:
    manu = read_workbook(SOURCE / "Manu_Reserved_200_New_Posts.xlsx")
    berhe = read_workbook(SOURCE / "Berhe_Reserved_200_New_Posts.xlsx")
    prepared = {r["review_id"]: r for r in json.loads(PREPARED.read_text(encoding="utf-8"))}
    if set(manu) != set(berhe) or set(manu) != set(prepared):
        raise ValueError("Review id mismatch")
    final = []
    for rid in prepared:
        m, b, p = manu[rid], berhe[rid], prepared[rid]
        if any(str(m[f] or "") != str(p[f] or "") or str(b[f] or "") != str(p[f] or "") for f in TEXT_FIELDS):
            raise ValueError(f"Post text changed: {rid}")
        if any(m[f] != b[f] for f in FIELDS):
            raise ValueError(f"Final answers differ: {rid}")
        if not str(m["reason"] or "").strip() or not str(b["reason"] or "").strip():
            raise ValueError(f"Missing reason: {rid}")
        if (m["about_software"] == "yes") == (m["discussion_type"] == "na"):
            raise ValueError(f"Invalid scope/type pair: {rid}")
        final.append({
            "review_id": rid,
            **{f: m[f] for f in FIELDS},
            "reason": m["reason"],
            "reason_berhe": b["reason"],
            "review_process": "joint_review_one_draft",
            "independent_first_pass_recorded": False,
        })
    OUT.write_text(json.dumps(final, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Saved {len(final)} final consensus records to {OUT}")


if __name__ == "__main__":
    main()
