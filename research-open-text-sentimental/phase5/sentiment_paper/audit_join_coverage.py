#!/usr/bin/env python3
"""Join reviewed posts to saved API snapshots and measure comment coverage.

Does not fit models, does not score tests, and does not fetch live threads.
"""

from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
PHASE3 = REPO / "phase3"
OUT = HERE / "results"

MASTER = REPO / "phase2" / "combined_dataset" / "master_records.json"
DEV = PHASE3 / "revised_development_v2" / "development_v2.jsonl"
REDDIT_OOF = PHASE3 / "reddit_only_sensitivity" / "results" / "grouped_oof_predictions.jsonl"
MIXED_OOF = PHASE3 / "diagnostic_results" / "grouped_oof_predictions.jsonl"
RESERVED = PHASE3 / "experiment_v1" / "data" / "reserved_test.jsonl"
FRESH = PHASE3 / "fresh_test_20261007" / "frozen_joint_labels" / "s2_test_344.jsonl"
FRESH_RAW = PHASE3 / "fresh_test_20261007" / "raw"
FRESH_METRICS = PHASE3 / "fresh_test_20261007" / "results_fixed_model" / "metrics.json"
LABELS = REPO / "tps_gds_classification" / "data" / "updated_labeled_dataset_unique.csv"
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
NEAR_DUP = {"1t0wme9", "1wrqch6"}
LEAK_FIELDS = (
    "metadata",
    "category",
    "classification",
    "sentiment",
    "sentiment_score",
    "author_description_sentiment",
    "comments_avg_sentiment_score",
    "features",
    "tag",
    "tags",
    "isAboutCve",
    "isAboutLatestUpdate",
    "mltl",
    "source",
)


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def host_of(url: str) -> str:
    host = urlparse(url or "").netloc.lower()
    return host[4:] if host.startswith("www.") else host


def load_snapshot(path: Path, family: str) -> dict[str, dict]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    posts = payload.get("data") or []
    out = {}
    for post in posts:
        rid = str(post.get("redditId") or post.get("reddit_id") or "").strip()
        if not rid:
            continue
        out[rid] = post
    return out


def comment_stats(post: dict | None) -> dict:
    if post is None:
        return {
            "joined": False,
            "has_title": False,
            "has_body": False,
            "n_stored_comments": 0,
            "n_nonempty_comments": 0,
            "n_author_replies": 0,
            "n_community_comments": 0,
            "num_comments": None,
            "post_timestamp": False,
            "comment_timestamps": 0,
            "comment_timestamps_missing": 0,
            "leak_fields_present": [],
        }
    author = (post.get("author") or "").strip()
    body = (post.get("author_description") or post.get("post_body") or "").strip()
    title = (post.get("title") or "").strip()
    comments = post.get("comments") or []
    n_author = 0
    n_comm = 0
    nonempty = 0
    ts_ok = 0
    ts_missing = 0
    for c in comments:
        cbody = (c.get("body") or "").strip()
        if not cbody:
            continue
        nonempty += 1
        cts = str(c.get("created_utc") or "").strip()
        if cts:
            ts_ok += 1
        else:
            ts_missing += 1
        is_author = bool(c.get("is_submitter")) or (
            author and (c.get("author") or "").strip() == author
        )
        if is_author:
            n_author += 1
        else:
            n_comm += 1
    return {
        "joined": True,
        "has_title": bool(title),
        "has_body": bool(body),
        "n_stored_comments": len(comments),
        "n_nonempty_comments": nonempty,
        "n_author_replies": n_author,
        "n_community_comments": n_comm,
        "num_comments": post.get("num_comments"),
        "post_timestamp": bool(str(post.get("created_utc") or "").strip()),
        "comment_timestamps": ts_ok,
        "comment_timestamps_missing": ts_missing,
        "leak_fields_present": [k for k in LEAK_FIELDS if k in post and post.get(k) not in (None, "", [], {})],
    }


def summarize(rows: list[dict], key: str) -> dict:
    group = [r for r in rows if r["stratum"] == key]
    n = len(group)
    if n == 0:
        return {"n": 0}

    def rate(pred):
        return sum(1 for r in group if pred(r)) / n

    stored = sum(r["chosen_n_stored"] for r in group)
    listed = sum(int(r["chosen_num_comments"] or 0) for r in group)
    return {
        "n": n,
        "joined_any_saved_snapshot": sum(r["joined_any"] for r in group),
        "joined_march_raw": sum(r["joined_march"] for r in group),
        "joined_oct5_raw": sum(r["joined_oct5"] for r in group),
        "joined_both": sum(r["joined_both"] for r in group),
        "title_rate": rate(lambda r: r["has_title"]),
        "body_rate": rate(lambda r: r["has_body"]),
        "title_only_n": sum(1 for r in group if r["has_title"] and not r["has_body"]),
        "any_nonempty_comment_n": sum(1 for r in group if r["chosen_n_nonempty"] > 0),
        "author_reply_n": sum(1 for r in group if r["chosen_n_author"] > 0),
        "community_comment_n": sum(1 for r in group if r["chosen_n_community"] > 0),
        "both_roles_n": sum(1 for r in group if r["chosen_n_author"] > 0 and r["chosen_n_community"] > 0),
        "sum_stored_comments": stored,
        "sum_num_comments": listed,
        "stored_over_num_comments": (stored / listed) if listed else None,
        "posts_stored_lt_num_comments": sum(
            1
            for r in group
            if r["chosen_num_comments"] is not None and r["chosen_n_stored"] < int(r["chosen_num_comments"])
        ),
        "post_timestamp_n": sum(1 for r in group if r["post_timestamp"]),
        "domain_counts": dict(Counter(r["domain"] or "missing" for r in group)),
        "saved_duplicate_group_n": sum(1 for r in group if r["duplicate_group"] is not None),
        "s2_class_counts": dict(Counter(str(r["s2_target"]) for r in group)),
        "discussion_type_counts": dict(Counter(r["discussion_type"] or "missing" for r in group)),
    }


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    master = json.loads(MASTER.read_text(encoding="utf-8"))
    by_master = {r["reddit_id"]: r for r in master}
    dev_rows = read_jsonl(DEV)
    dev_by_id = {r["reddit_id"]: r for r in dev_rows}
    reddit_oof = read_jsonl(REDDIT_OOF)
    mixed_oof = read_jsonl(MIXED_OOF)
    reserved = read_jsonl(RESERVED)
    fresh = read_jsonl(FRESH)
    gold = list(csv.DictReader(LABELS.open(encoding="utf-8")))
    gold_by_id = {}
    for row in gold:
        gold_by_id[str(row["reddit_id"]).strip()] = int(row["corrected_label"])

    march = {}
    march_file_hit = Counter()
    for name in ("tps_response.json", "gds_response.json"):
        posts = load_snapshot(OLD_RAW / name, "march")
        for rid in posts:
            march_file_hit[name] += 1
        march.update(posts)  # gds loaded second, matching trajectory.build
    oct5 = {}
    fresh_raw = {}
    fresh_pages_without_comments_key = []
    for path in sorted(FRESH_RAW.glob("update_related_page_*.json")):
        posts = load_snapshot(path, "fresh_collection")
        missing_key = 0
        for rid, post in posts.items():
            if "comments" not in post:
                missing_key += 1
            fresh_raw.setdefault(rid, post)
        if posts and missing_key == len(posts):
            fresh_pages_without_comments_key.append(path.name)
    oct5_route = {}
    for name in OCT5_FILES:
        route = "oct5_tps_candidate" if name.startswith("tps") else "oct5_gds_candidate"
        posts = load_snapshot(OCT5 / name, route)
        for rid, post in posts.items():
            if rid not in oct5:
                oct5[rid] = post
                oct5_route[rid] = route

    group = {}
    for row in reddit_oof:
        group[row["reddit_id"]] = ("reddit_2050", int(row["group_id"]), int(row["fold"]))
    for row in mixed_oof:
        group.setdefault(row["reddit_id"], ("mixed_2080_only", None, int(row["fold"])))

    reddit_ids = {r["reddit_id"] for r in reddit_oof}
    mixed_ids = {r["reddit_id"] for r in mixed_oof}
    reserved_ids = {r["reddit_id"] for r in reserved}
    fresh_ids = {r["reddit_id"] for r in fresh}
    s2_dev_ids = {
        r["reddit_id"]
        for r in dev_rows
        if r.get("s2_in_scope") and r.get("s2_target") in (0, 1) and r["reddit_id"] not in NEAR_DUP
    }

    label_rows = {r["reddit_id"]: r for r in dev_rows}
    for r in reserved + fresh:
        label_rows.setdefault(r["reddit_id"], r)

    records = []
    universe = list(by_master)
    for rid in fresh_ids:
        if rid not in by_master:
            universe.append(rid)
    for rid in universe:
        src = by_master.get(rid, {})
        mstat = comment_stats(march.get(rid))
        ostat = comment_stats(oct5.get(rid))
        fstat = comment_stats(fresh_raw.get(rid))
        # Declared snapshot rule for the combined collection: October 5 saved response
        # if present, else March raw. Fresh-test IDs are outside that collection and
        # use their own saved collection pages.
        if rid in fresh_ids and fstat["joined"]:
            chosen = fstat
            chosen_name = "fresh_collection_raw"
        elif ostat["joined"]:
            chosen = ostat
            chosen_name = "oct5"
        elif mstat["joined"]:
            chosen = mstat
            chosen_name = "march"
        else:
            chosen = mstat
            chosen_name = "master_text_only"
        lab = label_rows.get(rid, {})
        url = src.get("url") or (fresh_raw.get(rid) or {}).get("url") or ""
        if rid in fresh_ids:
            split = "fresh_s2"
        elif rid in reserved_ids:
            split = "reserved"
        elif rid in s2_dev_ids:
            split = "development_s2"
        elif rid in dev_by_id:
            split = "development_not_s2"
        else:
            split = "master_not_in_development_snapshot"
        records.append(
            {
                "reddit_id": rid,
                "stratum": split,
                "joined_march": mstat["joined"],
                "joined_oct5": ostat["joined"],
                "joined_fresh_raw": fstat["joined"],
                "joined_both": mstat["joined"] and ostat["joined"],
                "joined_any": mstat["joined"] or ostat["joined"] or fstat["joined"],
                "oct5_candidate_route_audit_only": oct5_route.get(rid),
                "has_title": chosen["has_title"] if chosen["joined"] else bool((src.get("title") or "").strip()),
                "has_body": chosen["has_body"] if chosen["joined"] else bool((src.get("post_body") or "").strip()),
                "chosen_snapshot": chosen_name,
                "chosen_n_stored": chosen["n_stored_comments"] if chosen["joined"] else int(src.get("n_comments_stored") or 0),
                "chosen_n_nonempty": chosen["n_nonempty_comments"] if chosen["joined"] else None,
                "chosen_n_author": chosen["n_author_replies"] if chosen["joined"] else None,
                "chosen_n_community": chosen["n_community_comments"] if chosen["joined"] else None,
                "chosen_num_comments": chosen["num_comments"] if chosen["joined"] else None,
                "post_timestamp": chosen["post_timestamp"] if chosen["joined"] else bool(src.get("created_utc")),
                "domain": host_of(url),
                "duplicate_group": None if rid not in group else group[rid][1],
                "saved_fold": None if rid not in group else group[rid][2],
                "fold_file": None if rid not in group else group[rid][0],
                "s2_in_scope": lab.get("s2_in_scope"),
                "s2_target": lab.get("s2_target"),
                "discussion_type": lab.get("discussion_type") or src.get("phase2_discussion_type"),
                "historical_corrected_label": gold_by_id.get(rid),
                "source_pool": src.get("source_pool"),
                "master_n_comments_stored": src.get("n_comments_stored"),
                "master_text_availability": src.get("text_availability"),
                "in_reddit_2050": rid in reddit_ids,
                "in_mixed_2080": rid in mixed_ids,
            }
        )

    strata = [
        "development_s2",
        "development_not_s2",
        "reserved",
        "fresh_s2",
        "master_not_in_development_snapshot",
    ]
    # S2 class and historical class cuts are separate. They are coverage strata, not model scores.
    def subset(pred):
        return [r for r in records if pred(r)]

    s2_dev = subset(lambda r: r["stratum"] == "development_s2")
    reddit_2050 = subset(lambda r: r["in_reddit_2050"])
    hist = subset(lambda r: r["historical_corrected_label"] is not None)

    discussion_counts = Counter((r["discussion_type"] or "missing") for r in s2_dev)
    gd_tt = [
        r
        for r in s2_dev
        if r["discussion_type"] in ("general_dissatisfaction", "technical_troubleshooting")
        and r["in_reddit_2050"]
    ]
    outcome_fields = sorted(
        {
            k
            for row in master[:50]
            for k in row
            if any(tok in k.lower() for tok in ("outcome", "resolv", "solved", "fix_confirmed"))
        }
    )
    dev_outcome_fields = sorted(
        {
            k
            for row in dev_rows[:20]
            for k in row
            if any(tok in k.lower() for tok in ("outcome", "resolv", "solved", "fix_confirmed"))
        }
    )

    fresh_metrics = json.loads(FRESH_METRICS.read_text(encoding="utf-8"))
    audit = {
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "live_fetch": False,
        "models_fit": False,
        "tests_scored": False,
        "label_guardrail": (
            "S2 negative class is other update discussion (s2_target 0), not historical GDS "
            "and not discussion_type general_dissatisfaction. Those populations are reported separately."
        ),
        "snapshot_rule": "Combined-collection IDs use the October 5 saved API response if present, otherwise the March 2026 raw response. Fresh-test IDs are outside the master and use phase3/fresh_test_20261007/raw pages. Snapshots are not concatenated and threads are not refetched.",
        "inputs": {
            "master_n": len(master),
            "master_sha256": sha256_file(MASTER),
            "development_v2_n": len(dev_rows),
            "development_v2_sha256": sha256_file(DEV),
            "reserved_n": len(reserved),
            "reserved_sha256": sha256_file(RESERVED),
            "fresh_s2_n": len(fresh),
            "fresh_s2_sha256": sha256_file(FRESH),
            "march_joined_ids": len(march),
            "oct5_joined_ids": len(oct5),
            "fresh_raw_ids": len(fresh_raw),
            "fresh_pages_without_comments_key": fresh_pages_without_comments_key,
            "oct5_route_counts": dict(Counter(oct5_route.values())),
        },
        "coverage_by_split": {name: summarize(records, name) for name in strata},
        "development_s2_by_class": {
            "troubleshooting_1": summarize(
                [{**r, "stratum": "troubleshooting_1"} for r in s2_dev if r["s2_target"] == 1],
                "troubleshooting_1",
            ),
            "other_update_0": summarize(
                [{**r, "stratum": "other_update_0"} for r in s2_dev if r["s2_target"] == 0],
                "other_update_0",
            ),
        },
        "reddit_2050_s2": {
            "n": len(reddit_2050),
            "by_s2": {
                "troubleshooting_1": sum(r["s2_target"] == 1 for r in reddit_2050),
                "other_update_0": sum(r["s2_target"] == 0 for r in reddit_2050),
            },
            "joined_any": sum(r["joined_any"] for r in reddit_2050),
            "any_nonempty_comment": sum((r["chosen_n_nonempty"] or 0) > 0 for r in reddit_2050),
            "author_reply": sum((r["chosen_n_author"] or 0) > 0 for r in reddit_2050),
            "community_comment": sum((r["chosen_n_community"] or 0) > 0 for r in reddit_2050),
            "both_roles": sum(
                (r["chosen_n_author"] or 0) > 0 and (r["chosen_n_community"] or 0) > 0 for r in reddit_2050
            ),
            "title_only": sum(r["has_title"] and not r["has_body"] for r in reddit_2050),
            "by_s2_comment": {
                "troubleshooting_with_comment": sum(
                    r["s2_target"] == 1 and (r["chosen_n_nonempty"] or 0) > 0 for r in reddit_2050
                ),
                "other_update_with_comment": sum(
                    r["s2_target"] == 0 and (r["chosen_n_nonempty"] or 0) > 0 for r in reddit_2050
                ),
            },
        },
        "fresh_comment_field": {
            "n": sum(1 for r in records if r["stratum"] == "fresh_s2"),
            "comments_key_absent": sum(
                1
                for r in records
                if r["stratum"] == "fresh_s2"
                and r["reddit_id"] in fresh_raw
                and "comments" not in fresh_raw[r["reddit_id"]]
            ),
            "comments_key_present": sum(
                1
                for r in records
                if r["stratum"] == "fresh_s2"
                and r["reddit_id"] in fresh_raw
                and "comments" in fresh_raw[r["reddit_id"]]
            ),
            "note": "A missing comments key is not evidence of zero Reddit comments. Page-level omission is recorded separately from an empty comments list.",
        },
        "historical_tps_gds_separate": {
            "n": len(hist),
            "tps_1": sum(r["historical_corrected_label"] == 1 for r in hist),
            "gds_0": sum(r["historical_corrected_label"] == 0 for r in hist),
            "joined_march": sum(r["joined_march"] for r in hist),
            "note": "Historical corrected_label is the ICMLA TPS/GDS gold file. It is not the revised S2 label.",
        },
        "restricted_discussion_type_on_reddit_2050": {
            "eligible_rule": "discussion_type in {technical_troubleshooting, general_dissatisfaction} and ID in the 2050 Reddit S2 folds",
            "n": len(gd_tt),
            "technical_troubleshooting": sum(r["discussion_type"] == "technical_troubleshooting" for r in gd_tt),
            "general_dissatisfaction": sum(r["discussion_type"] == "general_dissatisfaction" for r in gd_tt),
            "development_s2_discussion_type_counts": dict(discussion_counts),
        },
        "human_confirmed_outcome_label": {
            "present": False,
            "master_fields_matching_outcome_words_in_sample": outcome_fields,
            "development_fields_matching_outcome_words_in_sample": dev_outcome_fields,
            "decision": (
                "No human-confirmed resolution or outcome label was found. "
                "Saved replies cannot be described as evidence that a reply solved an issue. "
                "Absence of a confirmation is unknown outcome, not unresolved."
            ),
        },
        "api_fields_that_must_not_enter_a_classifier": {
            "reason": (
                "Saved API records can supply title, body, comment text, author flags, timestamps, "
                "num_comments, and URL domain. The same records also carry candidate-route names, "
                "metadata.predicted, metadata.labeled, keyword features, category, and precomputed sentiment. "
                "Those fields are API candidate signals, not reviewed S2 labels."
            ),
            "excluded_field_names": list(LEAK_FIELDS),
            "oct5_candidate_routes_are_not_labels": True,
        },
        "preserved_fresh_test_score_not_recomputed": {
            "source": str(FRESH_METRICS),
            "sha256": sha256_file(FRESH_METRICS),
            "macro_f1": fresh_metrics["model_metrics"]["macro_f1"],
            "n": fresh_metrics["model_metrics"]["n"],
            "support": fresh_metrics["model_metrics"]["support"],
            "confusion_matrix_labels_[0,1]": fresh_metrics["model_metrics"]["confusion_matrix_labels_[0,1]"],
            "note": "Quoted from the existing fixed-model evaluation. This audit did not rescore it.",
        },
        "releasetrain_3pct_and_risk_cadence": {
            "status": "unverified separate question",
            "local_evidence": (
                "phase2/new_sources/api/pagination_manifest.json records October 5 candidate pulls, "
                "not a prevalence. phase5/SCIENTIFIC_INTEGRATION_DECISION.md records inconsistent live "
                "route totals and states that the professor's 3% estimate has no documented numerator, "
                "denominator, time range, or risk definition in these files."
            ),
            "asserted_as_result": False,
        },
    }
    (OUT / "join_coverage_audit.json").write_text(
        json.dumps(audit, indent=2) + "\n", encoding="utf-8"
    )
    # Compact per-post coverage. No comment text and no model scores.
    with (OUT / "join_coverage_posts.jsonl").open("w", encoding="utf-8") as f:
        for row in records:
            if row["stratum"] == "master_not_in_development_snapshot" and row["historical_corrected_label"] is None:
                continue
            f.write(json.dumps(row, ensure_ascii=False) + "\n")
    write_audit_md(audit)
    print(json.dumps({
        "reddit_2050_comments": audit["reddit_2050_s2"],
        "gd_tt": audit["restricted_discussion_type_on_reddit_2050"]["n"],
        "gd": audit["restricted_discussion_type_on_reddit_2050"]["general_dissatisfaction"],
        "tt": audit["restricted_discussion_type_on_reddit_2050"]["technical_troubleshooting"],
        "fresh_macro_f1_quoted": audit["preserved_fresh_test_score_not_recomputed"]["macro_f1"],
    }, indent=2))
    return 0


def write_audit_md(audit: dict) -> None:
    cov = audit["coverage_by_split"]
    lines = [
        "# Join and coverage audit",
        "",
        f"**Created:** {audit['created_utc']}",
        "",
        "Reviewed IDs were joined to the March 2026 raw responses, the October 5 saved API pages, and the saved fresh-test collection pages by `redditId`. No live thread was fetched. No model was fit. The reserved and fresh files were used only to count coverage. They were not scored.",
        "",
        audit["label_guardrail"],
        "",
        "## Snapshot rule",
        "",
        audit["snapshot_rule"],
        "",
        f"Master posts: {audit['inputs']['master_n']}. March snapshot IDs: {audit['inputs']['march_joined_ids']}. October 5 snapshot IDs: {audit['inputs']['oct5_joined_ids']}. October 5 route counts, which are candidate files rather than labels: `{json.dumps(audit['inputs']['oct5_route_counts'])}`.",
        "",
        "## Coverage by split",
        "",
        "| Split | n | Joined any saved snapshot | Nonempty stored comment | Author reply | Community comment | Both roles | Title only | Stored/recorded comments |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for name, row in cov.items():
        if row.get("n", 0) == 0:
            lines.append(f"| {name} | 0 | 0 | 0 | 0 | 0 | 0 | 0 | n/a |")
            continue
        ratio = row.get("stored_over_num_comments")
        ratio_s = "n/a" if ratio is None else f"{ratio:.3f}"
        lines.append(
            f"| {name} | {row['n']} | {row['joined_any_saved_snapshot']} | {row['any_nonempty_comment_n']} | "
            f"{row['author_reply_n']} | {row['community_comment_n']} | {row['both_roles_n']} | "
            f"{row['title_only_n']} | {ratio_s} |"
        )
    r = audit["reddit_2050_s2"]
    d = audit["development_s2_by_class"]
    g = audit["restricted_discussion_type_on_reddit_2050"]
    h = audit["historical_tps_gds_separate"]
    lines.extend(
        [
            "",
            "## S2 development classes",
            "",
            "These counts use `s2_target`. Class 0 is other update discussion.",
            "",
            f"| S2 class | n | Nonempty comment | Author reply | Community comment |",
            f"|---|---:|---:|---:|---:|",
            f"| Troubleshooting | {d['troubleshooting_1']['n']} | {d['troubleshooting_1']['any_nonempty_comment_n']} | {d['troubleshooting_1']['author_reply_n']} | {d['troubleshooting_1']['community_comment_n']} |",
            f"| Other update discussion | {d['other_update_0']['n']} | {d['other_update_0']['any_nonempty_comment_n']} | {d['other_update_0']['author_reply_n']} | {d['other_update_0']['community_comment_n']} |",
            "",
            f"Reddit-URL modeling rows with saved folds: **{r['n']}** ({r['by_s2']['troubleshooting_1']} troubleshooting, {r['by_s2']['other_update_0']} other update). Joined to a saved snapshot: {r['joined_any']}. At least one nonempty stored comment: {r['any_nonempty_comment']} (troubleshooting {r['by_s2_comment']['troubleshooting_with_comment']}, other update {r['by_s2_comment']['other_update_with_comment']}). Author reply: {r['author_reply']}. Community comment: {r['community_comment']}. Both roles: {r['both_roles']}. Title only: {r['title_only']}.",
            "",
            "## Historical TPS/GDS, separate from S2",
            "",
            f"Gold file posts in the master join: {h['n']} (TPS {h['tps_1']}, GDS {h['gds_0']}). March snapshot join: {h['joined_march']}. {h['note']}",
            "",
            "## Restricted discussion-type population",
            "",
            f"On the 2,050 Reddit S2 rows, `technical_troubleshooting` versus `general_dissatisfaction` contains **{g['n']}** posts: {g['technical_troubleshooting']} troubleshooting-type and {g['general_dissatisfaction']} general-dissatisfaction. This is not a substitute for the S2 population. Development S2 discussion-type counts: `{json.dumps(g['development_s2_discussion_type_counts'])}`.",
            "",
            "## Outcome labels",
            "",
            audit["human_confirmed_outcome_label"]["decision"],
            "",
            "## Fields that can support text without using API categories",
            "",
            audit["api_fields_that_must_not_enter_a_classifier"]["reason"],
            "",
            "## Preserved fresh-test score",
            "",
            f"The existing fresh-test evaluation remains macro-F1 **{audit['preserved_fresh_test_score_not_recomputed']['macro_f1']:.4f}** on {audit['preserved_fresh_test_score_not_recomputed']['n']} posts (other update {audit['preserved_fresh_test_score_not_recomputed']['support']['other_update_0']}, troubleshooting {audit['preserved_fresh_test_score_not_recomputed']['support']['troubleshooting_1']}; confusion `{audit['preserved_fresh_test_score_not_recomputed']['confusion_matrix_labels_[0,1]']}`). This audit did not recompute it.",
            "",
            f"Fresh saved pages: comments key present for {audit['fresh_comment_field']['comments_key_present']} of {audit['fresh_comment_field']['n']} posts and absent for {audit['fresh_comment_field']['comments_key_absent']}. {audit['fresh_comment_field']['note']}",
            "",
            "## Unverified ReleaseTrain question",
            "",
            audit["releasetrain_3pct_and_risk_cadence"]["local_evidence"] + " It is not a result of this audit.",
            "",
        ]
    )
    (HERE / "AUDIT.md").write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(main())
