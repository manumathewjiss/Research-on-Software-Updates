#!/usr/bin/env python3
"""
experiment_v1 followup: Manu review sheet, within-dev duplicate audit,
and development-only grouped validation for the already-chosen model.

Does NOT touch reserved-test scoring, labels, or model/threshold selection.
"""

from __future__ import annotations

import csv
import json
import re
import unicodedata
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    balanced_accuracy_score,
    confusion_matrix,
    f1_score,
    precision_recall_fscore_support,
)
from sklearn.model_selection import StratifiedGroupKFold, StratifiedKFold
from sklearn.pipeline import Pipeline

EXP = Path(__file__).resolve().parent.parent
FOLLOWUP = Path(__file__).resolve().parent
DATA = EXP / "data"
V1_RESULTS = EXP / "results"
OUT = FOLLOWUP / "results"

SEED = 42
N_FOLDS = 5
# Match protocol / audit: high-confidence near-dup for grouping
NEAR_GROUP_THRESHOLD = 0.92
NEAR_REPORT_THRESHOLD = 0.85
CHOSEN_C = 4.0
TEXT_SETTING = "title_body"

TROUBLE_RE = re.compile(
    r"(?i)\b("
    r"error|bug|crash|broken|fix(?:ed|ing|ure)?|fix(?:s|ed|ing)?|"
    r"not\s+work(?:ing)?|doesn'?t\s+work|won'?t\s+(?:start|boot|launch|open|connect)|"
    r"unable\s+to|can'?t\s+(?:install|update|boot|login|log\s*in|start|open|connect)|"
    r"how\s+(?:do\s+i|to)\b|issue|help\s+(?:with|needed|me)|stuck|workaround|"
    r"after\s+(?:the\s+)?(?:update|upgrade|patch)|post[- ]?(?:update|upgrade)|"
    r"regression|stack\s*trace|exception|segfault|kernel\s+panic|bsod|"
    r"rollback|downgrade|reinstall|compatib|dependency|"
    r"black\s+screen|blank\s+screen|boot\s+loop|won'?t\s+boot"
    r")\b"
)
URL_RE = re.compile(r"https?://\S+|www\.\S+", re.I)

CONFLICT_IDS = ("1wxl2u9", "1wxl3ma", "1wxl35m")


def load_jsonl(path: Path) -> list[dict]:
    rows = []
    with path.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def norm_text(title: str, body: str) -> str:
    s = f"{title or ''}\n{body or ''}".lower()
    s = unicodedata.normalize("NFKC", s)
    s = re.sub(r"https?://\S+|www\.\S+", " ", s)
    s = re.sub(r"[^a-z0-9\s]+", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s


def jaccard_char_ngrams(a: str, b: str, n: int = 5) -> float:
    if not a or not b:
        return 0.0
    if a == b:
        return 1.0

    def grams(s: str) -> set[str]:
        if len(s) < n:
            return {s}
        return {s[i : i + n] for i in range(len(s) - n + 1)}

    A, B = grams(a), grams(b)
    if not A or not B:
        return 0.0
    return len(A & B) / len(A | B)


def clean_model_text(s: str) -> str:
    s = URL_RE.sub(" ", s or "")
    return re.sub(r"\s+", " ", s).strip().lower()


def make_text(row: dict) -> str:
    return clean_model_text(f"{row.get('title') or ''}\n{row.get('post_body') or ''}")


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


def metrics_bundle(y_true, y_pred) -> dict:
    y_true = np.asarray(y_true)
    y_pred = np.asarray(y_pred)
    p, r, f, s = precision_recall_fscore_support(
        y_true, y_pred, labels=[0, 1], zero_division=0
    )
    return {
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
        "confusion_matrix_labels_[0,1]": confusion_matrix(
            y_true, y_pred, labels=[0, 1]
        ).tolist(),
    }


def by_field(rows, y, pred, field: str) -> dict:
    buckets = defaultdict(lambda: {"y": [], "p": []})
    for i, r in enumerate(rows):
        key = r.get(field) or "unknown"
        buckets[key]["y"].append(y[i])
        buckets[key]["p"].append(pred[i])
    return {k: metrics_bundle(v["y"], v["p"]) for k, v in sorted(buckets.items())}


class UnionFind:
    def __init__(self, n: int):
        self.p = list(range(n))
        self.r = [0] * n

    def find(self, x: int) -> int:
        while self.p[x] != x:
            self.p[x] = self.p[self.p[x]]
            x = self.p[x]
        return x

    def union(self, a: int, b: int) -> None:
        ra, rb = self.find(a), self.find(b)
        if ra == rb:
            return
        if self.r[ra] < self.r[rb]:
            self.p[ra] = rb
        elif self.r[ra] > self.r[rb]:
            self.p[rb] = ra
        else:
            self.p[rb] = ra
            self.r[ra] += 1


def build_tfidf_lr(C: float) -> Pipeline:
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


def keyword_predict(texts: list[str]) -> np.ndarray:
    return np.array([1 if TROUBLE_RE.search(t or "") else 0 for t in texts], dtype=int)


def write_manu_review(dev_by_id: dict[str, dict], flags: list[dict]) -> Path:
    """CSV for Manu: 48 flags + 3 conflicting-text posts; unique reddit_ids; empty decisions."""
    rows_out = []
    seen = set()

    for f in flags:
        rid = f["reddit_id"]
        if rid in seen:
            continue
        seen.add(rid)
        r = dev_by_id.get(rid)
        if not r:
            # Still list the flag even if somehow missing from development
            r = {}
        reasons = f.get("flag_reasons") or []
        reason = (
            "Heuristic flag for human review (not a confirmed labeling error): "
            + "; ".join(reasons)
        )
        if f.get("note"):
            reason += f". Note: {f['note']}"
        rows_out.append(
            {
                "reddit_id": rid,
                "study_id": f.get("study_id") or r.get("study_id") or "",
                "title": r.get("title") if r else f.get("title") or "",
                "post_body": r.get("post_body") or "",
                "current_s2_target": r.get("s2_target") if r else f.get("s2_target"),
                "current_discussion_type": r.get("discussion_type")
                if r
                else f.get("discussion_type")
                or "",
                "source_pool_audit_only": r.get("source_pool_audit_only")
                if r
                else f.get("source_pool_audit_only")
                or "",
                "review_status_audit_only": r.get("review_status_audit_only")
                if r
                else f.get("review_status_audit_only")
                or "",
                "review_reason": reason,
                "manu_decision": "",
                "corrected_label_if_needed": "",
                "explanation": "",
            }
        )

    # Conflicting identical-text trio (senior review)
    conflict_reason = (
        "Exact identical normalized title+body as other development posts, but "
        "s2_target / discussion_type disagree across the group "
        f"{', '.join(CONFLICT_IDS)}. Adjudicate from post text and the labeling "
        "guide; do not resolve by majority vote. This is a confirmed text identity "
        "with conflicting labels — separate from the heuristic 48-flag list."
    )
    for rid in CONFLICT_IDS:
        if rid in seen:
            # Should not happen; if it does, append conflict note rather than duplicate row
            for row in rows_out:
                if row["reddit_id"] == rid:
                    row["review_reason"] += " | ALSO: " + conflict_reason
            continue
        seen.add(rid)
        r = dev_by_id[rid]
        rows_out.append(
            {
                "reddit_id": rid,
                "study_id": r.get("study_id") or "",
                "title": r.get("title") or "",
                "post_body": r.get("post_body") or "",
                "current_s2_target": r.get("s2_target"),
                "current_discussion_type": r.get("discussion_type") or "",
                "source_pool_audit_only": r.get("source_pool_audit_only") or "",
                "review_status_audit_only": r.get("review_status_audit_only") or "",
                "review_reason": conflict_reason,
                "manu_decision": "",
                "corrected_label_if_needed": "",
                "explanation": "",
            }
        )

    # Stable order: flags first (as in source file), then conflict trio
    path = FOLLOWUP / "MANU_LABEL_REVIEW.csv"
    fields = [
        "reddit_id",
        "study_id",
        "title",
        "post_body",
        "current_s2_target",
        "current_discussion_type",
        "source_pool_audit_only",
        "review_status_audit_only",
        "review_reason",
        "manu_decision",
        "corrected_label_if_needed",
        "explanation",
    ]
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields, quoting=csv.QUOTE_MINIMAL)
        w.writeheader()
        for row in rows_out:
            w.writerow(row)

    meta = {
        "n_rows": len(rows_out),
        "n_unique_reddit_id": len(seen),
        "n_from_heuristic_flags": sum(
            1 for r in rows_out if "Heuristic flag" in r["review_reason"]
        ),
        "n_conflict_identical_text": sum(
            1 for r in rows_out if r["reddit_id"] in CONFLICT_IDS
        ),
        "note": (
            "manu_decision / corrected_label_if_needed / explanation left blank. "
            "Heuristic flags are suggestions for review, not confirmed mistakes."
        ),
    }
    (OUT / "manu_review_manifest.json").write_text(
        json.dumps(meta, indent=2) + "\n", encoding="utf-8"
    )
    return path


def audit_within_dev(dev: list[dict]) -> dict:
    n = len(dev)
    norms = [norm_text(r.get("title") or "", r.get("post_body") or "") for r in dev]
    grams = []
    for t in norms:
        if len(t) < 5:
            grams.append({t} if t else set())
        else:
            grams.append({t[i : i + 5] for i in range(len(t) - 4)})

    # Exact groups
    by_exact: dict[str, list[int]] = defaultdict(list)
    for i, t in enumerate(norms):
        by_exact[t].append(i)
    exact_groups = []
    for text, idxs in by_exact.items():
        if len(idxs) < 2:
            continue
        ids = [dev[i]["reddit_id"] for i in idxs]
        targets = [int(dev[i]["s2_target"]) for i in idxs]
        types = [dev[i].get("discussion_type") for i in idxs]
        exact_groups.append(
            {
                "n_posts": len(idxs),
                "reddit_ids": ids,
                "study_ids": [dev[i].get("study_id") for i in idxs],
                "s2_targets": targets,
                "discussion_types": types,
                "label_conflict": len(set(targets)) > 1,
                "title_example": dev[idxs[0]].get("title") or "",
                "norm_text_sha1_prefix": __import__("hashlib")
                .sha1(text.encode())
                .hexdigest()[:12],
            }
        )
    exact_groups.sort(key=lambda g: (-int(g["label_conflict"]), -g["n_posts"], g["reddit_ids"][0]))

    # Near pairs (>= report threshold), excluding exact matches
    # Block by first 16 chars of norm text to keep search tractable
    blocks: dict[str, list[int]] = defaultdict(list)
    for i, t in enumerate(norms):
        key = t[:16] if t else f"__empty_{i}"
        blocks[key].append(i)

    near_pairs = []
    seen_pair = set()
    for idxs in blocks.values():
        for a in range(len(idxs)):
            for b in range(a + 1, len(idxs)):
                i, j = idxs[a], idxs[b]
                if norms[i] == norms[j]:
                    continue
                if not grams[i] or not grams[j]:
                    continue
                inter = len(grams[i] & grams[j])
                if inter == 0:
                    continue
                union = len(grams[i] | grams[j])
                sim = inter / union
                if sim < NEAR_REPORT_THRESHOLD:
                    continue
                pair = tuple(sorted((dev[i]["reddit_id"], dev[j]["reddit_id"])))
                if pair in seen_pair:
                    continue
                seen_pair.add(pair)
                near_pairs.append(
                    {
                        "similarity": round(sim, 4),
                        "method": "jaccard_char_5grams_norm_title_body",
                        "reddit_id_a": dev[i]["reddit_id"],
                        "reddit_id_b": dev[j]["reddit_id"],
                        "s2_target_a": int(dev[i]["s2_target"]),
                        "s2_target_b": int(dev[j]["s2_target"]),
                        "label_conflict": int(dev[i]["s2_target"])
                        != int(dev[j]["s2_target"]),
                        "title_a": dev[i].get("title") or "",
                        "title_b": dev[j].get("title") or "",
                    }
                )

    # Also compare across blocks when titles match exactly (catches near-dups with different body prefix)
    by_title: dict[str, list[int]] = defaultdict(list)
    for i, r in enumerate(dev):
        tn = unicodedata.normalize("NFKC", (r.get("title") or "").lower())
        tn = re.sub(r"\s+", " ", tn).strip()
        if tn:
            by_title[tn].append(i)
    for idxs in by_title.values():
        if len(idxs) < 2:
            continue
        for a in range(len(idxs)):
            for b in range(a + 1, len(idxs)):
                i, j = idxs[a], idxs[b]
                if norms[i] == norms[j]:
                    continue
                sim = jaccard_char_ngrams(norms[i], norms[j], n=5)
                if sim < NEAR_REPORT_THRESHOLD:
                    continue
                pair = tuple(sorted((dev[i]["reddit_id"], dev[j]["reddit_id"])))
                if pair in seen_pair:
                    continue
                seen_pair.add(pair)
                near_pairs.append(
                    {
                        "similarity": round(sim, 4),
                        "method": "jaccard_char_5grams_norm_title_body",
                        "reddit_id_a": dev[i]["reddit_id"],
                        "reddit_id_b": dev[j]["reddit_id"],
                        "s2_target_a": int(dev[i]["s2_target"]),
                        "s2_target_b": int(dev[j]["s2_target"]),
                        "label_conflict": int(dev[i]["s2_target"])
                        != int(dev[j]["s2_target"]),
                        "title_a": dev[i].get("title") or "",
                        "title_b": dev[j].get("title") or "",
                    }
                )

    near_pairs.sort(key=lambda x: (-x["similarity"], x["reddit_id_a"]))
    near_ge_group = [p for p in near_pairs if p["similarity"] >= NEAR_GROUP_THRESHOLD]

    # Union-find groups for validation: exact + near >= 0.92
    uf = UnionFind(n)
    for idxs in by_exact.values():
        for k in idxs[1:]:
            uf.union(idxs[0], k)
    id_to_idx = {dev[i]["reddit_id"]: i for i in range(n)}
    for p in near_ge_group:
        uf.union(id_to_idx[p["reddit_id_a"]], id_to_idx[p["reddit_id_b"]])

    components: dict[int, list[int]] = defaultdict(list)
    for i in range(n):
        components[uf.find(i)].append(i)
    multi = [idxs for idxs in components.values() if len(idxs) > 1]
    group_ids = np.array([uf.find(i) for i in range(n)], dtype=int)

    audit = {
        "method": {
            "exact": "identical normalized title+body (NFKC, lower, URLs stripped, non-alnum collapsed)",
            "near": (
                f"Jaccard similarity of character 5-grams on the same normalized text; "
                f"report pairs ≥ {NEAR_REPORT_THRESHOLD}; "
                f"group for validation at ≥ {NEAR_GROUP_THRESHOLD}"
            ),
            "blocking": "prefix-16 of normalized text, plus same raw-title groups for near search",
        },
        "n_eligible_development": n,
        "exact_duplicate_groups": {
            "n_groups": len(exact_groups),
            "n_posts_involved": sum(g["n_posts"] for g in exact_groups),
            "n_groups_with_label_conflict": sum(
                1 for g in exact_groups if g["label_conflict"]
            ),
            "groups": exact_groups,
        },
        "near_duplicate_pairs": {
            "n_pairs_ge_0.85": len(near_pairs),
            "n_pairs_ge_0.92": len(near_ge_group),
            "n_pairs_ge_0.85_with_label_conflict": sum(
                1 for p in near_pairs if p["label_conflict"]
            ),
            "n_pairs_ge_0.92_with_label_conflict": sum(
                1 for p in near_ge_group if p["label_conflict"]
            ),
            "pairs_ge_0.85": near_pairs,
        },
        "validation_grouping": {
            "rule": "union of exact-text identity and near-dup pairs with sim ≥ 0.92",
            "n_multi_post_groups": len(multi),
            "n_posts_in_multi_post_groups": sum(len(x) for x in multi),
            "n_singleton_posts": n - sum(len(x) for x in multi),
        },
        "note": (
            "Similarity findings are not confirmed labeling errors. "
            "Only exact groups with disagreeing s2_target are confirmed label conflicts on identical text."
        ),
    }
    return audit, group_ids


def run_oof(
    name: str,
    texts: list[str],
    y: np.ndarray,
    groups: np.ndarray | None,
    threshold: float | None,
) -> tuple[np.ndarray, np.ndarray, dict]:
    n = len(y)
    pred = np.zeros(n, dtype=int)
    scores = np.full(n, np.nan)
    if groups is None:
        splitter = StratifiedKFold(n_splits=N_FOLDS, shuffle=True, random_state=SEED)
        splits = splitter.split(np.zeros(n), y)
    else:
        splitter = StratifiedGroupKFold(n_splits=N_FOLDS, shuffle=True, random_state=SEED)
        splits = splitter.split(np.zeros(n), y, groups)

    for train_idx, test_idx in splits:
        y_tr = y[train_idx]
        X_tr = [texts[i] for i in train_idx]
        X_te = [texts[i] for i in test_idx]
        if name == "majority":
            maj = int(Counter(y_tr).most_common(1)[0][0])
            pred[test_idx] = maj
            scores[test_idx] = float(maj)
        elif name == "keyword":
            pr = keyword_predict(X_te)
            pred[test_idx] = pr
            scores[test_idx] = pr.astype(float)
        elif name == "tfidf_lr":
            pipe = build_tfidf_lr(CHOSEN_C)
            pipe.fit(X_tr, y_tr)
            sc = pipe.predict_proba(X_te)[:, 1]
            thr = 0.5 if threshold is None else threshold
            pred[test_idx] = (sc >= thr).astype(int)
            scores[test_idx] = sc
        else:
            raise ValueError(name)
    return pred, scores, metrics_bundle(y, pred)


def write_duplicate_report(audit: dict) -> None:
    path = FOLLOWUP / "DEVELOPMENT_DUPLICATES.md"
    eg = audit["exact_duplicate_groups"]
    np_ = audit["near_duplicate_pairs"]
    vg = audit["validation_grouping"]
    lines = [
        "# Within-development duplicate audit (followup)",
        "",
        f"**Generated:** {datetime.now(timezone.utc).isoformat()}",
        f"**Population:** eligible S2 development rows after protocol exclusions (n={audit['n_eligible_development']})",
        "",
        "Similarity findings are **not** confirmed labeling errors. Confirmed label conflicts on identical text are listed separately below.",
        "",
        "## Method",
        "",
        f"- Exact: {audit['method']['exact']}",
        f"- Near: {audit['method']['near']}",
        f"- Blocking for near search: {audit['method']['blocking']}",
        "",
        "## Exact duplicates (identical normalized title+body)",
        "",
        f"- Groups with ≥2 posts: **{eg['n_groups']}**",
        f"- Posts involved: **{eg['n_posts_involved']}**",
        f"- Groups with conflicting `s2_target`: **{eg['n_groups_with_label_conflict']}**",
        "",
    ]
    if eg["n_groups_with_label_conflict"]:
        lines.append("### Confirmed label conflicts on identical text")
        lines.append("")
        for g in eg["groups"]:
            if not g["label_conflict"]:
                continue
            lines.append(
                f"- IDs `{', '.join(g['reddit_ids'])}` — targets {g['s2_targets']} "
                f"({g['discussion_types']}) — title: {g['title_example']!r}"
            )
        lines.append("")
    lines.extend(
        [
            "### All exact groups (summary)",
            "",
            "| n | reddit_ids | targets | conflict | title |",
            "|---|------------|---------|----------|-------|",
        ]
    )
    for g in eg["groups"]:
        title = (g["title_example"] or "").replace("|", "/")[:60]
        lines.append(
            f"| {g['n_posts']} | {', '.join(g['reddit_ids'])} | {g['s2_targets']} | "
            f"{'yes' if g['label_conflict'] else 'no'} | {title} |"
        )
    lines.extend(
        [
            "",
            "## Near duplicates (similarity only)",
            "",
            f"- Pairs with sim ≥ {NEAR_REPORT_THRESHOLD}: **{np_['n_pairs_ge_0.85']}**",
            f"- Pairs with sim ≥ {NEAR_GROUP_THRESHOLD} (used for fold grouping): **{np_['n_pairs_ge_0.92']}**",
            f"- Pairs ≥ 0.85 with disagreeing targets: **{np_['n_pairs_ge_0.85_with_label_conflict']}** "
            "(disagreement on *similar* text is not automatic proof of error)",
            "",
        ]
    )
    if np_["pairs_ge_0.85"]:
        lines.append("| sim | id_a | id_b | targets | titles |")
        lines.append("|-----|------|------|---------|--------|")
        for p in np_["pairs_ge_0.85"][:40]:
            lines.append(
                f"| {p['similarity']:.4f} | `{p['reddit_id_a']}` | `{p['reddit_id_b']}` | "
                f"{p['s2_target_a']}/{p['s2_target_b']} | "
                f"{(p['title_a'] or '')[:40].replace('|','/')} / "
                f"{(p['title_b'] or '')[:40].replace('|','/')} |"
            )
        if len(np_["pairs_ge_0.85"]) > 40:
            lines.append("")
            lines.append(f"… {len(np_['pairs_ge_0.85']) - 40} more pairs in JSON.")
        lines.append("")
    lines.extend(
        [
            "## Groups used for followup validation folds",
            "",
            f"- Rule: {vg['rule']}",
            f"- Multi-post groups: **{vg['n_multi_post_groups']}** "
            f"({vg['n_posts_in_multi_post_groups']} posts)",
            f"- Singletons: **{vg['n_singleton_posts']}**",
            "",
            "Machine-readable: `results/development_duplicates.json`.",
            "",
        ]
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    (OUT / "development_duplicates.json").write_text(
        json.dumps(audit, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    with (OUT / "near_duplicate_pairs_within_dev.jsonl").open("w", encoding="utf-8") as f:
        for p in np_["pairs_ge_0.85"]:
            f.write(json.dumps(p, ensure_ascii=False) + "\n")


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)

    excl = json.loads((V1_RESULTS / "development_exclusions.json").read_text(encoding="utf-8"))
    exclude_ids = {
        x["reddit_id"] for x in excl.get("additional_near_duplicate_exclusions", [])
    }
    selection = json.loads((V1_RESULTS / "model_selection.json").read_text(encoding="utf-8"))
    chosen = selection["chosen"]
    assert chosen["model"] == "tfidf_lr"
    assert chosen["text_setting"] == "title_body"
    assert chosen["C"] == CHOSEN_C
    threshold = float(chosen["threshold"])
    original_oof = chosen["oof_metrics"]

    flags = load_jsonl(V1_RESULTS / "label_quality_flags.jsonl")
    dev_all = load_jsonl(DATA / "development.jsonl")
    # Full development by id for review sheet (include non-S2 if flagged)
    dev_by_id = {r["reddit_id"]: r for r in dev_all}
    review_path = write_manu_review(dev_by_id, flags)

    dev = eligible_dev(dev_all, exclude_ids)
    audit, group_ids = audit_within_dev(dev)
    write_duplicate_report(audit)

    texts = [make_text(r) for r in dev]
    y = np.array([int(r["s2_target"]) for r in dev])

    # Ungrouped replay of chosen config (for comparison to saved OOF)
    pred_u, scores_u, metrics_u = run_oof(
        "tfidf_lr", texts, y, groups=None, threshold=threshold
    )
    # Grouped sensitivity check
    pred_g, scores_g, metrics_g = run_oof(
        "tfidf_lr", texts, y, groups=group_ids, threshold=threshold
    )
    pred_maj, _, metrics_maj = run_oof(
        "majority", texts, y, groups=group_ids, threshold=None
    )
    pred_kw, _, metrics_kw = run_oof(
        "keyword", texts, y, groups=group_ids, threshold=None
    )

    report = {
        "purpose": "Development-only sensitivity check; not a new model-selection round",
        "reserved_test": "NOT rerun or rescored",
        "chosen_config_unchanged": {
            "text_setting": TEXT_SETTING,
            "model": "tfidf_lr",
            "C": CHOSEN_C,
            "threshold": threshold,
        },
        "n_development": len(dev),
        "grouping": audit["validation_grouping"],
        "original_saved_oof_after_threshold": {
            "macro_f1": original_oof["macro_f1"],
            "class_0_f1": original_oof["class_0_other_update"]["f1"],
            "class_1_f1": original_oof["class_1_troubleshooting"]["f1"],
            "confusion_matrix_labels_[0,1]": original_oof[
                "confusion_matrix_labels_[0,1]"
            ],
        },
        "ungrouped_replay_same_threshold": {
            "note": "StratifiedKFold seed=42 replay; should closely match original OOF",
            "metrics": metrics_u,
            "by_source": by_field(dev, y, pred_u, "source_pool_audit_only"),
            "by_text_availability": by_field(dev, y, pred_u, "text_availability"),
        },
        "grouped_validation": {
            "splitter": "StratifiedGroupKFold n_splits=5 shuffle random_state=42",
            "tfidf_lr": {
                "metrics": metrics_g,
                "by_source": by_field(dev, y, pred_g, "source_pool_audit_only"),
                "by_text_availability": by_field(dev, y, pred_g, "text_availability"),
            },
            "majority": {"metrics": metrics_maj},
            "keyword": {"metrics": metrics_kw},
        },
        "delta_macro_f1_grouped_minus_original_saved": round(
            metrics_g["macro_f1"] - original_oof["macro_f1"], 6
        ),
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
    }

    (OUT / "grouped_validation.json").write_text(
        json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )

    with (OUT / "grouped_oof_predictions.jsonl").open("w", encoding="utf-8") as f:
        for i, r in enumerate(dev):
            f.write(
                json.dumps(
                    {
                        "reddit_id": r["reddit_id"],
                        "study_id": r["study_id"],
                        "y_true": int(y[i]),
                        "y_pred_grouped_tfidf_lr": int(pred_g[i]),
                        "score_grouped_tfidf_lr": float(scores_g[i]),
                        "y_pred_ungrouped_replay": int(pred_u[i]),
                        "y_pred_grouped_majority": int(pred_maj[i]),
                        "y_pred_grouped_keyword": int(pred_kw[i]),
                        "group_id": int(group_ids[i]),
                        "source_pool_audit_only": r.get("source_pool_audit_only"),
                        "text_availability": r.get("text_availability"),
                    },
                    ensure_ascii=False,
                )
                + "\n"
            )

    # Markdown report
    og = original_oof
    md = [
        "# Grouped development validation (followup)",
        "",
        f"**Generated:** {report['timestamp_utc']}",
        "",
        "This is a **sensitivity check** of the already-chosen experiment_v1 model. "
        "Model, `C`, and decision threshold are unchanged. **Reserved test was not rerun.**",
        "",
        "## Config (locked from v1)",
        "",
        f"- Text: `{TEXT_SETTING}`",
        f"- Model: TF-IDF + logistic regression, `C={CHOSEN_C}`",
        f"- Threshold: `{threshold}` (exact saved value from `results/model_selection.json`)",
        f"- Folds: 5, `random_state={SEED}`",
        f"- Grouping: exact identical text ∪ near-dup pairs with Jaccard ≥ {NEAR_GROUP_THRESHOLD}",
        f"- Multi-post groups: {audit['validation_grouping']['n_multi_post_groups']} "
        f"({audit['validation_grouping']['n_posts_in_multi_post_groups']} posts)",
        "",
        "## Headline comparison",
        "",
        "| Setting | macro-F1 | other F1 | troubleshooting F1 | confusion [[TN,FP],[FN,TP]] |",
        "|---------|----------|----------|--------------------|-----------------------------|",
        f"| Original saved OOF (ungrouped, after threshold) | {og['macro_f1']:.4f} | "
        f"{og['class_0_other_update']['f1']:.4f} | {og['class_1_troubleshooting']['f1']:.4f} | "
        f"`{og['confusion_matrix_labels_[0,1]']}` |",
        f"| Ungrouped replay (this script) | {metrics_u['macro_f1']:.4f} | "
        f"{metrics_u['class_0_other_update']['f1']:.4f} | {metrics_u['class_1_troubleshooting']['f1']:.4f} | "
        f"`{metrics_u['confusion_matrix_labels_[0,1]']}` |",
        f"| **Grouped StratifiedGroupKFold** | **{metrics_g['macro_f1']:.4f}** | "
        f"**{metrics_g['class_0_other_update']['f1']:.4f}** | **{metrics_g['class_1_troubleshooting']['f1']:.4f}** | "
        f"`{metrics_g['confusion_matrix_labels_[0,1]']}` |",
        f"| Grouped majority baseline | {metrics_maj['macro_f1']:.4f} | "
        f"{metrics_maj['class_0_other_update']['f1']:.4f} | {metrics_maj['class_1_troubleshooting']['f1']:.4f} | "
        f"`{metrics_maj['confusion_matrix_labels_[0,1]']}` |",
        f"| Grouped keyword baseline | {metrics_kw['macro_f1']:.4f} | "
        f"{metrics_kw['class_0_other_update']['f1']:.4f} | {metrics_kw['class_1_troubleshooting']['f1']:.4f} | "
        f"`{metrics_kw['confusion_matrix_labels_[0,1]']}` |",
        "",
        f"**Delta (grouped − original saved macro-F1):** {report['delta_macro_f1_grouped_minus_original_saved']:+.4f}",
        "",
        "## Grouped TF-IDF LR by source pool",
        "",
        "| Source | n | macro-F1 | other F1 | trouble F1 |",
        "|--------|---|----------|----------|------------|",
    ]
    for src, m in report["grouped_validation"]["tfidf_lr"]["by_source"].items():
        md.append(
            f"| {src} | {m['n']} | {m['macro_f1']:.4f} | "
            f"{m['class_0_other_update']['f1']:.4f} | {m['class_1_troubleshooting']['f1']:.4f} |"
        )
    md.extend(
        [
            "",
            "## Grouped TF-IDF LR by text availability",
            "",
            "| Availability | n | macro-F1 | other F1 | trouble F1 |",
            "|--------------|---|----------|----------|------------|",
        ]
    )
    for ta, m in report["grouped_validation"]["tfidf_lr"]["by_text_availability"].items():
        md.append(
            f"| {ta} | {m['n']} | {m['macro_f1']:.4f} | "
            f"{m['class_0_other_update']['f1']:.4f} | {m['class_1_troubleshooting']['f1']:.4f} |"
        )
    md.extend(
        [
            "",
            "## Simple-language conclusion",
            "",
            _conclusion_paragraph(
                original_oof["macro_f1"],
                metrics_g["macro_f1"],
                metrics_maj["macro_f1"],
                metrics_kw["macro_f1"],
            ),
            "",
            "## Files",
            "",
            f"- Review sheet: `{review_path.name}`",
            "- `DEVELOPMENT_DUPLICATES.md` / `results/development_duplicates.json`",
            "- `results/grouped_validation.json`",
            "- `results/grouped_oof_predictions.jsonl`",
            "- `run_followup.py`",
            "",
        ]
    )
    (FOLLOWUP / "GROUPED_VALIDATION.md").write_text("\n".join(md) + "\n", encoding="utf-8")

    print(
        json.dumps(
            {
                "review_rows": json.loads(
                    (OUT / "manu_review_manifest.json").read_text()
                )["n_rows"],
                "exact_groups": audit["exact_duplicate_groups"]["n_groups"],
                "exact_posts": audit["exact_duplicate_groups"]["n_posts_involved"],
                "exact_conflicts": audit["exact_duplicate_groups"][
                    "n_groups_with_label_conflict"
                ],
                "near_pairs_085": audit["near_duplicate_pairs"]["n_pairs_ge_0.85"],
                "original_macro_f1": original_oof["macro_f1"],
                "grouped_macro_f1": metrics_g["macro_f1"],
                "delta": report["delta_macro_f1_grouped_minus_original_saved"],
            },
            indent=2,
        )
    )
    return 0


def _conclusion_paragraph(
    orig: float, grouped: float, maj: float, kw: float
) -> str:
    delta = grouped - orig
    if abs(delta) < 0.02:
        change = (
            f"Keeping identical/near-duplicate posts in the same fold changes development "
            f"macro-F1 by only {delta:+.3f} ({orig:.3f} → {grouped:.3f}). That is a small shift."
        )
    elif delta < 0:
        change = (
            f"Grouped validation lowers development macro-F1 by {abs(delta):.3f} "
            f"({orig:.3f} → {grouped:.3f}), so the original OOF number was somewhat optimistic."
        )
    else:
        change = (
            f"Grouped validation raises development macro-F1 by {delta:.3f} "
            f"({orig:.3f} → {grouped:.3f})."
        )
    still_beats = grouped > kw + 0.05 and grouped > maj + 0.05
    if still_beats:
        claim = (
            "The chosen TF-IDF model still clearly beats the majority and keyword baselines "
            "under the same grouped folds, so the **qualitative conclusion stands**: post text "
            "carries usable signal for troubleshooting vs other update discussion on this "
            "reviewed development set. This check does not change the model or re-open the "
            "reserved test."
        )
    else:
        claim = (
            "Under grouped folds the gap to baselines is weaker; treat development claims "
            "cautiously and wait for Manu’s label review before hardening manuscript numbers. "
            "The reserved-test result was not updated here."
        )
    return change + " " + claim


if __name__ == "__main__":
    raise SystemExit(main())
