"""Apply Manu's reviewed corrections to a new development snapshot."""

from __future__ import annotations

import hashlib
import json
from collections import Counter
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
V1 = ROOT / "phase3/experiment_v1"
DECISIONS = V1 / "followup/manu_review_2026-10-07/decisions.json"
SOURCE = V1 / "data/development.jsonl"
OUT = HERE / "development_v2.jsonl"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    decisions = json.loads(DECISIONS.read_text())
    by_id = {row["reddit_id"]: row for row in decisions}
    assert len(by_id) == 51
    rows = [json.loads(line) for line in SOURCE.read_text().splitlines() if line]
    assert len(rows) == 3155
    assert set(by_id).issubset({row["reddit_id"] for row in rows})
    revised = []
    for row in rows:
        decision = by_id.get(row["reddit_id"])
        if decision:
            assert row["discussion_type"] == decision["old_discussion_type"]
            assert row["s2_target"] == decision["old_s2_target"]
            if decision["decision"] == "uncertain":
                continue
            if decision["decision"] == "change":
                row["discussion_type"] = decision["new_discussion_type"]
                row["s2_target"] = decision["new_s2_target"]
                row["label_revision_source"] = "manu_review_2026-10-07"
        revised.append(row)
    assert len(revised) == 3151
    OUT.write_text("".join(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in revised))
    near_exclusions = json.loads((V1 / "results/development_exclusions.json").read_text())["additional_near_duplicate_exclusions"]
    near_ids = {row["reddit_id"] for row in near_exclusions}
    s2 = [row for row in revised if row["s2_in_scope"] and row["reddit_id"] not in near_ids]
    assert len(s2) == 2080
    manifest = {
        "version": "revised-development-v2",
        "source": str(SOURCE), "source_sha256": sha(SOURCE),
        "decisions": str(DECISIONS), "decisions_sha256": sha(DECISIONS),
        "output": str(OUT), "output_sha256": sha(OUT),
        "all_development_rows": len(revised),
        "s2_eligible_after_near_duplicate_exclusions": len(s2),
        "s2_class_counts": dict(Counter(str(row["s2_target"]) for row in s2)),
        "excluded_uncertain_ids": sorted(row["reddit_id"] for row in decisions if row["decision"] == "uncertain"),
        "changed_label_ids": sorted(row["reddit_id"] for row in decisions if row["decision"] == "change"),
        "near_duplicate_development_exclusions_for_s2": sorted(near_ids),
        "notes": ["Original Phase 2 master and experiment_v1 data/results are unchanged.", "This is development data, not a new test set."]
    }
    (HERE / "MANIFEST.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(json.dumps({k:manifest[k] for k in ("all_development_rows","s2_eligible_after_near_duplicate_exclusions","s2_class_counts","changed_label_ids","excluded_uncertain_ids")},indent=2))


if __name__ == "__main__":
    main()
