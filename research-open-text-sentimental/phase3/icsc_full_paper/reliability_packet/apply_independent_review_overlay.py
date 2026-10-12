"""Version matching first-pass decisions as a development-only sensitivity snapshot."""

from __future__ import annotations

import hashlib
import json
from collections import Counter
from pathlib import Path


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
BASE = REPO / "phase3/update_connection_audit/targeted_submission/development_after_update_audit.jsonl"
SUB = HERE / "submissions/2026-10-07-independent"
OUT = SUB / "development_after_independent_review.jsonl"


def main() -> None:
    rows = [json.loads(line) for line in BASE.read_text().splitlines() if line]
    mapping = {r["review_id"]: r for r in json.loads((HERE.parent / "ANALYST_ONLY_RELIABILITY_MAPPING.json").read_text())}
    decisions = json.loads((SUB / "reviewer_a_decisions.json").read_text())
    overlay = {mapping[d["review_id"]]["reddit_id"]: d for d in decisions}
    assert len(rows) == 3151 and len(overlay) == 200
    changes = []
    out = []
    for original in rows:
        row = dict(original)
        d = overlay.get(row["reddit_id"])
        if d:
            old = {k: row[k] for k in ("about_software", "update_related", "discussion_type", "s2_in_scope", "s2_target")}
            row.update({k: d[k] for k in ("about_software", "update_related", "discussion_type")})
            row["s2_in_scope"] = row["about_software"] == "yes" and row["update_related"] == "yes" and row["discussion_type"] in {"technical_troubleshooting", "general_dissatisfaction", "other"}
            # Preserve the existing snapshot convention: s2_target is a binary
            # derived from discussion type even when s2_in_scope is false.
            row["s2_target"] = 1 if row["discussion_type"] == "technical_troubleshooting" else 0
            new = {k: row[k] for k in old}
            if old != new:
                changes.append({"review_id": d["review_id"], "reddit_id": row["reddit_id"], "old": old, "new": new})
            row["independent_200_overlay_audit_only"] = True
        out.append(row)
    if len(changes) != 29:
        raise AssertionError(f"Expected 29 changed labels, found {len(changes)}")
    assert len(out) == len({r["reddit_id"] for r in out}) == 3151
    OUT.write_text("".join(json.dumps(r, ensure_ascii=False, sort_keys=True) + "\n" for r in out))
    (SUB / "changed_decisions.json").write_text(json.dumps(changes, ensure_ascii=False, indent=2) + "\n")
    report = {
        "status": "development_only_overlay_no_test_scoring",
        "base_sha256": hashlib.sha256(BASE.read_bytes()).hexdigest(),
        "output_sha256": hashlib.sha256(OUT.read_bytes()).hexdigest(),
        "reviewed_n": len(overlay),
        "changed_unique_n": len(changes),
        "raw_s2_before": sum(r["s2_in_scope"] for r in rows),
        "raw_s2_after": sum(r["s2_in_scope"] for r in out),
        "raw_s2_class_counts_after": dict(Counter("troubleshooting" if r["s2_target"] == 1 else "other_update" for r in out if r["s2_in_scope"])),
        "near_duplicate_exclusions": ["1t0wme9", "1wrqch6"],
        "historical_development_modified": False,
        "reserved_test_modified": False,
        "fresh_test_modified": False,
    }
    (SUB / "overlay_manifest.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
