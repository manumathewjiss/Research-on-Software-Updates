"""Analyze the frozen diagnostic review and fixed-model grouped development errors."""
from __future__ import annotations

import hashlib
import json
import sys
from collections import Counter
from pathlib import Path

import numpy as np
from sklearn.model_selection import StratifiedGroupKFold

ROOT = Path(__file__).resolve().parent
EXP = ROOT / "experiment_v1"
sys.path.insert(0, str(EXP))
from run_experiment import build_lr, make_text, metrics_bundle  # noqa: E402
sys.path.insert(0, str(EXP / "followup"))
from run_followup import audit_within_dev  # noqa: E402

DEV = ROOT / "revised_development_v2/development_v2.jsonl"
REVIEW = ROOT / "completed_reviews_20261007_corrected/diagnostic_answers.json"
MAP = ROOT / "diagnostic_pilot/main_sample_20261007/analyst_mapping.json"
OUT = ROOT / "diagnostic_results"
THRESHOLD = 0.5877137791150834
FIELDS = ["software_product", "identifiable_release", "environment", "specific_symptom",
          "reproduction_context", "error_evidence", "attempted_remedy", "help_request"]


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def wilson(k: int, n: int) -> list[float]:
    z = 1.959963984540054
    p = k / n
    center = (p + z*z/(2*n)) / (1 + z*z/n)
    margin = z * ((p*(1-p)/n + z*z/(4*n*n)) ** 0.5) / (1 + z*z/n)
    return [center - margin, center + margin]


def frequency(rows: list[dict], field: str) -> dict:
    n = len(rows)
    k = sum(r[field] == "present" for r in rows)
    return {"n": n, "present": k, "rate": k/n if n else None,
            "wilson_95": wilson(k, n) if n else None,
            "unclear": sum(r[field] == "unclear" for r in rows)}


def main() -> None:
    review = json.loads(REVIEW.read_text())
    mapping = {r["sample_id"]: r for r in json.loads(MAP.read_text())}
    assert len(review) == len(mapping) == 250
    yes = [r for r in review if r["troubleshooting_check"] == "yes"]
    assert len(yes) == 237
    report = {
        "design": "Simple random sample of 250 from 1658 Reddit-only reviewed troubleshooting development posts",
        "review_provenance": "User reports joint human review; no independent agreement estimate",
        "original_sample_n": 250,
        "check_counts": dict(Counter(r["troubleshooting_check"] for r in review)),
        "conditional_n_yes": len(yes),
        "conditional_field_rates": {f: frequency(yes, f) for f in FIELDS},
        "body_missing_n": sum(not (r["post_body"] or "").strip() for r in review),
        "by_body": {},
        "pilot_overlap_n": sum(mapping[r["sample_id"]]["pilot_overlap"] for r in review),
        "excluding_pilot_overlap": {},
        "field_count_distribution": dict(Counter(sum(r[f] == "present" for f in FIELDS) for r in yes)),
        "input_hashes": {"review": sha(REVIEW), "mapping": sha(MAP), "development": sha(DEV)},
    }
    for label, group in {
        "title_only": [r for r in yes if not (r["post_body"] or "").strip()],
        "title_and_body": [r for r in yes if (r["post_body"] or "").strip()],
    }.items():
        report["by_body"][label] = {"n": len(group), "fields": {f: frequency(group, f) for f in FIELDS}}
    without_pilot = [r for r in yes if not mapping[r["sample_id"]]["pilot_overlap"]]
    report["excluding_pilot_overlap"] = {"n": len(without_pilot),
                                         "fields": {f: frequency(without_pilot, f) for f in FIELDS}}

    dev = [json.loads(line) for line in DEV.read_text().splitlines() if line]
    dev = [r for r in dev if r["s2_in_scope"] and r["s2_target"] in (0, 1)
           and r["reddit_id"] not in {"1t0wme9", "1wrqch6"}]
    assert len(dev) == 2080
    _, groups = audit_within_dev(dev)
    y = np.array([r["s2_target"] for r in dev], dtype=int)
    texts = [make_text(r, "title_body") for r in dev]
    scores = np.full(len(dev), np.nan)
    fold_ids = np.full(len(dev), -1)
    splitter = StratifiedGroupKFold(n_splits=5, shuffle=True, random_state=42)
    for fold, (train, held) in enumerate(splitter.split(np.zeros(len(dev)), y, groups)):
        model = build_lr(4.0)
        model.fit([texts[i] for i in train], y[train])
        scores[held] = model.predict_proba([texts[i] for i in held])[:, 1]
        fold_ids[held] = fold
    assert np.isfinite(scores).all() and (fold_ids >= 0).all()
    pred = (scores >= THRESHOLD).astype(int)
    dev_metrics = metrics_bundle(y, pred)
    dev_by_id = {r["reddit_id"]: i for i, r in enumerate(dev)}
    joined = []
    for r in yes:
        rid = mapping[r["sample_id"]]["reddit_id"]
        i = dev_by_id.get(rid)
        if i is None:
            continue
        joined.append({"sample_id": r["sample_id"], "reddit_id": rid,
                       "y_true": int(y[i]), "y_pred": int(pred[i]),
                       "score": float(scores[i]), "fold": int(fold_ids[i]),
                       "has_body": bool((r["post_body"] or "").strip()),
                       "field_count": sum(r[f] == "present" for f in FIELDS),
                       **{f: r[f] for f in FIELDS}})
    assert len(joined) == 237
    error_table = {}
    for field in FIELDS:
        error_table[field] = {}
        for value in ["present", "not_observed", "unclear"]:
            subset = [r for r in joined if r[field] == value]
            if subset:
                error_table[field][value] = {"n": len(subset),
                                             "misses": sum(r["y_pred"] == 0 for r in subset),
                                             "miss_rate": sum(r["y_pred"] == 0 for r in subset)/len(subset)}
    report["grouped_development_oof"] = {
        "method": "Fixed model/threshold, StratifiedGroupKFold (exact and near-duplicate text grouped)",
        "metrics": dev_metrics,
        "diagnostic_yes_join_n": len(joined),
        "diagnostic_yes_missed_n": sum(r["y_pred"] == 0 for r in joined),
        "field_miss_table": error_table,
        "by_body": {label: {"n": len(subset), "misses": sum(r["y_pred"] == 0 for r in subset)}
                    for label, subset in {
                        "title_only": [r for r in joined if not r["has_body"]],
                        "title_and_body": [r for r in joined if r["has_body"]],
                    }.items()},
        "interpretation": "Exploratory association within development. Diagnostic fields were not labeled on the fresh test, so fresh-test errors cannot be joined to these fields."
    }
    OUT.mkdir(exist_ok=True)
    (OUT / "analysis.json").write_text(json.dumps(report, indent=2) + "\n")
    (OUT / "grouped_oof_predictions.jsonl").write_text("".join(
        json.dumps({"reddit_id": r["reddit_id"], "y_true": int(y[i]),
                    "y_pred": int(pred[i]), "score": float(scores[i]), "fold": int(fold_ids[i])}) + "\n"
        for i, r in enumerate(dev)))
    (OUT / "diagnostic_oof_join.jsonl").write_text("".join(json.dumps(r) + "\n" for r in joined))
    print(json.dumps({"check_counts": report["check_counts"],
                      "field_rates": {f: report["conditional_field_rates"][f]["rate"] for f in FIELDS},
                      "grouped_development_macro_f1": dev_metrics["macro_f1"],
                      "diagnostic_join_misses": report["grouped_development_oof"]["diagnostic_yes_missed_n"]}, indent=2))


if __name__ == "__main__":
    main()
