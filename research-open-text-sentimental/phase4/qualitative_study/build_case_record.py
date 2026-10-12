"""Build and verify the frozen qualitative-study case record; no source files change."""
from __future__ import annotations

import csv
import hashlib
import json
import re
import unicodedata
from collections import Counter
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
DEV = ROOT / "phase3/icsc_full_paper/reliability_packet/submissions/2026-10-07-independent/development_after_independent_review.jsonl"
MASTER = ROOT / "phase2/combined_dataset/master_records.json"
RESERVED = ROOT / "phase3/experiment_v1/data/reserved_test.jsonl"
FRESH = ROOT / "phase3/fresh_test_20261007/frozen_joint_labels/all_500_reviewed.jsonl"

# Investigator selection, frozen before external reviewers see any case.
MAIN = [
    ("1sandee", "version change; affected and unaffected applications", "upgrade,ui"),
    ("1spwh8z", "many inaccessible pages versus working dashboard and backup", "upgrade,access,error"),
    ("1si6d2u", "short post with an unusual screenshot symptom", "upgrade,ui,sparse"),
    ("1qj5weo", "application fails to start with little error evidence", "upgrade,startup,sparse"),
    ("1qqdsn4", "persistent microphone indicator despite settings checks", "upgrade,ui,attempted_fix"),
    ("1seglp5", "normal versus incognito contrast suggests alternative cause", "upgrade,crash,contrast"),
    ("1otvvjo", "release-specific UI report that already includes workaround", "upgrade,ui,workaround"),
    ("1rxg828", "author considers both update and hardware explanations", "upgrade,hardware,attempted_fix"),
    ("1td07b1", "specific build identifiers but brief error description", "upgrade,install,sparse"),
    ("1rmfe0d", "detailed failure sequence and failed recovery attempts", "upgrade,boot,attempted_fix"),
    ("1ojbw73", "new command behavior versus possible misunderstanding", "upgrade,storage,uncertainty"),
    ("1t2xx8i", "reported issue with a proposed fix already supplied", "upgrade,ui,resolved"),
    ("1ua4emd", "rendering failure with environment and attempted reset", "upgrade,ui,attempted_fix"),
    ("1ud1j0h", "password application reports empty values after upgrade", "upgrade,access,data"),
    ("1vx7e0u", "tentative update link with crash and alternative checks", "upgrade,crash,uncertainty"),
    ("1v1khho", "kernel timing and two graphics-card comparisons", "upgrade,hardware,error"),
    ("1nx29vh", "unexpected automatic update without an observed failure", "unexpected_update,configuration,uncertainty"),
    ("1sap4lh", "service inaccessible with exact socket error", "upgrade,access,error"),
    ("1rm9l7d", "terminal behavior with workaround and bug question", "upgrade,ui,workaround"),
    ("1u5hpsr", "lower-severity changed browser behavior", "upgrade,ui,sparse"),
    ("1tne77f", "upgrade planning informed by a prior failure", "planning,risk,prior_failure"),
    ("1swjx2c", "early-upgrade risk question and earlier warnings", "planning,risk,error"),
    ("1qz7a1y", "strong criticism alongside concrete UI effects", "upgrade,ui,discontent"),
    ("1p0bob2", "brief performance complaint after update", "upgrade,performance,discontent"),
    ("1ux7p8c", "positive update experience as a fault-triage negative case", "upgrade,positive,ui"),
    ("1v1np4z", "channel-change question also reports broken applications", "patch,compatibility,boundary"),
    ("1wup9pb", "preflight and rollback discussion without failed incident", "planning,risk,procedure"),
    ("1suy71k", "angry UI report with concrete effects and fix question", "upgrade,ui,discontent"),
    ("1v17vtk", "predominantly a keyboard-change complaint", "upgrade,ui,discontent"),
    ("1u71ioe", "firmware-version question without a fault", "planning,version,uncertainty"),
]
PILOT = [
    ("1scc0f7", "version and device context with a clear visual symptom", "upgrade,ui"),
    ("1uyn078", "problem followed by an author-provided fix", "upgrade,install,resolved"),
    ("1uy7hw8", "detailed error and attempts with a later reported fix", "upgrade,access,resolved"),
    ("1s3r9jj", "upgrade planning and method-selection questions", "planning,risk"),
    ("1u66nem", "smooth current update and older unrelated issue", "upgrade,positive"),
    ("1u4ei2o", "future OS update concern alongside an app update", "planning,multiple_updates"),
]


def read_jsonl(path: Path) -> list[dict]:
    with path.open(encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def norm(title: str, body: str) -> str:
    value = unicodedata.normalize("NFKC", f"{title or ''}\n{body or ''}".lower())
    value = re.sub(r"https?://\S+|www\.\S+", " ", value)
    value = re.sub(r"[^a-z0-9\s]+", " ", value)
    return re.sub(r"\s+", " ", value).strip()


def grams(value: str) -> set[str]:
    return {value[i : i + 5] for i in range(max(1, len(value) - 4))}


def main() -> None:
    dev_rows = read_jsonl(DEV)
    dev = {r["reddit_id"]: r for r in dev_rows}
    assert len(dev) == len(dev_rows), "duplicate development IDs"
    master = {r["reddit_id"]: r for r in json.loads(MASTER.read_text())}
    reserved = {r["reddit_id"] for r in read_jsonl(RESERVED)}
    fresh = {r["reddit_id"] for r in read_jsonl(FRESH)}
    selection = [("main", *row) for row in MAIN] + [("pilot", *row) for row in PILOT]
    ids = [x[1] for x in selection]
    assert len(MAIN) == 30 and len(PILOT) == 6 and len(set(ids)) == 36
    assert not set(ids) & (reserved | fresh), "test overlap"

    rows = []
    for cohort, rid, reason, variation in selection:
        assert rid in dev and rid in master, f"missing {rid}"
        d, m = dev[rid], master[rid]
        assert d.get("s2_in_scope") is True, f"out of scope {rid}"
        assert d.get("discussion_type") in {"technical_troubleshooting", "general_dissatisfaction", "other"}
        assert urlparse(m.get("url", "")).hostname in {"reddit.com", "www.reddit.com"}, f"non-Reddit {rid}"
        assert d.get("title", "").strip() and len(d.get("post_body", "").strip()) >= 100, f"missing text {rid}"
        assert d.get("title") == m.get("title") and d.get("post_body") == m.get("post_body"), f"master text differs {rid}"
        rows.append({
            "cohort": cohort,
            "study_case_id": f"{'Q' if cohort == 'main' else 'P'}{sum(x['cohort'] == cohort for x in rows) + 1:03d}",
            "reddit_id": rid,
            "subreddit": d["subreddit"],
            "created_utc": d.get("created_utc", ""),
            "historical_discussion_type": d["discussion_type"],
            "selection_reason": reason,
            "variation_tags": variation,
            "title": d["title"],
            "post_body": d["post_body"],
            "source_url": m["url"],
            "text_sha256": hashlib.sha256((d["title"] + "\n" + d["post_body"]).encode()).hexdigest(),
            "sensitive_text_manual_check": "required_before_distribution",
        })

    by_id = {r["reddit_id"]: r for r in rows}
    # The project rule compares normalized title+body and near duplicates at Jaccard >= .92.
    # Compare all selected pairs without blocking (more conservative than the prior audit).
    duplicate_pairs = []
    for i, a in enumerate(rows):
        na = norm(a["title"], a["post_body"])
        ga = grams(na)
        for b in rows[i + 1 :]:
            nb = norm(b["title"], b["post_body"])
            sim = 1.0 if na == nb else len(ga & grams(nb)) / len(ga | grams(nb))
            if sim >= 0.92:
                duplicate_pairs.append({"id_a": a["reddit_id"], "id_b": b["reddit_id"], "similarity": round(sim, 4)})
    assert not duplicate_pairs, f"selected duplicate pair: {duplicate_pairs}"

    # Check selected posts against both frozen tests, including text duplicates with distinct IDs.
    test_duplicate_pairs = []
    test_rows = read_jsonl(RESERVED) + read_jsonl(FRESH)
    for t in test_rows:
        nt = norm(t.get("title", ""), t.get("post_body", ""))
        if not nt:
            continue
        gt = grams(nt)
        for s in rows:
            ns = norm(s["title"], s["post_body"])
            if nt != ns and nt[:16] != ns[:16] and t.get("title") != s["title"]:
                continue
            sim = 1.0 if nt == ns else len(gt & grams(ns)) / len(gt | grams(ns))
            if sim >= 0.92:
                test_duplicate_pairs.append({"study_id": s["reddit_id"], "test_id": t["reddit_id"], "similarity": round(sim, 4)})
    assert not test_duplicate_pairs, f"test text overlap: {test_duplicate_pairs}"

    main_rows = [r for r in rows if r["cohort"] == "main"]
    type_counts = Counter(r["historical_discussion_type"] for r in main_rows)
    assert type_counts["technical_troubleshooting"] == 20 and sum(type_counts.values()) == 30
    community_counts = Counter(r["subreddit"] for r in main_rows)
    assert max(community_counts.values()) <= 3

    OUT.mkdir(parents=True, exist_ok=True)
    with (OUT / "ANALYST_ONLY_CASE_SELECTION.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    packet_rows = [
        {"cohort": r["cohort"], "study_case_id": r["study_case_id"], "title": r["title"], "post_body": r["post_body"]}
        for r in rows
    ]
    (OUT / "packet_source.json").write_text(json.dumps(packet_rows, ensure_ascii=False, indent=2), encoding="utf-8")
    report = {
        "status": "case_selection_prepared_not_approved_for_external_distribution",
        "source_hashes": {str(p.relative_to(ROOT)): digest(p) for p in [DEV, MASTER, RESERVED, FRESH]},
        "selected_main": len(main_rows), "selected_pilot": len(PILOT),
        "main_type_counts": dict(type_counts), "main_community_counts": dict(community_counts),
        "unique_ids": len(set(ids)), "reserved_id_overlap": len(set(ids) & reserved),
        "fresh_id_overlap": len(set(ids) & fresh), "selected_duplicate_pairs": duplicate_pairs,
        "selected_to_test_duplicate_pairs": test_duplicate_pairs,
        "packet_source_sha256": digest(OUT / "packet_source.json"),
        "case_selection_sha256": digest(OUT / "ANALYST_ONLY_CASE_SELECTION.csv"),
        "manual_gates": ["privacy_and_text_fidelity_review", "institutional_human_study_determination", "Reddit_ReleaseTrain_text_sharing_permission"],
    }
    (OUT / "SELECTION_VALIDATION.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps({k: v for k, v in report.items() if k not in {"source_hashes", "main_community_counts"}}, indent=2))


if __name__ == "__main__":
    main()
