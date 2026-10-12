"""Per-comment sentiment scoring for a Reddit discussion thread.

Pure functions: a post (or list of posts) in, a list of per-item scores
out. No network calls and no ReleaseTrain-specific coupling here; see
fetch.py for the optional live-API wrapper.

Uses VADER's standard thresholds (compound >= 0.05 positive,
<= -0.05 negative, otherwise neutral), the same thresholds the original
research code used for its trajectory analysis. This is distinct from the
"technical_first" keyword-override policy described in baseline_vader.py,
which was used only for the paper's TPS/GDS classification benchmark, not
for this trajectory scorer.
"""

from __future__ import annotations

from typing import Any, Iterable, TypedDict

from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

_ANALYZER = SentimentIntensityAnalyzer()

TEXT_SNIPPET_LENGTH = 200


class Comment(TypedDict, total=False):
    text: str
    author: str
    is_author: bool


class Post(TypedDict, total=False):
    title: str
    description: str
    comments: list[Comment]


class ScoredItem(TypedDict):
    source: str  # "post" or "comment"
    index: int  # position in the comments array; -1 for the post itself
    text: str
    is_author: bool
    compound: float
    pos: float
    neu: float
    neg: float
    label: str


def _label_for(compound: float) -> str:
    if compound >= 0.05:
        return "Positive"
    if compound <= -0.05:
        return "Negative"
    return "Neutral"


def _score_text(text: str) -> dict[str, Any]:
    text = text or ""
    scores = _ANALYZER.polarity_scores(text)
    return {
        "compound": scores["compound"],
        "pos": scores["pos"],
        "neu": scores["neu"],
        "neg": scores["neg"],
        "label": _label_for(scores["compound"]),
    }


def score_post(post: Post) -> list[ScoredItem]:
    """Score one post: its own title/description, then every comment.

    The post itself is always element 0, flagged source="post" and
    is_author=True (a post is definitionally its own author's content) -
    this is the trajectory's starting point. Every following element is
    source="comment", in the same order the input comments were given
    (chronological order is the caller's responsibility, same as the
    original research code's own sorted-by-timestamp step), so an output
    index always maps back to the same-index input comment.

    Example:
        >>> post = {
        ...     "title": "Update broke my build",
        ...     "description": "Nothing compiles since 3.2.0",
        ...     "comments": [
        ...         {"text": "Known issue, fix coming", "author": "dev1", "is_author": True},
        ...         {"text": "Same here, very annoying", "author": "user2", "is_author": False},
        ...     ],
        ... }
        >>> results = score_post(post)
        >>> len(results)
        3
        >>> results[0]["source"]
        'post'
        >>> results[1]["is_author"]
        True
    """
    title = post.get("title") or ""
    description = post.get("description") or ""
    post_text = f"{title}\n\n{description}".strip()
    post_scores = _score_text(post_text)

    items: list[ScoredItem] = [
        {
            "source": "post",
            "index": -1,
            "text": post_text[:TEXT_SNIPPET_LENGTH],
            "is_author": True,
            **post_scores,
        }
    ]

    for i, comment in enumerate(post.get("comments") or []):
        text = comment.get("text") or ""
        comment_scores = _score_text(text)
        items.append(
            {
                "source": "comment",
                "index": i,
                "text": text[:TEXT_SNIPPET_LENGTH],
                "is_author": bool(comment.get("is_author")),
                **comment_scores,
            }
        )

    return items


def score_posts(posts: Iterable[Post]) -> list[list[ScoredItem]]:
    """Score a list of posts. One results array per input post, same order.

    Example:
        >>> post_a = {"title": "a", "description": "", "comments": []}
        >>> post_b = {"title": "b", "description": "", "comments": []}
        >>> results = score_posts([post_a, post_b])
        >>> len(results) == 2
        True
    """
    return [score_post(post) for post in posts]


class TrajectorySummary(TypedDict):
    author_avg: float
    community_avg: float
    author_shift: float
    community_shift: float


def _shift(values: list[float]) -> float:
    if len(values) < 4:
        return 0.0
    midpoint = len(values) // 2
    early = sum(values[:midpoint]) / midpoint
    late = sum(values[midpoint:]) / (len(values) - midpoint)
    return late - early


def trajectory_summary(scored_items: list[ScoredItem]) -> TrajectorySummary:
    """Aggregate a score_post() result into the author-vs-community
    divergence metrics the paper's own analysis reports: each side's
    average compound score, and the shift from its own early replies to
    its own late replies. Kept separate from score_post() itself so a
    caller who only wants raw per-item scores isn't forced to pull in
    this aggregation step.
    """
    comments = [item for item in scored_items if item["source"] == "comment"]
    author_values = [c["compound"] for c in comments if c["is_author"]]
    community_values = [c["compound"] for c in comments if not c["is_author"]]

    return {
        "author_avg": sum(author_values) / len(author_values) if author_values else 0.0,
        "community_avg": sum(community_values) / len(community_values) if community_values else 0.0,
        "author_shift": _shift(author_values),
        "community_shift": _shift(community_values),
    }
