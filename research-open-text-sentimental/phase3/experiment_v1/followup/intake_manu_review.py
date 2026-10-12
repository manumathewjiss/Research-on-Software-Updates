"""Archive Manu's 51 decisions and run a development-only sensitivity check."""

from __future__ import annotations

import csv
import hashlib
import json
import shutil
from collections import Counter
from pathlib import Path

import numpy as np

from run_followup import DATA, EXP, V1_RESULTS, audit_within_dev, eligible_dev, load_jsonl, make_text, run_oof


HERE = Path(__file__).resolve().parent
SUBMISSION = Path("/Users/manumathewjiss/Documents/Codex/2026-10-06/i-wi/outputs/MANU_LABEL_REVIEW_completed.csv")
ORIGINAL = HERE / "MANU_LABEL_REVIEW.csv"
OUT = HERE / "manu_review_2026-10-07"
VALID_TYPES = {"technical_troubleshooting", "general_dissatisfaction", "other", "na"}


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_csv(path: Path) -> list[dict]:
    with path.open(newline="", encoding="utf-8-sig") as stream:
        return list(csv.DictReader(stream))


def main() -> None:
    original = read_csv(ORIGINAL)
    submitted = read_csv(SUBMISSION)
    assert len(original) == len(submitted) == 51
    old = {row["reddit_id"]: row for row in original}
    assert len(old) == 51 and {r["reddit_id"] for r in submitted} == set(old)
    fixed_columns = list(original[0])[:9]
    decisions = []
    for row in submitted:
        prior = old[row["reddit_id"]]
        assert all(row[col] == prior[col] for col in fixed_columns), row["reddit_id"]
        decision = row["manu_decision"].strip().lower()
        assert decision in {"keep", "change", "uncertain"}, row["reddit_id"]
        assert row["explanation"].strip(), row["reddit_id"]
        entry = {"reddit_id": row["reddit_id"], "decision": decision, "old_discussion_type": row["current_discussion_type"], "old_s2_target": int(row["current_s2_target"]), "reason": row["explanation"].strip()}
        correction = row["corrected_label_if_needed"].strip()
        if decision == "change":
            target_part, type_part = [part.strip() for part in correction.split(";")]
            assert target_part.startswith("s2_target=") and type_part.startswith("discussion_type=")
            target = int(target_part.split("=", 1)[1])
            label_type = type_part.split("=", 1)[1]
            assert target in {0, 1} and label_type in VALID_TYPES
            assert (target == 1) == (label_type == "technical_troubleshooting")
            entry.update({"new_s2_target": target, "new_discussion_type": label_type})
        else:
            assert not correction, row["reddit_id"]
        decisions.append(entry)

    OUT.mkdir(exist_ok=True)
    archived = OUT / SUBMISSION.name
    shutil.copy2(SUBMISSION, archived)
    (OUT / "decisions.json").write_text(json.dumps(decisions, indent=2, ensure_ascii=False) + "\n")

    exclusions = json.loads((V1_RESULTS / "development_exclusions.json").read_text())
    exclude_ids = {x["reddit_id"] for x in exclusions["additional_near_duplicate_exclusions"]}
    dev = eligible_dev(load_jsonl(DATA / "development.jsonl"), exclude_ids)
    by_id = {row["reddit_id"]: row for row in dev}
    assert all(entry["reddit_id"] in by_id for entry in decisions)
    for entry in decisions:
        row = by_id[entry["reddit_id"]]
        assert row["discussion_type"] == entry["old_discussion_type"]
        if entry["decision"] == "change":
            row["discussion_type"] = entry["new_discussion_type"]
            row["s2_target"] = entry["new_s2_target"]
    uncertain = {entry["reddit_id"] for entry in decisions if entry["decision"] == "uncertain"}
    dev = [row for row in dev if row["reddit_id"] not in uncertain]

    audit, groups = audit_within_dev(dev)
    threshold = json.loads((V1_RESULTS / "model_selection.json").read_text())["chosen"]["threshold"]
    texts = [make_text(row) for row in dev]
    y = np.array([row["s2_target"] for row in dev])
    _, _, model = run_oof("tfidf_lr", texts, y, groups=groups, threshold=threshold)
    _, _, keyword = run_oof("keyword", texts, y, groups=groups, threshold=None)
    _, _, majority = run_oof("majority", texts, y, groups=groups, threshold=None)
    summary = {
        "submission_sha256": digest(archived),
        "decisions": dict(Counter(entry["decision"] for entry in decisions)),
        "changed_ids": [entry["reddit_id"] for entry in decisions if entry["decision"] == "change"],
        "uncertain_excluded_ids": sorted(uncertain),
        "development_only": True,
        "reserved_test_touched": False,
        "config": {"model": "title_body TF-IDF logistic regression", "C": 4.0, "threshold": threshold, "grouping": "exact text plus near duplicates >= 0.92"},
        "development_n": len(dev),
        "development_class_counts": dict(Counter(row["s2_target"] for row in dev)),
        "grouped_validation": {"model": model, "keyword": keyword, "majority": majority},
        "duplicate_groups_with_conflicting_targets": audit["exact_duplicate_groups"]["n_groups_with_label_conflict"],
        "note": "Sensitivity check on revised development labels; the old model/test record remains unchanged.",
    }
    (OUT / "DEVELOPMENT_SENSITIVITY.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps({"decisions": summary["decisions"], "development_n": len(dev), "class_counts": summary["development_class_counts"], "model_macro_f1": model["macro_f1"], "keyword_macro_f1": keyword["macro_f1"], "duplicate_label_conflicts": summary["duplicate_groups_with_conflicting_targets"]}, indent=2))


if __name__ == "__main__":
    main()
