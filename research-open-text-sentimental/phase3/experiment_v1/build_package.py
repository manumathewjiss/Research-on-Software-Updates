"""Build the Phase 3 experiment snapshot without changing Phase 1 or Phase 2."""

from __future__ import annotations

import hashlib
import json
import re
from collections import Counter, defaultdict
from pathlib import Path


HERE = Path(__file__).resolve().parent
MASTER = HERE.parents[1] / "phase2/combined_dataset/master_records.json"
OUT = HERE / "data"
VALID_TYPES = {"technical_troubleshooting", "general_dissatisfaction", "other", "na"}


def normalized(text: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9]+", " ", text.lower())).strip()


def exact_text_key(row: dict) -> str:
    return normalized(row["title"]) + "|" + normalized(row["post_body"])


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_jsonl(path: Path, rows: list[dict]) -> None:
    with path.open("w", encoding="utf-8") as stream:
        for row in rows:
            stream.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")


def main() -> None:
    rows = json.loads(MASTER.read_text(encoding="utf-8"))
    assert len(rows) == 3362
    assert len({row["reddit_id"] for row in rows}) == len(rows)
    resolved = [row for row in rows if row["phase2_discussion_type"] in VALID_TYPES]
    unresolved = [row for row in rows if row["phase2_discussion_type"] not in VALID_TYPES]
    assert len(resolved) == 3357 and len(unresolved) == 5
    reserved = [row for row in resolved if row["phase2_review_status"] == "reserved_test_consensus"]
    development = [row for row in resolved if row["phase2_review_status"] != "reserved_test_consensus"]
    assert len(reserved) == 200 and len(development) == 3157

    test_keys = {exact_text_key(row) for row in reserved}
    duplicate_development = [row for row in development if exact_text_key(row) in test_keys]
    assert {row["reddit_id"] for row in duplicate_development} == {"1u3zzcs", "1so7xen"}
    development = [row for row in development if row not in duplicate_development]

    def export_row(row: dict) -> dict:
        # Source and provenance are retained for audits only; the model must use text alone.
        return {
            "study_id": row["study_id"],
            "reddit_id": row["reddit_id"],
            "title": row["title"],
            "post_body": row["post_body"],
            "discussion_context": row["discussion_context"],
            "text_availability": row["text_availability"],
            "created_utc": row["created_utc"],
            "subreddit": row["subreddit"],
            "source_pool_audit_only": row["source_pool"],
            "review_status_audit_only": row["phase2_review_status"],
            "about_software": row["phase2_about_software"],
            "update_related": row["phase2_update_related"],
            "discussion_type": row["phase2_discussion_type"],
            "s2_in_scope": row["phase2_about_software"] == "yes" and row["phase2_update_related"] == "yes",
            "s2_target": 1 if row["phase2_discussion_type"] == "technical_troubleshooting" else 0,
        }

    OUT.mkdir(exist_ok=True)
    dev_path = OUT / "development.jsonl"
    test_path = OUT / "reserved_test.jsonl"
    write_jsonl(dev_path, [export_row(row) for row in sorted(development, key=lambda row: row["study_id"])])
    write_jsonl(test_path, [export_row(row) for row in sorted(reserved, key=lambda row: row["study_id"])])

    def s2_counts(items: list[dict]) -> dict:
        selected = [row for row in items if row["phase2_about_software"] == "yes" and row["phase2_update_related"] == "yes"]
        return {"total": len(selected), "discussion_type": dict(sorted(Counter(row["phase2_discussion_type"] for row in selected).items()))}

    manifest = {
        "version": "phase3-experiment-v1",
        "source_master": str(MASTER),
        "source_master_sha256": sha256(MASTER),
        "files": {dev_path.name: sha256(dev_path), test_path.name: sha256(test_path)},
        "resolved_total": len(resolved),
        "unresolved_excluded_ids": sorted(row["reddit_id"] for row in unresolved),
        "reserved_total": len(reserved),
        "development_before_exact_dedup": 3157,
        "development_after_exact_dedup": len(development),
        "development_exact_duplicate_exclusions": [
            {"study_id": row["study_id"], "reddit_id": row["reddit_id"], "title": row["title"]}
            for row in duplicate_development
        ],
        "development_s2": s2_counts(development),
        "reserved_s2": s2_counts(reserved),
        "notes": [
            "Only exact normalized title+body development copies matching reserved test were excluded.",
            "Near-duplicate search and label quality checks still need to be completed before training.",
            "Reserved test labels were jointly decided; no independent agreement claim follows.",
        ],
    }
    (HERE / "MANIFEST.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({key: manifest[key] for key in ("resolved_total", "development_after_exact_dedup", "reserved_total", "development_s2", "reserved_s2")}, indent=2))


if __name__ == "__main__":
    main()
