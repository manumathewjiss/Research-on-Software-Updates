"""Grouped development-only fixed-config check after the 200-post overlay."""

from __future__ import annotations

import hashlib
import json
import sys
from collections import Counter
from pathlib import Path
from urllib.parse import urlparse

import numpy as np
from sklearn.model_selection import StratifiedGroupKFold


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
PHASE3 = REPO / "phase3"
sys.path.insert(0, str(PHASE3 / "experiment_v1"))
sys.path.insert(0, str(PHASE3 / "experiment_v1/followup"))
from run_experiment import build_lr, keyword_predict, make_text, metrics_bundle  # noqa: E402
from run_followup import audit_within_dev  # noqa: E402

SUB = HERE / "submissions/2026-10-07-independent"
INPUT = SUB / "development_after_independent_review.jsonl"
NEAR_DUP = {"1t0wme9", "1wrqch6"}
THRESHOLD = 0.5877137791150834


def main() -> None:
    rows = [json.loads(line) for line in INPUT.read_text().splitlines() if line]
    assert len(rows) == len({r["reddit_id"] for r in rows}) == 3151
    master = {r["reddit_id"]: r for r in json.loads((REPO / "phase2/combined_dataset/master_records.json").read_text())}
    subset = [r for r in rows if r["s2_in_scope"] and r["reddit_id"] not in NEAR_DUP]
    assert len(subset) == 2164
    reddit = [r for r in subset if urlparse(master[r["reddit_id"]]["url"]).netloc.lower().removeprefix("www.") == "reddit.com"]
    assert len(reddit) == 2134
    results = {}
    for name, records in (("mixed", subset), ("reddit_only", reddit)):
        texts = [make_text(r, "title_body") for r in records]
        y = np.array([int(r["s2_target"]) for r in records], dtype=int)
        _, groups = audit_within_dev(records)
        splitter = StratifiedGroupKFold(n_splits=5, shuffle=True, random_state=42)
        score = np.full(len(records), np.nan)
        pred = np.full(len(records), -1, dtype=int)
        majority = np.full(len(records), -1, dtype=int)
        keyword = np.full(len(records), -1, dtype=int)
        folds = np.full(len(records), -1, dtype=int)
        for fold, (train, test) in enumerate(splitter.split(np.zeros(len(records)), y, groups)):
            model = build_lr(4.0)
            model.fit([texts[i] for i in train], y[train])
            p = model.predict_proba([texts[i] for i in test])[:, 1]
            score[test] = p
            pred[test] = (p >= THRESHOLD).astype(int)
            majority[test] = Counter(y[train].tolist()).most_common(1)[0][0]
            keyword[test] = keyword_predict([texts[i] for i in test])
            folds[test] = fold
        assert np.isfinite(score).all() and min(pred) >= 0 and min(folds) >= 0
        results[name] = {
            "n": len(records),
            "class_counts": {"troubleshooting": int(sum(y)), "other_update": int(len(y) - sum(y))},
            "fixed_tfidf_lr": metrics_bundle(y, pred, score),
            "majority": metrics_bundle(y, majority),
            "keyword": metrics_bundle(y, keyword),
        }
    report = {
        "input_sha256": hashlib.sha256(INPUT.read_bytes()).hexdigest(),
        "status": "development_only_after_reported_independent_200_review",
        "method": "5-fold StratifiedGroupKFold seed 42, exact/near duplicate groups, fixed title+body TF-IDF LR C=4 balanced threshold 0.5877137791150834",
        "threshold_retuned": False,
        "reserved_test_scored": False,
        "fresh_test_scored": False,
        "comparison_limit": "Population and folds differ from earlier development checks; score changes are not paired effects or a new independent test.",
        "results": results,
    }
    (SUB / "independent_review_dev_grouped_validation.json").write_text(json.dumps(report, indent=2) + "\n")
    for name, result in results.items():
        print(name, result["n"], result["class_counts"], "model", result["fixed_tfidf_lr"]["macro_f1"], "majority", result["majority"]["macro_f1"], "keyword", result["keyword"]["macro_f1"])


if __name__ == "__main__":
    main()
