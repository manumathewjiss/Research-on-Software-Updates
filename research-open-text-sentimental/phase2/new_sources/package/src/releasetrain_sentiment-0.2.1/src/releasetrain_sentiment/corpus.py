"""Corpus and labeling documentation as versioned code, not prose.

Reviewers #4, #7, and #9 independently asked the same three questions:
which subreddits and timeframes were sampled, what API was used, and how
the gold labels were assigned, and by whom. Citing a specific installed
version of this package (e.g. releasetrain-sentiment==1.0.0) answers all
three with a pinned, reproducible artifact instead of prose that can drift
out of sync with what was actually done.

Two separate corpora are documented below. Do not conflate them:

ENHANCED_AUTOMATED_CORPUS describes the 324-post trajectory dataset
(enhanced_automated_sentiment_results.json in the research repo) - every
field below was read directly from that file's own analysis_metadata and
its posts' own "subreddit"/"created_utc" fields, not estimated.

TPSGDS542_CORPUS describes the paper's own gold-labeled TPS/GDS
classification dataset (N=542). Its exact subreddit list, date range, and
labeler identity were not available in the public research repo this
package was built from. The fields are left as None rather than guessed;
fill them in from the actual dataset before citing this spec in the paper.
"""

from __future__ import annotations

from typing import TypedDict


class CorpusSpec(TypedDict):
    name: str
    source_api: str | None
    total_posts_fetched: int | None
    total_posts_in_corpus: int | None
    date_range_start: str | None
    date_range_end: str | None
    subreddits: list[str] | None
    filtering_criteria: dict[str, object] | None
    notes: str


ENHANCED_AUTOMATED_CORPUS: CorpusSpec = {
    "name": "enhanced_automated_sentiment_results (324 posts)",
    "source_api": "https://releasetrain.io/api/reddit",
    "total_posts_fetched": 3519,
    "total_posts_in_corpus": 324,
    "date_range_start": "2025-09-27T17:10:48",
    "date_range_end": "2025-10-07T08:31:18",
    "subreddits": [
        "transformers", "comfyui", "Wordpress", "rust", "linux", "neovim",
        "Bitcoin", "immich", "MacOS", "Python", "react", "vscode", "node",
        "java", "Nest", "Android", "kubernetes", "django", "Supabase",
        "Nuxt", "typescript", "github", "Prometheus", "LangChain", "union",
        "IBM", "PHP", "anime", "windows", "oracle", "tailwindcss", "google",
        "FastAPI", "Sherlock", "MicrosoftEdge", "Gin", "laravel",
        "cprogramming", "Playwright", "rustdesk", "mermaid", "ollama",
        "arch", "ACT", "chrome", "servers", "rails",
    ],
    "filtering_criteria": {
        "min_total_comments": 10,
        "min_author_replies": 3,
        "min_community_comments": 5,
        "min_quality_score": 0.3,
    },
    "notes": (
        "Date range reflects whatever ReleaseTrain's /api/reddit returned as "
        "recent at fetch time (2025-10-07), not a deliberately chosen "
        "historical window. Re-running the fetch on a later date will "
        "produce a different, more recent window, not this exact set."
    ),
}


TPSGDS542_CORPUS: CorpusSpec = {
    "name": "TPSGDS-542 (paper's gold-labeled TPS/GDS classification set)",
    "source_api": "https://releasetrain.io/api/reddit",  # confirmed used elsewhere in the research repo's own scripts
    "total_posts_fetched": None,
    "total_posts_in_corpus": 542,
    "date_range_start": None,  # TODO: fill in from the actual TPSGDS-542 dataset
    "date_range_end": None,  # TODO: fill in from the actual TPSGDS-542 dataset
    "subreddits": None,  # TODO: fill in from the actual TPSGDS-542 dataset
    "filtering_criteria": None,
    "notes": (
        "This corpus's own file was not present in the public "
        "reddit-sentiment-manumathewjiss repo this package was built "
        "from. Replace the None fields above with the real values before "
        "citing this spec for the TPS/GDS classification experiments."
    ),
}


class LabelDefinition(TypedDict):
    label: str
    definition: str
    examples: list[str]


LABELING_GUIDE: list[LabelDefinition] = [
    {
        "label": "TPS",
        "definition": (
            "Technical Problem Solving: reporting an actual bug, crash, "
            "installation failure, feature confusion, or performance drop, "
            "or asking for or sharing a workaround."
        ),
        "examples": [
            "App crashes on launch after the 3.2.0 update.",
            "Found a workaround: downgrade to 3.1.4 until this is patched.",
        ],
    },
    {
        "label": "GDS",
        "definition": (
            "General Discontent: venting, complaining, or expressing "
            "fatigue about an update with no actionable technical detail."
        ),
        "examples": [
            "Another update, another disappointment.",
            "I'm so tired of this app changing every month.",
        ],
    },
]

# Who labeled TPSGDS-542 and what inter-rater agreement process, if any,
# was used is not documented in the public research repo. Fill this in
# (labeler identity, whether a second labeler cross-checked a subset, and
# any agreement score such as Cohen's kappa) before citing LABELING_GUIDE
# as a complete methodology description.
LABELING_PROCESS_NOTES = (
    "TODO: document who labeled the gold dataset and any inter-rater "
    "agreement check performed."
)
