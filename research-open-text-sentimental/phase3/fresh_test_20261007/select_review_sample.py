"""Freeze the blind 500-candidate fresh model-test review sample."""
from __future__ import annotations

import hashlib
import json
import random
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
ELIGIBLE = HERE / "eligible_candidates.json"
OLD_MASTER = HERE.parent.parent / "phase2/combined_dataset/master_records.json"
SEED = 20261007
N = 500


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(path: Path, obj: object) -> None:
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + "\n")


def main() -> None:
    candidates = json.loads(ELIGIBLE.read_text())
    old_ids = {r["reddit_id"] for r in json.loads(OLD_MASTER.read_text())}
    assert len(candidates) == 864
    assert all(r["redditId"] not in old_ids for r in candidates)
    candidates.sort(key=lambda r: r["redditId"])
    chosen = random.Random(SEED).sample(candidates, N)
    reviewer = []
    mapping = []
    for index, r in enumerate(chosen, 1):
        blind_id = f"T20261007-{index:03d}"
        reviewer.append({"test_id": blind_id, "title": r.get("title") or "",
                         "post_body": r.get("author_description") or ""})
        mapping.append({"test_id": blind_id, "reddit_id": r["redditId"],
                        "created_utc": r.get("created_utc"),
                        "subreddit": r.get("subreddit"),
                        "url": r.get("url"),
                        "has_body": bool((r.get("author_description") or "").strip())})
    write(HERE / "review_text.json", reviewer)
    assignment_rng = random.Random(SEED + 1)
    assignment_ids = [r["test_id"] for r in reviewer]
    assignment_rng.shuffle(assignment_ids)
    shared = set(assignment_ids[:100])
    a_only = set(assignment_ids[100:300])
    b_only = set(assignment_ids[300:500])
    by_id = {r["test_id"]: r for r in reviewer}
    a_rows = [by_id[x] for x in assignment_ids if x in shared or x in a_only]
    b_rows = [by_id[x] for x in reversed(assignment_ids) if x in shared or x in b_only]
    assert len(a_rows) == len(b_rows) == 300
    assert len({r["test_id"] for r in a_rows} & {r["test_id"] for r in b_rows}) == 100
    assert len({r["test_id"] for r in a_rows} | {r["test_id"] for r in b_rows}) == N
    write(HERE / "reviewer_A_rows.json", a_rows)
    write(HERE / "reviewer_B_rows.json", b_rows)
    for r in mapping:
        r["assigned_to"] = "both" if r["test_id"] in shared else "A" if r["test_id"] in a_only else "B"
    write(HERE / "analyst_mapping.json", mapping)
    write(HERE / "selection_manifest.json", {
        "purpose": "Fresh-to-study held-out candidate sample for blind human scope/type decisions",
        "source": "Dated broad API update-related candidate snapshot; API predictions are not labels",
        "source_eligible_sha256": digest(ELIGIBLE),
        "seed": SEED,
        "frame_n": len(candidates),
        "sample_n": len(chosen),
        "sampling_method": "Simple random sample without replacement after sorting by redditId",
        "inclusion_probability": f"{N}/{len(candidates)}",
        "previous_master_id_overlap": 0,
        "previous_master_text_near_duplicates_excluded_before_sampling": True,
        "body_missing_n": sum(not r["has_body"] for r in mapping),
        "date_min": min(r["created_utc"] for r in mapping),
        "date_max": max(r["created_utc"] for r in mapping),
        "subreddit_count": len({r["subreddit"] for r in mapping}),
        "review_text_sha256": digest(HERE / "review_text.json"),
        "mapping_sha256": digest(HERE / "analyst_mapping.json"),
        "reviewer_A_n": len(a_rows),
        "reviewer_B_n": len(b_rows),
        "independently_double_coded_target_n": len(shared),
        "review_assignment_seed": SEED + 1,
        "reviewer_sheet_has_prior_labels_or_model_predictions": False,
        "notes": "All 500 candidates are assigned at least once; 100 are assigned twice for initial agreement. The eventual S2 test size and class counts are unknown until human review. Do not select only convenient labels or tune models on these decisions."
    })
    print(json.dumps({"candidate_frame":len(candidates), "review_n":len(chosen),
                      "body_missing":sum(not r["has_body"] for r in mapping),
                      "recent_oct5_plus":sum(r["created_utc"] >= "2026-10-05" for r in mapping),
                      "subreddits":len({r["subreddit"] for r in mapping})}))


if __name__ == "__main__":
    main()
