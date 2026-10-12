"""Freeze the jointly reviewed, corrected fresh-test labels before model scoring."""
from __future__ import annotations

import hashlib
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent
REVIEWS = ROOT / "completed_reviews_20261007_corrected"
FRESH = ROOT / "fresh_test_20261007"
DEV = ROOT / "revised_development_v2/development_v2.jsonl"
OUT = FRESH / "frozen_joint_labels"
LABELS = ("about_software", "update_related", "discussion_type")


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_jsonl(path: Path, rows: list[dict]) -> None:
    path.write_text("".join(json.dumps(r, ensure_ascii=False, sort_keys=True) + "\n" for r in rows))


def main() -> None:
    a = {r["test_id"]: r for r in json.loads((REVIEWS / "manu_test_answers.json").read_text())}
    b = {r["test_id"]: r for r in json.loads((REVIEWS / "berhe_test_answers.json").read_text())}
    mapping = {r["test_id"]: r for r in json.loads((FRESH / "analyst_mapping.json").read_text())}
    expected = {r["test_id"]: r for r in json.loads((FRESH / "review_text.json").read_text())}
    assert len(expected) == len(mapping) == len(set(a) | set(b)) == 500
    shared = set(a) & set(b)
    assert len(shared) == 100
    for test_id in shared:
        assert all(a[test_id][f] == b[test_id][f] for f in LABELS)

    dev_ids = {json.loads(line)["reddit_id"] for line in DEV.read_text().splitlines() if line}
    all_rows = []
    for test_id in sorted(expected):
        chosen = a.get(test_id) or b[test_id]
        assert chosen["title"] == expected[test_id]["title"]
        assert (chosen["post_body"] or "") == expected[test_id]["post_body"]
        meta = mapping[test_id]
        assert meta["reddit_id"] not in dev_ids
        row = {
            "test_id": test_id,
            "reddit_id": meta["reddit_id"],
            "title": chosen["title"],
            "post_body": chosen["post_body"] or "",
            "created_utc": meta["created_utc"],
            "subreddit": meta["subreddit"],
            "about_software": chosen["about_software"],
            "update_related": chosen["update_related"],
            "discussion_type": chosen["discussion_type"],
            "confidence": chosen["confidence"],
            "review_assignment": meta["assigned_to"],
            "label_provenance": "user_reported_joint_manu_berhe_review",
        }
        row["s2_in_scope"] = row["about_software"] == "yes" and row["update_related"] == "yes"
        row["s2_target"] = (int(row["discussion_type"] == "technical_troubleshooting")
                            if row["s2_in_scope"] else None)
        all_rows.append(row)
    s2 = [r for r in all_rows if r["s2_in_scope"]]
    assert len(s2) == 344
    assert Counter(r["s2_target"] for r in s2) == {1: 277, 0: 67}
    OUT.mkdir(exist_ok=True)
    write_jsonl(OUT / "all_500_reviewed.jsonl", all_rows)
    write_jsonl(OUT / "s2_test_344.jsonl", s2)
    manifest = {
        "status": "frozen_before_model_scoring",
        "provenance": "User reports Manu and Professor Berhe wrote all labels together; no independent first-pass agreement can be estimated",
        "source_workbooks": {name: data["sha256"] for name, data in json.loads((REVIEWS / "intake_summary.json").read_text()).items() if name != "shared_test"},
        "candidate_n": len(all_rows), "s2_n": len(s2),
        "s2_class_counts": dict(Counter(str(r["s2_target"]) for r in s2)),
        "shared_review_n": len(shared),
        "shared_label_disagreement_n": 0,
        "development_id_overlap_n": 0,
        "development_snapshot_sha256": sha(DEV),
        "all_reviewed_sha256": sha(OUT / "all_500_reviewed.jsonl"),
        "s2_test_sha256": sha(OUT / "s2_test_344.jsonl"),
        "note": "Earlier mistaken AI_Assisted attachments had the same cell values but were withdrawn. Corrected workbooks are authoritative. Label-generation process is user-reported, not independently verifiable from files."
    }
    (OUT / "freeze_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
