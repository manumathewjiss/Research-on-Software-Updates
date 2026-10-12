"""Prepare a masked 15-post check of the revised diagnostic codebook."""
import json
import random
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "outputs" / "codebook-check-20261007"
rows = {r["pilot_id"]: r for r in json.loads((ROOT / "pilot_review_text.json").read_text())}
answers = {r["pilot_id"]: r for r in json.loads((ROOT / "submissions/2026-10-07-manu/answers.json").read_text())}
rng = random.Random(20261007)
selected = []

def add_where(predicate, count):
    candidates = [key for key in rows if key not in selected and predicate(answers[key])]
    rng.shuffle(candidates)
    selected.extend(candidates[:count])

for key in ["D20261007-031", "D20261007-039", "D20261007-050"]:
    selected.append(key)
add_where(lambda a: a["release_or_update"] == "unclear" and a["trigger_or_steps"] == "present", 4)
add_where(lambda a: a["attempted_fix"] == "present", 4)
add_where(lambda a: a["attempted_fix"] == "not_observed", 2)
add_where(lambda a: a["release_or_update"] == "present", 2)
assert len(selected) == 15 and len(set(selected)) == 15
rng.shuffle(selected)

OUT.mkdir(parents=True, exist_ok=True)
review = []
mapping = []
for index, old_id in enumerate(selected, 1):
    check_id = f"C20261007-{index:03d}"
    review.append({"check_id": check_id, "title": rows[old_id]["title"], "post_body": rows[old_id]["post_body"]})
    mapping.append({"check_id": check_id, "pilot_id": old_id})
(OUT / "review_text.json").write_text(json.dumps(review, ensure_ascii=False, indent=2) + "\n")
(OUT / "analyst_mapping.json").write_text(json.dumps(mapping, indent=2) + "\n")
(OUT / "selection_manifest.json").write_text(json.dumps({
    "purpose": "Deliberately selected boundary-case check of revised codebook v0.2; not representative",
    "seed": 20261007,
    "n": 15,
    "source": "The unchanged 50-post first-pass pilot",
    "reviewer_file_contains_first_pass_answers": False,
    "interpretation": "Feasibility and descriptive rule-change check; not within-reviewer consistency or independent agreement"
}, indent=2) + "\n")
print(OUT)
