"""Flag prior software/non-update development posts for rule review.

The output is a reading queue, not a label correction or classifier.
"""

import csv
import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
MASTER = ROOT / "phase2/combined_dataset/master_records.json"
DEV = ROOT / "phase3/reddit_only_sensitivity/development_reddit_only.jsonl"
dev_ids = {json.loads(line)["reddit_id"] for line in DEV.read_text().splitlines() if line}
rows = json.loads(MASTER.read_text())
frame = [r for r in rows if r["reddit_id"] in dev_ids and r["phase2_review_status"] == "manu_assisted_review" and r["phase2_about_software"] == "yes" and r["phase2_update_related"] == "no"]
patterns = {
    "after_or_since": r"\b(after|since|following|post)[ -]?(the |a |an )?(latest |recent |last |new )?(update|upgrade|patch|release)\b",
    "update_near_issue": r"\b(update|upgrade|patch|release)[^.!?]{0,70}\b(caus|broke|break|fail|issue|problem|bug|crash|stop|chang)",
    "question_near_update": r"\b(could|might|may|did|is|was|due to)[^.!?]{0,70}\b(update|upgrade|patch|release)\b",
}
out = []
for r in frame:
    text = " ".join((r["title"], r["post_body"], r["discussion_context"])).lower()
    hits = [name for name, pattern in patterns.items() if re.search(pattern, text)]
    out.append({"reddit_id": r["reddit_id"], "title": r["title"], "post_body": r["post_body"], "saved_reply_context": r["discussion_context"], "heuristic_flags": ",".join(hits), "human_update_decision": "", "human_reason": ""})
assert len(frame) == len(out) == 728
assert sum(bool(r["heuristic_flags"]) for r in out) == 208
out.sort(key=lambda r: (not bool(r["heuristic_flags"]), r["reddit_id"]))
with (HERE / "submission/update_connection_candidate_screen.csv").open("w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(out[0]))
    w.writeheader()
    w.writerows(out)
print({"frame": len(out), "flagged_candidates": sum(bool(r["heuristic_flags"]) for r in out), "unflagged": sum(not r["heuristic_flags"] for r in out)})
