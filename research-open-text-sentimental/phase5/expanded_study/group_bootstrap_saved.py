#!/usr/bin/env python3
"""Group bootstrap of already saved development predictions. No retraining."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
from sklearn.metrics import f1_score

HERE = Path(__file__).resolve().parent
PRED = HERE / "results" / "predictions.jsonl"
OUT = HERE / "results" / "group_bootstrap.json"
N_BOOT = 1000
SEED = 42
ARMS = (
    "pred_title",
    "pred_body",
    "pred_vader_only",
    "pred_title_body_plus_vader",
    "pred_textblob_only",
    "pred_title_body_plus_textblob",
    "pred_contextual_only",
    "pred_title_body_plus_contextual",
    "pred_minilm",
)


def macro(y, pred) -> float:
    return float(f1_score(y, pred, average="macro", zero_division=0))


def group_interval(y, base, other, groups) -> dict:
    rng = np.random.default_rng(SEED)
    uniq = np.unique(groups)
    members = {int(g): np.flatnonzero(groups == g) for g in uniq}
    point = macro(y, other) - macro(y, base)
    draws = np.empty(N_BOOT, dtype=float)
    for i in range(N_BOOT):
        chosen = rng.choice(uniq, size=len(uniq), replace=True)
        idx = np.concatenate([members[int(g)] for g in chosen])
        draws[i] = macro(y[idx], other[idx]) - macro(y[idx], base[idx])
    lo, hi = np.percentile(draws, [2.5, 97.5])
    return {
        "definition": "candidate minus pred_title_body; groups drawn with replacement; posts in a drawn group stay together",
        "n_posts": int(len(y)),
        "n_groups": int(len(uniq)),
        "n_multi_post_groups": int(sum(1 for ids in members.values() if len(ids) > 1)),
        "n_posts_in_multi_post_groups": int(sum(len(ids) for ids in members.values() if len(ids) > 1)),
        "point_delta_macro_f1": float(point),
        "ci95": [float(lo), float(hi)],
        "includes_zero": bool(lo <= 0 <= hi),
        "n_boot": N_BOOT,
        "seed": SEED,
    }


def main() -> None:
    rows = [json.loads(line) for line in PRED.read_text(encoding="utf-8").splitlines() if line.strip()]
    if len(rows) != 2050:
        raise SystemExit(len(rows))
    y = np.array([int(r["y_true"]) for r in rows])
    base = np.array([int(r["pred_title_body"]) for r in rows])
    groups = np.array([int(r["group_id"]) for r in rows])
    out = {
        "baseline": "pred_title_body",
        "baseline_macro_f1": macro(y, base),
        "note": "This uses saved predictions only. It does not refit models or read held-out tests. The metrics_table.csv intervals are post-level paired bootstraps from the same predictions.",
        "arms": {},
    }
    for name in ARMS:
        other = np.array([int(r[name]) for r in rows])
        out["arms"][name] = group_interval(y, base, other, groups)
    OUT.write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: {"delta": v["point_delta_macro_f1"], "ci": v["ci95"], "includes_zero": v["includes_zero"]} for k, v in out["arms"].items()}, indent=2))


if __name__ == "__main__":
    main()
