#!/usr/bin/env python3
"""Staged development sentiment analysis for a new paper packet.

Stage A repeats the frozen title/body VADER comparison by verifying its files.
Stage B describes comment sentiment on the development subset that has saved comments.
Stage C compares text and sentiment features on that same subset.
Reserved and fresh tests are not read or scored.
"""

from __future__ import annotations

import hashlib
import json
import platform
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
from scipy import stats
from scipy.sparse import csr_matrix, hstack
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    balanced_accuracy_score,
    confusion_matrix,
    f1_score,
    precision_recall_fscore_support,
)
from sklearn.naive_bayes import MultinomialNB
from sklearn.model_selection import StratifiedGroupKFold
from sklearn.preprocessing import StandardScaler
from sklearn.svm import LinearSVC

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
PHASE3 = REPO / "phase3"
sys.path.insert(0, str(REPO / "phase5" / "sentiment_reanalysis" / "vendor"))
sys.path.insert(0, str(PHASE3 / "experiment_v1"))
sys.path.insert(0, str(REPO))

from run_experiment import build_lr, clean_text, make_text  # noqa: E402
from evaluation.models.vader_rules import vader_rule_predict  # noqa: E402
from trajectory.build import load_raw_posts_by_id  # noqa: E402
from trajectory.sentiment import compound_score  # noqa: E402
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer  # noqa: E402
import sklearn  # noqa: E402
import vaderSentiment  # noqa: E402

OUT = HERE / "results"
FIG = OUT / "figures"
PRIOR = REPO / "phase5" / "sentiment_reanalysis"
PRIOR_METRICS = PRIOR / "results" / "reddit_2050" / "pooled_metrics.json"
REDDIT_DEV = PHASE3 / "reddit_only_sensitivity" / "development_reddit_only.jsonl"
REDDIT_OOF = PHASE3 / "reddit_only_sensitivity" / "results" / "grouped_oof_predictions.jsonl"
OLD_RAW = REPO / "tps_gds_classification" / "data" / "raw"
OCT5 = REPO / "phase2" / "new_sources" / "api"
OCT5_FILES = [
    "tps_response.json",
    "tps_page_2.json",
    "tps_page_3.json",
    "tps_page_4.json",
    "tps_page_5.json",
    "gds_response.json",
]
C = 4.0
SEED = 42
N_BOOT = 1000
THRESHOLD_GRID = [round(x, 2) for x in np.linspace(0.20, 0.80, 13)]
# Predeclared before subset scores are computed. Both-role coverage below this
# fraction cannot support a strong comment-feature classifier claim.
STRONG_COMMENT_CLAIM_MIN_BOTH_ROLE_FRACTION = 0.50
CODE_VERSION = "sentiment-paper-dev-v2"


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
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def load_oct5() -> dict[str, dict]:
    out = {}
    for name in OCT5_FILES:
        payload = json.loads((OCT5 / name).read_text(encoding="utf-8"))
        for post in payload.get("data") or []:
            rid = str(post.get("redditId") or "").strip()
            if rid and rid not in out:
                out[rid] = post
    return out


def load_population():
    by_id = {r["reddit_id"]: r for r in read_jsonl(REDDIT_DEV)}
    oof = read_jsonl(REDDIT_OOF)
    rows = []
    for item in oof:
        src = by_id[item["reddit_id"]]
        if int(src["s2_target"]) != int(item["y_true"]):
            raise SystemExit(f"label mismatch {item['reddit_id']}")
        rows.append(src)
    y = np.array([int(r["s2_target"]) for r in rows], dtype=int)
    folds = np.array([int(r["fold"]) for r in oof], dtype=int)
    groups = np.array([int(r["group_id"]) for r in oof], dtype=int)
    if len(rows) != 2050 or int((y == 1).sum()) != 1658 or int((y == 0).sum()) != 392:
        raise SystemExit("unexpected S2 population")
    return rows, y, folds, groups


def roles(post: dict) -> dict:
    author = (post.get("author") or "").strip()
    author_text = []
    community_text = []
    author_time = []
    community_time = []
    for c in post.get("comments") or []:
        body = (c.get("body") or "").strip()
        if not body:
            continue
        is_author = bool(c.get("is_submitter")) or (
            author and (c.get("author") or "").strip() == author
        )
        when = str(c.get("created_utc") or "")
        if is_author:
            author_text.append(body)
            author_time.append(when)
        else:
            community_text.append(body)
            community_time.append(when)
    return {
        "author_text": author_text,
        "community_text": community_text,
        "author_time": author_time,
        "community_time": community_time,
        "num_comments": post.get("num_comments"),
        "n_stored": len(post.get("comments") or []),
        "post_time": str(post.get("created_utc") or ""),
    }


def full_thread_document(post: dict) -> tuple[str, dict]:
    """Fixed thread string: title, body, then nonempty comments by saved timestamp.

    Author replies and community comments are both included. No role token is
    added. The same string is the text baseline and the text half of the hybrid.
    """
    comments = sorted(post.get("comments") or [], key=lambda c: str(c.get("created_utc") or ""))
    parts = [post.get("title") or "", post.get("author_description") or ""]
    post_time = str(post.get("created_utc") or "")
    timing = {
        "stored_comments": 0,
        "nonempty_comments": 0,
        "timestamp_missing": 0,
        "timestamp_before_post": 0,
        "timestamp_at_or_after_post": 0,
        "post_timestamp_missing": not post_time,
    }
    for comment in comments:
        timing["stored_comments"] += 1
        body = (comment.get("body") or "").strip()
        if not body:
            continue
        timing["nonempty_comments"] += 1
        parts.append(body)
        when = str(comment.get("created_utc") or "")
        if not when or not post_time:
            timing["timestamp_missing"] += 1
        elif when < post_time:
            timing["timestamp_before_post"] += 1
        else:
            timing["timestamp_at_or_after_post"] += 1
    return clean_text("\n".join(parts)), timing


def mean_compound(analyzer, texts: list[str]) -> float | None:
    if not texts:
        return None
    return float(np.mean([compound_score(analyzer, t) for t in texts]))


def metrics_at(y_true, y_pred) -> dict:
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
    return best[1]


def inner_split(y, groups, fit_fn):
    splitter = StratifiedGroupKFold(n_splits=3, shuffle=True, random_state=SEED)
    pieces = []
    for tr, va in splitter.split(np.zeros(len(y)), y, groups):
        pieces.append((y[va], fit_fn(tr, va)))
    return pieces


def lr():
    return LogisticRegression(
        C=C, class_weight="balanced", max_iter=2000, solver="liblinear", random_state=SEED
    )


def text_proba(texts_tr, y_tr, texts_va):
    pipe = build_lr(C)
    pipe.fit(texts_tr, y_tr)
    return pipe.predict_proba(texts_va)[:, 1]


def nb_proba(texts_tr, y_tr, texts_va):
    pipe = build_lr(C)
    # Replace the logistic head so the vectorizer matches the text baseline.
    x_tr = pipe.named_steps["tfidf"].fit_transform(texts_tr)
    x_va = pipe.named_steps["tfidf"].transform(texts_va)
    clf = MultinomialNB()
    clf.fit(x_tr, y_tr)
    return clf.predict_proba(x_va)[:, list(clf.classes_).index(1)]


def sentiment_matrix(comp, author, community, author_missing, community_missing):
    return np.column_stack(
        [
            comp,
            author,
            community,
            author_missing,
            community_missing,
        ]
    ).astype(float)


def hybrid_proba(texts_tr, extra_tr, y_tr, texts_va, extra_va, n_continuous=3):
    pipe = build_lr(C)
    pipe.fit(texts_tr, y_tr)
    x_tr = pipe.named_steps["tfidf"].transform(texts_tr)
    x_va = pipe.named_steps["tfidf"].transform(texts_va)
    scaler = StandardScaler()
    # Scale continuous sentiment columns only. Missingness indicators stay 0/1.
    z_tr = extra_tr.copy()
    z_va = extra_va.copy()
    z_tr[:, :n_continuous] = scaler.fit_transform(extra_tr[:, :n_continuous])
    z_va[:, :n_continuous] = scaler.transform(extra_va[:, :n_continuous])
    clf = lr()
    clf.fit(hstack([x_tr, csr_matrix(z_tr)]), y_tr)
    return clf.predict_proba(hstack([x_va, csr_matrix(z_va)]))[:, 1]


def paired_delta(y, pred_a, pred_b) -> dict:
    rng = np.random.default_rng(SEED)
    y = np.asarray(y)
    pred_a = np.asarray(pred_a)
    pred_b = np.asarray(pred_b)

    def diff(idx=None):
        if idx is None:
            yt, a, b = y, pred_a, pred_b
        else:
            yt, a, b = y[idx], pred_a[idx], pred_b[idx]
        return float(
            f1_score(yt, b, average="macro", zero_division=0)
            - f1_score(yt, a, average="macro", zero_division=0)
        )

    point = diff()
    draws = [diff(rng.integers(0, len(y), len(y))) for _ in range(N_BOOT)]
    lo, hi = np.percentile(draws, [2.5, 97.5])
    return {
        "point": point,
        "ci95": [float(lo), float(hi)],
        "includes_zero": bool(lo <= 0 <= hi),
        "n_boot": N_BOOT,
        "seed": SEED,
    }


def mean_diff(a, b) -> dict:
    a = np.asarray(a, dtype=float)
    b = np.asarray(b, dtype=float)
    if len(a) < 2 or len(b) < 2:
        return {"n_a": int(len(a)), "n_b": int(len(b)), "mean_a": None, "mean_b": None}
    welch = stats.ttest_ind(a, b, equal_var=False)
    rng = np.random.default_rng(SEED)
    draws = []
    for _ in range(N_BOOT):
        draws.append(float(rng.choice(a, len(a), replace=True).mean() - rng.choice(b, len(b), replace=True).mean()))
    lo, hi = np.percentile(draws, [2.5, 97.5])
    return {
        "n_a": int(len(a)),
        "n_b": int(len(b)),
        "mean_a": float(a.mean()),
        "mean_b": float(b.mean()),
        "difference_a_minus_b": float(a.mean() - b.mean()),
        "welch_p": float(welch.pvalue),
        "bootstrap_ci95": [float(lo), float(hi)],
        "ci_includes_zero": bool(lo <= 0 <= hi),
    }


def evaluate(texts, y, folds, groups, extra=None, keyword=None, include_nb_svm=False, n_continuous=3):
    n = len(y)
    text_pred = np.full(n, -1)
    sent_pred = np.full(n, -1)
    hyb_pred = np.full(n, -1)
    nb_pred = np.full(n, -1)
    svm_pred = np.full(n, -1)
    kw_pred = np.array(keyword if keyword is not None else np.full(n, -1), dtype=int)
    fold_rows = []
    for fold in sorted(set(folds.tolist())):
        test = np.flatnonzero(folds == fold)
        train = np.flatnonzero(folds != fold)
        y_tr = y[train]
        g_tr = groups[train]
        text_tr = [texts[i] for i in train]
        text_te = [texts[i] for i in test]

        def text_fit(tr, va, text_tr=text_tr, y_tr=y_tr):
            return text_proba([text_tr[i] for i in tr], y_tr[tr], [text_tr[i] for i in va])

        text_thr = choose_threshold(inner_split(y_tr, g_tr, text_fit))
        text_held = text_proba(text_tr, y_tr, text_te)
        text_pred[test] = (text_held >= text_thr).astype(int)
        report = {"fold": int(fold), "n_test": int(len(test)), "text_threshold": text_thr}
        if extra is not None:
            comp_tr = extra[train, 0]

            def sent_fit(tr, va, comp_tr=comp_tr, y_tr=y_tr):
                scaler = StandardScaler()
                z_tr = scaler.fit_transform(comp_tr[tr].reshape(-1, 1))
                clf = lr()
                clf.fit(z_tr, y_tr[tr])
                return clf.predict_proba(scaler.transform(comp_tr[va].reshape(-1, 1)))[:, 1]

            sent_thr = choose_threshold(inner_split(y_tr, g_tr, sent_fit))
            scaler = StandardScaler()
            clf = lr()
            clf.fit(scaler.fit_transform(comp_tr.reshape(-1, 1)), y_tr)
            sent_held = clf.predict_proba(scaler.transform(extra[test, 0].reshape(-1, 1)))[:, 1]
            sent_pred[test] = (sent_held >= sent_thr).astype(int)

            def hyb_fit(tr, va, text_tr=text_tr, extra=extra, train=train, y_tr=y_tr, n_continuous=n_continuous):
                return hybrid_proba(
                    [text_tr[i] for i in tr],
                    extra[train][tr],
                    y_tr[tr],
                    [text_tr[i] for i in va],
                    extra[train][va],
                    n_continuous=n_continuous,
                )

            hyb_thr = choose_threshold(inner_split(y_tr, g_tr, hyb_fit))
            hyb_held = hybrid_proba(
                text_tr, extra[train], y_tr, text_te, extra[test], n_continuous=n_continuous
            )
            hyb_pred[test] = (hyb_held >= hyb_thr).astype(int)
            report["sentiment_threshold"] = sent_thr
            report["hybrid_threshold"] = hyb_thr
        if include_nb_svm:
            def nb_fit(tr, va, text_tr=text_tr, y_tr=y_tr):
                return nb_proba([text_tr[i] for i in tr], y_tr[tr], [text_tr[i] for i in va])

            nb_thr = choose_threshold(inner_split(y_tr, g_tr, nb_fit))
            nb_pred[test] = (nb_proba(text_tr, y_tr, text_te) >= nb_thr).astype(int)
            svm = LinearSVC(C=C, class_weight="balanced", random_state=SEED, max_iter=5000)
            # The SVM uses the same TF-IDF. Its decision stays at the default margin of 0.
            pipe = build_lr(C)
            pipe.fit(text_tr, y_tr)
            x_tr = pipe.named_steps["tfidf"].transform(text_tr)
            x_te = pipe.named_steps["tfidf"].transform(text_te)
            svm.fit(x_tr, y_tr)
            svm_pred[test] = (svm.decision_function(x_te) >= 0).astype(int)
            report["nb_threshold"] = nb_thr
            report["svm_threshold"] = 0.0
            report["svm_threshold_note"] = "default LinearSVC margin; not inner-tuned"
        fold_rows.append(report)
        print(f"fold {fold} done {report}", flush=True)
    out = {
        "text": metrics_at(y, text_pred),
        "folds": fold_rows,
        "text_pred": text_pred,
    }
    if extra is not None:
        out["sentiment_only"] = metrics_at(y, sent_pred)
        out["hybrid"] = metrics_at(y, hyb_pred)
        out["hybrid_minus_text"] = paired_delta(y, text_pred, hyb_pred)
        out["sentiment_pred"] = sent_pred
        out["hybrid_pred"] = hyb_pred
    if keyword is not None:
        out["keyword_first_rule"] = metrics_at(y, kw_pred)
    if include_nb_svm:
        out["naive_bayes_text_only"] = metrics_at(y, nb_pred)
        out["linear_svm_text_only_default_margin"] = metrics_at(y, svm_pred)
        out["nb_pred"] = nb_pred
        out["svm_pred"] = svm_pred
    return out


def svg_bars(path: Path, title: str, labels: list[str], values: list[float], ymin=0.0, ymax=1.0) -> None:
    width, height = 760, 360
    left, right, top, bottom = 70, 20, 40, 80
    plot_w = width - left - right
    plot_h = height - top - bottom
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}">',
        '<rect width="100%" height="100%" fill="white"/>',
        f'<text x="{width/2}" y="24" text-anchor="middle" font-family="sans-serif" font-size="16">{title}</text>',
    ]
    n = max(len(values), 1)
    gap = 18
    bar_w = (plot_w - gap * (n + 1)) / n
    for i, (lab, val) in enumerate(zip(labels, values)):
        h = 0 if ymax == ymin else (val - ymin) / (ymax - ymin) * plot_h
        x = left + gap + i * (bar_w + gap)
        y = top + plot_h - h
        parts.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{bar_w:.1f}" height="{h:.1f}" fill="#2c6e49"/>')
        parts.append(
            f'<text x="{x+bar_w/2:.1f}" y="{y-6:.1f}" text-anchor="middle" font-family="sans-serif" font-size="12">{val:.3f}</text>'
        )
        parts.append(
            f'<text x="{x+bar_w/2:.1f}" y="{height-28}" text-anchor="middle" font-family="sans-serif" font-size="11">{lab}</text>'
        )
    parts.append("</svg>")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(parts), encoding="utf-8")


def stage_a() -> dict:
    metrics = json.loads(PRIOR_METRICS.read_text(encoding="utf-8"))
    manifest = json.loads((PRIOR / "MANIFEST.json").read_text(encoding="utf-8"))
    checks = {
        "reddit_development_sha_matches": manifest["inputs"]["reddit_development"]["sha256"] == sha256_file(REDDIT_DEV),
        "reddit_folds_sha_matches": manifest["inputs"]["reddit_folds"]["sha256"] == sha256_file(REDDIT_OOF),
        "pooled_metrics_sha": sha256_file(PRIOR_METRICS),
    }
    if not all(checks[k] for k in ("reddit_development_sha_matches", "reddit_folds_sha_matches")):
        raise SystemExit(f"stage A input hash mismatch {checks}")
    delta = metrics["paired_hybrid_minus_text"]["macro_f1"]
    return {
        "status": "replicated from the frozen sentiment_reanalysis run; not refit",
        "hash_checks": checks,
        "continuity_score_gap": metrics["continuity"]["max_abs_score_gap_vs_saved"],
        "population": {"n": metrics["n"], "support": metrics["support"]},
        "text_inner_macro_f1": metrics["text_inner_threshold"]["macro_f1"],
        "sentiment_only_macro_f1": metrics["sentiment_only_inner_threshold"]["macro_f1"],
        "hybrid_macro_f1": metrics["hybrid_inner_threshold"]["macro_f1"],
        "majority_macro_f1": metrics["majority"]["macro_f1"],
        "paired_hybrid_minus_text_macro_f1": delta,
        "other_update_f1": {
            "text": metrics["text_inner_threshold"]["class_0_other_update"],
            "hybrid": metrics["hybrid_inner_threshold"]["class_0_other_update"],
            "difference": metrics["paired_hybrid_minus_text"]["other_update_f1"],
        },
        "interpretation": (
            "No reliable S2 gain. The negative class in this comparison is other update discussion, not GDS."
            if delta["includes_zero"] or delta["point"] <= 0
            else "Interval excludes zero."
        ),
    }


def main() -> int:
    created = datetime.now(timezone.utc).isoformat()
    OUT.mkdir(parents=True, exist_ok=True)
    rows, y, folds, groups = load_population()
    stage_a_result = stage_a()
    march = load_raw_posts_by_id(OLD_RAW)
    oct5 = load_oct5()
    analyzer = SentimentIntensityAnalyzer()
    texts = [make_text(r, "title_body") for r in rows]
    thread_texts = [""] * len(rows)
    timing_by_row = {}
    pre = np.zeros(len(rows))
    author_mean = np.full(len(rows), np.nan)
    community_mean = np.full(len(rows), np.nan)
    has_comment = np.zeros(len(rows), dtype=bool)
    has_author = np.zeros(len(rows), dtype=bool)
    has_community = np.zeros(len(rows), dtype=bool)
    title_only = np.zeros(len(rows), dtype=bool)
    stored = np.zeros(len(rows), dtype=int)
    listed = np.zeros(len(rows), dtype=int)
    snapshot_name = []
    for i, row in enumerate(rows):
        rid = row["reddit_id"]
        post = oct5.get(rid) or march.get(rid)
        if post is None:
            raise SystemExit(f"S2 row missing from saved snapshots: {rid}")
        snapshot_name.append("oct5" if rid in oct5 else "march")
        thread_texts[i], timing = full_thread_document(post)
        timing_by_row[i] = timing
        info = roles(post)
        title_only[i] = not str(post.get("author_description") or "").strip()
        pre[i] = compound_score(analyzer, f"{post.get('title') or ''}\n{post.get('author_description') or ''}")
        if info["author_text"]:
            author_mean[i] = mean_compound(analyzer, info["author_text"])
            has_author[i] = True
        if info["community_text"]:
            community_mean[i] = mean_compound(analyzer, info["community_text"])
            has_community[i] = True
        has_comment[i] = has_author[i] or has_community[i]
        stored[i] = info["n_stored"]
        listed[i] = int(info["num_comments"] or 0)

    def by_class(mask, values):
        return mean_diff(values[mask & (y == 1)], values[mask & (y == 0)])

    observed_author = ~np.isnan(author_mean)
    observed_community = ~np.isnan(community_mean)
    gd = np.array([r.get("discussion_type") == "general_dissatisfaction" for r in rows])
    tt = np.array([r.get("discussion_type") == "technical_troubleshooting" for r in rows])
    stage_b = {
        "population": "Reddit-URL S2 development rows with saved outer folds. S2 class 0 is other update discussion.",
        "n": int(len(rows)),
        "snapshot_counts": dict(Counter(snapshot_name)),
        "missingness": {
            "title_only": int(title_only.sum()),
            "any_nonempty_stored_comment": int(has_comment.sum()),
            "author_reply": int(has_author.sum()),
            "community_comment": int(has_community.sum()),
            "both_roles": int((has_author & has_community).sum()),
            "stored_over_recorded": float(stored.sum() / listed.sum()) if listed.sum() else None,
            "both_role_fraction": float((has_author & has_community).mean()),
        },
        "pre_discussion_title_body_by_s2": by_class(np.ones(len(rows), dtype=bool), pre),
        "pre_discussion_title_only_by_s2": by_class(title_only, pre),
        "pre_discussion_has_body_by_s2": by_class(~title_only, pre),
        "author_reply_mean_by_s2_observed_only": by_class(observed_author, author_mean),
        "community_mean_by_s2_observed_only": by_class(observed_community, community_mean),
        "restricted_general_dissatisfaction_vs_technical_troubleshooting": {
            "n_technical_troubleshooting": int(tt.sum()),
            "n_general_dissatisfaction": int(gd.sum()),
            "not_a_substitute_for_s2": True,
            "pre_discussion": mean_diff(pre[tt], pre[gd]),
            "author_reply_observed": mean_diff(author_mean[tt & observed_author], author_mean[gd & observed_author]),
            "community_observed": mean_diff(community_mean[tt & observed_community], community_mean[gd & observed_community]),
        },
        "by_source_pool_comment_availability": {},
        "no_resolution_claim": "No human-confirmed outcome label exists. Reply sentiment is not evidence that a reply solved an issue.",
        "definition": {
            "pre_discussion": "VADER compound of saved title plus body only. Title is not used as an author-reply fallback.",
            "author_reply": "Mean VADER compound of nonempty original-poster comments. Missing when there is no such comment.",
            "community": "Mean VADER compound of nonempty non-author comments. Missing when there is none.",
            "class_a_in_mean_diff": "troubleshooting or technical_troubleshooting",
            "class_b_in_mean_diff": "other update discussion or general_dissatisfaction, depending on the named contrast",
        },
    }
    pools = defaultdict(lambda: {"n": 0, "with_comment": 0})
    subs = defaultdict(lambda: {"n": 0, "with_comment": 0, "troubleshooting": 0})
    for i, row in enumerate(rows):
        pool = row.get("source_pool_audit_only") or "missing"
        pools[pool]["n"] += 1
        pools[pool]["with_comment"] += int(has_comment[i])
        sub = row.get("subreddit") or "missing"
        subs[sub]["n"] += 1
        subs[sub]["with_comment"] += int(has_comment[i])
        subs[sub]["troubleshooting"] += int(y[i] == 1)
    stage_b["by_source_pool_comment_availability"] = dict(pools)
    stage_b["largest_subreddits"] = [
        {"subreddit": k, **v}
        for k, v in sorted(subs.items(), key=lambda kv: -kv[1]["n"])[:12]
    ]

    comment_idx = np.flatnonzero(has_comment)
    extra = sentiment_matrix(
        pre,
        np.nan_to_num(author_mean, nan=0.0),
        np.nan_to_num(community_mean, nan=0.0),
        (~has_author).astype(float),
        (~has_community).astype(float),
    )
    keyword = np.array(
        [
            vader_rule_predict(
                f"{row.get('title') or ''}\n{row.get('post_body') or ''}",
                analyzer,
                0.15,
                "technical_first",
            )[0]
            for row in rows
        ],
        dtype=int,
    )
    strong_claim_allowed = bool(
        stage_b["missingness"]["both_role_fraction"] >= STRONG_COMMENT_CLAIM_MIN_BOTH_ROLE_FRACTION
    )
    print("stage C title/body on comment subset", len(comment_idx), flush=True)
    comment_eval = evaluate(
        [texts[i] for i in comment_idx],
        y[comment_idx],
        folds[comment_idx],
        groups[comment_idx],
        extra=extra[comment_idx],
        keyword=keyword[comment_idx],
        include_nb_svm=False,
    )
    timing_sum = Counter()
    for i in comment_idx:
        timing_sum.update(timing_by_row[i])
    print("stage C fair full-thread comparison", len(comment_idx), flush=True)
    fair_eval = evaluate(
        [thread_texts[i] for i in comment_idx],
        y[comment_idx],
        folds[comment_idx],
        groups[comment_idx],
        extra=extra[comment_idx],
        keyword=None,
        include_nb_svm=False,
    )
    print("continuity NB/SVM on full S2 text", flush=True)
    continuity = evaluate(
        texts,
        y,
        folds,
        groups,
        extra=None,
        keyword=keyword,
        include_nb_svm=True,
    )
    restricted_idx = np.flatnonzero(tt | gd)
    restricted_y = tt[restricted_idx].astype(int)
    restricted_note = {
        "n": int(len(restricted_idx)),
        "technical_troubleshooting_1": int(restricted_y.sum()),
        "general_dissatisfaction_0": int((restricted_y == 0).sum()),
        "not_a_substitute_for_s2": True,
    }
    test_counts = Counter((int(folds[i]), int(restricted_y[j])) for j, i in enumerate(restricted_idx))
    train_ok = True
    for fold in range(5):
        train_gd = int((restricted_y == 0).sum() - test_counts[(fold, 0)])
        train_tt = int((restricted_y == 1).sum() - test_counts[(fold, 1)])
        if train_gd < 15 or train_tt < 50 or test_counts[(fold, 0)] < 1:
            train_ok = False
    can_fit_restricted = train_ok
    restricted_eval = None
    if not can_fit_restricted:
        restricted_note["model_fit"] = False
        restricted_note["reason"] = f"training-fold class counts missed the predeclared minimum: {dict(test_counts)}"
    if can_fit_restricted:
        only = np.column_stack(
            [
                pre[restricted_idx],
                np.zeros(len(restricted_idx)),
                np.zeros(len(restricted_idx)),
                np.zeros(len(restricted_idx)),
                np.zeros(len(restricted_idx)),
            ]
        )
        # Zero columns would make StandardScaler fail or erase the contrast.
        # Use a one-column compound appended through the sentiment-only and a text model.
        restricted_eval = evaluate(
            [texts[i] for i in restricted_idx],
            restricted_y,
            folds[restricted_idx],
            groups[restricted_idx],
            extra=np.column_stack([pre[restricted_idx]]),
            keyword=keyword[restricted_idx],
            include_nb_svm=False,
            n_continuous=1,
        )
        restricted_note["model_fit"] = True
        restricted_note["features"] = (
            "Text TF-IDF versus text plus the one title/body VADER compound. "
            "Comment features are not added in this restricted contrast."
        )
        restricted_note["label"] = "1 = technical_troubleshooting; 0 = general_dissatisfaction. Not S2."

    def public_eval(result):
        keep = {}
        for key, value in result.items():
            if key.endswith("_pred") or key == "folds":
                continue
            keep[key] = value
        keep["folds"] = result["folds"]
        return keep

    comment_public = public_eval(comment_eval)
    comment_public["n"] = int(len(comment_idx))
    comment_public["support_s2"] = {
        "troubleshooting_1": int((y[comment_idx] == 1).sum()),
        "other_update_0": int((y[comment_idx] == 0).sum()),
    }
    comment_public["strong_classifier_claim_allowed"] = strong_claim_allowed
    comment_public["comparison"] = "title_body_text_versus_title_body_text_plus_comment_sentiment"
    comment_public["does_not_isolate_sentiment"] = True
    comment_public["claim_limit"] = (
        "This contrast gives sentiment features access to saved comments that the title/body "
        "text baseline does not contain. Its difference is not evidence that sentiment adds "
        "information beyond comment text. The isolating comparison is full_thread_fair."
    )
    fair_public = public_eval(fair_eval)
    fair_public["n"] = int(len(comment_idx))
    fair_public["support_s2"] = comment_public["support_s2"]
    fair_public["comparison"] = "full_thread_text_versus_same_full_thread_text_plus_sentiment"
    fair_public["construction"] = (
        "Chosen snapshot title, body, then nonempty stored comments sorted by created_utc text. "
        "Author replies and community comments are included. No role marker is inserted. "
        "TF-IDF is fit inside each training fold. The hybrid appends the prespecified sentiment "
        "columns to that same vector."
    )
    fair_public["feature_timing"] = {
        "scope": "comment-available development posts only",
        "counts": {k: int(v) for k, v in timing_sum.items()},
        "interpretation": (
            "Comment timestamps are compared with the post timestamp as saved strings. "
            "Comments at or after the post time are later turns in the snapshot. "
            "The full-thread model uses those turns and is not a pre-discussion classifier. "
            "Stage A remains the pre-discussion title-and-body task. "
            "Timestamp order is not a causal or prospective claim."
        ),
    }
    fair_public["strong_classifier_claim_allowed"] = strong_claim_allowed
    fair_public["coverage_limit"] = (
        "Both author and community text are present for "
        f"{stage_b['missingness']['both_roles']} of 2050 posts "
        f"({stage_b['missingness']['both_role_fraction']:.3f}), below the predeclared "
        f"{STRONG_COMMENT_CLAIM_MIN_BOTH_ROLE_FRACTION:.0%} bar."
    )
    continuity_public = public_eval(continuity)
    continuity_public["model_change_note"] = (
        "Naive Bayes and the linear SVM use the same title/body TF-IDF as logistic regression and no sentiment feature. "
        "A difference among them is a model change, not evidence about sentiment. "
        "The SVM threshold is the default margin. Naive Bayes uses the same inner-threshold grid as logistic regression."
    )
    restricted_public = None if restricted_eval is None else {**restricted_note, **public_eval(restricted_eval)}
    if restricted_public is not None:
        restricted_public.update(restricted_note)

    stage_c = {
        "pre_discussion_task": "stage_a_title_body",
        "full_thread_fair": fair_public,
        "title_body_plus_comment_sentiment_does_not_isolate_sentiment": comment_public,
        "full_s2_model_continuity_no_new_sentiment_feature": continuity_public,
        "restricted_discussion_type": restricted_public,
    }
    # Drop bulky duplicate note merge if model failed
    write_json(OUT / "stage_a_title_body.json", stage_a_result)
    write_json(OUT / "stage_b_comment_description.json", stage_b)
    write_json(OUT / "stage_c_development_models.json", {
        "full_thread_fair": {k: v for k, v in fair_public.items() if k != "folds"},
        "full_thread_folds": fair_public["folds"],
        "title_body_plus_comment_sentiment_does_not_isolate_sentiment": {
            k: v for k, v in comment_public.items() if k != "folds"
        },
        "comment_folds": comment_public["folds"],
        "continuity": {k: v for k, v in continuity_public.items() if k != "folds"},
        "continuity_folds": continuity_public["folds"],
        "restricted_discussion_type": None
        if restricted_public is None
        else {k: v for k, v in restricted_public.items() if k != "folds"},
        "restricted_folds": None if restricted_public is None else restricted_public.get("folds"),
    })
    pred_rows = []
    for local, i in enumerate(comment_idx):
        pred_rows.append(
            {
                "reddit_id": rows[i]["reddit_id"],
                "fold": int(folds[i]),
                "y_true_s2": int(y[i]),
                "discussion_type": rows[i].get("discussion_type"),
                "pred_title_body_text": int(comment_eval["text_pred"][local]),
                "pred_title_body_plus_comment_sentiment": int(comment_eval["hybrid_pred"][local]),
                "pred_full_thread_text": int(fair_eval["text_pred"][local]),
                "pred_full_thread_plus_sentiment": int(fair_eval["hybrid_pred"][local]),
                "pred_sentiment_title_body_only": int(comment_eval["sentiment_pred"][local]),
                "pred_keyword_first": int(keyword[i]),
                "has_author_reply": bool(has_author[i]),
                "has_community_comment": bool(has_community[i]),
                "title_only": bool(title_only[i]),
            }
        )
    (OUT / "stage_c_comment_subset_predictions.jsonl").write_text(
        "".join(json.dumps(r) + "\n" for r in pred_rows), encoding="utf-8"
    )
    b = stage_b
    svg_bars(
        FIG / "comment_coverage.svg",
        "Saved comment coverage on 2,050 Reddit S2 posts",
        ["Any comment", "Author reply", "Community", "Both roles"],
        [
            b["missingness"]["any_nonempty_stored_comment"] / 2050,
            b["missingness"]["author_reply"] / 2050,
            b["missingness"]["community_comment"] / 2050,
            b["missingness"]["both_roles"] / 2050,
        ],
    )
    svg_bars(
        FIG / "full_thread_macro_f1.svg",
        "Fair full-thread macro-F1 on 797 posts",
        ["Thread text", "Thread+sentiment"],
        [fair_public["text"]["macro_f1"], fair_public["hybrid"]["macro_f1"]],
    )
    svg_bars(
        FIG / "s2_macro_f1.svg",
        "Development macro-F1, S2 other-update contrast",
        ["Text", "VADER only", "Text+VADER", "Keyword-first"],
        [
            stage_a_result["text_inner_macro_f1"],
            stage_a_result["sentiment_only_macro_f1"],
            stage_a_result["hybrid_macro_f1"],
            continuity_public["keyword_first_rule"]["macro_f1"],
        ],
    )
    pre_means = stage_b["pre_discussion_title_body_by_s2"]
    author_means = stage_b["author_reply_mean_by_s2_observed_only"]
    comm_means = stage_b["community_mean_by_s2_observed_only"]
    svg_bars(
        FIG / "role_means.svg",
        "Mean VADER compound by S2 class and role",
        ["Pre T", "Pre O", "Author T", "Author O", "Comm T", "Comm O"],
        [
            pre_means["mean_a"],
            pre_means["mean_b"],
            author_means["mean_a"],
            author_means["mean_b"],
            comm_means["mean_a"],
            comm_means["mean_b"],
        ],
        ymin=-0.4,
        ymax=0.6,
    )
    write_documents(
        created, stage_a_result, stage_b, comment_public, fair_public, continuity_public, restricted_public
    )
    print(json.dumps({
        "stage_a_delta": stage_a_result["paired_hybrid_minus_text_macro_f1"],
        "unfair_title_body_plus_comment_sentiment_delta": comment_public["hybrid_minus_text"],
        "fair_full_thread_delta": fair_public["hybrid_minus_text"],
        "strong_claim": strong_claim_allowed,
        "restricted_fit": can_fit_restricted,
        "keyword_macro_f1": continuity_public["keyword_first_rule"]["macro_f1"],
        "nb_macro_f1": continuity_public["naive_bayes_text_only"]["macro_f1"],
        "svm_macro_f1": continuity_public["linear_svm_text_only_default_margin"]["macro_f1"],
    }, indent=2), flush=True)
    return 0


def fmt_diff(d: dict) -> str:
    if d.get("mean_a") is None:
        return f"n {d.get('n_a')}/{d.get('n_b')}, means unavailable"
    return (
        f"{d['mean_a']:.4f} vs {d['mean_b']:.4f} (n {d['n_a']}/{d['n_b']}; "
        f"difference {d['difference_a_minus_b']:+.4f}; Welch p {d['welch_p']:.4g}; "
        f"bootstrap CI {d['bootstrap_ci95'][0]:+.4f} to {d['bootstrap_ci95'][1]:+.4f}; "
        f"includes zero: {d['ci_includes_zero']})"
    )


def fmt_model(m: dict) -> str:
    c0, c1 = m["class_0_other_update"], m["class_1_troubleshooting"]
    return (
        f"{m['macro_f1']:.4f} | {c0['precision']:.3f}/{c0['recall']:.3f}/{c0['f1']:.3f} | "
        f"{c1['precision']:.3f}/{c1['recall']:.3f}/{c1['f1']:.3f} | `{m['confusion_matrix_labels_[0,1]']}`"
    )


def write_documents(created, stage_a, stage_b, comment, fair, continuity, restricted) -> None:
    fresh = json.loads((HERE / "results" / "join_coverage_audit.json").read_text())
    fresh_score = fresh["preserved_fresh_test_score_not_recomputed"]
    delta = stage_a["paired_hybrid_minus_text_macro_f1"]
    unfair = comment["hybrid_minus_text"]
    fdelta = fair["hybrid_minus_text"]
    timing = fair["feature_timing"]["counts"]
    lines = [
        "# Sentiment-centered development packet",
        "",
        f"**Created:** {created}",
        f"**Code version:** `{CODE_VERSION}`",
        "",
        "This packet prepares a new paper. It does not edit the current manuscript or Overleaf. The reserved and fresh tests were not scored. S2 class 0 is other update discussion. Historical TPS/GDS and `general_dissatisfaction` are separate populations.",
        "",
        "## Stage A: exact title/body replication",
        "",
        "The frozen 2,050-row comparison was checked against its saved inputs rather than refit. Input hashes match. The saved TF-IDF scores had already matched the Phase 3 grouped predictions with maximum absolute gap "
        f"{stage_a['continuity_score_gap']}.",
        "",
        f"Text macro-F1 {stage_a['text_inner_macro_f1']:.4f}. VADER-only {stage_a['sentiment_only_macro_f1']:.4f}. Text plus VADER {stage_a['hybrid_macro_f1']:.4f}. Majority {stage_a['majority_macro_f1']:.4f}. Hybrid minus text {delta['point']:+.4f} (95% interval {delta['ci95'][0]:+.4f} to {delta['ci95'][1]:+.4f}; includes zero: {delta['includes_zero']}).",
        "",
        "This is not a positive incremental finding.",
        "",
        "## Stage B: comment roles on the development subset",
        "",
        f"Any nonempty stored comment: {stage_b['missingness']['any_nonempty_stored_comment']} / 2050. Author reply: {stage_b['missingness']['author_reply']}. Community comment: {stage_b['missingness']['community_comment']}. Both roles: {stage_b['missingness']['both_roles']} ({stage_b['missingness']['both_role_fraction']:.3f}). Title only: {stage_b['missingness']['title_only']}. Stored comments cover {stage_b['missingness']['stored_over_recorded']:.3f} of recorded `num_comments`.",
        "",
        "Mean compound, troubleshooting minus other update discussion:",
        "",
        f"- Pre-discussion title/body: {fmt_diff(stage_b['pre_discussion_title_body_by_s2'])}",
        f"- Title-only posts only: {fmt_diff(stage_b['pre_discussion_title_only_by_s2'])}",
        f"- Posts with a body: {fmt_diff(stage_b['pre_discussion_has_body_by_s2'])}",
        f"- Author replies, observed only: {fmt_diff(stage_b['author_reply_mean_by_s2_observed_only'])}",
        f"- Community comments, observed only: {fmt_diff(stage_b['community_mean_by_s2_observed_only'])}",
        "",
        stage_b["no_resolution_claim"],
        "",
        "### Restricted discussion type, not a substitute for S2",
        "",
        f"Technical troubleshooting {stage_b['restricted_general_dissatisfaction_vs_technical_troubleshooting']['n_technical_troubleshooting']} versus general dissatisfaction {stage_b['restricted_general_dissatisfaction_vs_technical_troubleshooting']['n_general_dissatisfaction']}.",
        "",
        f"- Pre-discussion: {fmt_diff(stage_b['restricted_general_dissatisfaction_vs_technical_troubleshooting']['pre_discussion'])}",
        f"- Author replies observed: {fmt_diff(stage_b['restricted_general_dissatisfaction_vs_technical_troubleshooting']['author_reply_observed'])}",
        f"- Community observed: {fmt_diff(stage_b['restricted_general_dissatisfaction_vs_technical_troubleshooting']['community_observed'])}",
        "",
        "Source-pool comment availability and the largest subreddits are in `results/stage_b_comment_description.json`. Source and subreddit are stratification, not classifier features.",
        "",
        "## Stage C: development models",
        "",
        "No manuscript recommendation is made here. The pre-discussion task and the full-thread task answer different questions.",
        "",
        "### Pre-discussion task",
        "",
        "Stage A compares title-and-body TF-IDF with the same title-and-body text plus the title-and-body VADER compound. Comments are not in either arm. That result stands on its own: hybrid minus text "
        f"{delta['point']:+.4f} (95% interval {delta['ci95'][0]:+.4f} to {delta['ci95'][1]:+.4f}; includes zero: {delta['includes_zero']}).",
        "",
        "### Feature timing",
        "",
        "On the 797 posts with at least one nonempty stored comment, the full-thread string contains "
        f"{timing.get('nonempty_comments', 0)} nonempty comments. "
        f"{timing.get('timestamp_at_or_after_post', 0)} have a timestamp at or after the post, "
        f"{timing.get('timestamp_before_post', 0)} have an earlier timestamp, and "
        f"{timing.get('timestamp_missing', 0)} lack a comparable timestamp. "
        "Those comments are later turns in the saved snapshot when the timestamp is at or after the post. "
        "Using them is a retrospective description of the stored thread, not a claim that the model could have classified the post before replies, and not a claim about what caused a later reply.",
        "",
        "### Fair full-thread comparison",
        "",
        fair["construction"],
        "",
        fair["coverage_limit"],
        "",
        "Same 797 posts, same saved grouped folds, thresholds chosen inside each training split.",
        "",
        "| Arm | macro-F1 | other P/R/F1 | positive-class P/R/F1 | confusion [[0,1]] |",
        "|---|---:|---|---|---|",
        f"| Full-thread text | {fmt_model(fair['text'])} |",
        f"| Same full-thread text plus sentiment features | {fmt_model(fair['hybrid'])} |",
        f"| VADER title/body only, for reference | {fmt_model(fair['sentiment_only'])} |",
        "",
        f"Full-thread hybrid minus full-thread text: macro-F1 {fdelta['point']:+.4f} "
        f"(95% interval {fdelta['ci95'][0]:+.4f} to {fdelta['ci95'][1]:+.4f}; includes zero: {fdelta['includes_zero']}). "
        + (
            "The interval includes zero, so the sentiment columns do not show a reliable gain beyond the same saved thread text."
            if fdelta["includes_zero"]
            else (
                "The interval lies entirely below zero: in this development comparison the sentiment columns have lower macro-F1 than the same thread text. That is not a gain. It is also not a prospective or causal finding, and both-role coverage remains below the predeclared bar for a strong claim."
                if fdelta["point"] < 0
                else "The interval lies entirely above zero on this partial snapshot. It is still not a prospective or causal finding, and both-role coverage remains below the predeclared bar for a strong claim."
            )
        ),
        "",
        "### Contrast that does not isolate sentiment",
        "",
        "Title/body TF-IDF versus title/body TF-IDF plus comment-derived sentiment uses comments only on the hybrid side. "
        f"That difference was {unfair['point']:+.4f} (95% interval {unfair['ci95'][0]:+.4f} to {unfair['ci95'][1]:+.4f}). "
        "It is not evidence that sentiment adds information beyond comment text, whether or not the interval contains zero.",
        "",
        "| Arm | macro-F1 | other P/R/F1 | positive-class P/R/F1 | confusion [[0,1]] |",
        "|---|---:|---|---|---|",
        f"| Title/body text | {fmt_model(comment['text'])} |",
        f"| Title/body text plus comment sentiment | {fmt_model(comment['hybrid'])} |",
        f"| Keyword-first rule on title/body, not pure sentiment | {fmt_model(comment['keyword_first_rule'])} |",
        "",
        "Full 2,050-row continuity checks use title and body only. They do not add a sentiment feature.",
        "",
        f"| Text logistic regression, inner threshold | {fmt_model(continuity['text'])} |",
        f"| Naive Bayes, same TF-IDF, inner threshold | {fmt_model(continuity['naive_bayes_text_only'])} |",
        f"| Linear SVM, same TF-IDF, default margin | {fmt_model(continuity['linear_svm_text_only_default_margin'])} |",
        f"| Keyword-first rule | {fmt_model(continuity['keyword_first_rule'])} |",
        "",
        continuity["model_change_note"],
        "",
    ]
    if restricted is None:
        lines.append("The restricted discussion-type model was not fit. See the stage C JSON for the fold counts.")
    else:
        lines.extend(
            [
                "### Restricted model",
                "",
                f"n={restricted['n']}: {restricted['technical_troubleshooting_1']} technical troubleshooting and {restricted['general_dissatisfaction_0']} general dissatisfaction. {restricted['label']}",
                "",
                f"| Text | {fmt_model(restricted['text'])} |",
                f"| VADER title/body only | {fmt_model(restricted['sentiment_only'])} |",
                f"| Text plus title/body VADER | {fmt_model(restricted['hybrid'])} |",
                "",
                f"Hybrid minus text macro-F1 {restricted['hybrid_minus_text']['point']:+.4f} "
                f"(95% interval {restricted['hybrid_minus_text']['ci95'][0]:+.4f} to {restricted['hybrid_minus_text']['ci95'][1]:+.4f}; "
                f"includes zero: {restricted['hybrid_minus_text']['includes_zero']}). "
                "This contrast drops other update posts whose discussion type is not general dissatisfaction. It does not replace the S2 result.",
                "",
            ]
        )
    lines.extend(
        [
            "## Preserved fresh-test score",
            "",
            f"The existing fresh test remains macro-F1 **{fresh_score['macro_f1']:.4f}** on {fresh_score['n']} posts, with confusion `{fresh_score['confusion_matrix_labels_[0,1]']}`. This run did not hide or recompute it. It is lower than the earlier reserved-test result and stays visible.",
            "",
            "## ReleaseTrain 3% and risk cadence",
            "",
            "This remains an unverified separate question. Local snapshots show candidate-pool sizes, not a prevalence, and they do not document the professor's numerator, denominator, time range, or risk definition.",
            "",
            "## Proposed paper questions",
            "",
            "1. In reviewed software-update posts, does title-and-body sentiment improve troubleshooting-versus-other-update classification beyond TF-IDF text? Current development answer: no reliable gain.",
            "2. On the partial saved thread, do sentiment summaries add information beyond a TF-IDF model that already contains the same title, body, author replies, and community comments? The title/body-plus-comment-sentiment difference does not answer this. The full-thread contrast is the relevant development comparison, and it is retrospective rather than prospective.",
            "3. If the question is specifically technical troubleshooting versus confirmed general dissatisfaction, what is the exact reviewed population, and does the title/body result change? Report that population separately from S2.",
            "4. Historical TPS/GDS divergence remains a limited exploratory finding with title-only fallback and incomplete comments. It is not an S2 result and not evidence of a conversation cadence.",
            "5. Whether about 3% of ReleaseTrain posts are recent update risks is a distinct study and is not answered here.",
            "",
            "Do not claim that replies solved an issue. No human-confirmed outcome label exists.",
            "",
            "## Files",
            "",
            "- `AUDIT.md`",
            "- `results/join_coverage_audit.json`",
            "- `results/stage_a_title_body.json`",
            "- `results/stage_b_comment_description.json`",
            "- `results/stage_c_development_models.json`",
            "- `results/stage_c_comment_subset_predictions.jsonl`",
            "- `results/figures/`",
            "",
        ]
    )
    (HERE / "RESULTS.md").write_text("\n".join(lines), encoding="utf-8")
    (HERE / "RUN.md").write_text(
        "\n".join(
            [
                "# Reproduce the sentiment-paper development packet",
                "",
                "From the research repository root:",
                "",
                "```bash",
                "phase3/experiment_v1/.venv/bin/python phase5/sentiment_paper/audit_join_coverage.py",
                "PYTHONPATH=phase5/sentiment_reanalysis/vendor \\",
                "  phase3/experiment_v1/.venv/bin/python phase5/sentiment_paper/run_staged_analysis.py",
                "```",
                "",
                "Run the audit first. The staged script reads the audit's preserved fresh-test quote and does not score either protected test. VADER is imported from `phase5/sentiment_reanalysis/vendor`. Outputs stay under `phase5/sentiment_paper/`.",
                "",
                f"Code version: `{CODE_VERSION}`.",
                "",
            ]
        ),
        encoding="utf-8",
    )
    import scipy
    import pandas
    outputs = sorted(p for p in OUT.rglob("*") if p.is_file())
    manifest = {
        "code_version": CODE_VERSION,
        "created_utc": created,
        "tests_scored": False,
        "paper_or_overleaf_edited": False,
        "s2_negative_class": "other update discussion",
        "historical_tps_gds_reported_separately": True,
        "general_dissatisfaction_is_not_s2": True,
        "versions": {
            "python": platform.python_version(),
            "sklearn": sklearn.__version__,
            "numpy": np.__version__,
            "scipy": scipy.__version__,
            "pandas": pandas.__version__,
            "vaderSentiment": getattr(vaderSentiment, "__version__", "unknown"),
        },
        "settings": {
            "C": C,
            "threshold_grid": THRESHOLD_GRID,
            "inner_folds": 3,
            "bootstrap": {"n": N_BOOT, "seed": SEED},
            "strong_comment_claim_min_both_role_fraction": STRONG_COMMENT_CLAIM_MIN_BOTH_ROLE_FRACTION,
            "keyword_rule": "evaluation.models.vader_rules technical_first, neutral band 0.15; not a pure sentiment model",
            "comment_features": [
                "title_body_compound",
                "author_reply_mean_or_zero",
                "community_mean_or_zero",
                "author_reply_missing",
                "community_comment_missing",
            ],
        },
        "outputs": {str(p.relative_to(HERE)): sha256_file(p) for p in outputs},
        "documents": {
            "AUDIT.md": sha256_file(HERE / "AUDIT.md"),
            "RESULTS.md": sha256_file(HERE / "RESULTS.md"),
            "RUN.md": sha256_file(HERE / "RUN.md"),
        },
    }
    write_json(HERE / "MANIFEST.json", manifest)


if __name__ == "__main__":
    raise SystemExit(main())
