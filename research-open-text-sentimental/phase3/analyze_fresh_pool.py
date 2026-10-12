"""Audit fresh API candidates against the complete Phase 2 master by ID and text."""
from __future__ import annotations

import bisect
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
RAW = ROOT / "fresh_test_20261007/raw"
MASTER = ROOT.parent / "phase2/combined_dataset/master_records.json"


def key(title: str, body: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9]+", " ", (title + " " + body).lower())).strip()


def grams(text: str) -> set[str]:
    if len(text) < 5:
        return {text}
    return {text[i:i + 5] for i in range(len(text) - 4)}


def near(a: set[str], b: set[str]) -> float:
    common = len(a & b)
    return common / (len(a) + len(b) - common)


def main() -> None:
    pages = sorted(RAW.glob("update_related_page_*.json"))
    manifest = json.loads((RAW / "collection_manifest.json").read_text())
    assert len(pages) == len(manifest["pages"])
    for path, record in zip(pages, manifest["pages"]):
        assert hashlib.sha256(path.read_bytes()).hexdigest() == record["sha256"]
    api = [r for path in pages for r in json.loads(path.read_text())["data"]]
    old = json.loads(MASTER.read_text())
    old_ids = {r["reddit_id"] for r in old}
    assert len(api) == len({r["redditId"] for r in api})
    unseen = [r for r in api if r["redditId"] not in old_ids]

    old_key_to_ids = {}
    old_index = []
    for r in old:
        text = key(r.get("title") or "", r.get("post_body") or "")
        old_key_to_ids.setdefault(text, []).append(r["reddit_id"])
        g = grams(text)
        old_index.append((len(g), r["reddit_id"], g))
    old_index.sort(key=lambda x: x[0])
    old_sizes = [r[0] for r in old_index]

    duplicates = []
    eligible = []
    seen_new = []
    for r in unseen:
        text = key(r.get("title") or "", r.get("author_description") or "")
        g = grams(text)
        exact = old_key_to_ids.get(text, [])
        hits = []
        if not exact:
            low = bisect.bisect_left(old_sizes, int(len(g) * 0.92))
            high = bisect.bisect_right(old_sizes, int(len(g) / 0.92) + 1)
            for _, other_id, other_g in old_index[low:high]:
                value = near(g, other_g)
                if value >= 0.92:
                    hits.append({"reddit_id": other_id, "jaccard_char5": round(value, 4)})
        for prev in seen_new:
            if 0.92 * len(g) <= len(prev[2]) <= len(g) / 0.92:
                value = near(g, prev[2])
                if value >= 0.92:
                    hits.append({"reddit_id": prev[0], "jaccard_char5": round(value, 4)})
        if exact or hits:
            duplicates.append({"reddit_id": r["redditId"], "exact_old_ids": exact, "near_hits": hits})
        else:
            eligible.append(r)
            seen_new.append((r["redditId"], text, g))

    out = ROOT / "fresh_test_20261007"
    (out / "excluded_duplicates.json").write_text(json.dumps(duplicates, indent=2) + "\n")
    (out / "eligible_candidates.json").write_text(json.dumps(eligible, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({"api_posts": len(api), "old_id_overlap": len(api) - len(unseen),
                      "unseen_ids": len(unseen), "text_duplicate_exclusions": len(duplicates),
                      "eligible_candidates": len(eligible)}))


if __name__ == "__main__":
    main()
