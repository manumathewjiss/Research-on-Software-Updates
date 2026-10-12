#!/usr/bin/env python3
"""Descriptive, exploratory valence slices for VADER and SentiStrength-SE."""

import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
sys.path.insert(0, str(REPO / "phase5" / "expanded_study"))
import run_expanded as ex  # noqa: E402


def main():
    rows, _, _, groups, population = ex.load_population()
    scores = ex.read_jsonl(HERE / "results" / "sentistrength_se_predictions.jsonl")
    if [r["reddit_id"] for r in rows] != [r["reddit_id"] for r in scores]:
        raise SystemExit("ID or row order mismatch")
    se = np.array([float(r["polarity_sum"]) for r in scores])
    vader, _ = ex.vader_scores(rows)
    kind = np.array([r["discussion_type"] for r in rows])
    labels = ("technical_troubleshooting", "general_dissatisfaction", "other")
    out = {"population": population, "exploratory_after_tool_comparison": True,
           "scores": {}, "n_boot": 1000, "seed": 42}
    uniq = np.unique(groups)
    members = {int(g): np.flatnonzero(groups == g) for g in uniq}
    rng = np.random.default_rng(42)
    for name, values in (("vader_compound", vader), ("sentistrength_se_sum", se)):
        summary = {label: {"n": int(np.sum(kind == label)),
                           "mean": float(np.mean(values[kind == label])),
                           "median": float(np.median(values[kind == label]))}
                   for label in labels}
        diff = summary["technical_troubleshooting"]["mean"] - summary["general_dissatisfaction"]["mean"]
        draws = []
        for _ in range(1000):
            chosen = rng.choice(uniq, size=len(uniq), replace=True)
            ix = np.concatenate([members[int(g)] for g in chosen])
            a, b = kind[ix] == labels[0], kind[ix] == labels[1]
            if a.any() and b.any():
                draws.append(float(np.mean(values[ix][a]) - np.mean(values[ix][b])))
        out["scores"][name] = {
            "groups": summary,
            "troubleshooting_minus_dissatisfaction_mean": float(diff),
            "duplicate_group_bootstrap_ci95": [float(v) for v in np.percentile(draws, [2.5, 97.5])],
            "n_valid_draws": len(draws),
        }
    ex.write_json(HERE / "results" / "sentistrength_se_subgroup.json", out)
    print(out["scores"])


if __name__ == "__main__":
    main()
