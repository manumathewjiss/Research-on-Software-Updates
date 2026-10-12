#!/usr/bin/env python3
"""Phase 3 experiment_v1 data/leakage audit. Does not train models or edit labels."""

from __future__ import annotations

import hashlib
import json
import re
import unicodedata
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"
MANIFEST = ROOT / "MANIFEST.json"
OUT_AUDIT = ROOT / "DATA_AUDIT.md"
OUT_FLAGS = ROOT / "results" / "label_quality_flags.jsonl"
OUT_NEAR = ROOT / "results" / "near_duplicate_candidates.jsonl"
OUT_EXCLUSIONS = ROOT / "results" / "development_exclusions.json"


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


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


def title_norm(title: str) -> str:
    s = unicodedata.normalize("NFKC", (title or "").lower())
    s = re.sub(r"https?://\S+|www\.\S+", " ", s)
    s = re.sub(r"[^a-z0-9\s]+", " ", s)
    return re.sub(r"\s+", " ", s).strip()


def main() -> int:
    (ROOT / "results").mkdir(parents=True, exist_ok=True)
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    dev_path = DATA / "development.jsonl"
    test_path = DATA / "reserved_test.jsonl"

    hashes = {
        "development.jsonl": sha256_file(dev_path),
        "reserved_test.jsonl": sha256_file(test_path),
    }
    hash_ok = {
        name: hashes[name] == manifest["files"][name] for name in hashes
    }

    dev = load_jsonl(dev_path)
    test = load_jsonl(test_path)

    # Structural checks
    def summarize(rows: list[dict], name: str) -> dict:
        ids = [r["reddit_id"] for r in rows]
        study = [r["study_id"] for r in rows]
        s2 = [r for r in rows if r.get("s2_in_scope") is True]
        # consistency
        bad_scope = []
        for r in rows:
            soft = r.get("about_software")
            upd = r.get("update_related")
            s2f = bool(r.get("s2_in_scope"))
            expect = soft == "yes" and upd == "yes"
            if s2f != expect:
                bad_scope.append(r["reddit_id"])
            if s2f:
                tgt = r.get("s2_target")
                dt = r.get("discussion_type")
                expect_tgt = 1 if dt == "technical_troubleshooting" else 0
                if tgt != expect_tgt:
                    bad_scope.append(r["reddit_id"] + ":target")
        empty_title = sum(1 for r in rows if not (r.get("title") or "").strip())
        empty_body = sum(1 for r in rows if not (r.get("post_body") or "").strip())
        return {
            "name": name,
            "n": len(rows),
            "unique_reddit_id": len(set(ids)),
            "unique_study_id": len(set(study)),
            "dup_reddit_id": len(ids) - len(set(ids)),
            "s2_n": len(s2),
            "s2_target": dict(Counter(r.get("s2_target") for r in s2)),
            "s2_discussion_type": dict(Counter(r.get("discussion_type") for r in s2)),
            "all_discussion_type": dict(Counter(r.get("discussion_type") for r in rows)),
            "about_software": dict(Counter(r.get("about_software") for r in rows)),
            "update_related": dict(Counter(r.get("update_related") for r in rows)),
            "source_pool": dict(Counter(r.get("source_pool_audit_only") for r in rows)),
            "review_status": dict(Counter(r.get("review_status_audit_only") for r in rows)),
            "text_availability": dict(Counter(r.get("text_availability") for r in rows)),
            "empty_title": empty_title,
            "empty_body": empty_body,
            "scope_or_target_inconsistencies": len(bad_scope),
            "scope_inconsistency_examples": bad_scope[:10],
            "s2_by_source": {
                src: dict(Counter(r.get("s2_target") for r in s2 if r.get("source_pool_audit_only") == src))
                for src in sorted({r.get("source_pool_audit_only") for r in s2})
            },
            "s2_by_review": {
                st: dict(Counter(r.get("s2_target") for r in s2 if r.get("review_status_audit_only") == st))
                for st in sorted({r.get("review_status_audit_only") for r in s2})
            },
        }

    sum_dev = summarize(dev, "development")
    sum_test = summarize(test, "reserved_test")

    # Exact text overlap remaining
    def key_tb(r):
        return norm_text(r.get("title") or "", r.get("post_body") or "")

    test_tb = {key_tb(r): r for r in test if key_tb(r)}
    exact_dev_in_test = []
    for r in dev:
        k = key_tb(r)
        if k and k in test_tb:
            exact_dev_in_test.append(
                {
                    "dev_reddit_id": r["reddit_id"],
                    "dev_study_id": r["study_id"],
                    "test_reddit_id": test_tb[k]["reddit_id"],
                    "test_study_id": test_tb[k]["study_id"],
                    "title": r.get("title"),
                    "both_s2": bool(r.get("s2_in_scope")) and bool(test_tb[k].get("s2_in_scope")),
                }
            )

    # Title-only exact overlap
    test_titles = defaultdict(list)
    for r in test:
        t = title_norm(r.get("title") or "")
        if t:
            test_titles[t].append(r)
    title_exact = []
    for r in dev:
        t = title_norm(r.get("title") or "")
        if t and t in test_titles:
            for tr in test_titles[t]:
                # skip if already exact full-text match
                if key_tb(r) == key_tb(tr):
                    continue
                title_exact.append(
                    {
                        "dev_reddit_id": r["reddit_id"],
                        "test_reddit_id": tr["reddit_id"],
                        "title": r.get("title"),
                        "dev_s2": bool(r.get("s2_in_scope")),
                        "test_s2": bool(tr.get("s2_in_scope")),
                        "dev_target": r.get("s2_target"),
                        "test_target": tr.get("s2_target"),
                        "same_full_text": False,
                    }
                )

    # Near-duplicate: for each S2 test text, scan S2 development for high Jaccard.
    # Bounded: only S2 vs S2 to keep runtime reasonable.
    s2_test = [r for r in test if r.get("s2_in_scope")]
    s2_dev = [r for r in dev if r.get("s2_in_scope")]
    near = []
    THRESH = 0.85
    # Index shortlist by first 12 chars of normalized text to reduce comparisons
    buckets = defaultdict(list)
    for r in s2_dev:
        k = key_tb(r)
        if not k:
            continue
        buckets[k[:12]].append((r, k))
    for tr in s2_test:
        tk = key_tb(tr)
        if not tk:
            continue
        # check same prefix bucket and neighboring empty short texts via full loop on short set
        candidates = buckets.get(tk[:12], [])
        # also check empty-prefix-like: compare against all if title-normalized equal
        tn = title_norm(tr.get("title") or "")
        extra = []
        if tn:
            for r in s2_dev:
                if title_norm(r.get("title") or "") == tn:
                    extra.append((r, key_tb(r)))
        seen = set()
        for r, dk in candidates + extra:
            if r["reddit_id"] in seen:
                continue
            seen.add(r["reddit_id"])
            if not dk or dk == tk:
                continue  # exact handled separately
            sim = jaccard_char_ngrams(dk, tk, n=5)
            if sim >= THRESH:
                near.append(
                    {
                        "similarity": round(sim, 4),
                        "method": "jaccard_char_5grams_norm_title_body",
                        "threshold": THRESH,
                        "dev_reddit_id": r["reddit_id"],
                        "dev_study_id": r["study_id"],
                        "test_reddit_id": tr["reddit_id"],
                        "test_study_id": tr["study_id"],
                        "dev_title": r.get("title"),
                        "test_title": tr.get("title"),
                        "dev_target": r.get("s2_target"),
                        "test_target": tr.get("s2_target"),
                        "dev_source": r.get("source_pool_audit_only"),
                        "test_source": tr.get("source_pool_audit_only"),
                    }
                )

    # Also brute-force high-sim for title-near pairs with different full text using title tokens
    # Expand near search: for each test, compare to all dev with same first 8 title chars
    title_buckets = defaultdict(list)
    for r in s2_dev:
        tn = title_norm(r.get("title") or "")
        if tn:
            title_buckets[tn[:16]].append(r)
    for tr in s2_test:
        tn = title_norm(tr.get("title") or "")
        if not tn:
            continue
        tk = key_tb(tr)
        for r in title_buckets.get(tn[:16], []):
            dk = key_tb(r)
            if not dk or dk == tk:
                continue
            sim = jaccard_char_ngrams(dk, tk, n=5)
            if sim >= THRESH:
                item = {
                    "similarity": round(sim, 4),
                    "method": "jaccard_char_5grams_norm_title_body",
                    "threshold": THRESH,
                    "dev_reddit_id": r["reddit_id"],
                    "dev_study_id": r["study_id"],
                    "test_reddit_id": tr["reddit_id"],
                    "test_study_id": tr["study_id"],
                    "dev_title": r.get("title"),
                    "test_title": tr.get("title"),
                    "dev_target": r.get("s2_target"),
                    "test_target": tr.get("s2_target"),
                    "dev_source": r.get("source_pool_audit_only"),
                    "test_source": tr.get("source_pool_audit_only"),
                }
                if not any(
                    x["dev_reddit_id"] == item["dev_reddit_id"]
                    and x["test_reddit_id"] == item["test_reddit_id"]
                    for x in near
                ):
                    near.append(item)

    near.sort(key=lambda x: -x["similarity"])

    # Document exclusion rule for near-duplicates >= 0.92 (high confidence)
    EXCLUDE_NEAR = 0.92
    exclude_ids = []
    for item in near:
        if item["similarity"] >= EXCLUDE_NEAR:
            exclude_ids.append(
                {
                    "reddit_id": item["dev_reddit_id"],
                    "study_id": item["dev_study_id"],
                    "reason": f"near_duplicate_of_reserved_{item['test_reddit_id']}",
                    "similarity": item["similarity"],
                }
            )
    # Deduplicate exclusions
    seen_ex = set()
    uniq_ex = []
    for e in exclude_ids:
        if e["reddit_id"] not in seen_ex:
            seen_ex.add(e["reddit_id"])
            uniq_ex.append(e)

    # Label quality heuristics (flags only)
    flags = []
    for r in [x for x in s2_dev if x["reddit_id"] not in seen_ex]:
        title = (r.get("title") or "").strip()
        body = (r.get("post_body") or "").strip()
        text = f"{title}\n{body}".lower()
        dt = r.get("discussion_type")
        tgt = r.get("s2_target")
        reasons = []
        # newsy title labeled troubleshooting
        if tgt == 1 and re.search(
            r"\b(release notes|changelog|is out|now available|rolling out|announcing)\b",
            title,
            re.I,
        ):
            reasons.append("troubleshoot_label_but_news_language_in_title")
        # rant-only language labeled troubleshooting with no tech cue
        if tgt == 1 and re.search(r"\b(hate|sucks|garbage|trash|ruined)\b", text) and not re.search(
            r"\b(error|crash|bug|fix|broken|fail|workaround|how (do|can) i|not working)\b",
            text,
        ):
            reasons.append("troubleshoot_label_with_rant_language_and_no_tech_cues")
        # clear tech failure labeled other/dissatisfaction
        if tgt == 0 and re.search(
            r"\b(crash(es|ed|ing)?|error|bug|broken|not working|doesn't work|traceback|segfault)\b",
            text,
        ) and re.search(r"\b(how (do|can) i|fix|workaround|help)\b", text):
            reasons.append("non_troubleshoot_label_but_strong_repair_ask")
        # empty body + short title
        if not body and len(title.split()) <= 3:
            reasons.append("very_thin_text")
        if reasons:
            flags.append(
                {
                    "reddit_id": r["reddit_id"],
                    "study_id": r["study_id"],
                    "source_pool_audit_only": r.get("source_pool_audit_only"),
                    "review_status_audit_only": r.get("review_status_audit_only"),
                    "discussion_type": dt,
                    "s2_target": tgt,
                    "title": title[:180],
                    "flag_reasons": reasons,
                    "note": "Heuristic flag only. Not a human correction.",
                }
            )

    # Stratified sample count for spot-check reporting
    flag_by_src = Counter(f["source_pool_audit_only"] for f in flags)
    flag_by_status = Counter(f["review_status_audit_only"] for f in flags)

    with OUT_NEAR.open("w", encoding="utf-8") as f:
        for item in near:
            f.write(json.dumps(item, ensure_ascii=False) + "\n")
    with OUT_FLAGS.open("w", encoding="utf-8") as f:
        for item in flags:
            f.write(json.dumps(item, ensure_ascii=False) + "\n")
    OUT_EXCLUSIONS.write_text(
        json.dumps(
            {
                "rule": (
                    "Exclude development S2 rows whose normalized title+body has "
                    f"Jaccard similarity >= {EXCLUDE_NEAR} (char 5-grams) with any reserved-test S2 row. "
                    "Reserved-test rows are never removed."
                ),
                "already_excluded_exact_in_package": manifest.get("development_exact_duplicate_exclusions"),
                "additional_near_duplicate_exclusions": uniq_ex,
                "n_additional": len(uniq_ex),
                "near_candidates_ge_0.85": len(near),
            },
            indent=2,
        ),
        encoding="utf-8",
    )

    # Write DATA_AUDIT.md
    lines = []
    lines.append("# Phase 3 experiment_v1 data audit")
    lines.append("")
    lines.append(f"**Generated:** {datetime.now(timezone.utc).isoformat()}")
    lines.append("**Input:** `data/development.jsonl`, `data/reserved_test.jsonl`")
    lines.append("**Manifest:** `MANIFEST.json`")
    lines.append("")
    lines.append("This audit does not change labels. Questionable rows are flagged for Manu, not auto-corrected.")
    lines.append("")
    lines.append("## 1. File integrity")
    lines.append("")
    lines.append("| File | Manifest SHA-256 match | Rows |")
    lines.append("|------|------------------------|------|")
    lines.append(f"| development.jsonl | {hash_ok['development.jsonl']} | {sum_dev['n']} |")
    lines.append(f"| reserved_test.jsonl | {hash_ok['reserved_test.jsonl']} | {sum_test['n']} |")
    lines.append("")
    lines.append(f"Manifest expected development rows after exact dedup: {manifest['development_after_exact_dedup']}.")
    lines.append(f"Observed: {sum_dev['n']}. Unique reddit_id: {sum_dev['unique_reddit_id']}. Duplicate reddit_id: {sum_dev['dup_reddit_id']}.")
    lines.append(f"Reserved observed: {sum_test['n']}. Unique reddit_id: {sum_test['unique_reddit_id']}.")
    lines.append("")
    lines.append("Package already excluded these exact development copies of reserved posts:")
    for ex in manifest.get("development_exact_duplicate_exclusions") or []:
        lines.append(f"- `{ex['reddit_id']}` / `{ex['study_id']}` — {ex.get('title','')}")
    lines.append("")
    lines.append("Unresolved Phase 2 IDs are absent from both files (manifest list): "
                 + ", ".join(f"`{i}`" for i in manifest.get("unresolved_excluded_ids") or []))
    lines.append("")
    lines.append("## 2. Provenance (reviewed labels of mixed origin)")
    lines.append("")
    lines.append("These are **reviewed decisions**, not all independent blind annotations.")
    lines.append("")
    lines.append("### Development `review_status_audit_only`")
    for k, v in sorted(sum_dev["review_status"].items(), key=lambda x: -x[1]):
        lines.append(f"- `{k}`: {v}")
    lines.append("")
    lines.append("### Reserved `review_status_audit_only`")
    for k, v in sorted(sum_test["review_status"].items(), key=lambda x: -x[1]):
        lines.append(f"- `{k}`: {v}")
    lines.append("")
    lines.append("`source_pool_audit_only` is a collection route (Phase 1 file / Oct 5 API candidate pools), **not** a class label.")
    lines.append("")
    lines.append("### Development source pools")
    for k, v in sorted(sum_dev["source_pool"].items(), key=lambda x: -x[1]):
        lines.append(f"- `{k}`: {v}")
    lines.append("")
    lines.append("The review set was assembled from keyword-driven API candidate pools and Phase 1 posts. Class proportions need not represent Reddit as a whole.")
    lines.append("")
    lines.append("## 3. S2 scope and class balance")
    lines.append("")
    lines.append("S2 = `about_software=yes` and `update_related=yes` (`s2_in_scope=true`). Target `s2_target`: 1 = technical troubleshooting, 0 = other update discussion (includes `other` and `general_dissatisfaction`).")
    lines.append("")
    lines.append("| Split | S2 n | troubleshooting (1) | other update (0) | by discussion_type |")
    lines.append("|-------|------|---------------------|------------------|--------------------|")
    lines.append(
        f"| Development | {sum_dev['s2_n']} | {sum_dev['s2_target'].get(1,0)} | {sum_dev['s2_target'].get(0,0)} | {sum_dev['s2_discussion_type']} |"
    )
    lines.append(
        f"| Reserved | {sum_test['s2_n']} | {sum_test['s2_target'].get(1,0)} | {sum_test['s2_target'].get(0,0)} | {sum_test['s2_discussion_type']} |"
    )
    lines.append("")
    lines.append(f"Scope/target consistency issues: development={sum_dev['scope_or_target_inconsistencies']}, reserved={sum_test['scope_or_target_inconsistencies']}.")
    lines.append(f"Empty titles: dev={sum_dev['empty_title']}, test={sum_test['empty_title']}. Empty bodies: dev={sum_dev['empty_body']}, test={sum_test['empty_body']}.")
    lines.append("")
    lines.append("### S2 development target by source pool")
    lines.append("")
    lines.append("```")
    lines.append(json.dumps(sum_dev["s2_by_source"], indent=2))
    lines.append("```")
    lines.append("")
    lines.append("Source and class are strongly related. Models must not receive `source_pool_audit_only` as a feature. Report metrics by source as a stress check.")
    lines.append("")
    lines.append("## 4. Leakage / near-duplicate audit")
    lines.append("")
    lines.append("### Method")
    lines.append("")
    lines.append("- Normalize title+body: NFKC, lower case, strip URLs, keep alphanumeric, collapse whitespace.")
    lines.append("- Exact match: identical normalized title+body.")
    lines.append("- Near match: Jaccard similarity of character 5-grams on normalized title+body, threshold report 0.85, **exclude development rows at ≥ 0.92** against any reserved S2 post.")
    lines.append("- Title-only exact matches with different bodies are reported separately.")
    lines.append("- Reserved-test rows are never removed.")
    lines.append("")
    lines.append(f"Remaining exact full-text development↔reserved overlaps after package dedup: **{len(exact_dev_in_test)}**.")
    lines.append(f"Title-only exact overlaps with different bodies: **{len(title_exact)}** (listed in audit outputs if any).")
    lines.append(f"Near-duplicate candidates (sim ≥ 0.85, S2↔S2): **{len(near)}**. Saved to `results/near_duplicate_candidates.jsonl`.")
    lines.append(f"Additional development exclusions (sim ≥ {EXCLUDE_NEAR}): **{len(uniq_ex)}**. Saved to `results/development_exclusions.json`.")
    lines.append("")
    if uniq_ex:
        lines.append("### Development IDs to exclude before fitting")
        lines.append("")
        for e in uniq_ex:
            lines.append(f"- `{e['reddit_id']}` (`{e['study_id']}`): {e['reason']} (sim={e['similarity']})")
        lines.append("")
    if near[:5]:
        lines.append("### Manual examples (highest similarity)")
        lines.append("")
        for item in near[:8]:
            lines.append(
                f"- sim={item['similarity']}: dev `{item['dev_reddit_id']}` “{item['dev_title']}” "
                f"↔ test `{item['test_reddit_id']}` “{item['test_title']}” "
                f"(targets {item['dev_target']} vs {item['test_target']})"
            )
        lines.append("")
    if title_exact[:5]:
        lines.append("### Title-only collisions (different full text)")
        for item in title_exact[:10]:
            lines.append(
                f"- `{item['dev_reddit_id']}` ↔ `{item['test_reddit_id']}`: “{item['title']}” "
                f"(S2 {item['dev_s2']}/{item['test_s2']}, targets {item['dev_target']}/{item['test_target']})"
            )
        lines.append("")

    # Save title exact too
    (ROOT / "results" / "title_only_collisions.jsonl").write_text(
        "".join(json.dumps(x, ensure_ascii=False) + "\n" for x in title_exact),
        encoding="utf-8",
    )

    lines.append("## 5. Label-quality spot check (heuristic flags only)")
    lines.append("")
    lines.append(f"Flagged development S2 rows (after intended near-dup exclusions): **{len(flags)}**.")
    lines.append("Saved to `results/label_quality_flags.jsonl`. These are **not** corrections.")
    lines.append("")
    lines.append(f"By source: {dict(flag_by_src)}")
    lines.append(f"By review status: {dict(flag_by_status)}")
    lines.append("")
    lines.append("Example flags (up to 12):")
    for f in flags[:12]:
        lines.append(
            f"- `{f['reddit_id']}` [{f['source_pool_audit_only']}/{f['review_status_audit_only']}] "
            f"target={f['s2_target']} type={f['discussion_type']}: {', '.join(f['flag_reasons'])} — “{f['title']}”"
        )
    lines.append("")
    lines.append("If Manu finds systematic errors in a large share of these flags, pause reserved-test scoring and adjudicate first.")
    lines.append("")
    lines.append("## 6. Freeze decision for modeling")
    lines.append("")
    lines.append("- Primary population: `s2_in_scope=true`.")
    lines.append("- Target: `s2_target`.")
    lines.append("- Text: `title` and `title + post_body` (separate runs). Do not use `discussion_context` in primary models.")
    lines.append("- Exclude additional near-duplicate development IDs listed above.")
    lines.append("- Do not use audit-only fields as features.")
    lines.append("- Reserved test: evaluate once after protocol/model/threshold are frozen on development only.")
    lines.append("")
    lines.append("## 7. Counts after planned exclusions")
    rem = [r for r in s2_dev if r["reddit_id"] not in seen_ex]
    lines.append(f"S2 development before extra exclusions: {len(s2_dev)}")
    lines.append(f"S2 development after extra exclusions: {len(rem)}")
    lines.append(f"S2 reserved (unchanged): {len(s2_test)}")
    lines.append(f"Post-exclusion class counts: {dict(Counter(r['s2_target'] for r in rem))}")
    lines.append("")

    OUT_AUDIT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps({
        "hash_ok": hash_ok,
        "dev_n": sum_dev["n"],
        "test_n": sum_test["n"],
        "s2_dev": sum_dev["s2_n"],
        "s2_test": sum_test["s2_n"],
        "exact_remaining": len(exact_dev_in_test),
        "title_exact": len(title_exact),
        "near": len(near),
        "exclude_near": len(uniq_ex),
        "flags": len(flags),
        "audit": str(OUT_AUDIT),
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
