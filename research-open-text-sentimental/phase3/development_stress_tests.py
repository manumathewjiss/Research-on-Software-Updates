"""Development-only temporal and held-out-community stress tests for the fixed model."""
from __future__ import annotations

import hashlib
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "experiment_v1"))
from run_experiment import build_lr, make_text, metrics_bundle  # noqa: E402

DEV = ROOT / "revised_development_v2/development_v2.jsonl"
OUT = ROOT / "diagnostic_results/development_stress_tests.json"
THRESHOLD = 0.5877137791150834
CUTOFF = "2026-07-01"


def score(train: list[dict], test: list[dict]) -> tuple[dict, list[dict]]:
    model = build_lr(4.0)
    model.fit([make_text(r, "title_body") for r in train],
              np.array([r["s2_target"] for r in train], dtype=int))
    scores = model.predict_proba([make_text(r, "title_body") for r in test])[:, 1]
    pred = (scores >= THRESHOLD).astype(int)
    truth = np.array([r["s2_target"] for r in test], dtype=int)
    records = [{"reddit_id": r["reddit_id"], "subreddit": r["subreddit"],
                "source_pool": r["source_pool_audit_only"],
                "y_true": int(truth[i]), "y_pred": int(pred[i]), "score": float(scores[i])}
               for i, r in enumerate(test)]
    return metrics_bundle(truth, pred, scores), records


def main() -> None:
    dev = [json.loads(line) for line in DEV.read_text().splitlines() if line]
    dev = [r for r in dev if r["s2_in_scope"] and r["s2_target"] in (0, 1)
           and r["reddit_id"] not in {"1t0wme9", "1wrqch6"}]
    assert len(dev) == 2080
    early = [r for r in dev if r["created_utc"][:10] < CUTOFF]
    late = [r for r in dev if r["created_utc"][:10] >= CUTOFF]
    temporal_metrics, temporal_predictions = score(early, late)

    groups = defaultdict(list)
    for r in dev:
        groups[(r.get("subreddit") or "unknown").lower()].append(r)
    eligible = {name: rows for name, rows in groups.items()
                if min(Counter(r["s2_target"] for r in rows).get(0, 0),
                       Counter(r["s2_target"] for r in rows).get(1, 0)) >= 5}
    held_out = []
    per_community = {}
    for name in sorted(eligible):
        train = [r for r in dev if (r.get("subreddit") or "unknown").lower() != name]
        test = eligible[name]
        metrics, predictions = score(train, test)
        per_community[name] = {"n": len(test), "support": metrics["support"],
                               "macro_f1": metrics["macro_f1"],
                               "other_f1": metrics["class_0_other_update"]["f1"],
                               "troubleshooting_f1": metrics["class_1_troubleshooting"]["f1"]}
        held_out.extend(predictions)
    held_out_metrics = metrics_bundle([r["y_true"] for r in held_out],
                                      [r["y_pred"] for r in held_out])
    report = {
        "status": "development-only stress checks; fresh test not used for model choice",
        "model": "fixed title_body TF-IDF logistic regression C=4 threshold=0.5877137791150834",
        "development_sha256": hashlib.sha256(DEV.read_bytes()).hexdigest(),
        "temporal_cutoff": CUTOFF,
        "temporal_train_n": len(early), "temporal_test_n": len(late),
        "temporal_train_class_counts": dict(Counter(str(r["s2_target"]) for r in early)),
        "temporal_test_class_counts": dict(Counter(str(r["s2_target"]) for r in late)),
        "temporal_test_metrics": temporal_metrics,
        "temporal_test_source_counts": dict(Counter(r["source_pool_audit_only"] for r in late)),
        "held_out_community_rule": "Each selected subreddit has at least five examples of each class in development; selection uses counts only",
        "eligible_community_count": len(eligible),
        "eligible_community_names": sorted(eligible),
        "held_out_community_pooled_n": len(held_out),
        "held_out_community_pooled_metrics": held_out_metrics,
        "per_community": per_community,
        "limitations": "Temporal and community changes are confounded with source and class mix. These are stress tests on development, not independent external validation."
    }
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({"temporal": {"train": len(early), "test": len(late),
                                   "macro_f1": temporal_metrics["macro_f1"]},
                      "held_out_community": {"n_communities": len(eligible),
                                             "n_posts": len(held_out),
                                             "macro_f1": held_out_metrics["macro_f1"]}}, indent=2))


if __name__ == "__main__":
    main()
