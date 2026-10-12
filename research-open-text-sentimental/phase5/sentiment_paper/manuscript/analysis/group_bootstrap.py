#!/usr/bin/env python3
"""Duplicate-group bootstrap for saved development predictions.

Does not refit models and does not read protected-test files.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
from sklearn.metrics import f1_score

HERE = Path(__file__).resolve().parent
PAPER = HERE.parents[1]
REPO = PAPER.parents[1]
OOF = REPO / "phase3" / "reddit_only_sensitivity" / "results" / "grouped_oof_predictions.jsonl"
THREAD = PAPER / "results" / "stage_c_comment_subset_predictions.jsonl"
PRE = PAPER.parent / "sentiment_reanalysis" / "results" / "reddit_2050" / "pooled_predictions.jsonl"
OUT = HERE / "group_bootstrap.json"
N_BOOT = 1000
SEED = 42


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def macro(y, pred) -> float:
    return float(f1_score(y, pred, average="macro", zero_division=0))


def group_bootstrap(y, pred_a, pred_b, groups) -> dict:
    rng = np.random.default_rng(SEED)
    y = np.asarray(y)
    pred_a = np.asarray(pred_a)
    pred_b = np.asarray(pred_b)
    groups = np.asarray(groups)
    uniq = np.unique(groups)
    members = {int(g): np.flatnonzero(groups == g) for g in uniq}
    point = macro(y, pred_b) - macro(y, pred_a)
    draws = []
    for _ in range(N_BOOT):
        chosen = rng.choice(uniq, size=len(uniq), replace=True)
        idx = np.concatenate([members[int(g)] for g in chosen])
        draws.append(macro(y[idx], pred_b[idx]) - macro(y[idx], pred_a[idx]))
    lo, hi = np.percentile(draws, [2.5, 97.5])
    multi = sum(1 for ids in members.values() if len(ids) > 1)
    return {
        "definition": "hybrid minus text; groups drawn with replacement, posts kept together",
        "n_posts": int(len(y)),
        "n_groups": int(len(uniq)),
        "n_multi_post_groups": int(multi),
        "n_posts_in_multi_post_groups": int(sum(len(ids) for ids in members.values() if len(ids) > 1)),
        "point": point,
        "ci95": [float(lo), float(hi)],
        "includes_zero": bool(lo <= 0 <= hi),
        "n_boot": N_BOOT,
        "seed": SEED,
    }


def main() -> int:
    groups = {row["reddit_id"]: int(row["group_id"]) for row in read_jsonl(OOF)}
    thread = read_jsonl(THREAD)
    missing = [row["reddit_id"] for row in thread if row["reddit_id"] not in groups]
    if missing:
        raise SystemExit(f"{len(missing)} thread rows lack a saved group")
    y = [int(row["y_true_s2"]) for row in thread]
    text = [int(row["pred_full_thread_text"]) for row in thread]
    hybrid = [int(row["pred_full_thread_plus_sentiment"]) for row in thread]
    g = [groups[row["reddit_id"]] for row in thread]
    full = group_bootstrap(y, text, hybrid, g)

    pre_rows = read_jsonl(PRE)
    pre = group_bootstrap(
        [int(row["y_true"]) for row in pre_rows],
        [int(row["pred_text_inner_threshold"]) for row in pre_rows],
        [int(row["pred_hybrid_inner_threshold"]) for row in pre_rows],
        [int(row["group_id"]) for row in pre_rows],
    )
    payload = {
        "tests_scored": False,
        "models_refit": False,
        "full_thread_797_group_bootstrap": full,
        "pre_discussion_2050_group_bootstrap": pre,
        "claim_rule": (
            "If a group-level interval includes zero, do not describe the post-level "
            "interval as establishing a reliable difference."
        ),
    }
    OUT.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
