"""Trainable TPS/GDS classifier.

Reviewer #9 reports that Multinomial Naive Bayes "achieves the best
balance in identifying the minority TPS class" among the paper's own
compared models (Naive Bayes, Logistic Regression, RoBERTa). This module
ships that same model family as a trainable scikit-learn pipeline, kept
separate from baseline_vader.py's keyword-override reconstruction, so the
TPS/GDS label a caller actually uses for decisions never depends on the
keyword-contamination policy Reviewer #7 flagged.

No pretrained model ships with this package: the original 542-post gold
dataset (TPSGDS-542) was not available when this package was built. Train
on your own labeled data with train_classifier(), then persist the result
with save_classifier() for reuse.

Requires the "classify" extra: pip install releasetrain-sentiment[classify]
"""

from __future__ import annotations

from pathlib import Path
from typing import Iterable

try:
    import joblib
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.naive_bayes import MultinomialNB
    from sklearn.pipeline import Pipeline
except ImportError as exc:  # pragma: no cover - exercised via packaging, not unit tests
    raise ImportError(
        "the classifier requires scikit-learn and joblib. "
        "Install with: pip install releasetrain-sentiment[classify]"
    ) from exc


def build_classifier() -> Pipeline:
    """A fresh, untrained TF-IDF + Multinomial Naive Bayes pipeline.

    Example:
        >>> pipe = build_classifier()
        >>> texts = [
        ...     "crash on launch every time",
        ...     "app freezes after the update",
        ...     "cannot install, setup fails immediately",
        ...     "I am so tired of this update",
        ...     "another pointless update, ugh",
        ...     "why do they keep ruining the app",
        ... ]
        >>> labels = ["TPS", "TPS", "TPS", "GDS", "GDS", "GDS"]
        >>> _ = pipe.fit(texts, labels)
        >>> pipe.predict(["the app keeps crashing on startup"])
        array(['TPS'], dtype='<U3')
    """
    # min_df=1 (scikit-learn's own default): min_df=2 was tried first and
    # crashed ("After pruning, no terms remain") on a small training set
    # where two documents share no repeated term - a realistic case for an
    # initial labeled seed set, not just this package's own tests. A caller
    # training on the full 542-post gold set who wants stricter pruning can
    # still pass their own TfidfVectorizer into a custom Pipeline.
    return Pipeline(
        [
            ("tfidf", TfidfVectorizer(ngram_range=(1, 2), min_df=1, max_features=20000)),
            ("clf", MultinomialNB()),
        ]
    )


def train_classifier(texts: Iterable[str], labels: Iterable[str]) -> Pipeline:
    """Fit a classifier on labeled text. `texts` should be the same
    text_raw representation the paper describes (post title + body + up
    to 10 highest-scored comments), `labels` the matching "TPS"/"GDS"
    gold labels, same order.
    """
    pipe = build_classifier()
    pipe.fit(list(texts), list(labels))
    return pipe


def classify(pipe: Pipeline, texts: Iterable[str]) -> list[str]:
    """Predict TPS/GDS for a list of texts using an already-trained pipeline.

    Returns plain Python str, not numpy.str_ (what pipe.predict() returns
    directly) - a caller shouldn't need to know this is a scikit-learn
    pipeline under the hood.
    """
    return [str(label) for label in pipe.predict(list(texts))]


def save_classifier(pipe: Pipeline, path: str | Path) -> None:
    """Persist a trained pipeline to disk (joblib format)."""
    joblib.dump(pipe, path)


def load_classifier(path: str | Path) -> Pipeline:
    """Load a pipeline previously saved with save_classifier()."""
    return joblib.load(path)
