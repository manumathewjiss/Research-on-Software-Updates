"""Paired group bootstrap for VADER added to its matching text input."""

import json
from pathlib import Path

import numpy as np
from sklearn.metrics import f1_score

HERE = Path(__file__).resolve().parent


def load(path):
    with path.open(encoding="utf-8") as stream:
        return {row["reddit_id"]: row for row in map(json.loads, stream)}


expanded = load(HERE.parent / "expanded_study/results/predictions.jsonl")
new = load(HERE / "results/predictions.jsonl")
assert len(expanded) == len(new) == 2050
ids = list(new)
assert set(ids) == set(expanded)
y = np.array([int(new[i]["y_true"]) for i in ids])
group = np.array([int(new[i]["group_id"]) for i in ids])
for i in ids:
    assert int(new[i]["y_true"]) == int(expanded[i]["y_true"])
    assert int(new[i]["fold"]) == int(expanded[i]["fold"])

unique = np.unique(group)
members = {g: np.flatnonzero(group == g) for g in unique}
rng = np.random.default_rng(42)
samples = [np.concatenate([members[g] for g in rng.choice(unique, len(unique), replace=True)]) for _ in range(1000)]
result = {}
for text_arm, plus_arm in (("title", "title_plus_vader"), ("body", "body_plus_vader")):
    before = np.array([int(expanded[i]["pred_" + text_arm]) for i in ids])
    after = np.array([int(new[i]["pred_" + plus_arm]) for i in ids])
    def delta(idx):
        return float(f1_score(y[idx], after[idx], average="macro") - f1_score(y[idx], before[idx], average="macro"))
    point = delta(np.arange(len(ids)))
    lo, hi = np.percentile([delta(s) for s in samples], [2.5, 97.5])
    result[text_arm] = {"point_delta_macro_f1": point, "group_ci95": [float(lo), float(hi)], "includes_zero": bool(lo <= 0 <= hi)}

out = HERE / "results/matched_vader_group_ci.json"
out.write_text(json.dumps({"n": len(ids), "n_groups": len(unique), "seed": 42, "n_boot": 1000, "results": result}, indent=2) + "\n")
print(out.read_text())
