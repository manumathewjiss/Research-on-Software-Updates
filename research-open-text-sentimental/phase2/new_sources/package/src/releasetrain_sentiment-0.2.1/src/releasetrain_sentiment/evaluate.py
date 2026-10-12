"""Downstream evaluation helpers.

Reviewer #4 (Weakness 2): the claim that TPS filtering helps developers
"more efficiently identify troubleshooting discussions" has no downstream
evaluation. The same reviewer's own suggested fallback, in the Detailed
Feedback section, is smaller and concrete: "a qualitative manual audit of
30 high-divergence TPS threads vs 30 high-divergence GDS threads." This
module implements that sampler, plus a small precision/recall harness for
when a labeled "was this report actually useful" ground truth is
available.
"""

from __future__ import annotations

from typing import TypedDict


class DivergencePost(TypedDict):
    post_id: str
    category: str  # "TPS" or "GDS"
    divergence: float  # e.g. abs(author_avg - community_avg) from trajectory_summary()


def sample_high_divergence(
    posts: list[DivergencePost], n: int = 30, category: str | None = None
) -> list[DivergencePost]:
    """Return the n highest-divergence posts, optionally filtered to one
    category, sorted most-divergent first.

    For Reviewer #4's suggested audit, call this twice:

    Example (posts is your own list of DivergencePost dicts):
        >>> tps_sample = sample_high_divergence(posts, n=30, category="TPS")  # doctest: +SKIP
        >>> gds_sample = sample_high_divergence(posts, n=30, category="GDS")  # doctest: +SKIP

    Each returned post is ready to hand to a human reviewer to inspect
    whether baseline_vader.flags_technical_keyword() fired on genuinely
    technical content or on an unrelated use of a keyword like "error."
    """
    pool = [p for p in posts if category is None or p["category"] == category]
    return sorted(pool, key=lambda p: p["divergence"], reverse=True)[:n]


class EvaluationResult(TypedDict):
    precision: float
    recall: float
    f1: float
    support: int


def evaluate_predictions(
    predicted: list[str], actual: list[str], positive_label: str = "TPS"
) -> EvaluationResult:
    """Precision/recall/F1 of a predicted label list against ground truth,
    for the positive_label class (defaults to "TPS", the minority class
    both the paper and reviewers focus on).

    This directly answers Reviewer #4's ask for a downstream evaluation:
    run this against even a small (20-30 example) hand-labeled "was this
    report actually useful to a developer" set, rather than reporting the
    practical benefit as an unverified claim.

    Example:
        >>> predicted = ["TPS", "GDS", "TPS", "GDS"]
        >>> actual =    ["TPS", "GDS", "GDS", "GDS"]
        >>> evaluate_predictions(predicted, actual)
        {'precision': 0.5, 'recall': 1.0, 'f1': 0.6666666666666666, 'support': 1}
    """
    if len(predicted) != len(actual):
        raise ValueError("predicted and actual must be the same length")

    true_positives = sum(1 for p, a in zip(predicted, actual) if p == positive_label and a == positive_label)
    predicted_positive = sum(1 for p in predicted if p == positive_label)
    actual_positive = sum(1 for a in actual if a == positive_label)

    precision = true_positives / predicted_positive if predicted_positive else 0.0
    recall = true_positives / actual_positive if actual_positive else 0.0
    f1 = (2 * precision * recall / (precision + recall)) if (precision + recall) else 0.0

    return {"precision": precision, "recall": recall, "f1": f1, "support": actual_positive}
