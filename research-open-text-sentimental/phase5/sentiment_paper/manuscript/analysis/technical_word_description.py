#!/usr/bin/env python3
"""Prespecified descriptive check on the 2,050 Reddit-URL development posts.

Does not read reserved or fresh test files and does not fit a model.
Incident terms are the phase-2 title mask without update/upgrade, because
this collection is already update-scoped. Discontent terms are a closed
evaluative list written before the counts were examined.
"""

from __future__ import annotations

import json
import re
import sys
from collections import Counter
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
PAPER = HERE.parents[1]
sys.path.insert(0, str(PAPER))

from run_staged_analysis import (  # noqa: E402
    REPO,
    load_oct5,
    load_population,
    load_raw_posts_by_id,
    OLD_RAW,
)
from trajectory.sentiment import compound_score  # noqa: E402
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer  # noqa: E402

INCIDENT = (
    "error", "bug", "bugs", "fix", "fixed", "crash", "crashed", "install",
    "installation", "broken", "issue", "issues", "problem", "problems",
    "dependency", "dependencies", "config", "configuration",
)
DISCONTENT = (
    "hate", "hates", "hated", "annoying", "annoyed", "frustrating",
    "frustrated", "disappointed", "disappointment", "useless", "terrible",
    "awful", "worst", "stupid", "garbage", "trash", "ridiculous", "sucks",
    "horrible",
)
INCIDENT_RE = re.compile(r"\b(" + "|".join(INCIDENT) + r")\b", re.I)
DISCONTENT_RE = re.compile(r"\b(" + "|".join(DISCONTENT) + r")\b", re.I)
JOIN = PAPER / "results" / "join_coverage_posts.jsonl"
OUT = HERE / "technical_word_description.json"


def cell(incident: bool, discontent: bool) -> str:
    if incident and discontent:
        return "both"
    if incident:
        return "incident_only"
    if discontent:
        return "discontent_only"
    return "neither"


def main() -> int:
    rows, y, _, _ = load_population()
    march = load_raw_posts_by_id(OLD_RAW)
    oct5 = load_oct5()
    analyzer = SentimentIntensityAnalyzer()
    buckets = {}
    for row, label in zip(rows, y):
        post = oct5.get(row["reddit_id"]) or march[row["reddit_id"]]
        text = f"{post.get('title') or ''}\n{post.get('author_description') or ''}"
        name = cell(bool(INCIDENT_RE.search(text)), bool(DISCONTENT_RE.search(text)))
        compound = float(compound_score(analyzer, text))
        buckets.setdefault((int(label), name), []).append(compound)

    by_class = {}
    for label, cname in ((1, "troubleshooting"), (0, "other_update")):
        block = {}
        for name in ("incident_only", "discontent_only", "both", "neither"):
            vals = buckets.get((label, name), [])
            block[name] = {
                "n": len(vals),
                "mean_compound": None if not vals else float(np.mean(vals)),
            }
        block["n"] = sum(block[n]["n"] for n in ("incident_only", "discontent_only", "both", "neither"))
        by_class[cname] = block

    missing = Counter()
    for line in JOIN.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        rec = json.loads(line)
        if rec.get("stratum") != "development_s2":
            continue
        missing[(rec.get("domain"), int(rec.get("s2_target")), bool(rec.get("chosen_n_nonempty")))] += 1

    payload = {
        "tests_read": False,
        "population": "reddit_url_s2_2050",
        "incident_terms": INCIDENT,
        "discontent_terms": DISCONTENT,
        "excluded_from_historical_mask": ["update", "upgrade"],
        "exclusion_reason": "Collection is already restricted to software-update discussion.",
        "by_class": by_class,
        "identifiers_written": False,
        "verbatim_text_written": False,
        "development_s2_comment_presence_by_domain_and_class": [
            {"domain": d, "s2_target": t, "has_nonempty_comment": h, "n": n}
            for (d, t, h), n in sorted(missing.items())
        ],
    }
    OUT.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(by_class, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
