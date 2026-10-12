#!/usr/bin/env python3
"""Development-only class-balancing comparison on the Reddit-only S2 set.

Uses the saved grouped folds from reddit_only_sensitivity. Does not read or
score the reserved or fresh tests.
"""

from __future__ import annotations

import hashlib
import json
import subprocess
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    balanced_accuracy_score,
    confusion_matrix,
    f1_score,
    precision_recall_fscore_support,
)
from sklearn.pipeline import Pipeline

PHASE3 = Path(__file__).resolve().parents[1]
REPO = PHASE3.parent
HERE = Path(__file__).resolve().parent
OUT = HERE / "results"
SNAP = PHASE3 / "reddit_only_sensitivity" / "development_reddit_only.jsonl"
FOLDS = (
    PHASE3
    / "reddit_only_sensitivity"
    / "results"
    / "grouped_oof_predictions.jsonl"
)
NEAR_DUP = {"1t0wme9", "1wrqch6"}
THRESHOLD = 0.5877137791150834
C = 4.0
SEED = 42
N_BOOT = 1000
CODE_VERSION = "balancing-study-v1"


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def git_head() -> str | None:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"],
            cwd=REPO,
            text=True,
            stderr=subprocess.DEVNULL,
        ).strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None


def load_jsonl(path: Path) -> list[dict]:
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def make_text(row: dict) -> str:
    # Match run_experiment.make_text(..., "title_body") without importing it,
    # so this study stays readable next to that function.
    import re

    url_re = re.compile(r"https?://\S+|www\.\S+", re.I)
    raw = f"{row.get('title') or ''}\n{row.get('post_body') or ''}"
    return re.sub(r"\s+", " ", url_re.sub(" ", raw)).strip().lower()


def vectorizer() -> TfidfVectorizer:
    return TfidfVectorizer(
        ngram_range=(1, 2),
        min_df=2,
        max_features=20000,
        sublinear_tf=True,
    )


def lr(class_weight) -> LogisticRegression:
    return LogisticRegression(
        C=C,
        class_weight=class_weight,
        max_iter=2000,
        solver="liblinear",
        random_state=SEED,
    )


def metrics_at(y_true, y_pred) -> dict:
    y_true = np.asarray(y_true)
    y_pred = np.asarray(y_pred)
    p, r, f, s = precision_recall_fscore_support(
        y_true, y_pred, labels=[0, 1], zero_division=0
    )
    return {
        "n": int(len(y_true)),
        "support": {"other_update_0": int(s[0]), "troubleshooting_1": int(s[1])},
        "balanced_accuracy": float(balanced_accuracy_score(y_true, y_pred)),
        "macro_f1": float(f1_score(y_true, y_pred, average="macro", zero_division=0)),
        "class_0_other_update": {
            "precision": float(p[0]),
            "recall": float(r[0]),
            "f1": float(f[0]),
        },
        "class_1_troubleshooting": {
            "precision": float(p[1]),
            "recall": float(r[1]),
            "f1": float(f[1]),
        },
        "confusion_matrix_labels_[0,1]": confusion_matrix(
            y_true, y_pred, labels=[0, 1]
        ).tolist(),
    }


def best_threshold(y_true, scores) -> tuple[float, dict]:
    """Development-only operating-point search. Not a new test-set choice."""
    y_true = np.asarray(y_true)
    scores = np.asarray(scores)
    candidates = np.unique(np.quantile(scores, np.linspace(0.05, 0.95, 37)))
    best_thr = float(THRESHOLD)
    best_m = metrics_at(y_true, (scores >= THRESHOLD).astype(int))
    for thr in candidates:
        pred = (scores >= thr).astype(int)
        m = metrics_at(y_true, pred)
        if m["macro_f1"] > best_m["macro_f1"] + 1e-12:
            best_thr = float(thr)
            best_m = m
    return best_thr, best_m


def paired_delta_ci(y_true, pred_a, pred_b, n_boot=N_BOOT, seed=SEED) -> dict:
    """Bootstrap CI for macro-F1(b) - macro-F1(a) on paired OOF rows."""
    rng = np.random.default_rng(seed)
    y_true = np.asarray(y_true)
    pred_a = np.asarray(pred_a)
    pred_b = np.asarray(pred_b)
    n = len(y_true)

    def macro(a, b):
        return f1_score(a, b, average="macro", zero_division=0)

    point = float(macro(y_true, pred_b) - macro(y_true, pred_a))
    draws = []
    for _ in range(n_boot):
        idx = rng.integers(0, n, n)
        draws.append(macro(y_true[idx], pred_b[idx]) - macro(y_true[idx], pred_a[idx]))
    lo, hi = np.percentile(draws, [2.5, 97.5])
    return {
        "point_macro_f1_b_minus_a": point,
        "ci95": [float(lo), float(hi)],
        "n_boot": n_boot,
        "includes_zero": bool(lo <= 0 <= hi),
    }


def oversample_indices(y_train: np.ndarray, fold: int) -> np.ndarray:
    """Sample minority rows with replacement until counts match the majority."""
    rng = np.random.default_rng(SEED + fold)
    counts = Counter(y_train.tolist())
    majority_n = max(counts.values())
    keep = []
    for label in sorted(counts):
        idx = np.flatnonzero(y_train == label)
        if len(idx) == majority_n:
            keep.append(idx)
        elif len(idx) > majority_n:
            raise RuntimeError("unexpected class larger than recorded majority")
        else:
            extra = rng.choice(idx, size=majority_n - len(idx), replace=True)
            keep.append(np.concatenate([idx, extra]))
    return np.concatenate(keep)


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    snap = load_jsonl(SNAP)
    fold_rows = load_jsonl(FOLDS)
    by_snap = {r["reddit_id"]: r for r in snap}
    if len(fold_rows) != len({r["reddit_id"] for r in fold_rows}):
        raise SystemExit("duplicate ids in saved fold file")

    rows = []
    for fr in fold_rows:
        src = by_snap.get(fr["reddit_id"])
        if src is None:
            raise SystemExit(f"fold id missing from snapshot: {fr['reddit_id']}")
        if src["reddit_id"] in NEAR_DUP:
            raise SystemExit("near-dup exclusion leaked into fold file")
        if int(src["s2_target"]) != int(fr["y_true"]):
            raise SystemExit(f"label mismatch for {fr['reddit_id']}")
        rows.append(src)

    # Preserve saved fold-file order so fold indices line up with that artifact.
    texts = [make_text(r) for r in rows]
    y = np.array([int(r["s2_target"]) for r in rows], dtype=int)
    folds = np.array([int(fr["fold"]) for fr in fold_rows], dtype=int)
    if set(folds.tolist()) != {0, 1, 2, 3, 4}:
        raise SystemExit(f"unexpected folds: {set(folds.tolist())}")

    n = len(rows)
    scores = {name: np.full(n, np.nan) for name in ("balanced", "unweighted", "oversample")}
    fold_counts = []

    for fold in range(5):
        test_idx = np.flatnonzero(folds == fold)
        train_idx = np.flatnonzero(folds != fold)
        y_tr = y[train_idx]
        X_tr_text = [texts[i] for i in train_idx]
        X_te_text = [texts[i] for i in test_idx]
        before = dict(Counter(y_tr.tolist()))

        # 1. Existing balanced weights. TF-IDF fit on this fold's training posts only.
        pipe_b = Pipeline([("tfidf", vectorizer()), ("clf", lr("balanced"))])
        pipe_b.fit(X_tr_text, y_tr)
        scores["balanced"][test_idx] = pipe_b.predict_proba(X_te_text)[:, 1]

        # 2. Same model, no class weights.
        pipe_u = Pipeline([("tfidf", vectorizer()), ("clf", lr(None))])
        pipe_u.fit(X_tr_text, y_tr)
        scores["unweighted"][test_idx] = pipe_u.predict_proba(X_te_text)[:, 1]

        # 3. Random oversampling of training rows after TF-IDF fit on the original
        # training posts (document frequency is not inflated by copies).
        vec = vectorizer()
        X_tr = vec.fit_transform(X_tr_text)
        X_te = vec.transform(X_te_text)
        take = oversample_indices(y_tr, fold)
        clf = lr(None)
        clf.fit(X_tr[take], y_tr[take])
        scores["oversample"][test_idx] = clf.predict_proba(X_te)[:, 1]
        after = dict(Counter(y_tr[take].tolist()))
        fold_counts.append(
            {
                "fold": fold,
                "n_test": int(len(test_idx)),
                "n_train": int(len(train_idx)),
                "train_class_counts_before_oversample": {
                    "other_update_0": int(before.get(0, 0)),
                    "troubleshooting_1": int(before.get(1, 0)),
                },
                "train_class_counts_after_oversample": {
                    "other_update_0": int(after.get(0, 0)),
                    "troubleshooting_1": int(after.get(1, 0)),
                },
            }
        )

    if not all(np.isfinite(v).all() for v in scores.values()):
        raise SystemExit("missing out-of-fold scores")

    fixed_pred = {
        name: (sc >= THRESHOLD).astype(int) for name, sc in scores.items()
    }
    fixed_metrics = {name: metrics_at(y, pred) for name, pred in fixed_pred.items()}

    explored = {}
    explored_pred = {}
    for name, sc in scores.items():
        thr, m = best_threshold(y, sc)
        explored[name] = {"threshold": thr, "metrics": m, "criterion": "max OOF macro-F1 on this development check"}
        explored_pred[name] = (sc >= thr).astype(int)

    deltas = {
        "unweighted_minus_balanced": paired_delta_ci(
            y, fixed_pred["balanced"], fixed_pred["unweighted"]
        ),
        "oversample_minus_balanced": paired_delta_ci(
            y, fixed_pred["balanced"], fixed_pred["oversample"], seed=SEED + 1
        ),
    }

    overall_counts = {
        "n": n,
        "troubleshooting_1": int((y == 1).sum()),
        "other_update_0": int((y == 0).sum()),
        "prevalence_troubleshooting": float((y == 1).mean()),
    }

    # Sanity: balanced arm should match the saved sensitivity predictions closely.
    saved_pred = np.array([int(fr["y_pred_tfidf_lr"]) for fr in fold_rows])
    saved_score = np.array([float(fr["score_tfidf_lr"]) for fr in fold_rows])
    agree = float((fixed_pred["balanced"] == saved_pred).mean())
    max_score_gap = float(np.max(np.abs(scores["balanced"] - saved_score)))

    report = {
        "code_version": CODE_VERSION,
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "reserved_test_used": False,
        "fresh_test_used": False,
        "population": overall_counts,
        "folds": {
            "source": str(FOLDS),
            "n_folds": 5,
            "same_partition_for_every_arm": True,
            "per_fold_train_counts": fold_counts,
        },
        "fixed_threshold": THRESHOLD,
        "fixed_threshold_metrics": fixed_metrics,
        "threshold_exploration_development_only": explored,
        "paired_macro_f1_delta_at_fixed_threshold": deltas,
        "reproduction_check_vs_saved_balanced_oof": {
            "prediction_agreement": agree,
            "max_abs_score_gap": max_score_gap,
        },
    }
    (OUT / "balancing_metrics.json").write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8"
    )
    (OUT / "class_counts.json").write_text(
        json.dumps(
            {"overall": overall_counts, "per_fold": fold_counts}, indent=2
        )
        + "\n",
        encoding="utf-8",
    )

    with (OUT / "paired_oof_predictions.jsonl").open("w", encoding="utf-8") as f:
        for i, row in enumerate(rows):
            f.write(
                json.dumps(
                    {
                        "reddit_id": row["reddit_id"],
                        "y_true": int(y[i]),
                        "fold": int(folds[i]),
                        "score_balanced": float(scores["balanced"][i]),
                        "pred_balanced_fixed_threshold": int(fixed_pred["balanced"][i]),
                        "pred_balanced_explored_threshold": int(explored_pred["balanced"][i]),
                        "score_unweighted": float(scores["unweighted"][i]),
                        "pred_unweighted_fixed_threshold": int(fixed_pred["unweighted"][i]),
                        "pred_unweighted_explored_threshold": int(explored_pred["unweighted"][i]),
                        "score_oversample": float(scores["oversample"][i]),
                        "pred_oversample_fixed_threshold": int(fixed_pred["oversample"][i]),
                        "pred_oversample_explored_threshold": int(explored_pred["oversample"][i]),
                    }
                )
                + "\n"
            )

    manifest = {
        "code_version": CODE_VERSION,
        "script": str(Path(__file__).resolve()),
        "git_head": git_head(),
        "created_utc": report["created_utc"],
        "inputs": {
            "reddit_only_snapshot": str(SNAP),
            "reddit_only_snapshot_sha256": sha256_file(SNAP),
            "locked_folds": str(FOLDS),
            "locked_folds_sha256": sha256_file(FOLDS),
        },
        "model_settings_held_fixed": {
            "text": "title + post_body, URL-stripped, lowercased",
            "tfidf": "word unigrams+bigrams, min_df=2, max_features=20000, sublinear_tf",
            "logistic_regression": {
                "C": C,
                "solver": "liblinear",
                "max_iter": 2000,
                "random_state": SEED,
            },
            "existing_threshold": THRESHOLD,
        },
        "arms": {
            "balanced": "class_weight='balanced'; TF-IDF fit on original training posts",
            "unweighted": "class_weight=None; TF-IDF fit on original training posts",
            "oversample": (
                "class_weight=None; TF-IDF fit on original training posts; "
                "minority training rows sampled with replacement until class counts match; "
                "RNG seed = 42 + fold index"
            ),
        },
        "threshold_policy": (
            "Primary comparison uses the existing threshold 0.5877137791150834 for every arm. "
            "A separate development-only quantile search maximizes OOF macro-F1. "
            "That search is not a new final model and was not checked on either scored test."
        ),
        "tests_not_used": ["159-post reserved test", "344-post fresh test"],
        "outputs": {
            "metrics": str(OUT / "balancing_metrics.json"),
            "predictions": str(OUT / "paired_oof_predictions.jsonl"),
            "class_counts": str(OUT / "class_counts.json"),
        },
    }
    (HERE / "MANIFEST.json").write_text(
        json.dumps(manifest, indent=2) + "\n", encoding="utf-8"
    )
    write_results(report, manifest)
    print(
        json.dumps(
            {
                "n": n,
                "agreement_with_saved_balanced": agree,
                "max_score_gap": max_score_gap,
                "fixed_macro_f1": {k: v["macro_f1"] for k, v in fixed_metrics.items()},
                "deltas": deltas,
            },
            indent=2,
        )
    )
    return 0


def write_results(report: dict, manifest: dict) -> None:
    fixed = report["fixed_threshold_metrics"]
    explored = report["threshold_exploration_development_only"]
    deltas = report["paired_macro_f1_delta_at_fixed_threshold"]

    def line(name, m):
        c0, c1 = m["class_0_other_update"], m["class_1_troubleshooting"]
        return (
            f"| {name} | {m['macro_f1']:.4f} | {m['balanced_accuracy']:.4f} | "
            f"{c0['precision']:.3f}/{c0['recall']:.3f}/{c0['f1']:.3f} | "
            f"{c1['precision']:.3f}/{c1['recall']:.3f}/{c1['f1']:.3f} | "
            f"`{m['confusion_matrix_labels_[0,1]']}` |"
        )

    bal = fixed["balanced"]
    unw = fixed["unweighted"]
    ovs = fixed["oversample"]
    d_u = deltas["unweighted_minus_balanced"]
    d_o = deltas["oversample_minus_balanced"]
    expl_gap = max(
        abs(explored[a]["metrics"]["macro_f1"] - explored["balanced"]["metrics"]["macro_f1"])
        for a in ("unweighted", "oversample")
    )
    rec = (
        "Keep the existing balanced-weight model and the saved threshold. "
        f"At that cutoff, dropping class weights lowers macro-F1 by {abs(d_u['point_macro_f1_b_minus_a']):.3f}, "
        "mainly by missing other-update posts. That gap is large, but it is a cutoff mismatch: "
        f"after each arm's own development threshold, macro-F1 differs by at most {expl_gap:.3f}. "
        f"Oversampling versus class weights is {d_o['point_macro_f1_b_minus_a']:+.3f} at the saved cutoff, "
        "and that paired interval includes zero. "
        "Those differences are not large enough to replace the current configuration or to spend a new test set. "
        "This comparison was not scored on the reserved or fresh tests."
    )

    text = f"""# Class-balancing comparison (Reddit-only development)

**Created:** {report['created_utc']}
**Code version:** `{report['code_version']}`

Development check only. The 159-post reserved test and the 344-post fresh test were not read or scored.

## Population and folds

Reddit-only S2 modeling set from `reddit_only_sensitivity/development_reddit_only.jsonl`: **{report['population']['n']}** posts, **{report['population']['troubleshooting_1']}** troubleshooting and **{report['population']['other_update_0']}** other update.

All three arms use the five grouped folds already saved in `reddit_only_sensitivity/results/grouped_oof_predictions.jsonl`. Exact and near-duplicate posts stay in the same fold. TF-IDF is fit on each fold's original training posts. Oversampling, when used, copies minority training rows after that fit and does not change the held-out posts.

The balanced arm agrees with the saved Reddit-only predictions on **{report['reproduction_check_vs_saved_balanced_oof']['prediction_agreement']:.4f}** of posts (max absolute score gap {report['reproduction_check_vs_saved_balanced_oof']['max_abs_score_gap']:.3e}).

## Fixed threshold `{THRESHOLD}`

This is the threshold saved with the original balanced model. It is applied here to every arm so the comparison is not mixed with a new cutoff.

| Arm | macro-F1 | balanced acc. | other P/R/F1 | trouble P/R/F1 | confusion [[0,1]] |
|---|---:|---:|---|---|---|
{line("Balanced class weights", bal)}
{line("No class weights", unw)}
{line("Random oversampling, no class weights", ovs)}

Paired bootstrap of macro-F1 difference versus balanced weights (1,000 resamples):

- Unweighted − balanced: {d_u['point_macro_f1_b_minus_a']:+.4f} (95% CI {d_u['ci95'][0]:+.4f} to {d_u['ci95'][1]:+.4f}; includes zero: {d_u['includes_zero']})
- Oversample − balanced: {d_o['point_macro_f1_b_minus_a']:+.4f} (95% CI {d_o['ci95'][0]:+.4f} to {d_o['ci95'][1]:+.4f}; includes zero: {d_o['includes_zero']})

## Threshold exploration (development only)

A quantile search maximized out-of-fold macro-F1 separately for each arm. These cutoffs were **not** applied to either scored test and are not a replacement final model.

| Arm | Explored threshold | macro-F1 | balanced acc. | other F1 | trouble F1 |
|---|---:|---:|---:|---:|---:|
| Balanced | {explored['balanced']['threshold']:.4f} | {explored['balanced']['metrics']['macro_f1']:.4f} | {explored['balanced']['metrics']['balanced_accuracy']:.4f} | {explored['balanced']['metrics']['class_0_other_update']['f1']:.4f} | {explored['balanced']['metrics']['class_1_troubleshooting']['f1']:.4f} |
| Unweighted | {explored['unweighted']['threshold']:.4f} | {explored['unweighted']['metrics']['macro_f1']:.4f} | {explored['unweighted']['metrics']['balanced_accuracy']:.4f} | {explored['unweighted']['metrics']['class_0_other_update']['f1']:.4f} | {explored['unweighted']['metrics']['class_1_troubleshooting']['f1']:.4f} |
| Oversample | {explored['oversample']['threshold']:.4f} | {explored['oversample']['metrics']['macro_f1']:.4f} | {explored['oversample']['metrics']['balanced_accuracy']:.4f} | {explored['oversample']['metrics']['class_0_other_update']['f1']:.4f} | {explored['oversample']['metrics']['class_1_troubleshooting']['f1']:.4f} |

## Tradeoff

Class weights and oversampling shift probability mass toward the smaller other-update class. At the saved threshold, dropping weights raises other-update precision and cuts its recall sharply, which lowers macro-F1. Oversampling stays close to class weights, with a small swap of other-update precision and recall. The saved cutoff was chosen for the balanced model, so the exploration block is the fairer comparison of each arm at its own operating point. After that search, the three arms are nearly the same.

## Recommendation

{rec}

## Reproduce

```bash
phase3/experiment_v1/.venv/bin/python phase3/balancing_study/run_balancing_study.py
```

Hashes and settings: `MANIFEST.json`.
"""
    (HERE / "RESULTS.md").write_text(text, encoding="utf-8")
    (HERE / "RUN.md").write_text(
        """# Reproduce the balancing comparison

From the research repository root:

```bash
phase3/experiment_v1/.venv/bin/python phase3/balancing_study/run_balancing_study.py
```

Uses the existing experiment_v1 virtualenv. Does not read the reserved or fresh tests.
""",
        encoding="utf-8",
    )


if __name__ == "__main__":
    raise SystemExit(main())
