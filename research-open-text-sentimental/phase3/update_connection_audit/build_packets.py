"""Build review packets without changing previous labels or model data."""

import csv
import hashlib
import json
import random
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
AUDIT = ROOT / "phase3/single_reviewer_audit_20261008"
SUB = AUDIT / "submission"
SEED = 20261008


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


blind = {r["audit_id"]: r for r in json.loads((AUDIT / "blind_review_rows.json").read_text())}
disagreements = list(csv.DictReader((SUB / "disagreements.csv").open()))
assert len(disagreements) == 22
decisions = []
for d in disagreements:
    post = blind[d["audit_id"]]
    decisions.append({
        "audit_id": d["audit_id"],
        "title": post["title"],
        "post_body": post["post_body"],
        "saved_reply_context": post["saved_reply_context"],
        "previous_about_software": d["previous_about_software"],
        "new_about_software": d["new_about_software"],
        "final_about_software": "",
        "previous_update_related": d["previous_update_related"],
        "new_update_related": d["new_update_related"],
        "final_update_related": "",
        "previous_discussion_type": d["previous_discussion_type"],
        "new_discussion_type": d["new_discussion_type"],
        "final_discussion_type": "",
        "final_reason": "",
    })

screen = list(csv.DictReader((SUB / "update_connection_candidate_screen.csv").open()))
assert len(screen) == 728
conflict_ids = {d["reddit_id"] for d in disagreements}
flagged = [r for r in screen if r["heuristic_flags"] and r["reddit_id"] not in conflict_ids]
unflagged = [r for r in screen if not r["heuristic_flags"] and r["reddit_id"] not in conflict_ids]
assert len(flagged) == 204 and len(unflagged) == 510
rng = random.Random(SEED)
sample = rng.sample(sorted(unflagged, key=lambda r: r["reddit_id"]), 50)
selected = [("phrase_flagged", r) for r in flagged] + [("random_unflagged", r) for r in sample]
rng.shuffle(selected)
targeted = []
mapping = []
for i, (group, r) in enumerate(selected, 1):
    review_id = f"U{i:03d}"
    targeted.append({
        "review_id": review_id,
        "title": r["title"],
        "post_body": r["post_body"],
        "saved_reply_context": r["saved_reply_context"],
        "about_software": "",
        "update_related": "",
        "discussion_type": "",
        "confidence": "",
        "reason": "",
    })
    mapping.append({
        "review_id": review_id,
        "reddit_id": r["reddit_id"],
        "selection_group_audit_only": group,
        "heuristic_flags_audit_only": r["heuristic_flags"],
        "prior_label_audit_only": "software_yes_update_no",
    })

assert len(decisions) == 22 and len(targeted) == len(mapping) == 254
assert len({m["reddit_id"] for m in mapping}) == 254
assert not ({m["reddit_id"] for m in mapping} & conflict_ids)
for name, value in [
    ("disagreement_rows.json", decisions),
    ("targeted_blind_rows.json", targeted),
    ("ANALYST_ONLY_TARGETED_MAPPING.json", mapping),
]:
    (HERE / name).write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n")

manifest = {
    "seed": SEED,
    "source_disagreements_sha256": sha(SUB / "disagreements.csv"),
    "source_candidate_screen_sha256": sha(SUB / "update_connection_candidate_screen.csv"),
    "source_frame_n": 728,
    "source_flagged_n": 208,
    "source_unflagged_n": 520,
    "disagreement_packet_n": 22,
    "disagreement_overlap_with_source_frame_n": 14,
    "flagged_already_in_disagreement_packet_n": 4,
    "unflagged_already_in_disagreement_packet_n": 10,
    "targeted_packet_n": 254,
    "targeted_flagged_n": 204,
    "targeted_random_unflagged_n": 50,
    "random_unflagged_frame_n": 510,
    "targeted_previous_labels_hidden": True,
    "targeted_source_group_hidden": True,
    "no_master_merge": True,
}
(HERE / "PACKET_MANIFEST.json").write_text(json.dumps(manifest, indent=2) + "\n")
print(json.dumps({"adjudication": len(decisions), "targeted": len(targeted), "flagged": len(flagged), "random_unflagged": len(sample)}, indent=2))
