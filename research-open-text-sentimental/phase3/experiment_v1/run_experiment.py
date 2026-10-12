#!/usr/bin/env python3
"""Phase 3 experiment_v1: S2 development CV, model selection, one reserved-test eval."""

from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    average_precision_score,
    balanced_accuracy_score,
    confusion_matrix,
    f1_score,
    precision_recall_fscore_support,
)
from sklearn.model_selection import StratifiedKFold
from sklearn.pipeline import Pipeline
from sklearn.svm import LinearSVC

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"
RESULTS = ROOT / "results"
EXCLUSIONS = RESULTS / "development_exclusions.json"

SEED = 42
N_FOLDS = 5
N_BOOT = 1000
C_GRID = [0.25, 1.0, 4.0]

# Transparent troubleshooting cues (keyword baseline; not from reserved test).
TROUBLE_RE = re.compile(
    r"(?i)\b("
    r"error|bug|crash|broken|fix(?:ed|ing|ure)?|fix(?:s|ed|ing)?|"
    r"not\s+work(?:ing)?|doesn'?t\s+work|won'?t\s+(?:start|boot|launch|open|connect)|"
    r"unable\s+to|can'?t\s+(?:install|update|boot|login|log\s*in|start|open|connect)|"
    r"how\s+(?:do\s+i|to)\b|fix|help\s+(?:with|needed|me)|stuck|workaround|"
    r"after\s+(?:the\s+)?(?:update|upgrade|patch)|post[- ]?(?:update|upgrade)|"
    r"regression|stack\s*trace|exception|segfault|kernel\s+panic|bsod|"
    r"rollback|downgrade|reinstall|compatib|dependency|"
    r"black\s+screen|blank\s+screen|boot\s+loop|won'?t\s+boot"
    r")\b"
)

URL_RE = re.compile(r"https?://\S+|www\.\S+", re.I)


def load_jsonl(path: Path) -> list[dict]:
    rows = []
    with path.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def clean_text(s: str) -> str:
    s = URL_RE.sub(" ", s or "")
    s = re.sub(r"\s+", " ", s).strip().lower()
    return s


def make_text(row: dict, setting: str) -> str:
    title = row.get("title") or ""
    body = row.get("post_body") or ""
    if setting == "title":
        return clean_text(title)
    return clean_text(f"{title}\n{body}")


def eligible_dev(rows: list[dict], exclude_ids: set[str]) -> list[dict]:
    out = []
    for r in rows:
        if not r.get("s2_in_scope"):
            continue
        if r.get("reddit_id") in exclude_ids:
            continue
        if r.get("s2_target") not in (0, 1):
            continue
        out.append(r)
    return out


def eligible_test(rows: list[dict]) -> list[dict]:
    return [r for r in rows if r.get("s2_in_scope") and r.get("s2_target") in (0, 1)]


def keyword_predict(texts: list[str]) -> np.ndarray:
    return np.array([1 if TROUBLE_RE.search(t or "") else 0 for t in texts], dtype=int)


def metrics_bundle(y_true, y_pred, scores=None) -> dict:
    y_true = np.asarray(y_true)
    y_pred = np.asarray(y_pred)
    p, r, f, s = precision_recall_fscore_support(
        y_true, y_pred, labels=[0, 1], zero_division=0
    )
    cm = confusion_matrix(y_true, y_pred, labels=[0, 1]).tolist()
    out = {
        "n": int(len(y_true)),
        "support": {"other_update_0": int(s[0]), "troubleshooting_1": int(s[1])},
        "accuracy": float(accuracy_score(y_true, y_pred)),
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
        "confusion_matrix_labels_[0,1]": cm,
    }
    if scores is not None:
        scores = np.asarray(scores, dtype=float)
        try:
            out["average_precision_troubleshooting"] = float(
                average_precision_score(y_true, scores)
            )
        except ValueError:
            out["average_precision_troubleshooting"] = None
        order = np.argsort(-scores)
        for k in (10, 20):
            if len(order) >= k:
                top = y_true[order[:k]]
                out[f"precision_at_{k}"] = float(top.mean())
            else:
                out[f"precision_at_{k}"] = None
    return out


def bootstrap_ci(y_true, y_pred, metric_fn, n_boot=N_BOOT, seed=SEED):
    rng = np.random.default_rng(seed)
    y_true = np.asarray(y_true)
    y_pred = np.asarray(y_pred)
    n = len(y_true)
    vals = []
    for _ in range(n_boot):
        idx = rng.integers(0, n, n)
        vals.append(metric_fn(y_true[idx], y_pred[idx]))
    lo, hi = np.percentile(vals, [2.5, 97.5])
    return {"point": float(metric_fn(y_true, y_pred)), "ci95": [float(lo), float(hi)]}


def build_lr(C: float) -> Pipeline:
    return Pipeline(
        [
            (
                "tfidf",
                TfidfVectorizer(
                    ngram_range=(1, 2),
                    min_df=2,
                    max_features=20000,
                    sublinear_tf=True,
                ),
            ),
            (
                "clf",
                LogisticRegression(
                    C=C,
                    class_weight="balanced",
                    max_iter=2000,
                    solver="liblinear",
                    random_state=SEED,
                ),
            ),
        ]
    )


def build_svm(C: float) -> Pipeline:
    return Pipeline(
        [
            (
                "tfidf",
                TfidfVectorizer(
                    ngram_range=(1, 2),
                    min_df=2,
                    max_features=20000,
                    sublinear_tf=True,
                ),
            ),
            (
                "clf",
                LinearSVC(
                    C=C,
                    class_weight="balanced",
                    max_iter=5000,
                    random_state=SEED,
                    dual="auto",
                ),
            ),
        ]
    )


def oof_eval(
    name: str,
    texts: list[str],
    y: np.ndarray,
    folds: StratifiedKFold,
    builder=None,
    C=None,
    threshold: float | None = None,
) -> dict:
    n = len(y)
    pred = np.zeros(n, dtype=int)
    scores = np.full(n, np.nan)
    for train_idx, test_idx in folds.split(np.zeros(n), y):
        y_tr = y[train_idx]
        if name == "majority":
            maj = int(Counter(y_tr).most_common(1)[0][0])
            pred[test_idx] = maj
            scores[test_idx] = float(maj)
        elif name == "keyword":
            pred[test_idx] = keyword_predict([texts[i] for i in test_idx])
            scores[test_idx] = pred[test_idx].astype(float)
        else:
            pipe = builder(C)
            X_tr = [texts[i] for i in train_idx]
            X_te = [texts[i] for i in test_idx]
            pipe.fit(X_tr, y_tr)
            if hasattr(pipe.named_steps["clf"], "predict_proba"):
                sc = pipe.predict_proba(X_te)[:, 1]
                thr = 0.5 if threshold is None else threshold
                pr = (sc >= thr).astype(int)
            else:
                sc = pipe.decision_function(X_te)
                thr = 0.0 if threshold is None else threshold
                pr = (sc >= thr).astype(int)
            pred[test_idx] = pr
            scores[test_idx] = sc
    m = metrics_bundle(y, pred, scores)
    m["bootstrap"] = {
        "macro_f1": bootstrap_ci(
            y, pred, lambda a, b: f1_score(a, b, average="macro", zero_division=0)
        ),
        "troubleshooting_f1": bootstrap_ci(
            y,
            pred,
            lambda a, b: f1_score(a, b, pos_label=1, average="binary", zero_division=0),
        ),
    }
    return {
        "model": name,
        "C": C,
        "threshold": threshold,
        "metrics": m,
        "oof_pred": pred,
        "oof_scores": scores,
    }


def by_source(rows, y, pred) -> dict:
    buckets = defaultdict(lambda: {"y": [], "p": []})
    for i, r in enumerate(rows):
        src = r.get("source_pool_audit_only") or "unknown"
        buckets[src]["y"].append(y[i])
        buckets[src]["p"].append(pred[i])
    out = {}
    for src, d in sorted(buckets.items()):
        out[src] = metrics_bundle(d["y"], d["p"])
    return out


def by_text_availability(rows, y, pred) -> dict:
    buckets = defaultdict(lambda: {"y": [], "p": []})
    for i, r in enumerate(rows):
        ta = r.get("text_availability") or "unknown"
        buckets[ta]["y"].append(y[i])
        buckets[ta]["p"].append(pred[i])
    return {k: metrics_bundle(v["y"], v["p"]) for k, v in sorted(buckets.items())}


def selection_key(res: dict) -> tuple:
    m = res["metrics"]
    return (
        m["macro_f1"],
        m["class_1_troubleshooting"]["f1"],
        m["class_1_troubleshooting"]["recall"],
    )


def main() -> int:
    RESULTS.mkdir(parents=True, exist_ok=True)
    excl = json.loads(EXCLUSIONS.read_text(encoding="utf-8"))
    exclude_ids = {
        x["reddit_id"] for x in excl.get("additional_near_duplicate_exclusions", [])
    }

    dev_all = load_jsonl(DATA / "development.jsonl")
    test_all = load_jsonl(DATA / "reserved_test.jsonl")
    dev = eligible_dev(dev_all, exclude_ids)
    test = eligible_test(test_all)

    y_dev = np.array([int(r["s2_target"]) for r in dev])
    folds = StratifiedKFold(n_splits=N_FOLDS, shuffle=True, random_state=SEED)

    # Environment
    freeze = subprocess.check_output(
        [sys.executable, "-m", "pip", "freeze"], text=True
    )
    (RESULTS / "environment.txt").write_text(freeze, encoding="utf-8")

    candidates = []
    all_oof_rows = []

    for text_setting in ("title", "title_body"):
        texts = [make_text(r, text_setting) for r in dev]

        # Majority / keyword (no C)
        for name in ("majority", "keyword"):
            res = oof_eval(name, texts, y_dev, folds)
            entry = {
                "text_setting": text_setting,
                "model": name,
                "C": None,
                "metrics": res["metrics"],
                "selection_score": selection_key(res),
            }
            candidates.append(entry)
            for i, r in enumerate(dev):
                all_oof_rows.append(
                    {
                        "reddit_id": r["reddit_id"],
                        "study_id": r["study_id"],
                        "text_setting": text_setting,
                        "model": name,
                        "C": None,
                        "y_true": int(y_dev[i]),
                        "y_pred": int(res["oof_pred"][i]),
                        "score": float(res["oof_scores"][i]),
                        "source_pool_audit_only": r.get("source_pool_audit_only"),
                    }
                )

        for name, builder in (("tfidf_lr", build_lr), ("tfidf_linear_svm", build_svm)):
            for C in C_GRID:
                res = oof_eval(name, texts, y_dev, folds, builder=builder, C=C)
                entry = {
                    "text_setting": text_setting,
                    "model": name,
                    "C": C,
                    "metrics": res["metrics"],
                    "selection_score": selection_key(res),
                    "_oof_pred": res["oof_pred"],
                    "_oof_scores": res["oof_scores"],
                }
                candidates.append(entry)

    # Rank (drop internal arrays for JSON summary)
    ranked = sorted(
        candidates,
        key=lambda e: e["selection_score"],
        reverse=True,
    )
    summary_ranked = []
    for e in ranked:
        summary_ranked.append(
            {
                "text_setting": e["text_setting"],
                "model": e["model"],
                "C": e["C"],
                "macro_f1": e["metrics"]["macro_f1"],
                "troubleshooting_f1": e["metrics"]["class_1_troubleshooting"]["f1"],
                "troubleshooting_recall": e["metrics"]["class_1_troubleshooting"][
                    "recall"
                ],
                "other_f1": e["metrics"]["class_0_other_update"]["f1"],
                "balanced_accuracy": e["metrics"]["balanced_accuracy"],
                "bootstrap": e["metrics"].get("bootstrap"),
            }
        )

    best = ranked[0]
    # Prefer a learned model if majority/keyword somehow wins with weak minority F1 —
    # protocol says pick by macro-F1; keep that.

    # Recompute OOF arrays for best for breakdowns
    texts_best = [make_text(r, best["text_setting"]) for r in dev]
    if best["model"] == "majority":
        best_res = oof_eval("majority", texts_best, y_dev, folds)
    elif best["model"] == "keyword":
        best_res = oof_eval("keyword", texts_best, y_dev, folds)
    elif best["model"] == "tfidf_lr":
        best_res = oof_eval(
            "tfidf_lr", texts_best, y_dev, folds, builder=build_lr, C=best["C"]
        )
    else:
        best_res = oof_eval(
            "tfidf_linear_svm",
            texts_best,
            y_dev,
            folds,
            builder=build_svm,
            C=best["C"],
        )

    # Optional threshold sweep on OOF for best model only (before reserved test)
    scores = best_res["oof_scores"]
    thr_default = 0.5 if best["model"] == "tfidf_lr" else 0.0
    if best["model"] in ("tfidf_lr", "tfidf_linear_svm") and np.isfinite(scores).all():
        best_thr = thr_default
        best_macro = best_res["metrics"]["macro_f1"]
        qs = np.unique(np.quantile(scores, np.linspace(0.05, 0.95, 37)))
        for thr in qs:
            pred_t = (scores >= thr).astype(int)
            mf = f1_score(y_dev, pred_t, average="macro", zero_division=0)
            if mf > best_macro + 1e-12:
                best_macro = mf
                best_thr = float(thr)
        chosen_threshold = float(best_thr)
        chosen_pred = (scores >= chosen_threshold).astype(int)
        chosen_metrics = metrics_bundle(y_dev, chosen_pred, scores)
        chosen_metrics["bootstrap"] = {
            "macro_f1": bootstrap_ci(
                y_dev,
                chosen_pred,
                lambda a, b: f1_score(a, b, average="macro", zero_division=0),
            ),
            "troubleshooting_f1": bootstrap_ci(
                y_dev,
                chosen_pred,
                lambda a, b: f1_score(
                    a, b, pos_label=1, average="binary", zero_division=0
                ),
            ),
        }
    else:
        chosen_threshold = thr_default if best["model"] in ("tfidf_lr", "tfidf_linear_svm") else None
        chosen_pred = best_res["oof_pred"]
        chosen_metrics = best_res["metrics"]

    selection = {
        "selection_metric": "macro_f1_then_troubleshooting_f1_then_troubleshooting_recall",
        "chosen": {
            "text_setting": best["text_setting"],
            "model": best["model"],
            "C": best["C"],
            "threshold": chosen_threshold,
            "oof_metrics": chosen_metrics,
            "oof_by_source": by_source(dev, y_dev, chosen_pred),
            "oof_by_text_availability": by_text_availability(dev, y_dev, chosen_pred),
        },
        "ranked_candidates": summary_ranked,
        "n_development_s2": len(dev),
        "excluded_reddit_ids": sorted(exclude_ids),
        "class_counts_dev": {
            "troubleshooting_1": int((y_dev == 1).sum()),
            "other_update_0": int((y_dev == 0).sum()),
        },
    }

    # Append OOF for chosen config for all_oof if learned
    for i, r in enumerate(dev):
        all_oof_rows.append(
            {
                "reddit_id": r["reddit_id"],
                "study_id": r["study_id"],
                "text_setting": best["text_setting"],
                "model": f"CHOSEN_{best['model']}",
                "C": best["C"],
                "threshold": chosen_threshold,
                "y_true": int(y_dev[i]),
                "y_pred": int(chosen_pred[i]),
                "score": float(scores[i]) if np.isfinite(scores[i]) else None,
                "source_pool_audit_only": r.get("source_pool_audit_only"),
            }
        )

    with (RESULTS / "development_oof_predictions.jsonl").open("w", encoding="utf-8") as f:
        for row in all_oof_rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")

    (RESULTS / "model_selection.json").write_text(
        json.dumps(selection, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )

    # --- Reserved test: ONE evaluation ---
    texts_dev = [make_text(r, best["text_setting"]) for r in dev]
    texts_test = [make_text(r, best["text_setting"]) for r in test]
    y_test = np.array([int(r["s2_target"]) for r in test])

    if best["model"] == "majority":
        maj = int(Counter(y_dev).most_common(1)[0][0])
        test_pred = np.full(len(test), maj, dtype=int)
        test_scores = test_pred.astype(float)
    elif best["model"] == "keyword":
        test_pred = keyword_predict(texts_test)
        test_scores = test_pred.astype(float)
    elif best["model"] == "tfidf_lr":
        pipe = build_lr(best["C"])
        pipe.fit(texts_dev, y_dev)
        test_scores = pipe.predict_proba(texts_test)[:, 1]
        test_pred = (test_scores >= chosen_threshold).astype(int)
    else:
        pipe = build_svm(best["C"])
        pipe.fit(texts_dev, y_dev)
        test_scores = pipe.decision_function(texts_test)
        test_pred = (test_scores >= chosen_threshold).astype(int)

    test_metrics = metrics_bundle(y_test, test_pred, test_scores)
    test_metrics["bootstrap"] = {
        "macro_f1": bootstrap_ci(
            y_test,
            test_pred,
            lambda a, b: f1_score(a, b, average="macro", zero_division=0),
        ),
        "troubleshooting_f1": bootstrap_ci(
            y_test,
            test_pred,
            lambda a, b: f1_score(a, b, pos_label=1, average="binary", zero_division=0),
        ),
    }

    reserved_report = {
        "evaluated_once": True,
        "protocol": "PROTOCOL.md",
        "chosen_config": {
            "text_setting": best["text_setting"],
            "model": best["model"],
            "C": best["C"],
            "threshold": chosen_threshold,
        },
        "n_reserved_s2": len(test),
        "class_counts_test": {
            "troubleshooting_1": int((y_test == 1).sum()),
            "other_update_0": int((y_test == 0).sum()),
        },
        "metrics": test_metrics,
        "by_source": by_source(test, y_test, test_pred),
        "by_text_availability": by_text_availability(test, y_test, test_pred),
        "input_hashes": {
            "development.jsonl": sha256_file(DATA / "development.jsonl"),
            "reserved_test.jsonl": sha256_file(DATA / "reserved_test.jsonl"),
        },
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
    }

    with (RESULTS / "reserved_test_predictions.jsonl").open("w", encoding="utf-8") as f:
        for i, r in enumerate(test):
            f.write(
                json.dumps(
                    {
                        "reddit_id": r["reddit_id"],
                        "study_id": r["study_id"],
                        "y_true": int(y_test[i]),
                        "y_pred": int(test_pred[i]),
                        "score": float(test_scores[i]),
                        "source_pool_audit_only": r.get("source_pool_audit_only"),
                        "discussion_type": r.get("discussion_type"),
                        "title": r.get("title"),
                    },
                    ensure_ascii=False,
                )
                + "\n"
            )

    (RESULTS / "reserved_test_metrics.json").write_text(
        json.dumps(reserved_report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )

    print(
        json.dumps(
            {
                "dev_n": len(dev),
                "test_n": len(test),
                "chosen": selection["chosen"],
                "test_macro_f1": test_metrics["macro_f1"],
                "test_troubleshooting_f1": test_metrics["class_1_troubleshooting"]["f1"],
            },
            indent=2,
            default=str,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
