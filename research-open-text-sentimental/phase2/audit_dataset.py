#!/usr/bin/env python3
"""Read-only Phase 2 audit computations. Does not modify Phase 1 data or labels.

Rerun requires vaderSentiment (`pip install vaderSentiment`). The numbers
cited in the audit were saved to phase2/audit_computations.json on 2026-10-05.
"""

from __future__ import annotations

import csv
import json
import math
import re
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer  # noqa: E402

LABELS_UNIQUE = ROOT / "tps_gds_classification/data/updated_labeled_dataset_unique.csv"
LABELS_FULL = ROOT / "tps_gds_classification/data/updated_labeled_dataset.csv"
DATA_JSON = ROOT / "tps_gds_classification/data/tps_gds_dataset.json"
RAW_TPS = ROOT / "tps_gds_classification/data/raw/tps_response.json"
RAW_GDS = ROOT / "tps_gds_classification/data/raw/gds_response.json"
C1 = ROOT / "data/c1_prime/c1_prime_metrics.csv"
HUMAN = ROOT / "data/human_eval/human_eval_template_80.csv"
OUT = ROOT / "phase2/audit_computations.json"

TIER_A = {
    "android", "chrome", "comfyui", "django", "docker", "firefox", "github",
    "godot", "ibm", "immich", "java", "kubernetes", "linux", "macos", "neovim",
    "nest", "node", "nuxt", "oracle", "php", "python", "react", "rust",
    "rustdesk", "supabase", "typescript", "vscode", "wordpress",
}

TECH = re.compile(
    r"\b(error|bug|bugs|fix|fixed|crash|crashed|failed|failure|exception|"
    r"install|broken|issue|problem|update|upgrade|dependency|config)\b",
    re.I,
)
ANNOUNCE = re.compile(
    r"\b(released|release notes|announcing|announcement|changelog|is out|"
    r"now available|what's new|whats new|version \d|software release)\b",
    re.I,
)
BOT = re.compile(r"\bi am a bot\b", re.I)


def read_csv(path: Path) -> list[dict]:
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def compound(sia, text: str) -> float:
    text = (text or "").strip()
    if not text:
        return 0.0
    return float(sia.polarity_scores(text)["compound"])


def mean(xs: list[float]) -> float | None:
    return sum(xs) / len(xs) if xs else None


def positive_score(post: dict) -> float | None:
    meta = post.get("metadata") or {}
    pred = meta.get("predicted") if isinstance(meta, dict) else None
    if isinstance(pred, dict) and pred.get("positiveScore") is not None:
        return float(pred["positiveScore"])
    return None


def is_update_related(post: dict):
    meta = post.get("metadata") or {}
    pred = meta.get("predicted") if isinstance(meta, dict) else None
    if isinstance(pred, dict):
        return pred.get("isUpdateRelated")
    return None


def main() -> None:
    sia = SentimentIntensityAnalyzer()
    labels = read_csv(LABELS_UNIQUE)
    labels_full = read_csv(LABELS_FULL)
    dataset = json.loads(DATA_JSON.read_text(encoding="utf-8"))
    raw_tps = json.loads(RAW_TPS.read_text(encoding="utf-8"))
    raw_gds = json.loads(RAW_GDS.read_text(encoding="utf-8"))
    c1 = read_csv(C1)
    human = read_csv(HUMAN)

    # --- labels ---
    id_counts = Counter(r["reddit_id"].strip() for r in labels_full)
    dup_ids = {i: n for i, n in id_counts.items() if n > 1}
    conflicts = []
    by_full = defaultdict(list)
    for r in labels_full:
        by_full[r["reddit_id"].strip()].append(r)
    for i, rows in by_full.items():
        labs = {row["corrected_label"] for row in rows}
        currents = {row["label_current"] for row in rows}
        if len(rows) > 1 and (len(labs) > 1 or len(currents) > 1):
            conflicts.append({
                "reddit_id": i,
                "n": len(rows),
                "corrected": sorted(labs),
                "label_current": sorted(currents),
                "title": rows[0]["title"][:120],
            })

    gold = []
    for r in labels:
        gold.append({
            **r,
            "reddit_id": r["reddit_id"].strip(),
            "corrected": int(r["corrected_label"]),
            "current": int(r["label_current"]) if str(r["label_current"]).strip() != "" else None,
            "sub": (r["subreddit"] or "").strip(),
        })
    n = len(gold)
    n_tps = sum(g["corrected"] == 1 for g in gold)
    n_gds = sum(g["corrected"] == 0 for g in gold)
    disagree = sum(g["current"] is not None and g["current"] != g["corrected"] for g in gold)
    tier_a = [g for g in gold if g["sub"].lower() in TIER_A]
    subs = Counter(g["sub"] for g in gold)
    subs_tps = Counter(g["sub"] for g in gold if g["corrected"] == 1)

    # guideline examples
    examples = {
        "1o0nzld": 1, "1r2myps": 1, "1nwebdk": 1, "1oetmbo": 1, "1ql2670": 1, "1nqixzh": 1,
        "1nze9rs": 0, "1misnpf": 0, "1mlixg3": 0, "1mhlyz0": 0, "1mul6k9": 0, "1mid4hg": 0,
    }
    gold_by_id = {g["reddit_id"]: g for g in gold}
    example_check = []
    for i, expected in examples.items():
        g = gold_by_id.get(i)
        example_check.append({
            "reddit_id": i,
            "expected": expected,
            "present": g is not None,
            "corrected": None if g is None else g["corrected"],
            "matches": None if g is None else g["corrected"] == expected,
            "subreddit": None if g is None else g["sub"],
            "title": None if g is None else g["title"][:140],
        })

    # --- raw pools ---
    def pool_stats(payload: dict, name: str) -> dict:
        data = payload.get("data") or []
        scores = [positive_score(p) for p in data]
        present = [s for s in scores if s is not None]
        num_c = sum(int(p.get("num_comments") or 0) for p in data)
        stored = sum(len(p.get("comments") or []) for p in data)
        trunc = sum(1 for p in data if len(p.get("comments") or []) < int(p.get("num_comments") or 0))
        empty_body = sum(1 for p in data if not (p.get("author_description") or "").strip())
        empty_comments_field = sum(1 for p in data if not (p.get("comments") or []))
        bot_posts = 0
        empty_comment_bodies = 0
        total_comment_bodies = 0
        submitter_mismatch = 0
        submitter_checked = 0
        bad_time = 0
        times = []
        update_flags = Counter()
        categories = Counter()
        tags = Counter()
        for p in data:
            categories[str(p.get("category"))] += 1
            tags[str(p.get("tag"))] += 1
            update_flags[str(is_update_related(p))] += 1
            try:
                times.append(datetime.fromisoformat(str(p.get("created_utc")).replace("Z", "+00:00")))
            except Exception:
                bad_time += 1
            comments = p.get("comments") or []
            author = (p.get("author") or "").strip()
            for c in comments:
                body = (c.get("body") or "").strip()
                total_comment_bodies += 1
                if not body:
                    empty_comment_bodies += 1
                if body and BOT.search(body):
                    bot_posts += 1
                flag = c.get("is_submitter")
                name_match = bool(author) and (c.get("author") or "").strip() == author
                if flag is True or flag is False:
                    submitter_checked += 1
                    if bool(flag) != name_match:
                        submitter_mismatch += 1
                cts = str(c.get("created_utc") or "")
                if cts and not re.match(r"\d{4}-\d{2}-\d{2}T", cts):
                    bad_time += 1
        return {
            "name": name,
            "fetched_at_utc": payload.get("fetched_at_utc"),
            "response_total_field": payload.get("total"),
            "n_returned": len(data),
            "filters": payload.get("filters"),
            "positiveScore_present": len(present),
            "positiveScore_missing": len(data) - len(present),
            "positiveScore_min": min(present) if present else None,
            "positiveScore_max": max(present) if present else None,
            "positiveScore_ge_0.3": sum(s >= 0.3 for s in present),
            "positiveScore_le_0.5": sum(s <= 0.5 for s in present),
            "positiveScore_between_0.3_and_0.5": sum(0.3 <= s <= 0.5 for s in present),
            "reddit_score_min": min(p.get("score") or 0 for p in data) if data else None,
            "reddit_score_has_zero": sum((p.get("score") or 0) == 0 for p in data),
            "sum_num_comments": num_c,
            "sum_stored_comments": stored,
            "stored_over_num_comments": round(stored / num_c, 4) if num_c else None,
            "posts_stored_lt_num_comments": trunc,
            "empty_author_description": empty_body,
            "posts_with_no_comments_array": empty_comments_field,
            "empty_comment_bodies": empty_comment_bodies,
            "comment_bodies": total_comment_bodies,
            "comments_matching_i_am_a_bot": bot_posts,
            "is_submitter_vs_author_name_mismatches": submitter_mismatch,
            "is_submitter_checked": submitter_checked,
            "unparsed_timestamps": bad_time,
            "created_min": min(times).isoformat() if times else None,
            "created_max": max(times).isoformat() if times else None,
            "isUpdateRelated": dict(update_flags),
            "category": dict(categories),
            "tag_top": tags.most_common(15),
        }

    tps_posts = {str(p.get("redditId")): p for p in raw_tps.get("data") or []}
    gds_posts = {str(p.get("redditId")): p for p in raw_gds.get("data") or []}
    overlap_ids = sorted(set(tps_posts) & set(gds_posts))
    overlap_diffs = []
    for i in overlap_ids:
        a, b = tps_posts[i], gds_posts[i]
        overlap_diffs.append({
            "reddit_id": i,
            "title_equal": (a.get("title") or "") == (b.get("title") or ""),
            "n_comments_tps_copy": len(a.get("comments") or []),
            "n_comments_gds_copy": len(b.get("comments") or []),
            "positiveScore_tps_copy": positive_score(a),
            "positiveScore_gds_copy": positive_score(b),
        })

    # trajectory role diagnostics on raw, using the C1' rules
    fallback = 0
    body_only = 0
    author_comments_n = []
    community_n = []
    no_community = 0
    missing_raw = 0
    by_id_gds_wins = {}
    for src in (tps_posts, gds_posts):
        by_id_gds_wins.update(src)  # gds loaded second, same as trajectory.build
    for g in gold:
        post = by_id_gds_wins.get(g["reddit_id"])
        if not post:
            missing_raw += 1
            continue
        author = (post.get("author") or "").strip()
        body = (post.get("author_description") or "").strip()
        comments = sorted(post.get("comments") or [], key=lambda c: str(c.get("created_utc") or ""))
        n_author_c = 0
        n_comm = 0
        for c in comments:
            if not (c.get("body") or "").strip():
                continue
            is_author = bool(c.get("is_submitter")) or (author and (c.get("author") or "").strip() == author)
            if is_author:
                n_author_c += 1
            else:
                n_comm += 1
        author_comments_n.append(n_author_c)
        community_n.append(n_comm)
        if n_comm == 0:
            no_community += 1
        if not body and n_author_c == 0:
            fallback += 1
        if body and n_author_c == 0:
            body_only += 1

    # lexical: title compound and tech-cue mask
    def mask_tech(text: str) -> str:
        return TECH.sub("item", text or "")

    lex_rows = []
    for g in gold:
        post = by_id_gds_wins.get(g["reddit_id"])
        if not post:
            continue
        title = post.get("title") or ""
        body = post.get("author_description") or ""
        title_c = compound(sia, title)
        masked = compound(sia, mask_tech(title))
        lex_rows.append({
            "label": g["corrected"],
            "title_c": title_c,
            "masked_c": masked,
            "tech": bool(TECH.search(title)),
            "announce": bool(ANNOUNCE.search(title)),
            "sub": g["sub"],
            "title": title,
            "reddit_id": g["reddit_id"],
            "category": str(post.get("category")),
            "tag": str(post.get("tag")),
            "pos": positive_score(post),
        })

    def split_mean(key, label):
        return mean([r[key] for r in lex_rows if r["label"] == label])

    def rate(pred, label):
        rows = [r for r in lex_rows if r["label"] == label]
        return sum(1 for r in rows if pred(r)) / len(rows) if rows else None

    announce_tps = [r for r in lex_rows if r["label"] == 1 and r["announce"]]
    tech_gds_examples = [r for r in lex_rows if r["label"] == 0 and r["tech"]]
    news_by_gold = Counter((r["label"], r["tag"]) for r in lex_rows)
    cat_by_gold = Counter((r["label"], r["category"]) for r in lex_rows)

    # c1 metrics
    c1_tps = [r for r in c1 if int(r["corrected_label"]) == 1]
    c1_gds = [r for r in c1 if int(r["corrected_label"]) == 0]

    def fmean(rows, col):
        return mean([float(r[col]) for r in rows])

    # human
    def norm_label(s):
        t = (s or "").strip().upper()
        if t in ("TPS", "1"):
            return 1
        if t in ("GDS", "0"):
            return 0
        return None

    def norm_div(s):
        t = (s or "").strip().lower().replace(" ", "_").replace("-", "_")
        if "author" in t or "op_more" in t:
            return "author_more_negative"
        if "community" in t or "crowd" in t:
            return "community_more_negative"
        if "align" in t or t == "similar":
            return "aligned"
        if "unclear" in t:
            return "unclear"
        return t or None

    human_rows = []
    for r in human:
        gold_l = int(r["gold_corrected_label"])
        human_l = norm_label(r.get("human_label_tps_gds"))
        div = float(r.get("vader_divergence") or 0)
        author_neg = str(r.get("vader_author_more_negative")).strip().lower() in ("true", "1")
        vader_bucket = "aligned" if div < 0.15 else ("author_more_negative" if author_neg else "community_more_negative")
        human_div = norm_div(r.get("human_divergence_rating"))
        note = (r.get("human_notes") or "").strip()
        note_l = note.lower()
        says_not_tps = any(p in note_l for p in [
            "not troubleshooting", "not a troubleshooting", "not technical problem",
            "no active troubleshooting", "no troubleshooting", "announcement",
            "showcase", "not software", "opinion", "news", "not a concrete",
        ])
        says_tps = any(p in note_l for p in [
            "troubleshooting", "bug", "error", "how do i", "crash", "broken",
        ]) and not says_not_tps
        human_rows.append({
            "reddit_id": r["reddit_id"],
            "subreddit": r["subreddit"],
            "title": r["title_raw"][:160],
            "gold": gold_l,
            "human": human_l,
            "agree_gold": human_l == gold_l,
            "note": note,
            "human_div": human_div,
            "vader_bucket": vader_bucket,
            "div_agree": human_div == vader_bucket,
            "note_vs_human_tps_conflict": bool(note) and says_not_tps and human_l == 1,
            "note_vs_human_gds_conflict": bool(note) and says_tps and human_l == 0,
            "note_vs_gold_tps_conflict": bool(note) and says_not_tps and gold_l == 1,
            "note_vs_gold_gds_conflict": bool(note) and says_tps and gold_l == 0,
        })

    # dataset json duplicates
    records = dataset.get("records") or []
    json_ids = [str(r.get("reddit_id") or "").strip() for r in records]
    json_id_counts = Counter(json_ids)
    empty_text = sum(1 for r in records if not (r.get("text") or "").strip())
    empty_title = sum(1 for r in records if not (r.get("title_raw") or "").strip())
    empty_body = sum(1 for r in records if not (r.get("body_raw") or "").strip())
    comments_included = Counter(int(r.get("comments_included") or 0) for r in records)

    label_ids = {g["reddit_id"] for g in gold}
    json_unique = set(json_ids)
    text_by_id = {}
    dup_text_groups = defaultdict(list)
    for r in records:
        rid = str(r.get("reddit_id") or "").strip()
        if rid in text_by_id:
            continue
        text_by_id[rid] = (r.get("text") or "").strip()
        title = (r.get("title_raw") or "").strip().lower()
        if title:
            dup_text_groups[title].append(rid)
    duplicate_titles = {t: ids for t, ids in dup_text_groups.items() if len(set(ids)) > 1}

    pos_by_gold = {"TPS": [], "GDS": []}
    for r in lex_rows:
        if r["pos"] is not None:
            pos_by_gold["TPS" if r["label"] == 1 else "GDS"].append(r["pos"])

    out = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "labels": {
            "unique_file_rows": n,
            "unique_ids": len({g["reddit_id"] for g in gold}),
            "tps": n_tps,
            "gds": n_gds,
            "nonunique_file_rows": len(labels_full),
            "duplicate_ids_in_nonunique": len(dup_ids),
            "extra_rows": len(labels_full) - len(set(id_counts)),
            "conflicting_duplicate_labels": conflicts,
            "nonempty_notes_unique": sum(1 for g in gold if (g.get("notes") or "").strip()),
            "api_vs_gold_disagreements": disagree,
            "disagreement_rate": round(disagree / n, 4) if n else None,
            "label_current_counts": dict(Counter(g["current"] for g in gold)),
            "missing_title": sum(1 for g in gold if not (g.get("title") or "").strip()),
            "missing_url": sum(1 for g in gold if not (g.get("url") or "").strip()),
            "missing_subreddit": sum(1 for g in gold if not g["sub"]),
            "n_subreddits": len(subs),
            "top_subreddits": subs.most_common(20),
            "top_tps_subreddits": subs_tps.most_common(15),
            "tier_a_n": len(tier_a),
            "tier_a_tps": sum(g["corrected"] == 1 for g in tier_a),
            "tier_a_gds": sum(g["corrected"] == 0 for g in tier_a),
            "outside_tier_a": (Counter(g["sub"] for g in gold if g["sub"].lower() not in TIER_A)).most_common(25),
            "guideline_examples": example_check,
        },
        "dataset_json": {
            "meta": dataset.get("meta"),
            "n_records": len(records),
            "duplicate_reddit_ids": sum(1 for i, c in json_id_counts.items() if c > 1),
            "ids_not_in_gold": sorted(json_unique - label_ids)[:30],
            "n_ids_not_in_gold": len(json_unique - label_ids),
            "gold_ids_not_in_json": sorted(label_ids - json_unique),
            "empty_cleaned_text": empty_text,
            "empty_title": empty_title,
            "empty_body": empty_body,
            "comments_included_hist": dict(sorted(comments_included.items())),
            "duplicate_exact_titles": [
                {"title": t[:140], "ids": ids} for t, ids in list(duplicate_titles.items())[:20]
            ],
            "n_duplicate_exact_titles": len(duplicate_titles),
        },
        "raw_pools": {
            "tps": pool_stats(raw_tps, "tps"),
            "gds": pool_stats(raw_gds, "gds"),
            "overlap_ids": len(overlap_ids),
            "overlap_comment_count_diffs": sum(
                1 for d in overlap_diffs if d["n_comments_tps_copy"] != d["n_comments_gds_copy"]
            ),
            "overlap_examples": overlap_diffs[:8],
            "trajectory_title_fallback_posts": fallback,
            "trajectory_body_but_no_author_comments": body_only,
            "trajectory_zero_community_comments": no_community,
            "mean_author_comment_count": mean(author_comments_n),
            "posts_with_zero_author_comments": sum(x == 0 for x in author_comments_n),
            "gold_missing_from_raw_merge": missing_raw,
        },
        "lexical_title_vader": {
            "mean_title_compound_tps": split_mean("title_c", 1),
            "mean_title_compound_gds": split_mean("title_c", 0),
            "mean_title_compound_tech_masked_tps": split_mean("masked_c", 1),
            "mean_title_compound_tech_masked_gds": split_mean("masked_c", 0),
            "tech_cue_rate_tps": rate(lambda r: r["tech"], 1),
            "tech_cue_rate_gds": rate(lambda r: r["tech"], 0),
            "announce_keyword_rate_tps": rate(lambda r: r["announce"], 1),
            "announce_keyword_rate_gds": rate(lambda r: r["announce"], 0),
            "announce_keyword_tps_examples": [
                {"id": r["reddit_id"], "sub": r["sub"], "title": r["title"][:140]} for r in announce_tps[:12]
            ],
            "positiveScore_mean_by_gold": {k: mean(v) for k, v in pos_by_gold.items()},
            "category_by_gold_label": [
                {"gold": lab, "category": cat, "n": n_}
                for (lab, cat), n_ in cat_by_gold.most_common()
            ],
            "tag_by_gold_label_top": [
                {"gold": lab, "tag": tag, "n": n_}
                for (lab, tag), n_ in news_by_gold.most_common(25)
            ],
        },
        "c1_saved_means": {
            "divergence_tps": fmean(c1_tps, "sentiment_divergence"),
            "divergence_gds": fmean(c1_gds, "sentiment_divergence"),
            "author_mean_tps": fmean(c1_tps, "author_mean_sentiment"),
            "author_mean_gds": fmean(c1_gds, "author_mean_sentiment"),
            "community_mean_tps": fmean(c1_tps, "community_mean_sentiment"),
            "community_mean_gds": fmean(c1_gds, "community_mean_sentiment"),
            "author_more_negative_tps": mean([1 if str(r["author_more_negative"]).lower()=="true" else 0 for r in c1_tps]),
            "author_more_negative_gds": mean([1 if str(r["author_more_negative"]).lower()=="true" else 0 for r in c1_gds]),
            "n": len(c1),
            "trajectory_eligible_false": sum(str(r.get("trajectory_eligible")).lower()=="false" for r in c1),
            "notes": dict(Counter(r.get("trajectory_notes") or "" for r in c1)),
        },
        "human": {
            "n": len(human_rows),
            "columns": list(human[0].keys()) if human else [],
            "gold_tps": sum(r["gold"] == 1 for r in human_rows),
            "label_agreement": mean([1 if r["agree_gold"] else 0 for r in human_rows]),
            "divergence_agreement": mean([1 if r["div_agree"] else 0 for r in human_rows]),
            "notes_nonempty": sum(1 for r in human_rows if r["note"]),
            "note_conflicts": [r for r in human_rows if r["note_vs_human_tps_conflict"] or r["note_vs_human_gds_conflict"] or r["note_vs_gold_tps_conflict"] or r["note_vs_gold_gds_conflict"]],
            "label_disagreements": [r for r in human_rows if not r["agree_gold"]],
            "div_confusion": [
                {"human_div": a, "vader_bucket": b, "n": n_}
                for (a, b), n_ in Counter((r["human_div"], r["vader_bucket"]) for r in human_rows).most_common()
            ],
        },
    }
    OUT.write_text(json.dumps(out, indent=2, default=str), encoding="utf-8")
    print("wrote", OUT)
    print("tps/gds", n_tps, n_gds, "disagree", disagree)
    print("fallback", fallback, "no_community", no_community, "overlap", len(overlap_ids))
    print("title compound TPS/GDS", out["lexical_title_vader"]["mean_title_compound_tps"], out["lexical_title_vader"]["mean_title_compound_gds"])
    print("masked", out["lexical_title_vader"]["mean_title_compound_tech_masked_tps"], out["lexical_title_vader"]["mean_title_compound_tech_masked_gds"])
    print("human conflicts", len(out["human"]["note_conflicts"]), "label disagreements", len(out["human"]["label_disagreements"]))
    print("pos means", out["lexical_title_vader"]["positiveScore_mean_by_gold"])


if __name__ == "__main__":
    main()
