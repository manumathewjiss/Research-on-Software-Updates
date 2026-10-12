#!/usr/bin/env python3
"""Development-only expansion on the frozen 2,050 Reddit-URL folds.

Does not read the reserved or fresh tests. Stops if the title+body
TF-IDF logistic regression does not reproduce macro-F1 0.8319320360990539.
"""

from __future__ import annotations

import hashlib
import json
import platform
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
from scipy.sparse import csr_matrix, hstack
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    balanced_accuracy_score,
    confusion_matrix,
    f1_score,
    precision_recall_fscore_support,
)
from sklearn.model_selection import StratifiedGroupKFold
from sklearn.preprocessing import StandardScaler

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
PHASE3 = REPO / "phase3"
sys.path.insert(0, str(HERE / "vendor"))
sys.path.insert(0, str(REPO / "phase5" / "sentiment_reanalysis" / "vendor"))
sys.path.insert(0, str(PHASE3 / "experiment_v1"))

from run_experiment import clean_text  # noqa: E402
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer  # noqa: E402
import sklearn
import vaderSentiment

REDDIT_DEV = PHASE3 / "reddit_only_sensitivity" / "development_reddit_only.jsonl"
REDDIT_OOF = PHASE3 / "reddit_only_sensitivity" / "results" / "grouped_oof_predictions.jsonl"
OUT = HERE / "results"
TARGET_MACRO = 0.8319320360990539
C = 4.0
SEED = 42
N_BOOT = 1000
THRESHOLD_GRID = [round(x, 2) for x in np.linspace(0.20, 0.80, 13)]
TOP_K = 25
# Predeclared before any contextual score is computed.
CONTEXTUAL_MODEL_ID = "cardiffnlp/twitter-roberta-base-sentiment-latest"
CONTEXTUAL_SCORE = "P(positive) - P(negative); neutral stays in the simplex and is not added"
CONTEXTUAL_MAX_LENGTH = 512


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def write_json(path: Path, payload) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def write_jsonl(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(json.dumps(r) + "\n" for r in rows), encoding="utf-8")


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def lr_head(C_value: float = C) -> LogisticRegression:
    return LogisticRegression(
        C=C_value,
        class_weight="balanced",
        max_iter=2000,
        solver="liblinear",
        random_state=SEED,
    )


def vectorizer() -> TfidfVectorizer:
    return TfidfVectorizer(
        ngram_range=(1, 2),
        min_df=2,
        max_features=20000,
        sublinear_tf=True,
    )


def metrics_at(y_true, y_pred) -> dict:
    y_true = np.asarray(y_true)
    y_pred = np.asarray(y_pred)
    p, r, f, s = precision_recall_fscore_support(y_true, y_pred, labels=[0, 1], zero_division=0)
    return {
        "n": int(len(y_true)),
        "support": {"other_update_0": int(s[0]), "troubleshooting_1": int(s[1])},
        "balanced_accuracy": float(balanced_accuracy_score(y_true, y_pred)),
        "macro_f1": float(f1_score(y_true, y_pred, average="macro", zero_division=0)),
        "class_0_other_update": {"precision": float(p[0]), "recall": float(r[0]), "f1": float(f[0])},
        "class_1_troubleshooting": {"precision": float(p[1]), "recall": float(r[1]), "f1": float(f[1])},
        "confusion_matrix_labels_[0,1]": confusion_matrix(y_true, y_pred, labels=[0, 1]).tolist(),
    }


def choose_threshold(pieces) -> float:
    best = None
    for thr in THRESHOLD_GRID:
        macros, others = [], []
        for y_val, proba in pieces:
            pred = (proba >= thr).astype(int)
            macros.append(f1_score(y_val, pred, average="macro", zero_division=0))
            others.append(f1_score(y_val, pred, pos_label=0, average="binary", zero_division=0))
        key = (float(np.mean(macros)), float(np.mean(others)), -abs(thr - 0.5))
        if best is None or key > best[0]:
            best = (key, thr)
    return float(best[1])


def inner_split(y, groups, fit_fn):
    splitter = StratifiedGroupKFold(n_splits=3, shuffle=True, random_state=SEED)
    pieces = []
    for tr, va in splitter.split(np.zeros(len(y)), y, groups):
        pieces.append((y[va], fit_fn(tr, va)))
    return pieces


def paired_delta(y, pred_base, pred_new) -> dict:
    rng = np.random.default_rng(SEED)
    y = np.asarray(y)
    pred_base = np.asarray(pred_base)
    pred_new = np.asarray(pred_new)

    def diff(idx=None):
        if idx is None:
            yt, a, b = y, pred_base, pred_new
        else:
            yt, a, b = y[idx], pred_base[idx], pred_new[idx]
        return float(
            f1_score(yt, b, average="macro", zero_division=0)
            - f1_score(yt, a, average="macro", zero_division=0)
        )

    point = diff()
    draws = [diff(rng.integers(0, len(y), len(y))) for _ in range(N_BOOT)]
    lo, hi = np.percentile(draws, [2.5, 97.5])
    return {
        "definition": "candidate minus title+body TF-IDF on the same posts",
        "point": point,
        "ci95": [float(lo), float(hi)],
        "includes_zero": bool(lo <= 0 <= hi),
        "n_boot": N_BOOT,
        "seed": SEED,
    }


def load_population():
    by_id = {r["reddit_id"]: r for r in read_jsonl(REDDIT_DEV)}
    oof = read_jsonl(REDDIT_OOF)
    if len(oof) != 2050:
        raise SystemExit(f"OOF row count changed: {len(oof)}")
    rows = []
    for item in oof:
        src = by_id.get(item["reddit_id"])
        if src is None:
            raise SystemExit(f"OOF id missing from development file: {item['reddit_id']}")
        if int(src["s2_target"]) != int(item["y_true"]):
            raise SystemExit(f"label mismatch {item['reddit_id']}")
        if item.get("verified_url_domain") != "reddit.com":
            raise SystemExit(f"sample definition changed, non-reddit row {item['reddit_id']}")
        rows.append(src)
    y = np.array([int(r["s2_target"]) for r in rows], dtype=int)
    folds = np.array([int(r["fold"]) for r in oof], dtype=int)
    groups = np.array([int(r["group_id"]) for r in oof], dtype=int)
    if int((y == 1).sum()) != 1658 or int((y == 0).sum()) != 392:
        raise SystemExit("class counts changed")
    bad_groups = []
    for gid in set(groups.tolist()):
        used = set(folds[groups == gid].tolist())
        if len(used) != 1:
            bad_groups.append(gid)
    if bad_groups:
        raise SystemExit(f"group crosses folds: {bad_groups[:5]}")
    id_fold = "\n".join(f"{r['reddit_id']}\t{int(f)}\t{int(g)}" for r, f, g in zip(rows, folds, groups))
    return rows, y, folds, groups, {
        "n": 2050,
        "troubleshooting": 1658,
        "other_update": 392,
        "development_sha256": sha256_file(REDDIT_DEV),
        "oof_sha256": sha256_file(REDDIT_OOF),
        "ordered_id_fold_group_sha256": hashlib.sha256(id_fold.encode()).hexdigest(),
        "n_groups": int(len(set(groups.tolist()))),
        "fold_counts": {str(i): int((folds == i).sum()) for i in range(5)},
    }


def input_text(row: dict, setting: str) -> str:
    title = row.get("title") or ""
    body = row.get("post_body") or ""
    if setting == "title":
        return clean_text(title)
    if setting == "body":
        return clean_text(body)
    if setting == "title_body":
        return clean_text(f"{title}\n{body}")
    raise SystemExit(setting)


def raw_document(row: dict) -> str:
    return f"{row.get('title') or ''}\n{row.get('post_body') or ''}"


def text_proba(texts_tr, y_tr, texts_va) -> np.ndarray:
    pipe_vec = vectorizer()
    x_tr = pipe_vec.fit_transform(texts_tr)
    x_va = pipe_vec.transform(texts_va)
    clf = lr_head()
    clf.fit(x_tr, y_tr)
    return clf.predict_proba(x_va)[:, 1]


def sentiment_proba(scores_tr, y_tr, scores_va) -> np.ndarray:
    scaler = StandardScaler()
    z_tr = scaler.fit_transform(np.asarray(scores_tr, dtype=float).reshape(-1, 1))
    clf = lr_head()
    clf.fit(z_tr, y_tr)
    z_va = scaler.transform(np.asarray(scores_va, dtype=float).reshape(-1, 1))
    return clf.predict_proba(z_va)[:, 1]


def hybrid_proba(texts_tr, scores_tr, y_tr, texts_va, scores_va) -> np.ndarray:
    pipe_vec = vectorizer()
    x_tr = pipe_vec.fit_transform(texts_tr)
    x_va = pipe_vec.transform(texts_va)
    scaler = StandardScaler()
    z_tr = scaler.fit_transform(np.asarray(scores_tr, dtype=float).reshape(-1, 1))
    z_va = scaler.transform(np.asarray(scores_va, dtype=float).reshape(-1, 1))
    clf = lr_head()
    clf.fit(hstack([x_tr, csr_matrix(z_tr)]), y_tr)
    return clf.predict_proba(hstack([x_va, csr_matrix(z_va)]))[:, 1]


def oof_text(texts, y, folds, groups):
    pred = np.full(len(y), -1)
    score = np.full(len(y), np.nan)
    thresholds = {}
    t0 = time.perf_counter()
    for fold in range(5):
        test = np.flatnonzero(folds == fold)
        train = np.flatnonzero(folds != fold)
        text_tr = [texts[i] for i in train]
        y_tr = y[train]
        g_tr = groups[train]

        def fit(tr, va, text_tr=text_tr, y_tr=y_tr):
            return text_proba([text_tr[i] for i in tr], y_tr[tr], [text_tr[i] for i in va])

        thr = choose_threshold(inner_split(y_tr, g_tr, fit))
        held = text_proba(text_tr, y_tr, [texts[i] for i in test])
        score[test] = held
        pred[test] = (held >= thr).astype(int)
        thresholds[str(fold)] = thr
        print(f"  text fold {fold} threshold {thr}", flush=True)
    elapsed = time.perf_counter() - t0
    if (pred < 0).any():
        raise SystemExit("incomplete text predictions")
    return pred, score, thresholds, elapsed


def oof_sentiment(scores, y, folds, groups):
    pred = np.full(len(y), -1)
    held_score = np.full(len(y), np.nan)
    thresholds = {}
    t0 = time.perf_counter()
    for fold in range(5):
        test = np.flatnonzero(folds == fold)
        train = np.flatnonzero(folds != fold)
        s_tr = scores[train]
        y_tr = y[train]
        g_tr = groups[train]

        def fit(tr, va, s_tr=s_tr, y_tr=y_tr):
            return sentiment_proba(s_tr[tr], y_tr[tr], s_tr[va])

        thr = choose_threshold(inner_split(y_tr, g_tr, fit))
        held = sentiment_proba(s_tr, y_tr, scores[test])
        held_score[test] = held
        pred[test] = (held >= thr).astype(int)
        thresholds[str(fold)] = thr
    return pred, held_score, thresholds, time.perf_counter() - t0


def oof_hybrid(texts, scores, y, folds, groups):
    pred = np.full(len(y), -1)
    held_score = np.full(len(y), np.nan)
    thresholds = {}
    t0 = time.perf_counter()
    for fold in range(5):
        test = np.flatnonzero(folds == fold)
        train = np.flatnonzero(folds != fold)
        text_tr = [texts[i] for i in train]
        s_tr = scores[train]
        y_tr = y[train]
        g_tr = groups[train]

        def fit(tr, va, text_tr=text_tr, s_tr=s_tr, y_tr=y_tr):
            return hybrid_proba(
                [text_tr[i] for i in tr],
                s_tr[tr],
                y_tr[tr],
                [text_tr[i] for i in va],
                s_tr[va],
            )

        thr = choose_threshold(inner_split(y_tr, g_tr, fit))
        held = hybrid_proba(text_tr, s_tr, y_tr, [texts[i] for i in test], scores[test])
        held_score[test] = held
        pred[test] = (held >= thr).astype(int)
        thresholds[str(fold)] = thr
        print(f"  hybrid fold {fold} threshold {thr}", flush=True)
    return pred, held_score, thresholds, time.perf_counter() - t0


def subgroup(y, pred, mask, name) -> dict:
    if int(mask.sum()) == 0:
        return {"name": name, "n": 0}
    return {"name": name, **metrics_at(y[mask], pred[mask])}


def vader_scores(rows) -> tuple[np.ndarray, dict]:
    analyzer = SentimentIntensityAnalyzer()
    out = np.empty(len(rows), dtype=float)
    empty = 0
    for i, row in enumerate(rows):
        text = raw_document(row)
        if not text.strip():
            out[i] = 0.0
            empty += 1
        else:
            out[i] = float(analyzer.polarity_scores(text)["compound"])
    return out, {
        "tool": "VADER",
        "version": getattr(vaderSentiment, "__version__", "unknown"),
        "package_file": getattr(vaderSentiment, "__file__", ""),
        "input": "raw title, newline, raw body",
        "empty_or_whitespace": "0.0, which collides with genuine neutral",
        "empty_n": empty,
        "exact_zero_n": int((out == 0).sum()),
    }


def textblob_scores(rows) -> tuple[np.ndarray, dict]:
    from textblob import TextBlob
    import textblob

    out = np.empty(len(rows), dtype=float)
    empty = 0
    for i, row in enumerate(rows):
        text = raw_document(row)
        if not text.strip():
            out[i] = 0.0
            empty += 1
        else:
            out[i] = float(TextBlob(text).sentiment.polarity)
    return out, {
        "tool": "TextBlob polarity",
        "version": getattr(textblob, "__version__", "unknown"),
        "input": "same raw title, newline, raw body as VADER",
        "range": "[-1, 1]",
        "empty_or_whitespace": "0.0, which collides with genuine neutral",
        "empty_n": empty,
        "exact_zero_n": int((out == 0).sum()),
    }


def contextual_scores(rows) -> tuple[np.ndarray | None, dict]:
    """Frozen Cardiff Twitter RoBERTa. Returns None and a blocker on failure."""
    info = {
        "model_id": CONTEXTUAL_MODEL_ID,
        "predeclared_score": CONTEXTUAL_SCORE,
        "max_length": CONTEXTUAL_MAX_LENGTH,
        "fine_tuned": False,
    }
    try:
        import torch
        from transformers import AutoConfig, AutoModelForSequenceClassification, AutoTokenizer
    except Exception as exc:
        info["status"] = "blocked"
        info["blocker"] = f"import failed: {type(exc).__name__}: {exc}"
        return None, info
    t0 = time.perf_counter()
    try:
        config = AutoConfig.from_pretrained(CONTEXTUAL_MODEL_ID)
        tokenizer = AutoTokenizer.from_pretrained(CONTEXTUAL_MODEL_ID)
        model = AutoModelForSequenceClassification.from_pretrained(CONTEXTUAL_MODEL_ID)
    except Exception as exc:
        info["status"] = "blocked"
        info["blocker"] = f"download or load failed: {type(exc).__name__}: {exc}"
        info["seconds"] = time.perf_counter() - t0
        return None, info
    id2label = {int(k): str(v).lower() for k, v in config.id2label.items()}
    needed = {"negative": None, "neutral": None, "positive": None}
    for idx, name in id2label.items():
        for key in needed:
            if key in name:
                needed[key] = idx
    if any(v is None for v in needed.values()):
        info["status"] = "blocked"
        info["blocker"] = f"unexpected labels: {config.id2label}"
        return None, info
    model.eval()
    texts = [raw_document(r) for r in rows]
    empty = np.array([not t.strip() for t in texts])
    lengths = []
    for text in texts:
        if not text.strip():
            lengths.append(0)
        else:
            lengths.append(len(tokenizer(text, add_special_tokens=True, truncation=False)["input_ids"]))
    lengths = np.asarray(lengths)
    scores = np.zeros(len(texts), dtype=float)
    batch = 16
    usable = [i for i, flag in enumerate(empty) if not flag]
    with torch.no_grad():
        for start in range(0, len(usable), batch):
            chunk = usable[start : start + batch]
            enc = tokenizer(
                [texts[i] for i in chunk],
                padding=True,
                truncation=True,
                max_length=CONTEXTUAL_MAX_LENGTH,
                return_tensors="pt",
            )
            prob = torch.softmax(model(**enc).logits, dim=-1).cpu().numpy()
            scores[chunk] = prob[:, needed["positive"]] - prob[:, needed["negative"]]
    info.update(
        {
            "status": "scored",
            "id2label": config.id2label,
            "label_indexes": needed,
            "transformers_name_or_path": CONTEXTUAL_MODEL_ID,
            "empty_n": int(empty.sum()),
            "empty_score": 0.0,
            "truncated_n": int((lengths > CONTEXTUAL_MAX_LENGTH).sum()),
            "median_tokens_including_special": float(np.median(lengths)),
            "seconds": time.perf_counter() - t0,
            "torch": torch.__version__,
        }
    )
    try:
        import transformers

        info["transformers"] = transformers.__version__
    except Exception:
        pass
    return scores, info


def sentiment_block(name, scores, meta, texts, y, folds, groups, text_pred):
    alone_pred, alone_proba, alone_thr, alone_s = oof_sentiment(scores, y, folds, groups)
    hyb_pred, hyb_proba, hyb_thr, hyb_s = oof_hybrid(texts, scores, y, folds, groups)
    return {
        "meta": meta,
        "sentiment_only": {
            "metrics": metrics_at(y, alone_pred),
            "thresholds": alone_thr,
            "seconds": alone_s,
            "paired_minus_title_body": paired_delta(y, text_pred, alone_pred),
        },
        "title_body_plus_score": {
            "metrics": metrics_at(y, hyb_pred),
            "thresholds": hyb_thr,
            "seconds": hyb_s,
            "paired_minus_title_body": paired_delta(y, text_pred, hyb_pred),
        },
        "_pred_only": alone_pred,
        "_pred_plus": hyb_pred,
        "_score": scores,
    }


def minilm_block(texts, y, folds, groups, text_pred):
    info = {"model_id": "sentence-transformers/all-MiniLM-L6-v2", "fine_tuned": False, "device": "cpu"}
    t0 = time.perf_counter()
    try:
        from sentence_transformers import SentenceTransformer
        import sentence_transformers
    except Exception as exc:
        info["status"] = "blocked"
        info["blocker"] = f"{type(exc).__name__}: {exc}"
        return info, None
    encoder = SentenceTransformer(info["model_id"], device="cpu")
    embeddings = np.asarray(
        encoder.encode(texts, batch_size=64, show_progress_bar=False, convert_to_numpy=True, normalize_embeddings=True),
        dtype=np.float32,
    )
    info["sentence_transformers"] = sentence_transformers.__version__
    info["embedding_dim"] = int(embeddings.shape[1])
    info["encode_seconds"] = time.perf_counter() - t0
    cache = Path.home() / ".cache/huggingface/hub/models--sentence-transformers--all-MiniLM-L6-v2/snapshots"
    if cache.exists():
        snaps = sorted(p.name for p in cache.iterdir() if p.is_dir())
        info["local_snapshot_dirs"] = snaps
    pred = np.full(len(y), -1)
    thresholds = {}
    t1 = time.perf_counter()
    for fold in range(5):
        test = np.flatnonzero(folds == fold)
        train = np.flatnonzero(folds != fold)
        emb_tr = embeddings[train]
        y_tr = y[train]
        g_tr = groups[train]

        def fit(tr, va, emb_tr=emb_tr, y_tr=y_tr):
            clf = lr_head(1.0)
            clf.fit(emb_tr[tr], y_tr[tr])
            return clf.predict_proba(emb_tr[va])[:, 1]

        thr = choose_threshold(inner_split(y_tr, g_tr, fit))
        clf = lr_head(1.0)
        clf.fit(emb_tr, y_tr)
        held = clf.predict_proba(embeddings[test])[:, 1]
        pred[test] = (held >= thr).astype(int)
        thresholds[str(fold)] = thr
        print(f"  minilm fold {fold} threshold {thr}", flush=True)
    info["status"] = "scored"
    info["head"] = "logistic regression C=1 class-balanced liblinear, not fine-tuned"
    info["thresholds"] = thresholds
    info["fit_seconds"] = time.perf_counter() - t1
    info["metrics"] = metrics_at(y, pred)
    info["paired_minus_title_body"] = paired_delta(y, text_pred, pred)
    return info, pred


def export_coefficients(texts, y):
    """One fit on all 2,050 development rows. Associative, not a test score."""
    t0 = time.perf_counter()
    vec = vectorizer()
    x = vec.fit_transform(texts)
    clf = lr_head()
    clf.fit(x, y)
    names = np.asarray(vec.get_feature_names_out())
    coef = clf.coef_.ravel()
    order = np.argsort(coef)
    def pack(idx):
        return [{"feature": str(names[i]), "coefficient": float(coef[i])} for i in idx]

    payload = {
        "fit": "all 2050 Reddit-URL development rows; not an outer-fold score",
        "interpretation": "associative with the troubleshooting class in this fit; not causal and not a held-out result",
        "positive_coefficient_means": "higher log-odds of troubleshooting versus other update discussion",
        "intercept": float(clf.intercept_[0]),
        "n_features": int(len(names)),
        "toward_troubleshooting": pack(order[-TOP_K:][::-1]),
        "toward_other_update": pack(order[:TOP_K]),
        "seconds": time.perf_counter() - t0,
    }
    return payload


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    started = now()
    rows, y, folds, groups, identity = load_population()
    write_json(OUT / "population_check.json", identity)
    print("population check passed", identity["n"], flush=True)
    empty_body = np.array([not str(r.get("post_body") or "").strip() for r in rows])
    empty_title = np.array([not str(r.get("title") or "").strip() for r in rows])
    supports = {
        "n": 2050,
        "empty_title": int(empty_title.sum()),
        "empty_body": int(empty_body.sum()),
        "empty_title_by_class": {
            "other_update_0": int(((y == 0) & empty_title).sum()),
            "troubleshooting_1": int(((y == 1) & empty_title).sum()),
        },
        "empty_body_by_class": {
            "other_update_0": int(((y == 0) & empty_body).sum()),
            "troubleshooting_1": int(((y == 1) & empty_body).sum()),
        },
        "note": "Missing title or body is retained as an empty string. Posts are not dropped.",
    }
    write_json(OUT / "input_supports.json", supports)

    texts = {
        "title": [input_text(r, "title") for r in rows],
        "body": [input_text(r, "body") for r in rows],
        "title_body": [input_text(r, "title_body") for r in rows],
    }
    print("reproducing title+body", flush=True)
    tb_pred, tb_score, tb_thr, tb_seconds = oof_text(texts["title_body"], y, folds, groups)
    tb_metrics = metrics_at(y, tb_pred)
    gap = abs(tb_metrics["macro_f1"] - TARGET_MACRO)
    repro = {
        "target_macro_f1": TARGET_MACRO,
        "observed_macro_f1": tb_metrics["macro_f1"],
        "abs_gap": gap,
        "passed": gap <= 1e-9,
        "thresholds": tb_thr,
        "seconds": tb_seconds,
        "metrics": tb_metrics,
        "sklearn": sklearn.__version__,
        "python": platform.python_version(),
    }
    write_json(OUT / "reproduction_title_body.json", repro)
    if not repro["passed"]:
        write_json(
            OUT / "REPRODUCTION_FAILURE.json",
            {"message": "title+body macro-F1 did not match the saved inner-threshold result", **repro},
        )
        print("REPRODUCTION FAILED", repro["observed_macro_f1"], file=sys.stderr)
        return 2
    print("reproduction passed", tb_metrics["macro_f1"], flush=True)

    ablation = {"title_body": {"metrics": tb_metrics, "thresholds": tb_thr, "seconds": tb_seconds, "subgroups": [
        subgroup(y, tb_pred, ~empty_body, "has_body"),
        subgroup(y, tb_pred, empty_body, "empty_body"),
    ]}}
    preds = {"title_body": tb_pred}
    for setting in ("title", "body"):
        print("ablation", setting, flush=True)
        pred, score, thr, seconds = oof_text(texts[setting], y, folds, groups)
        ablation[setting] = {
            "metrics": metrics_at(y, pred),
            "thresholds": thr,
            "seconds": seconds,
            "paired_minus_title_body": paired_delta(y, tb_pred, pred),
            "subgroups": [
                subgroup(y, pred, ~empty_body, "has_body"),
                subgroup(y, pred, empty_body, "empty_body"),
            ],
        }
        preds[setting] = pred
    write_json(OUT / "ablation.json", ablation)

    print("coefficients", flush=True)
    write_json(OUT / "tfidf_coefficients.json", export_coefficients(texts["title_body"], y))

    print("VADER", flush=True)
    v_scores, v_meta = vader_scores(rows)
    vader = sentiment_block("vader", v_scores, v_meta, texts["title_body"], y, folds, groups, tb_pred)
    print("TextBlob", flush=True)
    b_scores, b_meta = textblob_scores(rows)
    blob = sentiment_block("textblob", b_scores, b_meta, texts["title_body"], y, folds, groups, tb_pred)

    print("contextual sentiment", flush=True)
    c_scores, c_meta = contextual_scores(rows)
    contextual = {"meta": c_meta}
    c_pred_only = c_pred_plus = None
    if c_scores is not None:
        contextual = sentiment_block("contextual", c_scores, c_meta, texts["title_body"], y, folds, groups, tb_pred)
        c_pred_only = contextual.pop("_pred_only")
        c_pred_plus = contextual.pop("_pred_plus")
        np.save(OUT / "contextual_scores.npy", contextual.pop("_score"))
    write_json(OUT / "sentiment_comparison.json", {
        "vader": {k: v for k, v in vader.items() if not k.startswith("_")},
        "textblob": {k: v for k, v in blob.items() if not k.startswith("_")},
        "contextual": {k: v for k, v in contextual.items() if not str(k).startswith("_")},
        "baseline_title_body_macro_f1": tb_metrics["macro_f1"],
    })

    print("MiniLM", flush=True)
    mini_info, mini_pred = minilm_block(texts["title_body"], y, folds, groups, tb_pred)
    write_json(OUT / "minilm.json", {k: v for k, v in mini_info.items()})

    pred_rows = []
    for i, row in enumerate(rows):
        item = {
            "reddit_id": row["reddit_id"],
            "fold": int(folds[i]),
            "group_id": int(groups[i]),
            "y_true": int(y[i]),
            "empty_body": bool(empty_body[i]),
            "pred_title": int(preds["title"][i]),
            "pred_body": int(preds["body"][i]),
            "pred_title_body": int(tb_pred[i]),
            "score_title_body": float(tb_score[i]),
            "pred_vader_only": int(vader["_pred_only"][i]),
            "pred_title_body_plus_vader": int(vader["_pred_plus"][i]),
            "vader_compound": float(vader["_score"][i]),
            "pred_textblob_only": int(blob["_pred_only"][i]),
            "pred_title_body_plus_textblob": int(blob["_pred_plus"][i]),
            "textblob_polarity": float(blob["_score"][i]),
        }
        if c_pred_only is not None:
            item["pred_contextual_only"] = int(c_pred_only[i])
            item["pred_title_body_plus_contextual"] = int(c_pred_plus[i])
            item["contextual_score"] = float(c_scores[i])
        if mini_pred is not None:
            item["pred_minilm"] = int(mini_pred[i])
        pred_rows.append(item)
    write_jsonl(OUT / "predictions.jsonl", pred_rows)

    table_path = OUT / "metrics_table.csv"
    lines = ["arm,macro_f1,other_f1,trouble_f1,paired_minus_title_body,ci_low,ci_high,includes_zero"]
    def add(name, metrics, delta=None):
        if delta is None:
            lines.append(f"{name},{metrics['macro_f1']:.6f},{metrics['class_0_other_update']['f1']:.6f},{metrics['class_1_troubleshooting']['f1']:.6f},,,,")
        else:
            lines.append(
                f"{name},{metrics['macro_f1']:.6f},{metrics['class_0_other_update']['f1']:.6f},{metrics['class_1_troubleshooting']['f1']:.6f},{delta['point']:.6f},{delta['ci95'][0]:.6f},{delta['ci95'][1]:.6f},{delta['includes_zero']}"
            )
    add("title_body", tb_metrics)
    add("title", ablation["title"]["metrics"], ablation["title"]["paired_minus_title_body"])
    add("body", ablation["body"]["metrics"], ablation["body"]["paired_minus_title_body"])
    add("vader_only", vader["sentiment_only"]["metrics"], vader["sentiment_only"]["paired_minus_title_body"])
    add("title_body_plus_vader", vader["title_body_plus_score"]["metrics"], vader["title_body_plus_score"]["paired_minus_title_body"])
    add("textblob_only", blob["sentiment_only"]["metrics"], blob["sentiment_only"]["paired_minus_title_body"])
    add("title_body_plus_textblob", blob["title_body_plus_score"]["metrics"], blob["title_body_plus_score"]["paired_minus_title_body"])
    if c_scores is not None:
        add("contextual_only", contextual["sentiment_only"]["metrics"], contextual["sentiment_only"]["paired_minus_title_body"])
        add("title_body_plus_contextual", contextual["title_body_plus_score"]["metrics"], contextual["title_body_plus_score"]["paired_minus_title_body"])
    if mini_pred is not None:
        add("minilm", mini_info["metrics"], mini_info["paired_minus_title_body"])
    table_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    write_json(OUT / "run_manifest.json", {
        "started_utc": started,
        "finished_utc": now(),
        "reproduction_passed": True,
        "held_out_tests_read": False,
        "sklearn": sklearn.__version__,
        "python": platform.python_version(),
        "contextual_status": c_meta.get("status"),
        "minilm_status": mini_info.get("status"),
    })
    print("done", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
