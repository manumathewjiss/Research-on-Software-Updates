"""Record a provisional, text-based reading of frozen test errors.

These are analyst interpretations of post wording, not changes to reviewed labels
or proof of a causal model failure mechanism.
"""

import csv
import json
import random
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = Path(__file__).resolve().parent

# One primary descriptive pattern per error. The third field flags a label
# boundary that deserves independent adjudication if used as a manuscript case.
CODE = {
    "027": ("specific_malfunction", "panel resize fails after upgrade", False),
    "029": ("opinion_or_narrative", "telemetry complaint and migration story; no current fix request", False),
    "037": ("update_installation_problem", "upgrade command/config blocks installation", False),
    "046": ("general_experience_question", "asks whether others have issues; no own failure stated", False),
    "054": ("feature_observation", "title names a scrollbar change; saved body absent", True),
    "069": ("feature_observation", "asks why new visual changes are not apparent", True),
    "074": ("preventive_update_advice", "asks whether pending firmware should be applied", False),
    "078": ("documentation_or_navigation_problem", "new feature instructions point to wrong settings path", False),
    "102": ("brief_malfunction", "one short sentence describes intermittent screen glitch", False),
    "121": ("explanation_or_verification_question", "asks why package manager imported key and how to verify it", True),
    "132": ("changed_ui_behavior", "blank tab dragging after update; asks design versus glitch", True),
    "177": ("changed_or_removed_feature", "VPN option disappeared after update; asks why", True),
    "179": ("resolved_incident_narrative", "desktop files disappeared but author found recovery path", True),
    "181": ("feature_activation_problem", "cannot find new SIA-DC09 option; asks for setup help", True),
    "193": ("resolved_incident_narrative", "license loss traced to moved registry key; long explanation", True),
    "196": ("performance_or_resource_problem", "battery health loss attributed to upgrade", False),
    "197": ("resolved_incident_narrative", "plugin incompatibility diagnosed and fixed in post", True),
    "208": ("preventive_update_advice", "requests an update plan before installing", False),
    "213": ("design_criticism", "complains about gradients and asks how to disable them", True),
    "218": ("brief_malfunction", "short corruption report with linked image", False),
    "234": ("preventive_update_advice", "asks about risks before BIOS update", False),
    "245": ("feature_observation", "reports smoother tabs and asks if others notice", False),
    "256": ("update_installation_problem", "install blocked by storage error despite free space", False),
    "290": ("changed_or_removed_feature", "support/deprecation message after upgrade; asks why", True),
    "291": ("preventive_update_advice", "asks how to keep old computer useful before OS update", True),
    "333": ("design_criticism", "complains about restart requirement, no fix request", True),
    "335": ("specific_malfunction", "mpv playback changes after package upgrade", False),
    "338": ("brief_malfunction", "blur-my-shell stops working; mostly image link", False),
    "347": ("update_installation_problem", "expected Fedora release absent from update tools", False),
    "349": ("resolved_incident_narrative", "long account of Dell updater and BIOS problems", True),
    "359": ("specific_malfunction", "age verification blocks access after iOS update; title only", False),
    "360": ("how_to_update_question", "asks how to install newer Android; no current malfunction", True),
    "362": ("feature_observation", "positive surprise at Copilot autocomplete", False),
    "367": ("performance_or_quality_complaint", "says Deepseek quality degraded after update", True),
    "380": ("configuration_help", "asks how to restore previous context-menu search behavior", False),
    "411": ("design_criticism", "detailed criticism of Copilot UI changes, no explicit repair steps", True),
    "423": ("specific_malfunction", "speaker noise after updates; software versus hardware uncertain", True),
    "427": ("configuration_help", "asks how to resize search bar; solution appears in saved body", True),
    "445": ("performance_or_resource_problem", "high memory use after Firefox update with angry wording", False),
    "446": ("specific_malfunction", "crash and memory leak described with environment", False),
    "454": ("preventive_update_advice", "asks whether update is safe on old iPhone", False),
    "472": ("configuration_help", "asks how to change Dock appearance after update", True),
    "473": ("update_installation_problem", "cumulative update missing after migration; asks why", True),
    "479": ("specific_malfunction", "library repeatedly rehashes after updates", False),
    "480": ("changed_or_removed_feature", "history sorting removed; post is chiefly complaint", True),
    "492": ("alternatives_or_advice", "lists browser alternatives to a removed Edge feature", False),
}

pred = [json.loads(line) for line in (ROOT / "results_fixed_model/predictions.jsonl").read_text().splitlines() if line]
text = {r["test_id"]: r for r in json.loads((ROOT / "review_text.json").read_text())}
errors = [r for r in pred if not r["correct"]]
assert len(errors) == len(CODE) == 46
assert {r["test_id"][-3:] for r in errors} == set(CODE)

with (OUT / "provisional_error_codes.csv").open("w", newline="") as f:
    fields = ["test_id", "error_type", "primary_text_pattern", "borderline_for_adjudication", "analyst_note", "title"]
    w = csv.DictWriter(f, fieldnames=fields)
    w.writeheader()
    for r in errors:
        pattern, note, borderline = CODE[r["test_id"][-3:]]
        w.writerow({"test_id": r["test_id"], "error_type": "false_negative" if r["y_true"] == 1 else "false_positive", "primary_text_pattern": pattern, "borderline_for_adjudication": borderline, "analyst_note": note, "title": text[r["test_id"]]["title"]})

# A small control set helps distinguish descriptions of errors from descriptions
# common to correctly classified posts. It is matched on true class and, when
# possible, subreddit. This is not a causal or population-representative sample.
rng = random.Random(20261008)
used = set()
controls = []
for error in errors:
    eligible = [r for r in pred if r["correct"] and r["y_true"] == error["y_true"] and r["test_id"] not in used]
    same_community = [r for r in eligible if r["subreddit"] == error["subreddit"]]
    control = rng.choice(same_community or eligible)
    used.add(control["test_id"])
    controls.append((error, control))

with (OUT / "matched_correct_examples.csv").open("w", newline="") as f:
    fields = ["error_test_id", "control_test_id", "true_class", "same_subreddit", "control_subreddit", "control_title", "control_post_body"]
    w = csv.DictWriter(f, fieldnames=fields)
    w.writeheader()
    for error, control in controls:
        t = text[control["test_id"]]
        w.writerow({"error_test_id": error["test_id"], "control_test_id": control["test_id"], "true_class": control["y_true"], "same_subreddit": control["subreddit"] == error["subreddit"], "control_subreddit": control["subreddit"], "control_title": t["title"], "control_post_body": t.get("post_body", "")})

summary = {
    "errors_coded": len(errors),
    "patterns_by_error_type": {kind: dict(Counter(CODE[r["test_id"][-3:]][0] for r in errors if (r["y_true"] == 1) == (kind == "false_negative"))) for kind in ("false_negative", "false_positive")},
    "borderline_flag_n": sum(CODE[r["test_id"][-3:]][2] for r in errors),
    "matched_control_n": len(controls),
    "same_subreddit_control_n": sum(a["subreddit"] == b["subreddit"] for a, b in controls),
}
(OUT / "provisional_coding_summary.json").write_text(json.dumps(summary, indent=2) + "\n")
print(json.dumps(summary, indent=2))
