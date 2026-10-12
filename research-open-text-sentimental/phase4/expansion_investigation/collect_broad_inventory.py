"""Read-only inventory of the unfiltered ReleaseTrain update-related route.

This produces a candidate snapshot for a feasibility investigation. API predictions
are never copied into reviewed-label fields.
"""
import concurrent.futures
import datetime as dt
import hashlib
import json
import math
import pathlib
import random
import urllib.parse
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parent
BASE = "https://releasetrain.io/api/reddit/query/update-related"
LIMIT = 500
SEED = 20261008


def fetch(page):
    query = urllib.parse.urlencode({"limit": LIMIT, "page": page})
    url = f"{BASE}?{query}"
    req = urllib.request.Request(url, headers={"User-Agent": "SoftwareUpdateResearchFeasibility/1.0"})
    with urllib.request.urlopen(req, timeout=60) as response:
        raw = response.read()
        date = response.headers.get("Date")
    payload = json.loads(raw)
    if payload["pagination"]["page"] != page:
        raise ValueError(f"Wrong page {page}")
    return page, payload, hashlib.sha256(raw).hexdigest(), date


def main():
    ROOT.mkdir(parents=True, exist_ok=True)
    started = dt.datetime.now(dt.timezone.utc).isoformat()
    first = fetch(1)
    total = first[1]["pagination"]["total"]
    n_pages = math.ceil(total / LIMIT)
    results = [first]
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as pool:
        results.extend(pool.map(fetch, range(2, n_pages + 1)))
    results.sort(key=lambda x: x[0])
    rows = []
    pages = []
    for page, payload, sha, date in results:
        pg = payload["pagination"]
        pages.append({"page": page, "n": len(payload["data"]), "reported_total": pg["total"], "sha256": sha, "server_date": date})
        for x in payload["data"]:
            predicted = x.get("metadata", {}).get("predicted") or {}
            labeled = x.get("metadata", {}).get("labeled") or {}
            rows.append({
                "reddit_id": x.get("redditId"), "source": x.get("source"),
                "url": x.get("url"), "subreddit": x.get("subreddit"),
                "created_utc": x.get("created_utc"), "title": x.get("title"),
                "post_body": x.get("author_description"),
                "predicted_update_related": predicted.get("isUpdateRelated"),
                "existing_labeled_update_related": labeled.get("isUpdateRelated"),
                "n_comments_stored": len(x.get("comments") or []),
            })
    ids = [r["reddit_id"] for r in rows]
    old = json.loads((ROOT.parent.parent / "phase2/combined_dataset/master_records.json").read_text())
    old_ids = {r["reddit_id"] for r in old}
    fresh_path = ROOT.parent.parent / "phase3/fresh_test_20261007/frozen_joint_labels/all_500_reviewed.jsonl"
    fresh_ids = {json.loads(line)["reddit_id"] for line in fresh_path.open()}
    unseen = [r for r in rows if r["reddit_id"] and r["reddit_id"] not in old_ids and r["reddit_id"] not in fresh_ids]
    unseen.sort(key=lambda r: r["reddit_id"])
    sample = random.Random(SEED).sample(unseen, min(200, len(unseen)))
    sample.sort(key=lambda r: r["reddit_id"])
    for i, r in enumerate(sample, 1):
        r["pilot_id"] = f"E{i:03d}"
        r["provisional_about_software"] = ""
        r["provisional_update_related"] = ""
        r["provisional_discussion_type"] = ""
        r["provisional_diagnostic_note"] = ""
        r["uncertainty"] = ""
        r["human_about_software"] = ""
        r["human_update_related"] = ""
        r["human_discussion_type"] = ""
        r["human_diagnostic_note"] = ""
    with (ROOT / "pilot_200_candidates.jsonl").open("w") as f:
        for r in sample:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    from collections import Counter
    manifest = {
        "started_utc": started, "finished_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
        "endpoint": BASE, "query": {"limit": LIMIT, "page": "1..n"},
        "first_reported_total": total, "pages": pages,
        "downloaded_rows": len(rows), "unique_reddit_ids": len(set(ids)),
        "duplicate_id_rows": len(ids) - len(set(ids)),
        "overlap_master_rows": sum(r["reddit_id"] in old_ids for r in rows),
        "overlap_fresh_rows": sum(r["reddit_id"] in fresh_ids for r in rows),
        "unseen_rows": len(unseen), "sample_seed": SEED, "sample_n": len(sample),
        "sample_rule": "simple random sample from unique IDs absent from Phase 2 master and fresh 500 review",
        "source_counts": dict(Counter(r["source"] for r in rows)),
        "predicted_update_counts": dict(Counter(str(r["predicted_update_related"]) for r in rows)),
        "sample_predicted_update_counts": dict(Counter(str(r["predicted_update_related"]) for r in sample)),
        "sample_source_counts": dict(Counter(r["source"] for r in sample)),
        "warning": "Dynamic offset pages can shift during collection; verify counts and duplicates. API predictions are not human labels.",
    }
    (ROOT / "BROAD_INVENTORY.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(json.dumps({k: manifest[k] for k in ("first_reported_total", "downloaded_rows", "unique_reddit_ids", "duplicate_id_rows", "overlap_master_rows", "overlap_fresh_rows", "unseen_rows", "sample_n", "predicted_update_counts", "sample_predicted_update_counts")}, indent=2))


if __name__ == "__main__":
    main()
