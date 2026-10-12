"""Optional live wrapper around ReleaseTrain's public Reddit feed.

Isolated from score.py/classify.py/baseline_vader.py on purpose: those
modules take plain Python data and have no network dependency, so an
outside reviewer can run them against their own data without ever
touching this module or needing network access. Use this module only when
you actually want to pull fresh candidates from ReleaseTrain.

Requires the "fetch" extra: pip install releasetrain-sentiment[fetch]
"""

from __future__ import annotations

try:
    import requests
except ImportError as exc:  # pragma: no cover - exercised via packaging, not unit tests
    raise ImportError(
        "fetch.py requires requests. Install with: pip install releasetrain-sentiment[fetch]"
    ) from exc

DEFAULT_API_URL = "https://releasetrain.io/api/reddit"


def fetch_posts(api_url: str = DEFAULT_API_URL, timeout: int = 30) -> list[dict]:
    """Fetch the current Reddit post feed from ReleaseTrain, as raw dicts
    (ReleaseTrain's own JSON shape: title, author, subreddit, comments,
    etc., not yet converted to score.py's Post shape).

    Example:
        >>> posts = fetch_posts()  # doctest: +SKIP
        >>> len(posts) > 0  # doctest: +SKIP
        True
    """
    response = requests.get(api_url, timeout=timeout)
    response.raise_for_status()
    return response.json()


def to_scoreable_post(raw_post: dict) -> dict:
    """Convert one raw ReleaseTrain Reddit post into score.py's Post shape
    (title, description, comments: [{text, author, is_author}]),
    sorted chronologically by created_utc, same as the original research
    code's own sort step.
    """
    author = raw_post.get("author", "")
    comments = sorted(raw_post.get("comments", []), key=lambda c: c.get("created_utc", ""))
    return {
        "title": raw_post.get("title", ""),
        "description": raw_post.get("selftext") or raw_post.get("description", ""),
        "comments": [
            {
                "text": c.get("body", ""),
                "author": c.get("author", ""),
                "is_author": bool(c.get("is_submitter")) or c.get("author") == author,
            }
            for c in comments
        ],
    }
