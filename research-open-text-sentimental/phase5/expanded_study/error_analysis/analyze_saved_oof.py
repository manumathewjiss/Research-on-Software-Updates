#!/usr/bin/env python3
"""Count saved title+body OOF errors on the 2,050 Reddit-URL development rows.

Reads only development_reddit_only.jsonl and grouped_oof_predictions.jsonl.
Does not refit a model, does not read held-out tests, and does not write post
text or identifiers.
"""

from __future__ import annotations

import json
import re
from collections import Counter
from pathlib import Path

import numpy as np
from sklearn.metrics import confusion_matrix, f1_score

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
DEV = REPO / "phase3" / "reddit_only_sensitivity" / "development_reddit_only.jsonl"
OOF = REPO / "phase3" / "reddit_only_sensitivity" / "results" / "grouped_oof_predictions.jsonl"
NEW_PRED = HERE.parent / "results" / "predictions.jsonl"
INNER_TARGET = 0.8319320360990539

# Closed lists already fixed in the descriptive word analysis. Not refit on errors.
INCIDENT = (
    "error", "bug", "bugs", "fix", "fixed", "crash", "crashed", "install",
    "installation", "broken", "issue", "issues", "problem", "problems",
    "dependency", "dependencies", "config", "configuration",
)
DISCONTENT = (
    "hate", "hates", "hated", "annoying", "annoyed", "frustrating", "frustrated",
    "disappointed", "disappointment", "useless", "terrible", "awful", "worst",
    "stupid", "garbage", "trash", "ridiculous", "sucks", "horrible",
)
# Fixed before any error rate is computed. Character length of stored title,
# a newline, and stored body.
LENGTH_BINS = ((0, 100), (101, 300), (301, 800), (801, 10**9))
MIN_SUBREDDIT_N = 20


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def words(text: str) -> set[str]:
    return set(re.findall(r"[a-z0-9']+", text.lower()))


def length_bin(n: int) -> str:
    for lo, hi in LENGTH_BINS:
        if lo <= n <= hi:
            if hi > 100000:
                return f"{lo}+"
            return f"{lo}-{hi}"
    raise RuntimeError(n)


def rates(y, pred) -> dict:
    y = np.asarray(y)
    pred = np.asarray(pred)
    cm = confusion_matrix(y, pred, labels=[0, 1])
    tn, fp, fn, tp = (int(x) for x in cm.ravel())
    n = int(len(y))
    n0 = int((y == 0).sum())
    n1 = int((y == 1).sum())
    return {
        "n": n,
        "other_update_0": n0,
        "troubleshooting_1": n1,
        "tn": tn,
        "fp": fp,
        "fn": fn,
        "tp": tp,
        "fp_among_other_update": None if n0 == 0 else fp / n0,
        "fn_among_troubleshooting": None if n1 == 0 else fn / n1,
        "macro_f1": None if n == 0 or len(set(y.tolist())) < 1 else float(
            f1_score(y, pred, average="macro", zero_division=0)
        ),
    }


def build_rows(pred_by_id: dict[str, int], by_id: dict[str, dict], order: list[str]) -> tuple[list[int], list[int], list[dict]]:
    y, pred, rows = [], [], []
    for rid in order:
        src = by_id[rid]
        title = src.get("title") or ""
        body = src.get("post_body") or ""
        text = f"{title}\n{body}"
        toks = words(text)
        y_i = int(src["s2_target"])
        p_i = int(pred_by_id[rid])
        y.append(y_i)
        pred.append(p_i)
        if y_i == 0 and p_i == 1:
            kind = "fp"
        elif y_i == 1 and p_i == 0:
            kind = "fn"
        elif y_i == 1 and p_i == 1:
            kind = "tp"
        else:
            kind = "tn"
        n_chars = len(text)
        rows.append(
            {
                "kind": kind,
                "y": y_i,
                "empty_body": not str(body).strip(),
                "source_pool": src.get("source_pool_audit_only") or "missing",
                "subreddit": src.get("subreddit") or "missing",
                "length_bin": length_bin(n_chars),
                "n_chars": n_chars,
                "incident": bool(toks & set(INCIDENT)),
                "discontent": bool(toks & set(DISCONTENT)),
            }
        )
    return y, pred, rows


def summarize(y, pred, rows, prediction_note: str, source_note: str) -> dict:
    y = np.asarray(y)
    pred = np.asarray(pred)
    overall = rates(y, pred)
    overall["prediction_field"] = prediction_note
    overall["label_field"] = "development s2_target"
    overall["threshold_note"] = source_note

    def slice_table(key: str) -> list[dict]:
        out = []
        levels = sorted({r[key] for r in rows})
        for level in levels:
            mask = np.array([r[key] == level for r in rows])
            out.append({"level": level, **rates(y[mask], pred[mask])})
        return out

    def cue_table() -> list[dict]:
        specs = (
            ("incident_term", lambda r: r["incident"] and not r["discontent"]),
            ("discontent_term", lambda r: r["discontent"] and not r["incident"]),
            ("both_term_lists", lambda r: r["incident"] and r["discontent"]),
            ("neither_term_list", lambda r: not r["incident"] and not r["discontent"]),
        )
        out = []
        for name, fn in specs:
            mask = np.array([fn(r) for r in rows])
            out.append({"level": name, **rates(y[mask], pred[mask])})
        return out

    subreddit = slice_table("subreddit")
    large = [r for r in subreddit if r["n"] >= MIN_SUBREDDIT_N]
    small = [r for r in subreddit if r["n"] < MIN_SUBREDDIT_N]
    small_mask = np.array([r["subreddit"] not in {x["level"] for x in large} for r in rows])
    payload = {
        "population_n": 2050,
        "sources": {
            "predictions": prediction_note,
            "snapshot": str(DEV.relative_to(REPO)),
            "fields": {
                "source_pool": "source_pool_audit_only",
                "body": "post_body",
                "title": "title",
                "subreddit": "subreddit",
                "length": "character length of stored title, newline, and stored body",
            },
        },
        "overall": overall,
        "empty_body": slice_table("empty_body"),
        "source_pool": slice_table("source_pool"),
        "length_bin": slice_table("length_bin"),
        "lexical_cues": cue_table(),
        "subreddit_n_at_least_20": large,
        "subreddit_below_20_pooled": {
            "n_communities": len(small),
            **rates(y[small_mask], pred[small_mask]),
        },
        "correct_vs_error_shares": {},
    }
    # Within each descriptive slice, share of TP/FN among troubleshooting and TN/FP among other update.
    for name, table in (
        ("empty_body", payload["empty_body"]),
        ("source_pool", payload["source_pool"]),
        ("length_bin", payload["length_bin"]),
        ("lexical_cues", payload["lexical_cues"]),
    ):
        payload["correct_vs_error_shares"][name] = table
    return payload


def main() -> None:
    by_id = {r["reddit_id"]: r for r in read_jsonl(DEV)}
    new_rows = read_jsonl(NEW_PRED)
    oof = read_jsonl(OOF)
    if len(new_rows) != 2050 or len(oof) != 2050:
        raise SystemExit("row count is not 2050")
    order = [r["reddit_id"] for r in new_rows]
    if len(set(order)) != 2050:
        raise SystemExit("duplicate ids in new predictions")
    oof_by = {r["reddit_id"]: r for r in oof}
    pred_new = {}
    pred_old = {}
    for rid in order:
        src = by_id.get(rid)
        item = oof_by.get(rid)
        row = next(r for r in new_rows if r["reddit_id"] == rid)
        if src is None or item is None:
            raise SystemExit(f"missing development or OOF row {rid}")
        if int(src["s2_target"]) != int(row["y_true"]) or int(item["y_true"]) != int(row["y_true"]):
            raise SystemExit(f"label mismatch {rid}")
        if item.get("verified_url_domain") != "reddit.com":
            raise SystemExit("non-reddit URL in the 2050 file")
        pred_new[rid] = int(row["pred_title_body"])
        pred_old[rid] = int(item["y_pred_tfidf_lr"])
    y, pred, rows = build_rows(pred_new, by_id, order)
    payload = summarize(
        y,
        pred,
        rows,
        "phase5/expanded_study/results/predictions.jsonl pred_title_body",
        "Inner-fold thresholds on the 2050 grouped folds. Target macro-F1 0.8319320360990539. Not the continuity-threshold field y_pred_tfidf_lr.",
    )
    if abs(payload["overall"]["macro_f1"] - INNER_TARGET) > 1e-12:
        raise SystemExit(f"inner-threshold macro-F1 changed: {payload['overall']['macro_f1']}")
    HERE.joinpath("counts.json").write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    y2, pred2, rows2 = build_rows(pred_old, by_id, order)
    old = summarize(
        y2,
        pred2,
        rows2,
        "phase3/reddit_only_sensitivity/results/grouped_oof_predictions.jsonl y_pred_tfidf_lr",
        "SENSITIVITY ONLY. Continuity threshold 0.5877137791150834. Not the primary inner-threshold analysis.",
    )
    HERE.joinpath("sensitivity_continuity_threshold.json").write_text(json.dumps(old, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "primary_macro_f1": payload["overall"]["macro_f1"],
        "primary_cm": [payload["overall"]["tn"], payload["overall"]["fp"], payload["overall"]["fn"], payload["overall"]["tp"]],
        "continuity_macro_f1": old["overall"]["macro_f1"],
        "continuity_cm": [old["overall"]["tn"], old["overall"]["fp"], old["overall"]["fn"], old["overall"]["tp"]],
    }))


if __name__ == "__main__":
    main()
