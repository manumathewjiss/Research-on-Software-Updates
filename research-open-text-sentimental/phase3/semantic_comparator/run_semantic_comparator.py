#!/usr/bin/env python3
"""One frozen sentence-embedding comparison against TF-IDF logistic regression.

Development folds only. Does not read the reserved or fresh test sets.
The encoder and the threshold grid below are fixed before any outer-fold score
is computed. No second backbone is tried.
"""

from __future__ import annotations

import hashlib
import json
import platform
import subprocess
import sys
import time
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    balanced_accuracy_score,
    confusion_matrix,
    f1_score,
    precision_recall_fscore_support,
)
from sklearn.model_selection import StratifiedGroupKFold

PHASE3 = Path(__file__).resolve().parents[1]
REPO = PHASE3.parent
HERE = Path(__file__).resolve().parent
OUT = HERE / "results"
sys.path.insert(0, str(PHASE3 / "experiment_v1"))
sys.path.insert(0, str(PHASE3 / "experiment_v1" / "followup"))

from run_experiment import build_lr, make_text  # noqa: E402
from run_followup import audit_within_dev  # noqa: E402

DEV = PHASE3 / "update_connection_audit/targeted_submission/development_after_update_audit.jsonl"
OOF = PHASE3 / "update_connection_audit/targeted_submission/post_audit_reddit_only_oof.jsonl"
MASTER = REPO / "phase2/combined_dataset/master_records.json"
NEAR_DUP = {"1t0wme9", "1wrqch6"}
MODEL_ID = "sentence-transformers/all-MiniLM-L6-v2"
MAX_WORDPIECES = 256
# Preregistered before outer-fold scoring. Not chosen from held-out labels.
THRESHOLD_GRID = [round(x, 2) for x in np.linspace(0.20, 0.80, 13)]
SEED = 42
N_BOOT = 1000
CODE_VERSION = "semantic-comparator-v1"


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def git_head() -> str | None:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=REPO, text=True, stderr=subprocess.DEVNULL
        ).strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None


def host_of(url: str) -> str:
    host = urlparse(url or "").netloc.lower()
    return host[4:] if host.startswith("www.") else host


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


def semantic_head() -> LogisticRegression:
    return LogisticRegression(
        C=1.0,
        class_weight="balanced",
        max_iter=2000,
        solver="liblinear",
        random_state=SEED,
    )


def choose_threshold(fold_pieces: list[tuple[np.ndarray, np.ndarray]]) -> dict:
    """Pick a grid threshold from inner-fold probabilities only."""
    best = None
    table = []
    for thr in THRESHOLD_GRID:
        macros, others = [], []
        for y_val, proba in fold_pieces:
            pred = (proba >= thr).astype(int)
            macros.append(f1_score(y_val, pred, average="macro", zero_division=0))
            others.append(
                f1_score(y_val, pred, pos_label=0, average="binary", zero_division=0)
            )
        row = {
            "threshold": thr,
            "mean_inner_macro_f1": float(np.mean(macros)),
            "mean_inner_other_f1": float(np.mean(others)),
        }
        table.append(row)
        key = (row["mean_inner_macro_f1"], row["mean_inner_other_f1"], -abs(thr - 0.5))
        if best is None or key > best[0]:
            best = (key, thr)
    return {"threshold": best[1], "grid": table}


def inner_pieces(y, groups, fit_val_proba) -> list[tuple[np.ndarray, np.ndarray]]:
    splitter = StratifiedGroupKFold(n_splits=3, shuffle=True, random_state=SEED)
    pieces = []
    for train_idx, val_idx in splitter.split(np.zeros(len(y)), y, groups):
        proba = fit_val_proba(train_idx, val_idx)
        pieces.append((y[val_idx], proba))
    return pieces


def by_field(rows, y, pred, field: str) -> dict:
    buckets = defaultdict(list)
    for i, row in enumerate(rows):
        buckets[row.get(field) or "unknown"].append(i)
    out = {}
    for key in sorted(buckets):
        idx = np.array(buckets[key])
        out[key] = metrics_at(y[idx], pred[idx])
    return out


def paired_delta(y, pred_a, pred_b, seed=SEED) -> dict:
    """Bootstrap CI for macro-F1(b) - macro-F1(a), paired on the same posts."""
    rng = np.random.default_rng(seed)
    y = np.asarray(y)
    pred_a = np.asarray(pred_a)
    pred_b = np.asarray(pred_b)
    n = len(y)

    def macro(a, b):
        return f1_score(a, b, average="macro", zero_division=0)

    def other(a, b):
        return f1_score(a, b, pos_label=0, average="binary", zero_division=0)

    point_macro = float(macro(y, pred_b) - macro(y, pred_a))
    point_other = float(other(y, pred_b) - other(y, pred_a))
    d_macro, d_other = [], []
    for _ in range(N_BOOT):
        idx = rng.integers(0, n, n)
        d_macro.append(macro(y[idx], pred_b[idx]) - macro(y[idx], pred_a[idx]))
        d_other.append(other(y[idx], pred_b[idx]) - other(y[idx], pred_a[idx]))
    lo_m, hi_m = np.percentile(d_macro, [2.5, 97.5])
    lo_o, hi_o = np.percentile(d_other, [2.5, 97.5])
    return {
        "definition": "semantic minus tfidf on identical posts",
        "macro_f1": {
            "point": point_macro,
            "ci95": [float(lo_m), float(hi_m)],
            "includes_zero": bool(lo_m <= 0 <= hi_m),
        },
        "other_update_f1": {
            "point": point_other,
            "ci95": [float(lo_o), float(hi_o)],
            "includes_zero": bool(lo_o <= 0 <= hi_o),
        },
        "n_boot": N_BOOT,
        "seed": seed,
    }


def load_population():
    dev = {
        json.loads(line)["reddit_id"]: json.loads(line)
        for line in DEV.read_text(encoding="utf-8").splitlines()
        if line.strip()
    }
    # Re-parse once properly
    dev = {}
    for line in DEV.read_text(encoding="utf-8").splitlines():
        if line.strip():
            row = json.loads(line)
            dev[row["reddit_id"]] = row
    master = {
        r["reddit_id"]: r for r in json.loads(MASTER.read_text(encoding="utf-8"))
    }
    oof = [
        json.loads(line)
        for line in OOF.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    rows = []
    for item in oof:
        src = dev[item["reddit_id"]]
        url = master[item["reddit_id"]]["url"]
        host = host_of(url)
        if host != "reddit.com" and not host.endswith(".reddit.com"):
            raise SystemExit(f"non-Reddit row in saved folds: {item['reddit_id']} {host}")
        if item["reddit_id"] in NEAR_DUP:
            raise SystemExit("near-duplicate exclusion missing")
        if int(src["s2_target"]) != int(item["y_true"]):
            raise SystemExit(f"label mismatch {item['reddit_id']}")
        if not src.get("s2_in_scope"):
            raise SystemExit(f"non-S2 row in folds: {item['reddit_id']}")
        rows.append(src)
    y = np.array([int(r["s2_target"]) for r in rows], dtype=int)
    folds = np.array([int(item["fold"]) for item in oof], dtype=int)
    saved_scores = np.array([float(item["score"]) for item in oof])
    if len(rows) != 2136 or int((y == 1).sum()) != 1733 or int((y == 0).sum()) != 403:
        raise SystemExit(
            f"unexpected population {len(rows)} {(y == 1).sum()} {(y == 0).sum()}"
        )
    return rows, y, folds, saved_scores


def truncation_report(tokenizer, texts, y) -> dict:
    lengths = []
    truncated = np.zeros(len(texts), dtype=bool)
    for i, text in enumerate(texts):
        n_tok = len(tokenizer(text, add_special_tokens=True, truncation=False)["input_ids"])
        lengths.append(n_tok)
        truncated[i] = n_tok > MAX_WORDPIECES
    lengths = np.array(lengths)

    def pack(mask):
        n = int(mask.sum())
        k = int(truncated[mask].sum())
        return {
            "n": n,
            "truncated_n": k,
            "truncated_rate": (k / n) if n else None,
            "median_wordpieces": float(np.median(lengths[mask])) if n else None,
            "p90_wordpieces": float(np.percentile(lengths[mask], 90)) if n else None,
        }

    return {
        "max_wordpieces": MAX_WORDPIECES,
        "counting": "tokenizer input ids including special tokens; truncated if longer than 256",
        "all": pack(np.ones(len(texts), dtype=bool)),
        "troubleshooting_1": pack(y == 1),
        "other_update_0": pack(y == 0),
        "truncated": truncated,
        "n_wordpieces": lengths,
    }


def main() -> int:
    started = time.perf_counter()
    OUT.mkdir(parents=True, exist_ok=True)
    rows, y, folds, saved_scores = load_population()
    texts = [make_text(r, "title_body") for r in rows]

    from sentence_transformers import SentenceTransformer
    import sentence_transformers
    import torch
    import transformers
    import sklearn

    t0 = time.perf_counter()
    encoder = SentenceTransformer(MODEL_ID, device="cpu")
    load_s = time.perf_counter() - t0
    tokenizer = encoder.tokenizer
    trunc = truncation_report(tokenizer, texts, y)
    t1 = time.perf_counter()
    embeddings = np.asarray(
        encoder.encode(
            texts,
            batch_size=64,
            show_progress_bar=False,
            convert_to_numpy=True,
            normalize_embeddings=True,
        ),
        dtype=np.float32,
    )
    encode_s = time.perf_counter() - t1
    revision = getattr(encoder, "model_card_data", None)
    snapshot = None
    try:
        snapshot = Path(encoder.model_card_data.model_name) if False else None
    except Exception:
        snapshot = None
    cache_root = Path.home() / ".cache/huggingface/hub/models--sentence-transformers--all-MiniLM-L6-v2/snapshots"
    revision_hash = None
    if cache_root.exists():
        snaps = sorted(p for p in cache_root.iterdir() if p.is_dir())
        if snaps:
            revision_hash = snaps[-1].name

    n = len(rows)
    sem_score = np.full(n, np.nan)
    tfidf_score = np.full(n, np.nan)
    sem_pred = np.full(n, -1)
    tfidf_pred = np.full(n, -1)
    sem_thr = np.full(n, np.nan)
    tfidf_thr = np.full(n, np.nan)
    fixed_pred = np.full(n, -1)
    fold_reports = []
    tfidf_seconds = 0.0
    semantic_seconds = 0.0

    for fold in range(5):
        test_idx = np.flatnonzero(folds == fold)
        train_idx = np.flatnonzero(folds != fold)
        train_rows = [rows[i] for i in train_idx]
        _, groups = audit_within_dev(train_rows)
        y_tr = y[train_idx]
        emb_tr = embeddings[train_idx]
        text_tr = [texts[i] for i in train_idx]

        t_s = time.perf_counter()

        def sem_fit(tr, va, emb_tr=emb_tr, y_tr=y_tr):
            clf = semantic_head()
            clf.fit(emb_tr[tr], y_tr[tr])
            return clf.predict_proba(emb_tr[va])[:, 1]

        sem_choice = choose_threshold(inner_pieces(y_tr, groups, sem_fit))
        clf = semantic_head()
        clf.fit(emb_tr, y_tr)
        sem_held = clf.predict_proba(embeddings[test_idx])[:, 1]
        semantic_seconds += time.perf_counter() - t_s

        t_t = time.perf_counter()

        def tfidf_fit(tr, va, text_tr=text_tr, y_tr=y_tr):
            pipe = build_lr(4.0)
            pipe.fit([text_tr[i] for i in tr], y_tr[tr])
            return pipe.predict_proba([text_tr[i] for i in va])[:, 1]

        tfidf_choice = choose_threshold(inner_pieces(y_tr, groups, tfidf_fit))
        pipe = build_lr(4.0)
        pipe.fit(text_tr, y_tr)
        tfidf_held = pipe.predict_proba([texts[i] for i in test_idx])[:, 1]
        tfidf_seconds += time.perf_counter() - t_t

        sem_score[test_idx] = sem_held
        tfidf_score[test_idx] = tfidf_held
        sem_pred[test_idx] = (sem_held >= sem_choice["threshold"]).astype(int)
        tfidf_pred[test_idx] = (tfidf_held >= tfidf_choice["threshold"]).astype(int)
        sem_thr[test_idx] = sem_choice["threshold"]
        tfidf_thr[test_idx] = tfidf_choice["threshold"]
        fixed_pred[test_idx] = (tfidf_held >= 0.5877137791150834).astype(int)
        fold_reports.append(
            {
                "fold": fold,
                "n_train": int(len(train_idx)),
                "n_test": int(len(test_idx)),
                "train_class_counts": {
                    "troubleshooting_1": int((y_tr == 1).sum()),
                    "other_update_0": int((y_tr == 0).sum()),
                },
                "semantic_threshold": sem_choice["threshold"],
                "semantic_inner_macro_f1": next(
                    g["mean_inner_macro_f1"]
                    for g in sem_choice["grid"]
                    if g["threshold"] == sem_choice["threshold"]
                ),
                "tfidf_threshold": tfidf_choice["threshold"],
                "tfidf_inner_macro_f1": next(
                    g["mean_inner_macro_f1"]
                    for g in tfidf_choice["grid"]
                    if g["threshold"] == tfidf_choice["threshold"]
                ),
                "semantic_outer_metrics": metrics_at(y[test_idx], sem_pred[test_idx]),
                "tfidf_outer_metrics": metrics_at(y[test_idx], tfidf_pred[test_idx]),
            }
        )
        print(
            f"fold {fold}: semantic thr {sem_choice['threshold']} "
            f"tfidf thr {tfidf_choice['threshold']}",
            flush=True,
        )

    if not np.isfinite(sem_score).all() or min(sem_pred) < 0:
        raise SystemExit("incomplete outer predictions")

    sem_metrics = metrics_at(y, sem_pred)
    tfidf_metrics = metrics_at(y, tfidf_pred)
    delta = paired_delta(y, tfidf_pred, sem_pred)
    reproduction_gap = float(np.max(np.abs(tfidf_score - saved_scores)))

    report = {
        "code_version": CODE_VERSION,
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "reserved_test_used": False,
        "fresh_test_used": False,
        "population": {
            "n": int(len(rows)),
            "troubleshooting_1": int((y == 1).sum()),
            "other_update_0": int((y == 0).sum()),
        },
        "threshold_grid": THRESHOLD_GRID,
        "semantic": sem_metrics,
        "tfidf": tfidf_metrics,
        "paired_difference_semantic_minus_tfidf": delta,
        "by_source_pool": {
            "semantic": by_field(rows, y, sem_pred, "source_pool_audit_only"),
            "tfidf": by_field(rows, y, tfidf_pred, "source_pool_audit_only"),
        },
        "by_text_availability": {
            "semantic": by_field(rows, y, sem_pred, "text_availability"),
            "tfidf": by_field(rows, y, tfidf_pred, "text_availability"),
        },
        "folds": fold_reports,
        "truncation": {
            k: trunc[k]
            for k in ("max_wordpieces", "counting", "all", "troubleshooting_1", "other_update_0")
        },
        "saved_tfidf_score_reproduction_max_abs_gap": reproduction_gap,
        "saved_fixed_threshold_tfidf_macro_f1_on_these_scores": metrics_at(y, fixed_pred)["macro_f1"],
        "compute": {
            "device": "cpu",
            "encoder_load_seconds": round(load_s, 3),
            "encode_seconds": round(encode_s, 3),
            "semantic_head_seconds": round(semantic_seconds, 3),
            "tfidf_seconds": round(tfidf_seconds, 3),
            "wall_seconds": round(time.perf_counter() - started, 3),
            "platform": platform.platform(),
        },
    }
    (OUT / "metrics.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    (OUT / "fold_thresholds.json").write_text(
        json.dumps(fold_reports, indent=2) + "\n", encoding="utf-8"
    )
    with (OUT / "oof_predictions.jsonl").open("w", encoding="utf-8") as handle:
        for i, row in enumerate(rows):
            handle.write(
                json.dumps(
                    {
                        "reddit_id": row["reddit_id"],
                        "y_true": int(y[i]),
                        "fold": int(folds[i]),
                        "source_pool_audit_only": row.get("source_pool_audit_only"),
                        "text_availability": row.get("text_availability"),
                        "n_wordpieces": int(trunc["n_wordpieces"][i]),
                        "truncated_at_256": bool(trunc["truncated"][i]),
                        "semantic_score": float(sem_score[i]),
                        "semantic_threshold": float(sem_thr[i]),
                        "semantic_pred": int(sem_pred[i]),
                        "tfidf_score": float(tfidf_score[i]),
                        "tfidf_threshold": float(tfidf_thr[i]),
                        "tfidf_pred": int(tfidf_pred[i]),
                    }
                )
                + "\n"
            )

    manifest = {
        "code_version": CODE_VERSION,
        "git_head": git_head(),
        "created_utc": report["created_utc"],
        "model_id": MODEL_ID,
        "model_revision": revision_hash,
        "encoder_frozen": True,
        "encoder_not_finetuned": True,
        "normalize_embeddings": True,
        "semantic_head": "LogisticRegression C=1.0 class_weight=balanced liblinear max_iter=2000 random_state=42",
        "tfidf_comparator": "word unigrams+bigrams min_df=2 max_features=20000 sublinear_tf; LogisticRegression C=4 class_weight=balanced",
        "text": "make_text title+body: URLs removed, lowercased, whitespace collapsed. Comments, source, subreddit, and IDs are not predictors.",
        "outer_folds": "saved fold ids in post_audit_reddit_only_oof.jsonl",
        "inner_folds": "3 StratifiedGroupKFold on each outer training split, seed 42, exact/near-duplicate groups",
        "threshold_grid": THRESHOLD_GRID,
        "threshold_rule": "maximize mean inner macro-F1; ties broken by mean inner other-update F1, then closeness to 0.5",
        "packages": {
            "sentence_transformers": sentence_transformers.__version__,
            "transformers": transformers.__version__,
            "torch": torch.__version__,
            "scikit_learn": sklearn.__version__,
            "numpy": np.__version__,
        },
        "inputs": {
            "development": str(DEV),
            "development_sha256": sha256_file(DEV),
            "outer_folds": str(OOF),
            "outer_folds_sha256": sha256_file(OOF),
            "master_sha256": sha256_file(MASTER),
        },
        "tests_not_used": ["159-post reserved test", "344-post fresh test"],
        "compute": report["compute"],
        "model_card_name": getattr(revision, "model_name", MODEL_ID) if revision else MODEL_ID,
    }
    (HERE / "MANIFEST.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    write_results(report, manifest)
    print(
        json.dumps(
            {
                "semantic_macro_f1": sem_metrics["macro_f1"],
                "tfidf_macro_f1": tfidf_metrics["macro_f1"],
                "delta": delta["macro_f1"],
                "truncation_rate": trunc["all"]["truncated_rate"],
                "score_gap": reproduction_gap,
                "wall_seconds": report["compute"]["wall_seconds"],
            },
            indent=2,
        )
    )
    return 0


def write_results(report: dict, manifest: dict) -> None:
    sem = report["semantic"]
    tf = report["tfidf"]
    d = report["paired_difference_semantic_minus_tfidf"]
    tr = report["truncation"]
    better = d["macro_f1"]["point"] > 0 and not d["macro_f1"]["includes_zero"]
    if better:
        verdict = (
            "On these development folds the frozen MiniLM representation has a higher macro-F1 "
            "than TF-IDF, and the paired interval does not include zero."
        )
    elif d["macro_f1"]["includes_zero"]:
        verdict = (
            "The frozen MiniLM representation does not reliably beat the existing TF-IDF model "
            "on these development folds. The paired interval for the macro-F1 difference includes zero."
        )
    else:
        verdict = (
            "The frozen MiniLM representation is worse than the existing TF-IDF model on these "
            "development folds. That is a valid negative result; no other embedding model was tried."
        )
    lines = [
        "# Semantic comparator result",
        "",
        f"**Created:** {report['created_utc']}",
        "",
        "This is one development comparison. It does not score the reserved or fresh tests, and it is not evidence of a new architecture or of independent generalization.",
        "",
        "## Question and setup",
        "",
        "Does a frozen `all-MiniLM-L6-v2` sentence embedding separate troubleshooting from other software-update discussion more reliably than the existing title-and-body TF-IDF logistic regression, on the audited Reddit-only development posts?",
        "",
        f"Population: **{report['population']['n']}** posts, **{report['population']['troubleshooting_1']}** troubleshooting and **{report['population']['other_update_0']}** other update. Both models use the saved outer folds. Each outer training split chooses its own threshold from three inner grouped folds on the grid {', '.join(str(x) for x in THRESHOLD_GRID)}. The encoder is not fine-tuned. Semantic head: logistic regression `C=1`, class-balanced. TF-IDF head: `C=4`, class-balanced.",
        "",
        "## Outer-fold result",
        "",
        "| Model | macro-F1 | balanced acc. | other P/R/F1 | trouble P/R/F1 | confusion [[0,1]] |",
        "|---|---:|---:|---|---|---|",
        _row("TF-IDF LR", tf),
        _row("MiniLM + LR", sem),
        "",
        f"Paired bootstrap, MiniLM minus TF-IDF, {N_BOOT} resamples: macro-F1 **{d['macro_f1']['point']:+.4f}** (95% CI {d['macro_f1']['ci95'][0]:+.4f} to {d['macro_f1']['ci95'][1]:+.4f}; includes zero: {d['macro_f1']['includes_zero']}). Other-update F1 **{d['other_update_f1']['point']:+.4f}** (95% CI {d['other_update_f1']['ci95'][0]:+.4f} to {d['other_update_f1']['ci95'][1]:+.4f}).",
        "",
        verdict,
        "",
        "## Source pool and text availability",
        "",
        "### Source pool",
        "",
        "| Source | n | TF-IDF macro-F1 | MiniLM macro-F1 | TF-IDF other F1 | MiniLM other F1 |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    sources = sorted(set(report["by_source_pool"]["tfidf"]) | set(report["by_source_pool"]["semantic"]))
    for src in sources:
        a = report["by_source_pool"]["tfidf"][src]
        b = report["by_source_pool"]["semantic"][src]
        lines.append(
            f"| {src} | {a['n']} | {a['macro_f1']:.3f} | {b['macro_f1']:.3f} | "
            f"{a['class_0_other_update']['f1']:.3f} | {b['class_0_other_update']['f1']:.3f} |"
        )
    lines.extend(
        [
            "",
            "### Text availability",
            "",
            "| Availability | n | TF-IDF macro-F1 | MiniLM macro-F1 |",
            "|---|---:|---:|---:|",
        ]
    )
    for key in sorted(report["by_text_availability"]["tfidf"]):
        a = report["by_text_availability"]["tfidf"][key]
        b = report["by_text_availability"]["semantic"][key]
        lines.append(f"| {key} | {a['n']} | {a['macro_f1']:.3f} | {b['macro_f1']:.3f} |")
    lines.extend(
        [
            "",
            "Outside the dominant TPS pool, MiniLM is higher on the GDS pool and lower on the Phase 1 pool. That is not a consistent gain away from the main source.",
            "",
        ]
    )
    lines.extend(
        [
            "",
            "## Truncation and cost",
            "",
            f"MiniLM keeps 256 word-pieces. **{tr['all']['truncated_n']} / {tr['all']['n']}** posts ({tr['all']['truncated_rate']:.1%}) are longer than that before truncation: "
            f"{tr['troubleshooting_1']['truncated_n']} / {tr['troubleshooting_1']['n']} troubleshooting "
            f"({tr['troubleshooting_1']['truncated_rate']:.1%}) and "
            f"{tr['other_update_0']['truncated_n']} / {tr['other_update_0']['n']} other update "
            f"({tr['other_update_0']['truncated_rate']:.1%}). "
            f"Median length is {tr['all']['median_wordpieces']:.0f} word-pieces.",
            "",
            f"CPU wall time {report['compute']['wall_seconds']:.0f}s, of which encoding took {report['compute']['encode_seconds']:.0f}s and the TF-IDF fits took {report['compute']['tfidf_seconds']:.0f}s. Model revision `{manifest.get('model_revision')}`.",
            "",
            "The refit TF-IDF probabilities match the saved Reddit-only out-of-fold scores "
            f"(max absolute gap {report['saved_tfidf_score_reproduction_max_abs_gap']:.3e}). "
            f"Applying the historical 0.588 cutoff to those same scores gives macro-F1 {report['saved_fixed_threshold_tfidf_macro_f1_on_these_scores']:.3f}. "
            "The table above uses the inner-fold thresholds instead, so it is the fair comparison, not a reprint of that older cutoff.",
            "",
            "## What this does not show",
            "",
            "These folds reuse the audited development posts. A higher or lower development score is not a new test result. The reserved and fresh tests were not opened.",
            "",
        ]
    )
    (HERE / "RESULTS.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    (HERE / "RUN.md").write_text(
        """# Reproduce the semantic comparison

From the research repository root:

```bash
phase3/experiment_v1/.venv/bin/python phase3/semantic_comparator/run_semantic_comparator.py
```

The script downloads `sentence-transformers/all-MiniLM-L6-v2` on first run. It does not read the reserved or fresh tests.
""",
        encoding="utf-8",
    )


def _row(name, m):
    c0, c1 = m["class_0_other_update"], m["class_1_troubleshooting"]
    return (
        f"| {name} | {m['macro_f1']:.4f} | {m['balanced_accuracy']:.4f} | "
        f"{c0['precision']:.3f}/{c0['recall']:.3f}/{c0['f1']:.3f} | "
        f"{c1['precision']:.3f}/{c1['recall']:.3f}/{c1['f1']:.3f} | "
        f"`{m['confusion_matrix_labels_[0,1]']}` |"
    )


if __name__ == "__main__":
    raise SystemExit(main())
