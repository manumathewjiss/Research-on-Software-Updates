"""Summarize frozen fresh-test predictions without fitting or changing a model."""

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PREDICTIONS = ROOT / "results_fixed_model" / "predictions.jsonl"
TEXT = ROOT / "review_text.json"
OUTPUT = ROOT / "saved_error_analysis"
OUTPUT.mkdir(exist_ok=True)

predictions = [json.loads(line) for line in PREDICTIONS.read_text().splitlines() if line]
texts = {row["test_id"]: row for row in json.loads(TEXT.read_text())}

if len(predictions) != 344 or len({r["test_id"] for r in predictions}) != 344:
    raise ValueError("Expected 344 unique frozen S2 predictions")

rows = []
for p in predictions:
    t = texts[p["test_id"]]
    row = {**p, "title": t["title"], "post_body": t.get("post_body", "")}
    row["error_type"] = "correct" if p["correct"] else ("false_negative" if p["y_true"] == 1 else "false_positive")
    row["body_chars"] = len(row["post_body"].strip())
    row["title_chars"] = len(row["title"].strip())
    row["score_margin_from_threshold"] = abs(p["troubleshooting_score"] - 0.5877137791150834)
    rows.append(row)

errors = [r for r in rows if not r["correct"]]
fields = ["test_id", "reddit_id", "error_type", "y_true", "y_pred", "troubleshooting_score", "score_margin_from_threshold", "subreddit", "created_utc", "has_body", "title_chars", "body_chars", "title", "post_body"]
with (OUTPUT / "all_46_errors.csv").open("w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=fields)
    writer.writeheader()
    writer.writerows({k: r[k] for k in fields} for r in errors)

def summarize(items):
    return {
        "n": len(items),
        "error_counts": dict(Counter(r["error_type"] for r in items)),
        "title_only_n": sum(not r["has_body"] for r in items),
        "median_body_chars": sorted(r["body_chars"] for r in items)[len(items) // 2] if items else None,
        "score_within_0_05_of_threshold_n": sum(r["score_margin_from_threshold"] <= 0.05 for r in items),
        "top_subreddits": Counter(r["subreddit"] for r in items).most_common(10),
    }

groups = defaultdict(list)
for r in rows:
    groups[(r["y_true"], r["has_body"])].append(r)

report = {
    "source": str(PREDICTIONS.relative_to(ROOT)),
    "test_n": len(rows),
    "all": summarize(rows),
    "errors": summarize(errors),
    "false_positives": summarize([r for r in errors if r["error_type"] == "false_positive"]),
    "false_negatives": summarize([r for r in errors if r["error_type"] == "false_negative"]),
    "by_true_class_and_body": {
        f"class_{label}_{'body' if body else 'title_only'}": summarize(items)
        for (label, body), items in sorted(groups.items())
    },
}
(OUTPUT / "summary.json").write_text(json.dumps(report, indent=2) + "\n")
print(json.dumps(report, indent=2))
