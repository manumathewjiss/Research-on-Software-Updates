"""Score the frozen fresh S2 test once using the previously fixed model."""
from __future__ import annotations

import hashlib
import json
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
from sklearn.metrics import f1_score

ROOT = Path(__file__).resolve().parent
PHASE3 = ROOT.parent
EXPERIMENT = PHASE3 / "experiment_v1"
sys.path.insert(0, str(EXPERIMENT))
from run_experiment import build_lr, bootstrap_ci, keyword_predict, make_text, metrics_bundle  # noqa: E402

DEV = PHASE3 / "revised_development_v2/development_v2.jsonl"
TEST = ROOT / "frozen_joint_labels/s2_test_344.jsonl"
FREEZE = ROOT / "frozen_joint_labels/freeze_manifest.json"
OUT = ROOT / "results_fixed_model"
THRESHOLD = 0.5877137791150834


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text().splitlines() if line]


def main() -> None:
    freeze = json.loads(FREEZE.read_text())
    assert freeze["status"] == "frozen_before_model_scoring"
    assert sha(DEV) == freeze["development_snapshot_sha256"]
    assert sha(TEST) == freeze["s2_test_sha256"]
    OUT.mkdir(exist_ok=True)
    if (OUT / "metrics.json").exists() or (OUT / "predictions.jsonl").exists():
        raise RuntimeError("This test has already been scored. Refusing to overwrite the one-shot record.")

    development = [r for r in load(DEV) if r["s2_in_scope"] and r["s2_target"] in (0, 1)
                   and r["reddit_id"] not in {"1t0wme9", "1wrqch6"}]
    test = load(TEST)
    assert len(development) == 2080 and len(test) == 344
    assert not ({r["reddit_id"] for r in development} & {r["reddit_id"] for r in test})
    y_dev = np.array([r["s2_target"] for r in development], dtype=int)
    y_test = np.array([r["s2_target"] for r in test], dtype=int)
    assert Counter(y_dev) == {1: 1686, 0: 394}
    assert Counter(y_test) == {1: 277, 0: 67}

    text_dev = [make_text(r, "title_body") for r in development]
    text_test = [make_text(r, "title_body") for r in test]
    model = build_lr(4.0)
    model.fit(text_dev, y_dev)
    scores = model.predict_proba(text_test)[:, 1]
    predictions = (scores >= THRESHOLD).astype(int)

    metrics = metrics_bundle(y_test, predictions, scores)
    metrics["bootstrap"] = {
        "macro_f1": bootstrap_ci(y_test, predictions,
                                 lambda a, b: f1_score(a, b, average="macro", zero_division=0)),
        "other_update_f1": bootstrap_ci(y_test, predictions,
                                        lambda a, b: f1_score(a, b, pos_label=0, zero_division=0)),
        "troubleshooting_f1": bootstrap_ci(y_test, predictions,
                                           lambda a, b: f1_score(a, b, pos_label=1, zero_division=0)),
    }
    majority = np.ones(len(test), dtype=int)
    keyword = keyword_predict(text_test)
    baselines = {
        "majority": metrics_bundle(y_test, majority),
        "fixed_keyword": metrics_bundle(y_test, keyword),
    }
    by_body = {}
    for label, indices in {
        "title_only": [i for i, r in enumerate(test) if not r["post_body"].strip()],
        "title_and_body": [i for i, r in enumerate(test) if r["post_body"].strip()],
    }.items():
        if indices:
            by_body[label] = metrics_bundle(y_test[indices], predictions[indices], scores[indices])
    by_time = {}
    for label, indices in {
        "posted_october_2026": [i for i, r in enumerate(test) if r["created_utc"] >= "2026-10-01"],
        "posted_before_october_2026": [i for i, r in enumerate(test) if r["created_utc"] < "2026-10-01"],
    }.items():
        if indices:
            by_time[label] = metrics_bundle(y_test[indices], predictions[indices], scores[indices])

    rows = [{"test_id": r["test_id"], "reddit_id": r["reddit_id"],
             "y_true": int(y_test[i]), "y_pred": int(predictions[i]),
             "troubleshooting_score": float(scores[i]), "correct": bool(predictions[i] == y_test[i]),
             "has_body": bool(r["post_body"].strip()), "subreddit": r["subreddit"],
             "created_utc": r["created_utc"]} for i, r in enumerate(test)]
    result = {
        "evaluated_once": True,
        "evaluated_at_utc": datetime.now(timezone.utc).isoformat(),
        "model": "title_body TF-IDF logistic regression",
        "C": 4.0,
        "threshold": THRESHOLD,
        "development_n": len(development),
        "test_n": len(test),
        "development_sha256": sha(DEV),
        "frozen_test_sha256": sha(TEST),
        "model_metrics": metrics,
        "baselines": baselines,
        "by_body": by_body,
        "by_post_date": by_time,
        "label_provenance": freeze["provenance"],
    }
    (OUT / "metrics.json").write_text(json.dumps(result, indent=2) + "\n")
    (OUT / "predictions.jsonl").write_text("".join(json.dumps(r, sort_keys=True) + "\n" for r in rows))
    print(json.dumps({"model": metrics, "baselines": baselines,
                      "by_body": by_body, "by_post_date": by_time}, indent=2))


if __name__ == "__main__":
    main()
