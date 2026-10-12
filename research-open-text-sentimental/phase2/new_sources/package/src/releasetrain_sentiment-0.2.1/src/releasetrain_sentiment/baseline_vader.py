"""Reconstruction of the paper's "technical_first" VADER baseline.

This is NOT the original experiment script. It was built from Reviewer #7's
written description of the policy (ICMLA 2026, Paper 483, Weakness 1), not
from the original code, because the original "technical_first" script was
not available when this package was built. Treat this module as a
diagnostic tool for reproducing and inspecting the described flaw, not as
a verified, byte-for-byte reproduction of the paper's reported numbers.

The described flaw: any comment containing a keyword like "error", "crash",
or "fix" was automatically exempted from the GDS (General Discontent)
class, regardless of context (e.g., "that UI change was a massive error" is
not a bug report). Combined with a narrow neutral band (+/- 0.15, versus
the standard +/- 0.05 used elsewhere in this package's score.py), this
over-exempts ordinary venting as "technical," which Reviewer #7 identifies
as the likely cause of VADER's weak relative performance in Table I.

Use flags_technical_keyword() to check whether a given comment would have
tripped this exemption, for the qualitative audit Reviewer #4 suggested
(30 high-divergence TPS threads vs 30 high-divergence GDS threads, see
evaluate.py's sample_high_divergence()).
"""

from __future__ import annotations

import re

from .score import _score_text

# Reconstructed from Reviewer #7's examples ("error", "crash", "fix") plus
# a small number of plainly equivalent terms. This list is a best-effort
# reconstruction, not a transcription of the original code: if the actual
# keyword list is available, replace this constant with the real one.
#
# Stored as word stems, not exact words: the pattern below matches each
# stem plus any trailing letters (\w*), so "crash" also matches "crashes"/
# "crashed"/"crashing" without listing every inflected form separately.
TECHNICAL_KEYWORDS: tuple[str, ...] = (
    "error",
    "crash",
    "fix",
    "bug",
    "broken",
    "freeze",
    "frozen",
    "workaround",
)

_KEYWORD_PATTERN = re.compile(
    r"\b(" + "|".join(re.escape(k) for k in TECHNICAL_KEYWORDS) + r")\w*\b",
    re.IGNORECASE,
)


def flags_technical_keyword(text: str) -> bool:
    """True if text contains a keyword that would trip the "technical_first"
    exemption, regardless of the surrounding sentence's real meaning.

    Example:
        >>> flags_technical_keyword("That redesign was a massive error.")
        True
        >>> flags_technical_keyword("I love the new dashboard.")
        False
    """
    return bool(_KEYWORD_PATTERN.search(text or ""))


def vader_sentiment_label(text: str, neutral_band: float = 0.15) -> str:
    """VADER compound-score label using a configurable neutral band.

    Defaults to 0.15 (the narrow band Reviewer #7 describes) rather than
    score.py's standard 0.05, so this module reproduces the specific
    described configuration rather than silently reusing the other
    module's default.
    """
    compound = _score_text(text)["compound"]
    if compound >= neutral_band:
        return "Positive"
    if compound <= -neutral_band:
        return "Negative"
    return "Neutral"


def classify_technical_first(text: str, neutral_band: float = 0.15) -> str:
    """Reconstructs the full described "technical_first" decision: a
    keyword hit exempts the comment into TPS outright; otherwise the
    comment is labeled by vader_sentiment_label(), with Negative treated
    as GDS and Positive/Neutral treated as not-GDS.

    This mapping from sentiment label to TPS/GDS is inferred, not
    confirmed, since the reviewer's description covers the keyword
    exemption and the neutral band but not the full label-to-class
    mapping. Verify against the original paper/code before citing this
    function's output as a faithful reproduction.
    """
    if flags_technical_keyword(text):
        return "TPS"
    label = vader_sentiment_label(text, neutral_band=neutral_band)
    return "GDS" if label == "Negative" else "TPS"
