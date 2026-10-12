"""Build a blind single-review consistency sample from reviewed Reddit development posts."""

import hashlib
import json
import random
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
MASTER = ROOT / "phase2/combined_dataset/master_records.json"
DEV = ROOT / "phase3/reddit_only_sensitivity/development_reddit_only.jsonl"
DIAGNOSTIC = ROOT / "phase3/diagnostic_results/diagnostic_oof_join.jsonl"
SEED = 20261008
QUOTAS = {"troubleshooting": 50, "other_update": 30, "software_nonupdate": 20, "nonsoftware": 20}


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


master = json.loads(MASTER.read_text())
dev_ids = {json.loads(line)["reddit_id"] for line in DEV.read_text().splitlines() if line}
diagnostic_ids = {json.loads(line)["reddit_id"] for line in DIAGNOSTIC.read_text().splitlines() if line}
assert len(dev_ids) == 3121


def stratum(r):
    software = r["phase2_about_software"]
    update = r["phase2_update_related"]
    dtype = r["phase2_discussion_type"]
    if software == "yes" and update == "yes":
        return "troubleshooting" if dtype == "technical_troubleshooting" else "other_update"
    if software == "yes" and update == "no":
        return "software_nonupdate"
    if software == "no":
        return "nonsoftware"
    return None


frame = [r for r in master if r["reddit_id"] in dev_ids and r["phase2_review_status"] == "manu_assisted_review" and r["reddit_id"] not in diagnostic_ids and stratum(r) in QUOTAS]
by_group = {k: sorted([r for r in frame if stratum(r) == k], key=lambda r: r["reddit_id"]) for k in QUOTAS}
rng = random.Random(SEED)
selected = []
for group, quota in QUOTAS.items():
    assert len(by_group[group]) >= quota
    selected.extend((group, row) for row in rng.sample(by_group[group], quota))
rng.shuffle(selected)

sheet_rows = []
mapping = []
for i, (group, row) in enumerate(selected, 1):
    blind_id = f"A{i:03d}"
    sheet_rows.append({
        "audit_id": blind_id,
        "title": row["title"],
        "post_body": row["post_body"],
        "saved_reply_context": row["discussion_context"],
        "about_software": "",
        "update_related": "",
        "discussion_type": "",
        "confidence": "",
        "reason": "",
    })
    mapping.append({
        "audit_id": blind_id,
        "reddit_id": row["reddit_id"],
        "study_id": row["study_id"],
        "sampling_stratum_audit_only": group,
        "source_pool_audit_only": row["source_pool"],
        "previous_about_software_audit_only": row["phase2_about_software"],
        "previous_update_related_audit_only": row["phase2_update_related"],
        "previous_discussion_type_audit_only": row["phase2_discussion_type"],
        "previous_review_status_audit_only": row["phase2_review_status"],
    })

assert len(sheet_rows) == len(mapping) == 120
assert len({x["reddit_id"] for x in mapping}) == 120
assert not ({x["reddit_id"] for x in mapping} & diagnostic_ids)
assert not ({x["reddit_id"] for x in mapping} - dev_ids)
assert all(not r[k] for r in sheet_rows for k in ("about_software", "update_related", "discussion_type", "confidence", "reason"))

(HERE / "blind_review_rows.json").write_text(json.dumps(sheet_rows, ensure_ascii=False, indent=2) + "\n")
(HERE / "ANALYST_ONLY_MAPPING.json").write_text(json.dumps(mapping, ensure_ascii=False, indent=2) + "\n")
manifest = {
    "purpose": "Single-review blind consistency audit; no independent inter-annotator agreement can be estimated",
    "seed": SEED,
    "sampling_method": "Fixed quotas; random sample within each prior-label stratum after sorting by Reddit ID; final order shuffled",
    "frame": "Reddit-only revised development, prior status manu_assisted_review, excluding 237 diagnostic-reviewed IDs and unclear prior strata",
    "frame_n": len(frame),
    "frame_stratum_counts": {k: len(v) for k, v in by_group.items()},
    "sample_n": len(sheet_rows),
    "sample_quotas": QUOTAS,
    "source_counts_audit_only": dict(Counter(r["source_pool"] for _, r in selected)),
    "master_sha256": digest(MASTER),
    "reddit_development_sha256": digest(DEV),
    "diagnostic_oof_sha256": digest(DIAGNOSTIC),
    "blind_rows_sha256": digest(HERE / "blind_review_rows.json"),
    "mapping_sha256": digest(HERE / "ANALYST_ONLY_MAPPING.json"),
    "reserved_200_in_sample": 0,
    "fresh_500_in_sample": 0,
    "diagnostic_sample_in_sample": 0,
    "prior_labels_in_reviewer_rows": False,
}
(HERE / "sampling_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
print(json.dumps({"sample_n": len(sheet_rows), "frame_n": len(frame), "strata": QUOTAS, "source_counts": manifest["source_counts_audit_only"]}, indent=2))
