#!/usr/bin/env python3
"""Phase A: title/body VADER arms and fold-wise TF-IDF coefficients.

Does not fine-tune a transformer, does not read protected tests, and does
not import the classification virtualenv.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
from sklearn.metrics import f1_score

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
EXPANDED = REPO / "phase5" / "expanded_study"
sys.path.insert(0, str(EXPANDED))

import run_expanded as ex  # noqa: E402

OUT = HERE / "results"
SAVED_PRED = EXPANDED / "results" / "predictions.jsonl"
TARGET_TEXT = 0.8319320360990539
TARGET_PLUS_VADER = 0.8331300906317138
N_BOOT = 1000
SEED = 42


def group_interval(y, base, other, groups) -> dict:
    rng = np.random.default_rng(SEED)
    uniq = np.unique(groups)
    members = {int(g): np.flatnonzero(groups == g) for g in uniq}
    point = float(f1_score(y, other, average="macro", zero_division=0) - f1_score(y, base, average="macro", zero_division=0))
    draws = np.empty(N_BOOT, dtype=float)
    for i in range(N_BOOT):
        chosen = rng.choice(uniq, size=len(uniq), replace=True)
        idx = np.concatenate([members[int(g)] for g in chosen])
        draws[i] = f1_score(y[idx], other[idx], average="macro", zero_division=0) - f1_score(
            y[idx], base[idx], average="macro", zero_division=0
        )
    lo, hi = np.percentile(draws, [2.5, 97.5])
    return {
        "definition": "candidate minus saved pred_title_body; groups drawn with replacement",
        "point_delta_macro_f1": point,
        "ci95": [float(lo), float(hi)],
        "includes_zero": bool(lo <= 0 <= hi),
        "n_boot": N_BOOT,
        "seed": SEED,
        "n_groups": int(len(uniq)),
    }


def field_vader(rows, field: str) -> tuple[np.ndarray, int]:
    analyzer = ex.SentimentIntensityAnalyzer()
    out = np.empty(len(rows), dtype=float)
    empty = 0
    for i, row in enumerate(rows):
        text = row.get(field) or ""
        if not str(text).strip():
            out[i] = 0.0
            empty += 1
        else:
            out[i] = float(analyzer.polarity_scores(str(text))["compound"])
    return out, empty


def fold_coefficients(texts, y, folds) -> dict:
    """Coefficients from each outer training fold only. Held-out fold is unused."""
    per_fold = {}
    positive_sets = []
    negative_sets = []
    for fold in range(5):
        train = np.flatnonzero(folds != fold)
        vec = ex.vectorizer()
        x = vec.fit_transform([texts[i] for i in train])
        clf = ex.lr_head()
        clf.fit(x, y[train])
        names = np.asarray(vec.get_feature_names_out())
        coef = clf.coef_.ravel()
        pos_idx = np.argsort(coef)[-25:][::-1]
        neg_idx = np.argsort(coef)[:25]
        pos = [{"feature": str(names[j]), "coefficient": float(coef[j])} for j in pos_idx]
        neg = [{"feature": str(names[j]), "coefficient": float(coef[j])} for j in neg_idx]
        per_fold[str(fold)] = {
            "n_train": int(len(train)),
            "toward_troubleshooting": pos,
            "toward_other_update": neg,
        }
        positive_sets.append({item["feature"] for item in pos})
        negative_sets.append({item["feature"] for item in neg})
    def stable(sets):
        counts = {}
        for s in sets:
            for term in s:
                counts[term] = counts.get(term, 0) + 1
        kept = sorted((t for t, c in counts.items() if c >= 4), key=lambda t: (-counts[t], t))
        return [{"feature": t, "folds_in_top25": counts[t]} for t in kept]
    return {
        "rule": "top 25 coefficients in each direction, fit on the outer training fold only; reported if present in at least 4 of 5 folds",
        "held_out_fold_used_for_selection": False,
        "stable_toward_troubleshooting": stable(positive_sets),
        "stable_toward_other_update": stable(negative_sets),
        "per_fold": per_fold,
    }


def arm_record(name, texts, scores, y, folds, groups, base) -> dict:
    pred, proba, thr, seconds = ex.oof_hybrid(texts, scores, y, folds, groups)
    metrics = ex.metrics_at(y, pred)
    return {
        "name": name,
        "metrics": metrics,
        "thresholds": thr,
        "seconds": seconds,
        "group_bootstrap_minus_pred_title_body": group_interval(y, base, pred, groups),
        "post_bootstrap_minus_pred_title_body": ex.paired_delta(y, base, pred),
        "_pred": pred,
    }


def main() -> int:
    rows, y, folds, groups, population = ex.load_population()
    saved = ex.read_jsonl(SAVED_PRED)
    if [r["reddit_id"] for r in saved] != [r["reddit_id"] for r in rows]:
        raise SystemExit("saved prediction order does not match the development load")
    base = np.array([int(r["pred_title_body"]) for r in saved])
    base_f1 = float(f1_score(y, base, average="macro", zero_division=0))
    if abs(base_f1 - TARGET_TEXT) > 1e-12:
        ex.write_json(OUT / "REPRODUCTION_FAILURE.json", {"observed": base_f1, "target": TARGET_TEXT})
        raise SystemExit(f"saved title+body macro-F1 changed: {base_f1}")
    texts = {
        "title": [ex.input_text(r, "title") for r in rows],
        "body": [ex.input_text(r, "body") for r in rows],
        "title_body": [ex.input_text(r, "title_body") for r in rows],
    }
    title_v, title_empty = field_vader(rows, "title")
    body_v, body_empty = field_vader(rows, "post_body")
    both_v, both_empty = ex.vader_scores(rows)
    print("title+body+VADER reproduction", flush=True)
    plus = arm_record("title_body_plus_vader", texts["title_body"], both_v, y, folds, groups, base)
    gap = abs(plus["metrics"]["macro_f1"] - TARGET_PLUS_VADER)
    if gap > 1e-9:
        ex.write_json(OUT / "REPRODUCTION_FAILURE.json", {
            "arm": "title_body_plus_vader",
            "observed": plus["metrics"]["macro_f1"],
            "target": TARGET_PLUS_VADER,
            "abs_gap": gap,
        })
        raise SystemExit("title+body+VADER did not reproduce")
    print("title+VADER", flush=True)
    title_arm = arm_record("title_plus_vader", texts["title"], title_v, y, folds, groups, base)
    print("body+VADER", flush=True)
    body_arm = arm_record("body_plus_vader", texts["body"], body_v, y, folds, groups, base)
    print("fold coefficients", flush=True)
    coef = fold_coefficients(texts["title_body"], y, folds)
    payload = {
        "saved_pred_title_body_macro_f1": base_f1,
        "vader_inputs": {
            "title_plus_vader": "compound of raw title only; empty title -> 0.0",
            "body_plus_vader": "compound of raw body only; empty body -> 0.0",
            "title_body_plus_vader": "compound of raw title, newline, raw body",
            "title_empty_n": title_empty,
            "body_empty_n": body_empty,
            "title_body_empty_n": both_empty,
        },
        "arms": {
            name: {k: v for k, v in rec.items() if k != "_pred"}
            for name, rec in {
                "title_body_plus_vader": plus,
                "title_plus_vader": title_arm,
                "body_plus_vader": body_arm,
            }.items()
        },
    }
    ex.write_json(OUT / "vader_input_ablation.json", payload)
    ex.write_json(OUT / "fold_coefficients.json", coef)
    boot = {
        "baseline": "saved pred_title_body",
        "baseline_macro_f1": base_f1,
        "arms": {name: rec["group_bootstrap_minus_pred_title_body"] for name, rec in {
            "title_body_plus_vader": plus,
            "title_plus_vader": title_arm,
            "body_plus_vader": body_arm,
        }.items()},
    }
    ex.write_json(OUT / "group_bootstrap.json", boot)
    pred_rows = []
    for i, row in enumerate(rows):
        pred_rows.append({
            "reddit_id": row["reddit_id"],
            "fold": int(folds[i]),
            "group_id": int(groups[i]),
            "y_true": int(y[i]),
            "pred_title_body": int(base[i]),
            "pred_title_plus_vader": int(title_arm["_pred"][i]),
            "pred_body_plus_vader": int(body_arm["_pred"][i]),
            "pred_title_body_plus_vader": int(plus["_pred"][i]),
            "vader_title": float(title_v[i]),
            "vader_body": float(body_v[i]),
            "vader_title_body": float(both_v[i]),
        })
    ex.write_jsonl(OUT / "predictions.jsonl", pred_rows)
    lines = ["arm,macro_f1,delta,group_ci_low,group_ci_high,includes_zero"]
    for name, rec in payload["arms"].items():
        g = rec["group_bootstrap_minus_pred_title_body"]
        lines.append(
            f"{name},{rec['metrics']['macro_f1']:.6f},{g['point_delta_macro_f1']:.6f},{g['ci95'][0]:.6f},{g['ci95'][1]:.6f},{g['includes_zero']}"
        )
    (OUT / "metrics_table.csv").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps({"baseline": base_f1, "table": lines[1:]}), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
