#!/usr/bin/env python3
"""
Build the Phase 2 blinded labeling pilot (~100 posts).

- Does not modify Phase 1 labels or experiment outputs.
- Does not fill human labels.
- Writes reviewer sheets without gold labels, source pools, keywords,
  VADER scores, or model predictions.
"""

from __future__ import annotations

import csv
import hashlib
import json
import random
import re
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SEED = 20261005
TARGET_N = 100

OUT_DIR = ROOT / "phase2" / "annotation" / "pilot"
OUT_DIR.mkdir(parents=True, exist_ok=True)

GOLD_CSV = ROOT / "tps_gds_classification" / "data" / "updated_labeled_dataset_unique.csv"
DATASET_JSON = ROOT / "tps_gds_classification" / "data" / "tps_gds_dataset.json"
RAW_TPS = ROOT / "tps_gds_classification" / "data" / "raw" / "tps_response.json"
RAW_GDS = ROOT / "tps_gds_classification" / "data" / "raw" / "gds_response.json"
API_DIR = ROOT / "phase2" / "new_sources" / "api"

# Difficult / interesting reddit_ids highlighted in the Phase 2 audit (examples for review).
AUDIT_HARD_IDS = {
    "1nuwiid",
    "1nznnb8",
    "1nv3m8j",
    "1nwgz8q",
    "1o1cbch",
    "1nww0mp",
    "1oiwr33",
    "1nqu3ag",
    "1pf32mo",
    "1onnoh7",
    "1nw9rwz",
    "1oqaia9",
    "1qone71",
    "1nu697z",
    "1nqxc6f",
    "1r7chxn",
    "1qz4z4c",
    "1nze9rs",
    "1ozp5qj",
    "1oualms",
}

LIKELY_OOS_SUBS = {"transformers", "bitcoin", "anime", "union"}
NEWS_RE = re.compile(
    r"\b(released|release notes|announcing|announcement|changelog|is out|"
    r"now available|what's new|whats new|rolling out|security update)\b",
    re.I,
)
TECH_RE = re.compile(
    r"\b(error|bug|crash|broken|fix|failed|freeze|frozen|workaround|how do i|"
    r"not working|doesn't work|doesnt work|regression|stuck|leak|leaks|"
    r"glitch|glitches|defect|segfault|traceback|install failed|"
    r"won't (start|launch|open|boot)|wont (start|launch|open|boot))\b",
    re.I,
)
RANT_RE = re.compile(r"\b(hate|sucks|ruined|garbage|trash|tired of|another update)\b", re.I)


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def load_gold() -> dict[str, dict]:
    rows = {}
    with GOLD_CSV.open(encoding="utf-8", newline="") as f:
        for r in csv.DictReader(f):
            rid = (r.get("reddit_id") or "").strip()
            if rid:
                rows[rid] = r
    return rows


def load_dataset_by_id() -> dict[str, dict]:
    payload = load_json(DATASET_JSON)
    out = {}
    for r in payload.get("records") or []:
        rid = str(r.get("reddit_id") or "").strip()
        if rid and rid not in out:
            out[rid] = r
    return out


def load_raw_by_id() -> dict[str, dict]:
    by_id: dict[str, dict] = {}
    for path in (RAW_TPS, RAW_GDS):
        payload = load_json(path)
        for post in payload.get("data") or []:
            rid = str(post.get("redditId") or "").strip()
            if rid:
                by_id[rid] = post
    return by_id


def load_new_api_posts() -> tuple[list[dict], list[dict]]:
    tps_files = [API_DIR / "tps_response.json"] + sorted(
        API_DIR.glob("tps_page_*.json"),
        key=lambda p: int(p.stem.split("_")[-1]),
    )
    tps: list[dict] = []
    seen = set()
    for path in tps_files:
        for post in load_json(path).get("data") or []:
            rid = str(post.get("redditId") or "").strip()
            if not rid or rid in seen:
                continue
            seen.add(rid)
            tps.append(post)
    gds = []
    seen_g = set()
    for post in load_json(API_DIR / "gds_response.json").get("data") or []:
        rid = str(post.get("redditId") or "").strip()
        if not rid or rid in seen_g:
            continue
        seen_g.add(rid)
        gds.append(post)
    return tps, gds


def clip(text: str, limit: int) -> str:
    text = (text or "").strip()
    if len(text) <= limit:
        return text
    return text[: limit - 1].rstrip() + "…"


def comment_snippets(comments: list[dict], max_comments: int = 5, max_chars_each: int = 280) -> str:
    if not comments:
        return ""
    scored = sorted(
        comments,
        key=lambda c: (
            c.get("score") is None,
            -(c.get("score") or 0),
            str(c.get("created_utc") or ""),
        ),
    )
    parts = []
    for i, c in enumerate(scored[:max_comments], start=1):
        body = clip((c.get("body") or "").strip(), max_chars_each)
        if not body:
            continue
        who = "OP" if c.get("is_submitter") else "reply"
        parts.append(f"[{i}:{who}] {body}")
    return "\n".join(parts)


def text_available(title: str, body: str, context: str) -> tuple[bool, str]:
    title = (title or "").strip()
    body = (body or "").strip()
    context = (context or "").strip()
    if not title and not body and not context:
        return False, "no_title_body_or_comments"
    if not title and not body and context:
        return True, "comments_only"
    if title and not body and not context:
        return True, "title_only"
    if title and not body and context:
        return True, "title_plus_comments"
    if title and body:
        return True, "title_and_body" if not context else "title_body_comments"
    return True, "partial"


def stratum_for_original(rid: str, gold: dict, title: str, subreddit: str) -> str:
    if rid in AUDIT_HARD_IDS:
        return "orig_audit_hard"
    sub = (subreddit or "").lower()
    if sub in LIKELY_OOS_SUBS:
        return "orig_likely_out_of_scope"
    if NEWS_RE.search(title or ""):
        return "orig_news_announce"
    lab = str(gold.get("corrected_label", ""))
    if lab == "1":
        return "orig_gold_tps"
    if TECH_RE.search(title or ""):
        return "orig_gold_gds_techish"
    if RANT_RE.search(title or ""):
        return "orig_gold_gds_rantish"
    return "orig_gold_gds_other"


def stratum_for_new(pool: str, title: str, body: str, keywords: list[str] | None) -> str:
    text = f"{title or ''}\n{body or ''}"
    if pool == "new_tps":
        # Keyword hit that may still look like news/success/advice.
        if NEWS_RE.search(text) or re.search(r"\b(successful|success|working fine|love)\b", text, re.I):
            return "new_tps_keyword_ambiguous"
        if keywords and any(k in {"fix", "fixed", "error"} for k in keywords):
            return "new_tps_keyword_common"
        return "new_tps_ordinary"
    # new_gds: no troubleshooting keyword according to API, but may still be technical.
    if TECH_RE.search(text):
        return "new_gds_techish_no_keyword"
    if NEWS_RE.search(text):
        return "new_gds_news"
    if RANT_RE.search(text):
        return "new_gds_rantish"
    return "new_gds_ordinary"


def anonymous_id(seed: int, reddit_id: str) -> str:
    digest = hashlib.sha256(f"{seed}:{reddit_id}".encode("utf-8")).hexdigest()[:10].upper()
    return f"P2-{digest}"


def sample_from(rng: random.Random, items: list[dict], k: int) -> list[dict]:
    if k <= 0 or not items:
        return []
    if len(items) <= k:
        return list(items)
    return rng.sample(items, k)


def build_candidate_pool() -> list[dict]:
    gold = load_gold()
    dataset = load_dataset_by_id()
    raw = load_raw_by_id()
    new_tps, new_gds = load_new_api_posts()

    candidates: list[dict] = []

    # Original 542
    for rid, g in gold.items():
        ds = dataset.get(rid) or {}
        post = raw.get(rid) or {}
        title = (ds.get("title_raw") or g.get("title") or post.get("title") or "").strip()
        body = (ds.get("body_raw") or post.get("author_description") or "").strip()
        comments = post.get("comments") or []
        context = comment_snippets(comments)
        ok, avail = text_available(title, body, context)
        if not ok:
            continue
        candidates.append(
            {
                "reddit_id": rid,
                "source_family": "phase1_542",
                "source_pool": "phase1_gold_file",
                "phase1_corrected_label": g.get("corrected_label"),
                "phase1_label_current": g.get("label_current"),
                "api_matched_keywords": None,
                "subreddit": g.get("subreddit") or ds.get("subreddit") or post.get("subreddit") or "",
                "url": g.get("url") or ds.get("url") or post.get("url") or "",
                "title": title,
                "post_body": body,
                "discussion_context": context,
                "n_comments_stored": len(comments),
                "text_availability": avail,
                "stratum": stratum_for_original(rid, g, title, g.get("subreddit") or ""),
                "created_utc": post.get("created_utc") or "",
            }
        )

    gold_ids = set(gold)

    for post in new_tps:
        rid = str(post.get("redditId") or "").strip()
        if not rid or rid in gold_ids:
            # Prefer the Phase 1 record for overlapping ids; do not double-sample.
            continue
        title = (post.get("title") or "").strip()
        body = (post.get("author_description") or "").strip()
        comments = post.get("comments") or []
        context = comment_snippets(comments)
        ok, avail = text_available(title, body, context)
        if not ok:
            continue
        feats = post.get("features") or {}
        kws = feats.get("matchedKeywords") if isinstance(feats, dict) else None
        candidates.append(
            {
                "reddit_id": rid,
                "source_family": "oct5_api",
                "source_pool": "oct5_query_tps",
                "phase1_corrected_label": None,
                "phase1_label_current": None,
                "api_matched_keywords": kws,
                "subreddit": post.get("subreddit") or "",
                "url": post.get("url") or "",
                "title": title,
                "post_body": body,
                "discussion_context": context,
                "n_comments_stored": len(comments),
                "text_availability": avail,
                "stratum": stratum_for_new("new_tps", title, body, kws if isinstance(kws, list) else None),
                "created_utc": post.get("created_utc") or "",
            }
        )

    for post in new_gds:
        rid = str(post.get("redditId") or "").strip()
        if not rid or rid in gold_ids:
            continue
        title = (post.get("title") or "").strip()
        body = (post.get("author_description") or "").strip()
        comments = post.get("comments") or []
        context = comment_snippets(comments)
        ok, avail = text_available(title, body, context)
        if not ok:
            continue
        candidates.append(
            {
                "reddit_id": rid,
                "source_family": "oct5_api",
                "source_pool": "oct5_query_gds",
                "phase1_corrected_label": None,
                "phase1_label_current": None,
                "api_matched_keywords": None,
                "subreddit": post.get("subreddit") or "",
                "url": post.get("url") or "",
                "title": title,
                "post_body": body,
                "discussion_context": context,
                "n_comments_stored": len(comments),
                "text_availability": avail,
                "stratum": stratum_for_new("new_gds", title, body, None),
                "created_utc": post.get("created_utc") or "",
            }
        )

    return candidates


def select_sample(candidates: list[dict], seed: int, target_n: int) -> list[dict]:
    rng = random.Random(seed)
    by_stratum: dict[str, list[dict]] = defaultdict(list)
    for c in candidates:
        by_stratum[c["stratum"]].append(c)

    # Target quotas: intentionally oversample difficult strata, keep ordinary cases too.
    # Exact fills depend on pool size; leftovers are topped up at the end.
    quotas = {
        "orig_audit_hard": 12,
        "orig_gold_tps": 10,
        "orig_gold_gds_techish": 8,
        "orig_news_announce": 5,
        "orig_likely_out_of_scope": 6,
        "orig_gold_gds_rantish": 4,
        "orig_gold_gds_other": 5,
        "new_tps_keyword_ambiguous": 10,
        "new_tps_keyword_common": 10,
        "new_tps_ordinary": 10,
        "new_gds_techish_no_keyword": 8,
        "new_gds_news": 4,
        "new_gds_rantish": 4,
        "new_gds_ordinary": 4,
    }

    selected: list[dict] = []
    selected_ids: set[str] = set()
    fill_log = []

    for stratum, want in quotas.items():
        pool = by_stratum.get(stratum) or []
        take = sample_from(rng, pool, min(want, len(pool)))
        for item in take:
            if item["reddit_id"] in selected_ids:
                continue
            selected.append(item)
            selected_ids.add(item["reddit_id"])
        fill_log.append(
            {
                "stratum": stratum,
                "quota": want,
                "available": len(pool),
                "taken": len(take),
            }
        )

    if len(selected) < target_n:
        remaining = [c for c in candidates if c["reddit_id"] not in selected_ids]
        # Prefer mixed sources when topping up.
        remaining.sort(
            key=lambda c: (
                0 if c["source_family"] == "phase1_542" else 1,
                c["stratum"],
                c["reddit_id"],
            )
        )
        need = target_n - len(selected)
        topup = sample_from(rng, remaining, need)
        for item in topup:
            selected.append(item)
            selected_ids.add(item["reddit_id"])
        fill_log.append(
            {
                "stratum": "_topup",
                "quota": need,
                "available": len(remaining),
                "taken": len(topup),
            }
        )

    # If somehow over target (should not happen), trim deterministically.
    if len(selected) > target_n:
        selected = sample_from(rng, selected, target_n)

    # Stable anonymous order for reviewers (shuffled, not grouped by source).
    order = list(selected)
    rng.shuffle(order)
    for i, item in enumerate(order, start=1):
        item["pilot_id"] = anonymous_id(seed, item["reddit_id"])
        item["sheet_order"] = i

    # Guarantee unique pilot_ids.
    id_counts = Counter(x["pilot_id"] for x in order)
    if any(v > 1 for v in id_counts.values()):
        raise RuntimeError("pilot_id collision; change seed or hash length")

    return order, fill_log


def availability_note(code: str) -> str:
    return {
        "title_only": "Title only; no body or replies were available in the saved snapshot.",
        "title_plus_comments": "No post body in the saved snapshot; limited replies are shown.",
        "comments_only": "No title/body; only limited replies were available.",
        "title_and_body": "Title and body available; no replies in the saved snapshot.",
        "title_body_comments": "Title, body, and limited replies are shown.",
        "partial": "Partial text only.",
    }.get(code, code)


def write_reviewer_sheet(rows: list[dict], path: Path) -> None:
    fieldnames = [
        "pilot_id",
        "sheet_order",
        "title",
        "post_body",
        "discussion_context",
        "text_availability_note",
        "about_software",
        "update_related",
        "discussion_type",
        "confidence",
        "reason",
    ]
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for r in rows:
            w.writerow(
                {
                    "pilot_id": r["pilot_id"],
                    "sheet_order": r["sheet_order"],
                    "title": r["title"],
                    "post_body": clip(r["post_body"], 2500),
                    "discussion_context": clip(r["discussion_context"], 2000),
                    "text_availability_note": availability_note(r["text_availability"]),
                    "about_software": "",
                    "update_related": "",
                    "discussion_type": "",
                    "confidence": "",
                    "reason": "",
                }
            )


def rebuild_rows_from_mapping(mapping_path: Path) -> list[dict]:
    """Preserve an existing 100-post selection; refresh text fields from sources."""
    with mapping_path.open(encoding="utf-8", newline="") as f:
        mapping = list(csv.DictReader(f))
    if not mapping:
        raise SystemExit(f"Empty mapping: {mapping_path}")

    by_id = {c["reddit_id"]: c for c in build_candidate_pool()}
    rows: list[dict] = []
    missing = []
    for m in mapping:
        rid = m["reddit_id"].strip()
        base = by_id.get(rid)
        if not base:
            missing.append(rid)
            continue
        item = dict(base)
        item["pilot_id"] = m["pilot_id"]
        item["sheet_order"] = int(m["sheet_order"])
        # Keep mapping stratum/source as previously selected.
        item["stratum"] = m.get("stratum") or item.get("stratum")
        item["source_pool"] = m.get("source_pool") or item.get("source_pool")
        item["source_family"] = m.get("source_family") or item.get("source_family")
        rows.append(item)
    if missing:
        raise SystemExit(f"Mapping reddit_ids missing from candidate rebuild: {missing[:10]}")
    rows.sort(key=lambda r: r["sheet_order"])
    return rows


def write_mapping(rows: list[dict], path: Path) -> None:
    fieldnames = [
        "pilot_id",
        "sheet_order",
        "reddit_id",
        "url",
        "subreddit",
        "source_family",
        "source_pool",
        "stratum",
        "phase1_corrected_label",
        "phase1_label_current",
        "api_matched_keywords",
        "text_availability",
        "n_comments_stored",
        "created_utc",
        "title",
    ]
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for r in sorted(rows, key=lambda x: x["sheet_order"]):
            kws = r.get("api_matched_keywords")
            if isinstance(kws, list):
                kws_s = "|".join(str(x) for x in kws)
            else:
                kws_s = ""
            w.writerow(
                {
                    "pilot_id": r["pilot_id"],
                    "sheet_order": r["sheet_order"],
                    "reddit_id": r["reddit_id"],
                    "url": r["url"],
                    "subreddit": r["subreddit"],
                    "source_family": r["source_family"],
                    "source_pool": r["source_pool"],
                    "stratum": r["stratum"],
                    "phase1_corrected_label": r.get("phase1_corrected_label") or "",
                    "phase1_label_current": r.get("phase1_label_current") or "",
                    "api_matched_keywords": kws_s,
                    "text_availability": r["text_availability"],
                    "n_comments_stored": r["n_comments_stored"],
                    "created_utc": r.get("created_utc") or "",
                    "title": r["title"],
                }
            )


def write_sampling_manifest(rows: list[dict], fill_log: list[dict], path: Path) -> None:
    payload = {
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "seed": SEED,
        "target_n": TARGET_N,
        "n_selected": len(rows),
        "unique_reddit_ids": len({r["reddit_id"] for r in rows}),
        "unique_pilot_ids": len({r["pilot_id"] for r in rows}),
        "source_counts": dict(Counter(r["source_pool"] for r in rows)),
        "family_counts": dict(Counter(r["source_family"] for r in rows)),
        "stratum_counts": dict(Counter(r["stratum"] for r in rows)),
        "text_availability_counts": dict(Counter(r["text_availability"] for r in rows)),
        "quota_fill_log": fill_log,
        "notes": [
            "API source_pool values are candidate pools only, not labels.",
            "phase1_corrected_label is stored only in the analysis mapping file.",
            "Reviewer sheets omit reddit_id, url, subreddit, source, keywords, labels, and scores.",
        ],
    }
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


FORBIDDEN_REVIEWER_COLUMNS = {
    "reddit_id",
    "url",
    "subreddit",
    "source_pool",
    "source_family",
    "stratum",
    "phase1_corrected_label",
    "corrected_label",
    "gold",
    "label_current",
    "api_matched_keywords",
    "matchedkeywords",
    "vader",
    "sentiment",
    "prediction",
    "pred",
    "scope",  # retired combined field; must not reappear on sheets
}

ANSWER_FIELDS = (
    "about_software",
    "update_related",
    "discussion_type",
    "confidence",
    "reason",
)


def assert_reviewer_sheet_blind(path: Path) -> list[str]:
    with path.open(encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        cols = [c.lower() for c in (reader.fieldnames or [])]
        problems = []
        required = {
            "pilot_id",
            "sheet_order",
            "title",
            "post_body",
            "discussion_context",
            "text_availability_note",
            *ANSWER_FIELDS,
        }
        missing_cols = sorted(required - set(cols))
        if missing_cols:
            problems.append(f"{path.name} missing columns: {missing_cols}")
        for bad in FORBIDDEN_REVIEWER_COLUMNS:
            if any(bad == c or (bad in c and bad not in {"pred"}) for c in cols):
                # allow 'prediction' style only if exact forbidden; keep simple exact/substring
                if bad in cols or any(bad == c for c in cols):
                    problems.append(
                        f"column looks sensitive: {bad} in {path.name} columns={reader.fieldnames}"
                    )
                elif bad not in {"pred"} and any(bad in c for c in cols):
                    problems.append(
                        f"column looks sensitive: {bad} in {path.name} columns={reader.fieldnames}"
                    )
        for i, row in enumerate(reader, start=2):
            for field in ANSWER_FIELDS:
                if (row.get(field) or "").strip():
                    problems.append(f"{path.name} row {i} has prefilled {field}")
        return problems


def main() -> int:
    import argparse

    p = argparse.ArgumentParser(description="Build or refresh Phase 2 pilot sheets.")
    p.add_argument(
        "--from-mapping",
        action="store_true",
        help="Preserve existing pilot_id_mapping.csv selection and only refresh sheets.",
    )
    p.add_argument(
        "--resample",
        action="store_true",
        help="Ignore existing mapping and draw a new sample (destructive).",
    )
    args = p.parse_args()

    mapping_path = OUT_DIR / "pilot_id_mapping.csv"
    sheet_a = OUT_DIR / "reviewer_A_sheet.csv"
    sheet_b = OUT_DIR / "reviewer_B_sheet.csv"
    manifest_path = OUT_DIR / "sampling_manifest.json"
    candidate_summary = OUT_DIR / "candidate_pool_summary.json"

    candidates = build_candidate_pool()

    if args.resample or not mapping_path.exists() or (not args.from_mapping and not mapping_path.exists()):
        if mapping_path.exists() and not args.resample and not args.from_mapping:
            # Default: preserve mapping when present.
            args.from_mapping = True

    if args.from_mapping or (mapping_path.exists() and not args.resample):
        rows = rebuild_rows_from_mapping(mapping_path)
        fill_log = [
            {
                "stratum": "_preserved_mapping",
                "quota": len(rows),
                "available": len(rows),
                "taken": len(rows),
                "note": "Existing 100-post mapping preserved; sheets refreshed.",
            }
        ]
        # Refresh mapping text metadata but keep ids/order/labels.
        write_mapping(rows, mapping_path)
        # Update manifest with preserve note while keeping prior seed record if present.
        prior = {}
        if manifest_path.exists():
            prior = json.loads(manifest_path.read_text(encoding="utf-8"))
        write_sampling_manifest(rows, fill_log, manifest_path)
        updated = json.loads(manifest_path.read_text(encoding="utf-8"))
        updated["seed"] = prior.get("seed", SEED)
        updated["preserved_mapping"] = True
        updated["prior_quota_fill_log"] = prior.get("quota_fill_log")
        updated["reviewer_fields"] = list(ANSWER_FIELDS)
        updated["notes"] = list(updated.get("notes") or []) + [
            "Sheets refreshed with about_software and update_related fields.",
            "Same pilot_id / reddit_id pairing preserved from prior mapping.",
        ]
        manifest_path.write_text(json.dumps(updated, indent=2), encoding="utf-8")
    else:
        rows, fill_log = select_sample(candidates, SEED, TARGET_N)
        write_mapping(rows, mapping_path)
        write_sampling_manifest(rows, fill_log, manifest_path)

    write_reviewer_sheet(rows, sheet_a)
    write_reviewer_sheet(rows, sheet_b)

    cand_summary = {
        "n_candidates_after_dedup_and_text_filter": len(candidates),
        "by_source_pool": dict(Counter(c["source_pool"] for c in candidates)),
        "by_stratum": dict(Counter(c["stratum"] for c in candidates)),
        "by_text_availability": dict(Counter(c["text_availability"] for c in candidates)),
    }
    candidate_summary.write_text(json.dumps(cand_summary, indent=2), encoding="utf-8")

    problems = assert_reviewer_sheet_blind(sheet_a) + assert_reviewer_sheet_blind(sheet_b)
    if problems:
        raise SystemExit("Blindness check failed:\n" + "\n".join(problems))

    a = sheet_a.read_text(encoding="utf-8")
    b = sheet_b.read_text(encoding="utf-8")
    if a != b:
        raise SystemExit("Reviewer A and B sheets differ")

    print(
        json.dumps(
            {
                "n": len(rows),
                "preserved_mapping": bool(mapping_path.exists() and not args.resample),
                "sources": dict(Counter(r["source_pool"] for r in rows)),
                "strata": dict(Counter(r["stratum"] for r in rows)),
                "answer_fields": list(ANSWER_FIELDS),
                "sheet_a": str(sheet_a),
                "sheet_b": str(sheet_b),
                "mapping": str(mapping_path),
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
