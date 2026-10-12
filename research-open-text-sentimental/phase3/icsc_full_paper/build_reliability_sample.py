"""Deterministically select a blind, development-only reliability sample.

This script does not label posts or modify the development/test records.
"""

from __future__ import annotations

import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent / "reliability_packet"
DEV = ROOT / "phase3/update_connection_audit/targeted_submission/development_after_update_audit.jsonl"
RESERVED = ROOT / "phase3/experiment_v1/data/reserved_test.jsonl"
FRESH = ROOT / "phase3/fresh_test_20261007/frozen_joint_labels/all_500_reviewed.jsonl"
DIAGNOSTIC = ROOT / "phase3/diagnostic_pilot/main_sample_20261007/analyst_mapping.json"
SEED = "ICSC-RELIABILITY-20261007-v1"
QUOTAS = {
    "s2_troubleshooting": 80,
    "s2_other_update": 60,
    "software_nonupdate": 40,
    "nonsoftware": 20,
}


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def bucket(row: dict) -> str | None:
    software, update, kind = row.get("about_software"), row.get("update_related"), row.get("discussion_type")
    if software == "yes" and update == "yes" and kind == "technical_troubleshooting":
        return "s2_troubleshooting"
    if software == "yes" and update == "yes" and kind in {"general_dissatisfaction", "other"}:
        return "s2_other_update"
    if software == "yes" and update == "no":
        return "software_nonupdate"
    if software == "no":
        return "nonsoftware"
    return None


def order_key(row: dict, tag: str) -> str:
    return hashlib.sha256(f"{SEED}|{tag}|{row['reddit_id']}".encode()).hexdigest()


def balanced_pick(rows: list[dict], quota: int, tag: str) -> list[dict]:
    """Cycle through source pools so one historical pool cannot monopolize a stratum."""
    pools: dict[str, list[dict]] = defaultdict(list)
    for row in rows:
        pools[row.get("source_pool_audit_only", "unknown")].append(row)
    for pool in pools:
        pools[pool].sort(key=lambda r: order_key(r, tag))
    selected: list[dict] = []
    names = sorted(pools, key=lambda name: hashlib.sha256(f"{SEED}|{tag}|{name}".encode()).hexdigest())
    while len(selected) < quota:
        progressed = False
        for name in names:
            if pools[name] and len(selected) < quota:
                selected.append(pools[name].pop())
                progressed = True
        if not progressed:
            raise RuntimeError(f"Too few eligible records for {tag}: {len(selected)} < {quota}")
    return selected


def main() -> None:
    dev, reserved, fresh = map(read_jsonl, (DEV, RESERVED, FRESH))
    diagnostic = json.loads(DIAGNOSTIC.read_text())
    reserved_ids = {r["reddit_id"] for r in reserved}
    fresh_ids = {r["reddit_id"] for r in fresh}
    diagnostic_ids = {r["reddit_id"] for r in diagnostic}
    assert len(dev) == 3151
    assert len(reserved_ids) == 200
    assert len(fresh_ids) == 500
    assert len(diagnostic_ids) == 250
    assert not (reserved_ids & fresh_ids)
    assert len({r["reddit_id"] for r in dev}) == len(dev)

    eligible = [r for r in dev if not r["reddit_id"].startswith("so_") and r["reddit_id"] not in reserved_ids | fresh_ids | diagnostic_ids]
    candidates: dict[str, list[dict]] = defaultdict(list)
    for row in eligible:
        group = bucket(row)
        if group:
            candidates[group].append(row)
    selected: list[dict] = []
    for group, quota in QUOTAS.items():
        selected.extend(balanced_pick(candidates[group], quota, group))
    selected.sort(key=lambda r: order_key(r, "sheet_order"))
    selected_ids = {r["reddit_id"] for r in selected}
    assert len(selected) == len(selected_ids) == 200
    assert not (selected_ids & reserved_ids | selected_ids & fresh_ids | selected_ids & diagnostic_ids)

    public = []
    private = []
    for i, row in enumerate(selected, 1):
        review_id = f"IR-{i:03d}"
        public.append({
            "review_id": review_id,
            "title": row["title"],
            "post_body": row.get("post_body") or "",
            "discussion_context": row.get("discussion_context") or "",
        })
        private.append({
            "review_id": review_id,
            "reddit_id": row["reddit_id"],
            "study_id": row.get("study_id"),
            "stratum_for_sampling_only": bucket(row),
            "source_pool": row.get("source_pool_audit_only"),
            "prior_about_software": row.get("about_software"),
            "prior_update_related": row.get("update_related"),
            "prior_discussion_type": row.get("discussion_type"),
        })
    OUT.mkdir(exist_ok=True)
    public_path = OUT / "blind_rows.json"
    private_path = Path(__file__).resolve().parent / "ANALYST_ONLY_RELIABILITY_MAPPING.json"
    public_path.write_text(json.dumps(public, ensure_ascii=False, indent=2) + "\n")
    private_path.write_text(json.dumps(private, ensure_ascii=False, indent=2) + "\n")
    manifest = {
        "status": "unlabeled_independent_reliability_packet",
        "seed": SEED,
        "population": "audited development, Reddit IDs only",
        "quota": QUOTAS,
        "selected_n": len(selected),
        "eligible_by_stratum_after_exclusions": {k: len(candidates[k]) for k in QUOTAS},
        "selected_by_stratum": dict(Counter(bucket(r) for r in selected)),
        "selected_by_source_pool": dict(Counter(r.get("source_pool_audit_only", "unknown") for r in selected)),
        "excluded_diagnostic_sample_ids": len(diagnostic_ids),
        "reserved_overlap": len(selected_ids & reserved_ids),
        "fresh_overlap": len(selected_ids & fresh_ids),
        "diagnostic_overlap": len(selected_ids & diagnostic_ids),
        "non_reddit_ids": sum(r["reddit_id"].startswith("so_") for r in selected),
        "input_sha256": {"development": sha256(DEV), "reserved": sha256(RESERVED), "fresh": sha256(FRESH), "diagnostic": sha256(DIAGNOSTIC)},
        "blind_rows_sha256": sha256(public_path),
        "mapping_sha256": sha256(private_path),
        "note": "Previously reviewed development records; Manu may remember some. Independent first passes are independent of each other, not necessarily blind to all prior exposure.",
    }
    (OUT / "MANIFEST.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(json.dumps({k: manifest[k] for k in ("selected_n", "selected_by_stratum", "selected_by_source_pool", "reserved_overlap", "fresh_overlap", "diagnostic_overlap", "non_reddit_ids")}, indent=2))


if __name__ == "__main__":
    main()
