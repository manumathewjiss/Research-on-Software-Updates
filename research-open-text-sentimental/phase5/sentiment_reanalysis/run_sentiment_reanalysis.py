#!/usr/bin/env python3
"""Bounded VADER reanalysis on saved development folds.

Does not read or score the reserved or fresh tests, and does not write
outside phase5/sentiment_reanalysis/.
"""

from __future__ import annotations

import csv
import hashlib
import json
import platform
import subprocess
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
from scipy import stats
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    average_precision_score,
    balanced_accuracy_score,
    confusion_matrix,
    f1_score,
    precision_recall_fscore_support,
)
from sklearn.model_selection import StratifiedGroupKFold
from sklearn.preprocessing import StandardScaler
from scipy.sparse import csr_matrix, hstack

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
PHASE3 = REPO / "phase3"
sys.path.insert(0, str(HERE / "vendor"))
sys.path.insert(0, str(PHASE3 / "experiment_v1"))
sys.path.insert(0, str(PHASE3 / "experiment_v1" / "followup"))
sys.path.insert(0, str(REPO))

from run_experiment import build_lr, make_text  # noqa: E402
from run_followup import audit_within_dev  # noqa: E402
from trajectory.build import (  # noqa: E402
    analyze_post_trajectories,
    compute_metrics_row,
    load_raw_posts_by_id,
)
from trajectory.sentiment import compound_score  # noqa: E402
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer  # noqa: E402
import vaderSentiment  # noqa: E402

REDDIT_DEV = PHASE3 / "reddit_only_sensitivity" / "development_reddit_only.jsonl"
REDDIT_OOF = PHASE3 / "reddit_only_sensitivity" / "results" / "grouped_oof_predictions.jsonl"
MIXED_DEV = PHASE3 / "revised_development_v2" / "development_v2.jsonl"
MIXED_OOF = PHASE3 / "diagnostic_results" / "grouped_oof_predictions.jsonl"
C1_METRICS = REPO / "data" / "c1_prime" / "c1_prime_metrics.csv"
RAW_DIR = REPO / "tps_gds_classification" / "data" / "raw"
LABELS = REPO / "tps_gds_classification" / "data" / "updated_labeled_dataset_unique.csv"
SAVED_DIVERGENCE = REPO / "analysis" / "outputs" / "c1_prime_divergence" / "divergence_report_full.md"
OUT = HERE / "results"

THRESHOLD = 0.5877137791150834
C = 4.0
SEED = 42
N_OUTER = 5
N_INNER = 3
N_BOOT = 1000
# Same grid already used for inner grouped threshold selection in
# phase3/semantic_comparator. Fixed before any outer score is inspected.
THRESHOLD_GRID = [round(x, 2) for x in np.linspace(0.20, 0.80, 13)]
NEAR_DUP = {"1t0wme9", "1wrqch6"}
CODE_VERSION = "sentiment-reanalysis-v1"
SCORE_TOL = 1e-6


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


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


def read_jsonl(path: Path) -> list[dict]:
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            rows.append(json.loads(line))
    return rows


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def write_jsonl(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows),
        encoding="utf-8",
    )


def lr_head() -> LogisticRegression:
    return LogisticRegression(
        C=C,
        class_weight="balanced",
        max_iter=2000,
        solver="liblinear",
        random_state=SEED,
    )


def metrics_at(y_true, y_pred, scores=None) -> dict:
    y_true = np.asarray(y_true)
    y_pred = np.asarray(y_pred)
    p, r, f, s = precision_recall_fscore_support(
        y_true, y_pred, labels=[0, 1], zero_division=0
    )
    out = {
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
    if scores is not None:
        out["average_precision_troubleshooting"] = float(
            average_precision_score(y_true, scores)
        )
    return out


def choose_threshold(pieces: list[tuple[np.ndarray, np.ndarray]]) -> dict:
    best = None
    table = []
    for thr in THRESHOLD_GRID:
        macros, others = [], []
        for y_val, proba in pieces:
            pred = (proba >= thr).astype(int)
            macros.append(f1_score(y_val, pred, average="macro", zero_division=0))
            others.append(f1_score(y_val, pred, pos_label=0, average="binary", zero_division=0))
        row = {
            "threshold": thr,
            "mean_inner_macro_f1": float(np.mean(macros)),
            "mean_inner_other_f1": float(np.mean(others)),
        }
        table.append(row)
        key = (row["mean_inner_macro_f1"], row["mean_inner_other_f1"], -abs(thr - 0.5))
        if best is None or key > best[0]:
            best = (key, row)
    return {"threshold": best[1]["threshold"], "selected": best[1], "grid": table}


def inner_pieces(y_tr, groups_tr, fit_val_proba):
    splitter = StratifiedGroupKFold(n_splits=N_INNER, shuffle=True, random_state=SEED)
    pieces = []
    for tr, va in splitter.split(np.zeros(len(y_tr)), y_tr, groups_tr):
        pieces.append((y_tr[va], fit_val_proba(tr, va)))
    return pieces


def text_proba(texts_tr, y_tr, texts_va) -> np.ndarray:
    pipe = build_lr(C)
    pipe.fit(texts_tr, y_tr)
    return pipe.predict_proba(texts_va)[:, 1]


def sentiment_proba(comp_tr, y_tr, comp_va) -> np.ndarray:
    scaler = StandardScaler()
    z_tr = scaler.fit_transform(np.asarray(comp_tr, dtype=float).reshape(-1, 1))
    clf = lr_head()
    clf.fit(z_tr, y_tr)
    if list(clf.classes_) != [0, 1]:
        raise SystemExit(f"sentiment classes {clf.classes_}")
    z_va = scaler.transform(np.asarray(comp_va, dtype=float).reshape(-1, 1))
    return clf.predict_proba(z_va)[:, 1]


def hybrid_proba(texts_tr, comp_tr, y_tr, texts_va, comp_va) -> tuple[np.ndarray, float]:
    pipe = build_lr(C)
    pipe.fit(texts_tr, y_tr)
    x_tr = pipe.named_steps["tfidf"].transform(texts_tr)
    x_va = pipe.named_steps["tfidf"].transform(texts_va)
    scaler = StandardScaler()
    z_tr = scaler.fit_transform(np.asarray(comp_tr, dtype=float).reshape(-1, 1))
    z_va = scaler.transform(np.asarray(comp_va, dtype=float).reshape(-1, 1))
    clf = lr_head()
    clf.fit(hstack([x_tr, csr_matrix(z_tr)]), y_tr)
    if list(clf.classes_) != [0, 1]:
        raise SystemExit(f"hybrid classes {clf.classes_}")
    proba = clf.predict_proba(hstack([x_va, csr_matrix(z_va)]))[:, 1]
    return proba, float(clf.coef_.ravel()[-1])


def paired_delta(y, pred_text, pred_hybrid) -> dict:
    rng = np.random.default_rng(SEED)
    y = np.asarray(y)
    pred_text = np.asarray(pred_text)
    pred_hybrid = np.asarray(pred_hybrid)
    n = len(y)

    def macro(a, b):
        return f1_score(a, b, average="macro", zero_division=0)

    def binary(a, b, label):
        return f1_score(a, b, pos_label=label, average="binary", zero_division=0)

    def pack(idx=None):
        if idx is None:
            yt, a, b = y, pred_text, pred_hybrid
        else:
            yt, a, b = y[idx], pred_text[idx], pred_hybrid[idx]
        return {
            "macro_f1": float(macro(yt, b) - macro(yt, a)),
            "other_update_f1": float(binary(yt, b, 0) - binary(yt, a, 0)),
            "troubleshooting_f1": float(binary(yt, b, 1) - binary(yt, a, 1)),
        }

    point = pack()
    draws = {k: [] for k in point}
    for _ in range(N_BOOT):
        sample = pack(rng.integers(0, n, n))
        for k, v in sample.items():
            draws[k].append(v)
    out = {
        "definition": "hybrid minus text-only on identical posts; both use inner-fold thresholds",
        "n_boot": N_BOOT,
        "seed": SEED,
    }
    for k, vals in draws.items():
        lo, hi = np.percentile(vals, [2.5, 97.5])
        out[k] = {
            "point": point[k],
            "ci95": [float(lo), float(hi)],
            "includes_zero": bool(lo <= 0 <= hi),
        }
    return out


def raw_title_body(row: dict) -> str:
    return f"{row.get('title') or ''}\n{row.get('post_body') or ''}"


def vader_compounds(rows: list[dict], analyzer: SentimentIntensityAnalyzer) -> np.ndarray:
    return np.array(
        [compound_score(analyzer, raw_title_body(row)) for row in rows],
        dtype=float,
    )


def text_audit(rows: list[dict]) -> dict:
    empty_title = sum(1 for r in rows if not str(r.get("title") or "").strip())
    empty_body = sum(1 for r in rows if not str(r.get("post_body") or "").strip())
    both = sum(
        1
        for r in rows
        if not str(r.get("title") or "").strip() and not str(r.get("post_body") or "").strip()
    )
    return {
        "n": len(rows),
        "empty_title": empty_title,
        "empty_body": empty_body,
        "empty_title_and_body": both,
        "tfidf_text": "run_experiment.make_text title_body: URL stripped, lowercased, whitespace collapsed",
        "vader_text": "raw saved title, newline, raw saved body; VADER compound. Empty or whitespace-only string returns 0.0, which is also the compound of neutral text",
        "comments_used": False,
    }


def load_reddit() -> dict:
    by_id = {r["reddit_id"]: r for r in read_jsonl(REDDIT_DEV)}
    oof = read_jsonl(REDDIT_OOF)
    if len(oof) != 2050:
        raise SystemExit(f"expected 2050 saved Reddit folds, found {len(oof)}")
    rows = []
    for item in oof:
        src = by_id.get(item["reddit_id"])
        if src is None:
            raise SystemExit(f"missing development row {item['reddit_id']}")
        if int(src["s2_target"]) != int(item["y_true"]):
            raise SystemExit(f"label mismatch {item['reddit_id']}")
        if item["reddit_id"] in NEAR_DUP:
            raise SystemExit("near-duplicate present in saved folds")
        rows.append(src)
    y = np.array([int(r["s2_target"]) for r in rows], dtype=int)
    folds = np.array([int(r["fold"]) for r in oof], dtype=int)
    groups = np.array([int(r["group_id"]) for r in oof], dtype=int)
    if sorted(set(folds.tolist())) != list(range(N_OUTER)):
        raise SystemExit(f"unexpected folds {set(folds.tolist())}")
    if int((y == 1).sum()) != 1658 or int((y == 0).sum()) != 392:
        raise SystemExit("unexpected Reddit class counts")
    for gid in set(groups.tolist()):
        used = set(folds[groups == gid].tolist())
        if len(used) != 1:
            raise SystemExit(f"group {gid} split across folds {used}")
    return {
        "name": "reddit_2050",
        "rows": rows,
        "y": y,
        "folds": folds,
        "groups": groups,
        "saved_scores": np.array([float(r["score_tfidf_lr"]) for r in oof]),
        "saved_preds": np.array([int(r["y_pred_tfidf_lr"]) for r in oof], dtype=int),
        "population_note": "Reddit-URL S2 development rows and exact grouped outer folds from phase3/reddit_only_sensitivity",
    }


def load_mixed() -> dict:
    dev = [
        r
        for r in read_jsonl(MIXED_DEV)
        if r.get("s2_in_scope")
        and r.get("s2_target") in (0, 1)
        and r["reddit_id"] not in NEAR_DUP
    ]
    if len(dev) != 2080:
        raise SystemExit(f"expected 2080 mixed S2 rows, found {len(dev)}")
    oof = read_jsonl(MIXED_OOF)
    if [r["reddit_id"] for r in oof] != [r["reddit_id"] for r in dev]:
        raise SystemExit("mixed OOF order does not match revised development S2 order")
    y = np.array([int(r["s2_target"]) for r in dev], dtype=int)
    if np.any(y != np.array([int(r["y_true"]) for r in oof])):
        raise SystemExit("mixed OOF label mismatch")
    _, groups = audit_within_dev(dev)
    groups = np.asarray(groups)
    folds = np.array([int(r["fold"]) for r in oof], dtype=int)
    for gid in set(groups.tolist()):
        used = set(folds[groups == gid].tolist())
        if len(used) != 1:
            raise SystemExit(f"mixed group {gid} split across saved folds {used}")
    conflicting = [r["reddit_id"] for r in dev if str(r["reddit_id"]).startswith("so_")]
    return {
        "name": "mixed_2080",
        "rows": dev,
        "y": y,
        "folds": folds,
        "groups": groups,
        "saved_scores": np.array([float(r["score"]) for r in oof]),
        "saved_preds": np.array([int(r["y_pred"]) for r in oof], dtype=int),
        "population_note": (
            "Revised S2 development snapshot, near-duplicate IDs 1t0wme9 and 1wrqch6 excluded, "
            "saved diagnostic grouped folds. Includes 30 so_ records with conflicting source metadata."
        ),
        "conflicting_source_ids_n": len(conflicting),
        "conflicting_source_class_counts": dict(Counter(int(r["s2_target"]) for r in dev if str(r["reddit_id"]).startswith("so_"))),
    }


def evaluate_population(spec: dict, compounds: np.ndarray) -> dict:
    rows = spec["rows"]
    y = spec["y"]
    folds = spec["folds"]
    groups = spec["groups"]
    texts = [make_text(r, "title_body") for r in rows]
    n = len(rows)
    saved_scores = spec["saved_scores"]
    saved_preds = spec["saved_preds"]

    # Continuity pass: frozen TF-IDF and the recorded threshold, before nested tuning.
    repro_scores = np.full(n, np.nan)
    for fold in range(N_OUTER):
        test_idx = np.flatnonzero(folds == fold)
        train_idx = np.flatnonzero(folds != fold)
        repro_scores[test_idx] = text_proba(
            [texts[i] for i in train_idx],
            y[train_idx],
            [texts[i] for i in test_idx],
        )
        print(f"{spec['name']} continuity fold {fold}", flush=True)
    gap = float(np.max(np.abs(repro_scores - saved_scores)))
    repro_pred = (repro_scores >= THRESHOLD).astype(int)
    continuity = {
        "max_abs_score_gap_vs_saved": gap,
        "prediction_mismatches_vs_saved": int(np.sum(repro_pred != saved_preds)),
        "within_tolerance": bool(gap <= SCORE_TOL and np.array_equal(repro_pred, saved_preds)),
        "tolerance": SCORE_TOL,
        "fixed_threshold": THRESHOLD,
        "fixed_threshold_metrics": metrics_at(y, repro_pred, repro_scores),
    }
    if not continuity["within_tolerance"]:
        raise SystemExit(
            f"{spec['name']} TF-IDF reproduction failed: max abs gap {gap}, "
            f"prediction mismatches {continuity['prediction_mismatches_vs_saved']}"
        )

    text_score = np.full(n, np.nan)
    sent_score = np.full(n, np.nan)
    hyb_score = np.full(n, np.nan)
    text_pred = np.full(n, -1)
    sent_pred = np.full(n, -1)
    hyb_pred = np.full(n, -1)
    maj_pred = np.full(n, -1)
    text_thr = np.full(n, np.nan)
    sent_thr = np.full(n, np.nan)
    hyb_thr = np.full(n, np.nan)
    fold_reports = []

    for fold in range(N_OUTER):
        test_idx = np.flatnonzero(folds == fold)
        train_idx = np.flatnonzero(folds != fold)
        y_tr = y[train_idx]
        groups_tr = groups[train_idx]
        text_tr = [texts[i] for i in train_idx]
        comp_tr = compounds[train_idx]
        maj = int(Counter(y_tr.tolist()).most_common(1)[0][0])

        def text_fit(tr, va, text_tr=text_tr, y_tr=y_tr):
            return text_proba(
                [text_tr[i] for i in tr],
                y_tr[tr],
                [text_tr[i] for i in va],
            )

        def sent_fit(tr, va, comp_tr=comp_tr, y_tr=y_tr):
            return sentiment_proba(comp_tr[tr], y_tr[tr], comp_tr[va])

        def hyb_fit(tr, va, text_tr=text_tr, comp_tr=comp_tr, y_tr=y_tr):
            proba, _coef = hybrid_proba(
                [text_tr[i] for i in tr],
                comp_tr[tr],
                y_tr[tr],
                [text_tr[i] for i in va],
                comp_tr[va],
            )
            return proba

        text_choice = choose_threshold(inner_pieces(y_tr, groups_tr, text_fit))
        sent_choice = choose_threshold(inner_pieces(y_tr, groups_tr, sent_fit))
        hyb_choice = choose_threshold(inner_pieces(y_tr, groups_tr, hyb_fit))

        text_held = text_proba(text_tr, y_tr, [texts[i] for i in test_idx])
        sent_held = sentiment_proba(comp_tr, y_tr, compounds[test_idx])
        hyb_held, coef = hybrid_proba(
            text_tr, comp_tr, y_tr, [texts[i] for i in test_idx], compounds[test_idx]
        )
        # The continuity scores and this outer refit must match.
        if float(np.max(np.abs(text_held - repro_scores[test_idx]))) > SCORE_TOL:
            raise SystemExit(f"{spec['name']} fold {fold} outer text refit drifted")

        text_score[test_idx] = text_held
        sent_score[test_idx] = sent_held
        hyb_score[test_idx] = hyb_held
        text_pred[test_idx] = (text_held >= text_choice["threshold"]).astype(int)
        sent_pred[test_idx] = (sent_held >= sent_choice["threshold"]).astype(int)
        hyb_pred[test_idx] = (hyb_held >= hyb_choice["threshold"]).astype(int)
        maj_pred[test_idx] = maj
        text_thr[test_idx] = text_choice["threshold"]
        sent_thr[test_idx] = sent_choice["threshold"]
        hyb_thr[test_idx] = hyb_choice["threshold"]
        fold_reports.append(
            {
                "fold": fold,
                "n_train": int(len(train_idx)),
                "n_test": int(len(test_idx)),
                "train_support": {
                    "other_update_0": int((y_tr == 0).sum()),
                    "troubleshooting_1": int((y_tr == 1).sum()),
                },
                "test_support": {
                    "other_update_0": int((y[test_idx] == 0).sum()),
                    "troubleshooting_1": int((y[test_idx] == 1).sum()),
                },
                "majority_class": maj,
                "text_threshold": text_choice["threshold"],
                "text_inner": text_choice["selected"],
                "sentiment_threshold": sent_choice["threshold"],
                "sentiment_inner": sent_choice["selected"],
                "hybrid_threshold": hyb_choice["threshold"],
                "hybrid_inner": hyb_choice["selected"],
                "scaled_vader_coefficient": coef,
                "text_outer": metrics_at(y[test_idx], text_pred[test_idx], text_held),
                "sentiment_outer": metrics_at(y[test_idx], sent_pred[test_idx], sent_held),
                "hybrid_outer": metrics_at(y[test_idx], hyb_pred[test_idx], hyb_held),
                "majority_outer": metrics_at(y[test_idx], maj_pred[test_idx]),
                "fixed_threshold_text_outer": metrics_at(
                    y[test_idx], repro_pred[test_idx], repro_scores[test_idx]
                ),
            }
        )
        print(
            f"{spec['name']} fold {fold}: text {text_choice['threshold']} "
            f"sentiment {sent_choice['threshold']} hybrid {hyb_choice['threshold']}",
            flush=True,
        )

    changed = []
    for i, row in enumerate(rows):
        if text_pred[i] == hyb_pred[i]:
            continue
        true = int(y[i])
        text_ok = int(text_pred[i]) == true
        hyb_ok = int(hyb_pred[i]) == true
        if (not text_ok) and hyb_ok:
            kind = "hybrid_corrects_text_error"
        elif text_ok and (not hyb_ok):
            kind = "hybrid_adds_error"
        else:
            kind = "both_wrong_prediction_changed"
        changed.append(
            {
                "reddit_id": row["reddit_id"],
                "fold": int(folds[i]),
                "y_true": true,
                "text_pred": int(text_pred[i]),
                "hybrid_pred": int(hyb_pred[i]),
                "change": kind,
                "title": str(row.get("title") or "")[:180],
                "note": "Title is context for the changed decision, not a validated explanation.",
            }
        )

    def change_counts(items: list[dict]) -> dict:
        return dict(Counter(item["change"] + f"_y{item['y_true']}" for item in items))

    predictions = []
    for i, row in enumerate(rows):
        predictions.append(
            {
                "reddit_id": row["reddit_id"],
                "fold": int(folds[i]),
                "group_id": int(groups[i]),
                "y_true": int(y[i]),
                "vader_compound_title_body": float(compounds[i]),
                "score_text": float(text_score[i]),
                "pred_text_inner_threshold": int(text_pred[i]),
                "text_threshold": float(text_thr[i]),
                "pred_text_fixed_threshold": int(repro_pred[i]),
                "saved_text_score": float(saved_scores[i]),
                "saved_text_pred": int(saved_preds[i]),
                "score_sentiment": float(sent_score[i]),
                "pred_sentiment_inner_threshold": int(sent_pred[i]),
                "sentiment_threshold": float(sent_thr[i]),
                "score_hybrid": float(hyb_score[i]),
                "pred_hybrid_inner_threshold": int(hyb_pred[i]),
                "hybrid_threshold": float(hyb_thr[i]),
                "pred_majority": int(maj_pred[i]),
                "text_availability": row.get("text_availability"),
                "empty_title": not str(row.get("title") or "").strip(),
                "empty_body": not str(row.get("post_body") or "").strip(),
            }
        )

    pooled = {
        "population": spec["population_note"],
        "n": n,
        "n_folds": N_OUTER,
        "support": {"other_update_0": int((y == 0).sum()), "troubleshooting_1": int((y == 1).sum())},
        "text_fixed_threshold": continuity["fixed_threshold_metrics"],
        "text_inner_threshold": metrics_at(y, text_pred, text_score),
        "sentiment_only_inner_threshold": metrics_at(y, sent_pred, sent_score),
        "hybrid_inner_threshold": metrics_at(y, hyb_pred, hyb_score),
        "majority": metrics_at(y, maj_pred),
        "paired_hybrid_minus_text": paired_delta(y, text_pred, hyb_pred),
        "changed_error_counts": change_counts(changed),
        "n_prediction_changes": len(changed),
        "continuity": continuity,
        "folds": fold_reports,
        "text_behavior": text_audit(rows),
        "vader_compound_summary": {
            "min": float(compounds.min()),
            "max": float(compounds.max()),
            "mean": float(compounds.mean()),
            "n_exact_zero": int(np.sum(compounds == 0.0)),
            "mean_other_update_0": float(compounds[y == 0].mean()),
            "mean_troubleshooting_1": float(compounds[y == 1].mean()),
        },
    }
    if "conflicting_source_ids_n" in spec:
        pooled["conflicting_source_ids_n"] = spec["conflicting_source_ids_n"]
        pooled["conflicting_source_class_counts"] = {
            str(k): int(v) for k, v in spec["conflicting_source_class_counts"].items()
        }
    return {"pooled": pooled, "predictions": predictions, "changed": changed, "folds": fold_reports}


def historical_audit(analyzer: SentimentIntensityAnalyzer) -> dict:
    saved_rows = list(csv.DictReader(C1_METRICS.open(encoding="utf-8")))
    if len(saved_rows) != 542:
        raise SystemExit(f"expected 542 c1 metrics rows, found {len(saved_rows)}")
    posts = load_raw_posts_by_id(RAW_DIR)
    labels = list(csv.DictReader(LABELS.open(encoding="utf-8")))
    # Unique gold IDs in file order, matching the trajectory builder's row loop.
    seen = []
    for lab in labels:
        rid = str(lab["reddit_id"]).strip()
        if rid not in {x[0] for x in seen}:
            seen.append((rid, lab))

    fallback = 0
    body_only = 0
    author_comment_counts = []
    missing = []
    recomputed = []
    mismatches = []
    title_only_ids = []
    stored_comments = 0
    num_comments = 0
    posts_short = 0
    empty_comment_bodies = 0
    comment_bodies = 0
    by_label_fallback = Counter()
    by_label_real_author = Counter()

    for rid, lab in seen:
        post = posts.get(rid)
        if not post:
            missing.append(rid)
            continue
        author = (post.get("author") or "").strip()
        body = (post.get("author_description") or "").strip()
        comments = sorted(post.get("comments") or [], key=lambda c: str(c.get("created_utc") or ""))
        n_author_c = 0
        n_comm = 0
        for c in comments:
            cbody = (c.get("body") or "").strip()
            comment_bodies += 1
            if not cbody:
                empty_comment_bodies += 1
                continue
            is_author = bool(c.get("is_submitter")) or (
                author and (c.get("author") or "").strip() == author
            )
            if is_author:
                n_author_c += 1
            else:
                n_comm += 1
        listed = int(post.get("num_comments") or 0)
        stored = len(post.get("comments") or [])
        stored_comments += stored
        num_comments += listed
        if stored < listed:
            posts_short += 1
        author_comment_counts.append(n_author_c)
        label = int(lab["corrected_label"])
        title_only = (not body) and n_author_c == 0
        if title_only:
            fallback += 1
            by_label_fallback[label] += 1
            title_only_ids.append(rid)
        else:
            by_label_real_author[label] += 1
        if body and n_author_c == 0:
            body_only += 1
        author_traj, community_traj, title_c = analyze_post_trajectories(post, analyzer)
        metrics = compute_metrics_row(
            reddit_id=rid,
            subreddit=str(lab.get("subreddit") or post.get("subreddit") or ""),
            corrected_label=label,
            url=str(lab.get("url") or post.get("url") or ""),
            author_traj=author_traj,
            community_traj=community_traj,
            title_compound=title_c,
        )
        rec = metrics.to_dict()
        rec["title_only_author_track"] = title_only
        recomputed.append(rec)

    saved_by_id = {r["reddit_id"]: r for r in saved_rows}
    compare_fields = [
        "author_mean_sentiment",
        "community_mean_sentiment",
        "sentiment_divergence",
        "author_trend",
        "community_trend",
        "author_early_late_shift",
        "community_early_late_shift",
        "n_author_replies",
        "n_community_comments",
    ]
    for rec in recomputed:
        saved = saved_by_id.get(rec["reddit_id"])
        if saved is None:
            mismatches.append({"reddit_id": rec["reddit_id"], "issue": "missing from saved csv"})
            continue
        for field in compare_fields:
            if abs(float(saved[field]) - float(rec[field])) > 5e-4:
                mismatches.append(
                    {
                        "reddit_id": rec["reddit_id"],
                        "field": field,
                        "saved": float(saved[field]),
                        "recomputed": float(rec[field]),
                    }
                )
                break

    def frame(records: list[dict]) -> dict:
        tps = [r for r in records if int(r["corrected_label"]) == 1]
        gds = [r for r in records if int(r["corrected_label"]) == 0]

        def arrays(col):
            return (
                np.array([float(r[col]) for r in tps]),
                np.array([float(r[col]) for r in gds]),
            )

        tests = {}
        for col in (
            "sentiment_divergence",
            "author_mean_sentiment",
            "community_mean_sentiment",
            "author_trend",
            "author_early_late_shift",
            "community_trend",
            "community_early_late_shift",
        ):
            a, b = arrays(col)
            mw = stats.mannwhitneyu(a, b, alternative="two-sided", method="asymptotic")
            welch = stats.ttest_ind(a, b, equal_var=False)
            tests[col] = {
                "n_tps": int(len(a)),
                "n_gds": int(len(b)),
                "mean_tps": float(np.mean(a)),
                "mean_gds": float(np.mean(b)),
                "welch_p": float(welch.pvalue),
                "mannwhitney_asymptotic_p": float(mw.pvalue),
            }
        author_neg_tps = np.array([1 if r["author_more_negative"] else 0 for r in tps], dtype=float)
        author_neg_gds = np.array([1 if r["author_more_negative"] else 0 for r in gds], dtype=float)
        mw_neg = stats.mannwhitneyu(
            author_neg_tps, author_neg_gds, alternative="two-sided", method="asymptotic"
        )
        return {
            "n": len(records),
            "n_tps": len(tps),
            "n_gds": len(gds),
            "author_more_negative_rate_tps": float(np.mean(author_neg_tps)) if len(tps) else None,
            "author_more_negative_rate_gds": float(np.mean(author_neg_gds)) if len(gds) else None,
            "author_more_negative_mannwhitney_asymptotic_p": float(mw_neg.pvalue),
            "tests": tests,
        }

    # Pool coverage uses each raw response file, matching the Phase 2 audit.
    pools = {}
    for fname in ("tps_response.json", "gds_response.json"):
        payload = json.loads((RAW_DIR / fname).read_text(encoding="utf-8"))
        data = payload.get("data") or []
        listed = sum(int(p.get("num_comments") or 0) for p in data)
        stored = sum(len(p.get("comments") or []) for p in data)
        short = sum(1 for p in data if len(p.get("comments") or []) < int(p.get("num_comments") or 0))
        pools[fname] = {
            "n_posts": len(data),
            "sum_num_comments": listed,
            "sum_stored_comments": stored,
            "stored_over_num_comments": (stored / listed) if listed else None,
            "posts_stored_lt_num_comments": short,
        }

    title_only_set = set(title_only_ids)
    saved_for_split = []
    for row in saved_rows:
        item = {
            "reddit_id": row["reddit_id"],
            "corrected_label": int(row["corrected_label"]),
            "author_mean_sentiment": float(row["author_mean_sentiment"]),
            "community_mean_sentiment": float(row["community_mean_sentiment"]),
            "sentiment_divergence": float(row["sentiment_divergence"]),
            "author_trend": float(row["author_trend"]),
            "author_early_late_shift": float(row["author_early_late_shift"]),
            "community_trend": float(row["community_trend"]),
            "community_early_late_shift": float(row["community_early_late_shift"]),
            "author_more_negative": str(row["author_more_negative"]).lower() == "true",
            "title_only_author_track": row["reddit_id"] in title_only_set,
        }
        saved_for_split.append(item)

    with_title = [r for r in saved_for_split if r["title_only_author_track"]]
    without_title = [r for r in saved_for_split if not r["title_only_author_track"]]
    return {
        "status": "historical and exploratory; not part of the 2050-row classifier",
        "n_saved_metrics": len(saved_rows),
        "n_unique_gold_ids": len(seen),
        "n_recomputed": len(recomputed),
        "gold_missing_from_raw": missing,
        "metric_recompute_mismatches": mismatches[:20],
        "n_metric_recompute_mismatches": len(mismatches),
        "title_only_author_fallback_n": fallback,
        "title_only_by_historical_label": {
            "tps_1": int(by_label_fallback[1]),
            "gds_0": int(by_label_fallback[0]),
        },
        "body_or_author_comment_by_historical_label": {
            "tps_1": int(by_label_real_author[1]),
            "gds_0": int(by_label_real_author[0]),
        },
        "body_present_but_no_author_comment_n": body_only,
        "mean_author_comment_count_excluding_title_fallback": float(np.mean(author_comment_counts)),
        "labeled_post_comment_coverage": {
            "sum_stored_comments": stored_comments,
            "sum_num_comments": num_comments,
            "stored_over_num_comments": (stored_comments / num_comments) if num_comments else None,
            "posts_with_fewer_stored_comments_than_num_comments": posts_short,
            "comment_bodies": comment_bodies,
            "empty_comment_bodies": empty_comment_bodies,
        },
        "raw_pool_comment_coverage": pools,
        "saved_column_tests_all_542": frame(saved_for_split),
        "saved_divergence_title_only_author_tracks": frame(with_title),
        "saved_divergence_excluding_title_only_author_tracks": frame(without_title),
        "published_reference": {
            "file": str(SAVED_DIVERGENCE),
            "sha256": sha256_file(SAVED_DIVERGENCE),
            "full_divergence_means": "0.371 TPS vs 0.2872 GDS, Mann-Whitney p 0.009221",
            "author_more_negative": "69.77% TPS vs 53.73% GDS, Mann-Whitney p 0.006007",
            "author_mean": "0.0091 TPS vs 0.1911 GDS, Welch p 4.7e-05",
            "community_mean": "0.1683 TPS vs 0.194 GDS, Welch p 0.331788",
            "author_trend_welch_p": 0.274128,
            "author_early_late_welch_p": 0.425444,
            "phase2_audit_title_only_subset_approx_p": 0.076,
            "phase2_audit_real_author_subset_approx_p": 0.060,
        },
        "temporal_interpretation": (
            "Author slope and author early-versus-late shift do not differ between the historical classes. "
            "A cumulative sentiment plot is not treated as evidence of change over time."
        ),
        "keyword_first_vader_rule_used": False,
    }


def fmt_prf(m: dict) -> str:
    c0, c1 = m["class_0_other_update"], m["class_1_troubleshooting"]
    return (
        f"{m['macro_f1']:.4f} | "
        f"{c0['precision']:.3f}/{c0['recall']:.3f}/{c0['f1']:.3f} | "
        f"{c1['precision']:.3f}/{c1['recall']:.3f}/{c1['f1']:.3f} | "
        f"{m['balanced_accuracy']:.4f} | `{m['confusion_matrix_labels_[0,1]']}`"
    )


def recommendation(primary: dict) -> dict:
    delta = primary["paired_hybrid_minus_text"]["macro_f1"]
    other = primary["paired_hybrid_minus_text"]["other_update_f1"]
    text_f = primary["text_inner_threshold"]["macro_f1"]
    sent_f = primary["sentiment_only_inner_threshold"]["macro_f1"]
    reliable_gain = delta["point"] > 0 and not delta["includes_zero"]
    sentiment_carries_task = sent_f + 0.02 >= text_f
    other_reliably_worse = other["point"] < 0 and not other["includes_zero"]
    if reliable_gain and sentiment_carries_task and not other_reliably_worse:
        choice = "pivot_to_sentiment_centered_revision"
        text = (
            "Sentiment-only performance is close to the text model and the hybrid gain is reliable. "
            "That would support a sentiment-centered revision. This run does not edit the paper."
        )
    elif reliable_gain and not other_reliably_worse:
        choice = "bounded_addition"
        text = (
            "The hybrid interval lies above zero without a reliable loss on the other-update class. "
            "That would support a bounded addition to the current paper, not a sentiment-centered rewrite. "
            "This run does not edit the paper or make a submission claim."
        )
    else:
        choice = "retain_current_paper_without_new_sentiment_claims"
        if not reliable_gain:
            reason = (
                f"Hybrid minus text macro-F1 is {delta['point']:+.4f} and the 95% interval "
                f"({delta['ci95'][0]:+.4f} to {delta['ci95'][1]:+.4f}) includes zero, so title-and-body "
                "VADER does not add a reliable gain."
            )
        else:
            reason = (
                "The macro-F1 gain is positive, but the other-update F1 difference is reliably negative, "
                "so the added feature is not a useful improvement for the smaller class."
            )
        text = (
            f"{reason} Sentiment-only macro-F1 is {sent_f:.4f}, well below the text model at {text_f:.4f}. "
            "Retain the current paper without a new claim that this sentiment feature improves troubleshooting detection. "
            "This run does not edit the paper."
        )
    return {"choice": choice, "text": text, "rules": {
        "reliable_macro_gain": reliable_gain,
        "sentiment_only_within_0.02_macro_f1_of_text": sentiment_carries_task,
        "other_update_f1_reliably_worse": other_reliably_worse,
    }}


def write_results(primary: dict, mixed: dict, historical: dict, manifest: dict) -> None:
    rec = recommendation(primary)
    d = primary["paired_hybrid_minus_text"]
    h = historical
    full = h["saved_column_tests_all_542"]
    title_only = h["saved_divergence_title_only_author_tracks"]
    real_author = h["saved_divergence_excluding_title_only_author_tracks"]
    lines = [
        "# Sentiment reanalysis results",
        "",
        f"**Created:** {manifest['created_utc']}",
        f"**Code version:** `{CODE_VERSION}`",
        "",
        "Verified on the saved development folds. The 159-row reserved test and the 344-row fresh test were not read or scored. Phase 1 files, labels, Phase 3 outputs, the manuscript, and Overleaf were not modified.",
        "",
        "## Question",
        "",
        "Does VADER compound sentiment from the saved title and body add useful information beyond the frozen TF-IDF logistic regression for troubleshooting versus other update discussion?",
        "",
        "## Primary population",
        "",
        f"{primary['population']} n={primary['n']}: {primary['support']['troubleshooting_1']} troubleshooting and {primary['support']['other_update_0']} other update. Five grouped outer folds. TF-IDF uses word unigrams and bigrams, `min_df=2`, `max_features=20000`, `sublinear_tf`, logistic regression `C=4`, `class_weight='balanced'`, `liblinear`.",
        "",
        f"The reproduced text scores match the saved grouped out-of-fold scores within {primary['continuity']['max_abs_score_gap_vs_saved']:.3e} (tolerance {SCORE_TOL}). Fixed-threshold prediction mismatches: {primary['continuity']['prediction_mismatches_vs_saved']}.",
        "",
        f"VADER is one compound score of the raw title and body. Empty text returns 0.0. Empty title: {primary['text_behavior']['empty_title']}. Empty body: {primary['text_behavior']['empty_body']}. Both empty: {primary['text_behavior']['empty_title_and_body']}. Exact-zero compounds, including genuine neutral text: {primary['vader_compound_summary']['n_exact_zero']}. Mean compound is {primary['vader_compound_summary']['mean_troubleshooting_1']:.4f} on troubleshooting and {primary['vader_compound_summary']['mean_other_update_0']:.4f} on other update. No comments, source, community, identifiers, timestamps, or review fields enter the classifier. The historical keyword-first VADER rule is not used.",
        "",
        "The compound is standardized inside each training fold. Inner thresholds use three grouped folds of the outer training split only, on the grid 0.20 through 0.80 by 0.05. The selection rule is mean inner macro-F1, then mean inner other-update F1, then proximity to 0.50. Outer labels are not used to choose cutoffs.",
        "",
        "## Primary scores",
        "",
        "| Arm | macro-F1 | other P/R/F1 | trouble P/R/F1 | balanced acc. | confusion [[0,1]] |",
        "|---|---:|---|---|---:|---|",
        f"| Text, saved threshold {THRESHOLD} | {fmt_prf(primary['text_fixed_threshold'])} |",
        f"| Text, inner threshold | {fmt_prf(primary['text_inner_threshold'])} |",
        f"| VADER compound only, inner threshold | {fmt_prf(primary['sentiment_only_inner_threshold'])} |",
        f"| Text plus VADER, inner threshold | {fmt_prf(primary['hybrid_inner_threshold'])} |",
        f"| Majority on the same folds | {fmt_prf(primary['majority'])} |",
        "",
        f"Fair paired difference, hybrid minus text: macro-F1 **{d['macro_f1']['point']:+.4f}** (95% bootstrap interval {d['macro_f1']['ci95'][0]:+.4f} to {d['macro_f1']['ci95'][1]:+.4f}; includes zero: {d['macro_f1']['includes_zero']}). Other-update F1 **{d['other_update_f1']['point']:+.4f}** ({d['other_update_f1']['ci95'][0]:+.4f} to {d['other_update_f1']['ci95'][1]:+.4f}; includes zero: {d['other_update_f1']['includes_zero']}). Troubleshooting F1 **{d['troubleshooting_f1']['point']:+.4f}** ({d['troubleshooting_f1']['ci95'][0]:+.4f} to {d['troubleshooting_f1']['ci95'][1]:+.4f}; includes zero: {d['troubleshooting_f1']['includes_zero']}). Bootstrap: {N_BOOT} post-level resamples, seed {SEED}.",
        "",
        "A positive point estimate whose interval includes zero is not counted as an improvement.",
        "",
        f"Prediction changes between inner-threshold text and hybrid: **{primary['n_prediction_changes']}**. Counts by change and true class: `{json.dumps(primary['changed_error_counts'])}`. Titles in `results/reddit_2050/changed_errors.jsonl` are illustrations, not validated explanations.",
        "",
        "Supplementary threshold-free average precision for troubleshooting: "
        f"text {primary['text_inner_threshold']['average_precision_troubleshooting']:.4f}, "
        f"sentiment-only {primary['sentiment_only_inner_threshold']['average_precision_troubleshooting']:.4f}, "
        f"hybrid {primary['hybrid_inner_threshold']['average_precision_troubleshooting']:.4f}. "
        "This is not a second model-selection result.",
        "",
        "## Smaller class",
        "",
        f"Other-update support is {primary['support']['other_update_0']}. "
        f"Inner-threshold text F1 is {primary['text_inner_threshold']['class_0_other_update']['f1']:.4f} "
        f"(precision {primary['text_inner_threshold']['class_0_other_update']['precision']:.3f}, "
        f"recall {primary['text_inner_threshold']['class_0_other_update']['recall']:.3f}). "
        f"Hybrid F1 is {primary['hybrid_inner_threshold']['class_0_other_update']['f1']:.4f} "
        f"(precision {primary['hybrid_inner_threshold']['class_0_other_update']['precision']:.3f}, "
        f"recall {primary['hybrid_inner_threshold']['class_0_other_update']['recall']:.3f}). "
        f"Sentiment-only F1 is {primary['sentiment_only_inner_threshold']['class_0_other_update']['f1']:.4f}.",
        "",
        "## Mixed-source sensitivity",
        "",
        f"{mixed['population']} n={mixed['n']}: {mixed['support']['troubleshooting_1']} troubleshooting and {mixed['support']['other_update_0']} other update. Conflicting-source `so_` records included: {mixed['conflicting_source_ids_n']} (class counts {json.dumps(mixed['conflicting_source_class_counts'])}).",
        "",
        f"Reproduced text scores match the saved mixed grouped scores within {mixed['continuity']['max_abs_score_gap_vs_saved']:.3e}. Fixed-threshold mismatches: {mixed['continuity']['prediction_mismatches_vs_saved']}.",
        "",
        "| Arm | macro-F1 | other P/R/F1 | trouble P/R/F1 | balanced acc. | confusion [[0,1]] |",
        "|---|---:|---|---|---:|---|",
        f"| Text, saved threshold | {fmt_prf(mixed['text_fixed_threshold'])} |",
        f"| Text, inner threshold | {fmt_prf(mixed['text_inner_threshold'])} |",
        f"| VADER compound only, inner threshold | {fmt_prf(mixed['sentiment_only_inner_threshold'])} |",
        f"| Text plus VADER, inner threshold | {fmt_prf(mixed['hybrid_inner_threshold'])} |",
        f"| Majority | {fmt_prf(mixed['majority'])} |",
        "",
        f"Hybrid minus text macro-F1 **{mixed['paired_hybrid_minus_text']['macro_f1']['point']:+.4f}** "
        f"(95% interval {mixed['paired_hybrid_minus_text']['macro_f1']['ci95'][0]:+.4f} to {mixed['paired_hybrid_minus_text']['macro_f1']['ci95'][1]:+.4f}; "
        f"includes zero: {mixed['paired_hybrid_minus_text']['macro_f1']['includes_zero']}). "
        f"Other-update F1 **{mixed['paired_hybrid_minus_text']['other_update_f1']['point']:+.4f}** "
        f"({mixed['paired_hybrid_minus_text']['other_update_f1']['ci95'][0]:+.4f} to {mixed['paired_hybrid_minus_text']['other_update_f1']['ci95'][1]:+.4f}; "
        f"includes zero: {mixed['paired_hybrid_minus_text']['other_update_f1']['includes_zero']}). "
        "This sensitivity is separate from the Reddit-URL primary result.",
        "",
        "## Historical 542-post author/community check",
        "",
        "This section uses the Phase 1 trajectory code and the saved C1′ table. It is not merged into the 2,050-row classifier. Comments are not available as a complete field for that classifier population, and the historical labels are the old TPS/GDS gold labels.",
        "",
        f"Recomputed trajectory metrics for {h['n_recomputed']} posts. Mismatches against `c1_prime_metrics.csv` at rounding tolerance 0.0005: **{h['n_metric_recompute_mismatches']}**. Title-only author fallback: **{h['title_only_author_fallback_n']}** ({h['title_only_by_historical_label']['tps_1']} historical TPS, {h['title_only_by_historical_label']['gds_0']} historical GDS). Body present and no author comment: **{h['body_present_but_no_author_comment_n']}**. Mean author-comment count, excluding the title fallback: {h['mean_author_comment_count_excluding_title_fallback']:.4f}.",
        "",
        f"On the 542 labeled posts, stored comments cover {h['labeled_post_comment_coverage']['stored_over_num_comments']:.4f} of the recorded `num_comments` field ({h['labeled_post_comment_coverage']['sum_stored_comments']} stored / {h['labeled_post_comment_coverage']['sum_num_comments']} recorded; {h['labeled_post_comment_coverage']['posts_with_fewer_stored_comments_than_num_comments']} posts short). Empty comment bodies: {h['labeled_post_comment_coverage']['empty_comment_bodies']}.",
        "",
        f"Full raw pools, matching the Phase 2 coverage definition: TPS stored/recorded = {h['raw_pool_comment_coverage']['tps_response.json']['stored_over_num_comments']:.4f} ({h['raw_pool_comment_coverage']['tps_response.json']['posts_stored_lt_num_comments']} of {h['raw_pool_comment_coverage']['tps_response.json']['n_posts']} posts short); GDS stored/recorded = {h['raw_pool_comment_coverage']['gds_response.json']['stored_over_num_comments']:.4f} ({h['raw_pool_comment_coverage']['gds_response.json']['posts_stored_lt_num_comments']} of {h['raw_pool_comment_coverage']['gds_response.json']['n_posts']} posts short).",
        "",
        f"Saved full-set means: author {full['tests']['author_mean_sentiment']['mean_tps']:.4f} vs {full['tests']['author_mean_sentiment']['mean_gds']:.4f} (Welch p {full['tests']['author_mean_sentiment']['welch_p']:.6g}); community {full['tests']['community_mean_sentiment']['mean_tps']:.4f} vs {full['tests']['community_mean_sentiment']['mean_gds']:.4f} (Welch p {full['tests']['community_mean_sentiment']['welch_p']:.6g}); absolute divergence {full['tests']['sentiment_divergence']['mean_tps']:.4f} vs {full['tests']['sentiment_divergence']['mean_gds']:.4f} (asymptotic Mann-Whitney p {full['tests']['sentiment_divergence']['mannwhitney_asymptotic_p']:.6g}). Author-more-negative rates {full['author_more_negative_rate_tps']:.4f} vs {full['author_more_negative_rate_gds']:.4f}.",
        "",
        f"Title-only author tracks ({title_only['n_tps']} TPS / {title_only['n_gds']} GDS): divergence {title_only['tests']['sentiment_divergence']['mean_tps']:.4f} vs {title_only['tests']['sentiment_divergence']['mean_gds']:.4f}, asymptotic Mann-Whitney p {title_only['tests']['sentiment_divergence']['mannwhitney_asymptotic_p']:.6g}.",
        "",
        f"Author tracks with a body or author comment ({real_author['n_tps']} TPS / {real_author['n_gds']} GDS): divergence {real_author['tests']['sentiment_divergence']['mean_tps']:.4f} vs {real_author['tests']['sentiment_divergence']['mean_gds']:.4f}, asymptotic Mann-Whitney p {real_author['tests']['sentiment_divergence']['mannwhitney_asymptotic_p']:.6g}. Author means in that subset: {real_author['tests']['author_mean_sentiment']['mean_tps']:.4f} vs {real_author['tests']['author_mean_sentiment']['mean_gds']:.4f}.",
        "",
        f"Author slope Welch p {full['tests']['author_trend']['welch_p']:.6g}; author early-versus-late Welch p {full['tests']['author_early_late_shift']['welch_p']:.6g}. Community slope Welch p {full['tests']['community_trend']['welch_p']:.6g} (asymptotic Mann-Whitney p {full['tests']['community_trend']['mannwhitney_asymptotic_p']:.6g}). {h['temporal_interpretation']}",
        "",
        "The published full-corpus report remains the historical reference for the rounded Table II figures. These recomputed tests use the saved metric columns and an asymptotic Mann-Whitney test. They do not create a current-label result.",
        "",
        "## Recommendation",
        "",
        rec["text"],
        "",
        f"**Choice:** `{rec['choice']}`.",
        "",
        "No manuscript file was edited and no submission claim is made.",
        "",
        "## Limitations",
        "",
        "- Development out-of-fold scores are not a held-out test estimate.",
        "- The other-update class is much smaller than the troubleshooting class.",
        "- VADER's zero value mixes empty text and neutral text.",
        "- Inner threshold selection uses development labels inside the outer training split. It does not use the outer fold.",
        "- The 542-post analysis depends on partial stored comment threads and a title fallback.",
        "",
        "## Files",
        "",
        "- `results/reddit_2050/pooled_metrics.json`",
        "- `results/reddit_2050/pooled_predictions.jsonl`",
        "- `results/reddit_2050/fold_<k>_metrics.json` and `fold_<k>_predictions.jsonl`",
        "- `results/mixed_2080/` with the same layout",
        "- `results/historical_542_audit.json`",
        "- `MANIFEST.json`",
        "",
    ]
    (HERE / "RESULTS.md").write_text("\n".join(lines), encoding="utf-8")


def write_run_md() -> None:
    (HERE / "RUN.md").write_text(
        "\n".join(
            [
                "# Reproduce the sentiment reanalysis",
                "",
                "From `/Users/manumathewjiss/Documents/Research-on-Software-Updates/research-open-text-sentimental/`:",
                "",
                "```bash",
                "PYTHONPATH=phase5/sentiment_reanalysis/vendor \\",
                "  phase3/experiment_v1/.venv/bin/python \\",
                "  phase5/sentiment_reanalysis/run_sentiment_reanalysis.py",
                "```",
                "",
                "The experiment virtualenv supplies scikit-learn, numpy, scipy, and pandas. VADER 3.3.2 is imported from `phase5/sentiment_reanalysis/vendor` so the Phase 3 environment is not modified.",
                "",
                "The script reads the saved Reddit-only development rows and folds, the revised 2,080-row development snapshot, the Phase 1 trajectory inputs, and the saved C1′ metrics. It does not read reserved-test or fresh-test labels, scores, predictions, or errors, and it writes only under `phase5/sentiment_reanalysis/`.",
                "",
                f"Code version: `{CODE_VERSION}`.",
                "",
            ]
        ),
        encoding="utf-8",
    )


def main() -> int:
    created = datetime.now(timezone.utc).isoformat()
    analyzer = SentimentIntensityAnalyzer()
    import sklearn
    import scipy
    import pandas

    lexicon = Path(vaderSentiment.__file__).resolve().parent / "vader_lexicon.txt"
    reddit = load_reddit()
    reddit_compounds = vader_compounds(reddit["rows"], analyzer)
    reddit_result = evaluate_population(reddit, reddit_compounds)

    mixed = load_mixed()
    mixed_compounds = vader_compounds(mixed["rows"], analyzer)
    mixed_result = evaluate_population(mixed, mixed_compounds)
    historical = historical_audit(analyzer)

    for result in (reddit_result, mixed_result):
        name = "reddit_2050" if result is reddit_result else "mixed_2080"
        dest = OUT / name
        write_jsonl(dest / "pooled_predictions.jsonl", result["predictions"])
        write_jsonl(dest / "changed_errors.jsonl", result["changed"])
        pooled_public = {k: v for k, v in result["pooled"].items() if k != "folds"}
        write_json(dest / "pooled_metrics.json", pooled_public)
        for fold_report in result["folds"]:
            fold = fold_report["fold"]
            write_json(dest / f"fold_{fold}_metrics.json", fold_report)
            write_jsonl(
                dest / f"fold_{fold}_predictions.jsonl",
                [r for r in result["predictions"] if r["fold"] == fold],
            )
    write_json(OUT / "historical_542_audit.json", historical)

    output_paths = sorted(p for p in OUT.rglob("*") if p.is_file())
    manifest = {
        "code_version": CODE_VERSION,
        "script": str(Path(__file__).resolve()),
        "script_sha256": sha256_file(Path(__file__).resolve()),
        "protocol_sha256": sha256_file(HERE / "PROTOCOL.md"),
        "git_head": git_head(),
        "created_utc": created,
        "reserved_test_used": False,
        "fresh_test_used": False,
        "paper_edited": False,
        "versions": {
            "python": platform.python_version(),
            "platform": platform.platform(),
            "sklearn": sklearn.__version__,
            "numpy": np.__version__,
            "scipy": scipy.__version__,
            "pandas": pandas.__version__,
            "vaderSentiment": getattr(vaderSentiment, "__version__", "unknown"),
            "vader_lexicon_sha256": sha256_file(lexicon),
        },
        "settings": {
            "C": C,
            "class_weight": "balanced",
            "solver": "liblinear",
            "tfidf": "word ngram_range (1, 2), min_df 2, max_features 20000, sublinear_tf",
            "saved_threshold_continuity_only": THRESHOLD,
            "inner_folds": N_INNER,
            "outer_folds": N_OUTER,
            "threshold_grid": THRESHOLD_GRID,
            "threshold_rule": "max mean inner macro-F1, then mean inner other-update F1, then closer to 0.5",
            "vader_feature": "one compound score of raw title + newline + raw body; StandardScaler fit on the training fold only",
            "bootstrap": {"n": N_BOOT, "seed": SEED, "unit": "post"},
            "keyword_first_vader_rule_used": False,
            "comments_in_classifier": False,
        },
        "inputs": {
            "reddit_development": {"path": str(REDDIT_DEV), "sha256": sha256_file(REDDIT_DEV)},
            "reddit_folds": {"path": str(REDDIT_OOF), "sha256": sha256_file(REDDIT_OOF)},
            "mixed_development": {"path": str(MIXED_DEV), "sha256": sha256_file(MIXED_DEV)},
            "mixed_folds": {"path": str(MIXED_OOF), "sha256": sha256_file(MIXED_OOF)},
            "c1_metrics": {"path": str(C1_METRICS), "sha256": sha256_file(C1_METRICS)},
            "labels": {"path": str(LABELS), "sha256": sha256_file(LABELS)},
            "raw_tps": {"path": str(RAW_DIR / "tps_response.json"), "sha256": sha256_file(RAW_DIR / "tps_response.json")},
            "raw_gds": {"path": str(RAW_DIR / "gds_response.json"), "sha256": sha256_file(RAW_DIR / "gds_response.json")},
        },
        "outputs": {str(p.relative_to(HERE)): sha256_file(p) for p in output_paths},
    }
    write_results(reddit_result["pooled"], mixed_result["pooled"], historical, manifest)
    write_run_md()
    manifest["documents"] = {
        "RESULTS.md": sha256_file(HERE / "RESULTS.md"),
        "RUN.md": sha256_file(HERE / "RUN.md"),
    }
    write_json(HERE / "MANIFEST.json", manifest)
    summary = {
        "reddit_text_fixed_macro_f1": reddit_result["pooled"]["text_fixed_threshold"]["macro_f1"],
        "reddit_text_inner_macro_f1": reddit_result["pooled"]["text_inner_threshold"]["macro_f1"],
        "reddit_sentiment_macro_f1": reddit_result["pooled"]["sentiment_only_inner_threshold"]["macro_f1"],
        "reddit_hybrid_macro_f1": reddit_result["pooled"]["hybrid_inner_threshold"]["macro_f1"],
        "reddit_delta": reddit_result["pooled"]["paired_hybrid_minus_text"]["macro_f1"],
        "score_gap_reddit": reddit_result["pooled"]["continuity"]["max_abs_score_gap_vs_saved"],
        "score_gap_mixed": mixed_result["pooled"]["continuity"]["max_abs_score_gap_vs_saved"],
        "title_only_fallback": historical["title_only_author_fallback_n"],
        "metric_mismatches": historical["n_metric_recompute_mismatches"],
        "recommendation": recommendation(reddit_result["pooled"])["choice"],
    }
    print(json.dumps(summary, indent=2), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
