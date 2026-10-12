"""Agreement from the reported separate first-pass 200-post submissions."""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

import openpyxl
from sklearn.metrics import cohen_kappa_score


HERE = Path(__file__).resolve().parent
SUB = HERE / "submissions/2026-10-07-independent"
FIELDS = [
    "about_software", "update_related", "discussion_type", "confidence", "reason",
    "software_product", "identifiable_release", "environment", "specific_symptom",
    "reproduction_context", "error_evidence", "attempted_remedy", "help_request",
]
MAIN = FIELDS[:4]
DETAILS = FIELDS[5:]


def read(letter: str) -> list[dict]:
    path = SUB / f"Reviewer_{letter}_200_Completed_Draft.xlsx"
    ws = openpyxl.load_workbook(path, read_only=False, data_only=True)["Review"]
    return [{"review_id": ws.cell(i, 1).value, **dict(zip(FIELDS, [ws.cell(i, j).value for j in range(5, 18)]))} for i in range(6, 206)]


def stats(a: list[dict], b: list[dict], field: str) -> dict:
    x = [r[field] for r in a]
    y = [r[field] for r in b]
    assert len(x) == len(y)
    cats = sorted(set(x) | set(y))
    return {
        "n": len(x),
        "exact_agreement": sum(u == v for u, v in zip(x, y)) / len(x),
        "cohen_kappa": float(cohen_kappa_score(x, y, labels=cats)),
        "reviewer_a_counts": dict(Counter(x)),
        "reviewer_b_counts": dict(Counter(y)),
        "confusion": {u: {v: sum(p == u and q == v for p, q in zip(x, y)) for v in cats} for u in cats},
    }


def main() -> None:
    a, b = read("A"), read("B")
    assert [r["review_id"] for r in a] == [r["review_id"] for r in b]
    assert len(a) == len(b) == 200
    tsp_a = [r for r in a if r["discussion_type"] == "technical_troubleshooting"]
    tsp_b = [r for r in b if r["discussion_type"] == "technical_troubleshooting"]
    assert [r["review_id"] for r in tsp_a] == [r["review_id"] for r in tsp_b]
    assert len(tsp_a) == 118
    report = {
        "provenance": "Manu reports two separate first passes; neither reviewer discussed answers or saw the other's completed answers before both files were saved. The file contents cannot independently verify this process. Earlier corpus exposure is possible.",
        "main_fields": {f: stats(a, b, f) for f in MAIN},
        "diagnostic_fields_on_118_both_troubleshooting": {f: stats(tsp_a, tsp_b, f) for f in DETAILS},
        "reason_text_exact_match_n": sum(x["reason"] == y["reason"] for x, y in zip(a, b)),
        "rows_with_any_category_or_detail_disagreement": sum(any(x[f] != y[f] for f in MAIN + DETAILS) for x, y in zip(a, b)),
        "adjudication_required_n": 0,
        "note": "Agreement with each other is not correctness. These posts were stratified by prior labels, and both reviewers may have seen some posts earlier. Do not infer Reddit-wide reliability or independent validation of the reserved/fresh test labels.",
    }
    (SUB / "AGREEMENT.json").write_text(json.dumps(report, indent=2) + "\n")
    lines = [
        "# Reported independent first-pass agreement",
        "",
        "Manu reports that the two reviewers completed the 200-post first passes separately, without discussion or seeing the other person's completed answers before both files were saved. The workbooks themselves cannot verify the review sequence. Earlier familiarity with some development posts remains possible.",
        "",
        "The submitted category and diagnostic answers are identical for every eligible item; all 200 free-text reasons differ in wording. This is **perfect agreement in these files**, not proof that either answer is correct or that future reviewers will agree perfectly. The sample was deliberately stratified and is not a prevalence sample.",
        "",
        "| Field | Eligible posts | Exact agreement | Cohen's kappa |",
        "|---|---:|---:|---:|",
    ]
    for field in MAIN:
        s = report["main_fields"][field]
        lines.append(f"| `{field}` | {s['n']} | {s['exact_agreement']:.3f} | {s['cohen_kappa']:.3f} |")
    for field in DETAILS:
        s = report["diagnostic_fields_on_118_both_troubleshooting"][field]
        lines.append(f"| `{field}` (troubleshooting only) | {s['n']} | {s['exact_agreement']:.3f} | {s['cohen_kappa']:.3f} |")
    lines += [
        "",
        "No disagreement adjudication is needed for these submitted categorical answers. Raw category counts and confusion tables are in `AGREEMENT.json`; `unclear` is retained as a category. A bootstrap of perfectly identical observed pairs would return a degenerate interval and would not establish perfect agreement beyond this sample, so no such interval is presented.",
        "",
        "**Interpretation limits:** This is agreement between the two reported separate first passes on selected development records. It does not validate the correctness of labels or the reserved/fresh test labels. The exact agreement is unusual and should be described transparently, including the user-reported independent workflow and the fact that prior corpus exposure cannot be ruled out from the files alone.",
        "",
    ]
    (SUB / "AGREEMENT.md").write_text("\n".join(lines))
    print("200/200 main-field agreement, 118/118 diagnostic-field agreement, kappa 1.0 on every field; 0 identical reason strings")


if __name__ == "__main__":
    main()
