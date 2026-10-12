"""releasetrain-sentiment: author-vs-community sentiment trajectory
scoring for Reddit software-update discussions.

Core (no extra dependencies beyond vaderSentiment):
    score_post, score_posts, trajectory_summary
    flags_technical_keyword, vader_sentiment_label, classify_technical_first
    ENHANCED_AUTOMATED_CORPUS, TPSGDS542_CORPUS, LABELING_GUIDE
    sample_high_divergence, evaluate_predictions

Optional (pip install releasetrain-sentiment[classify]):
    build_classifier, train_classifier, classify, save_classifier, load_classifier

Optional (pip install releasetrain-sentiment[fetch]):
    fetch_posts, to_scoreable_post
"""

from .baseline_vader import (
    TECHNICAL_KEYWORDS,
    classify_technical_first,
    flags_technical_keyword,
    vader_sentiment_label,
)
from .corpus import (
    ENHANCED_AUTOMATED_CORPUS,
    LABELING_GUIDE,
    LABELING_PROCESS_NOTES,
    TPSGDS542_CORPUS,
)
from .evaluate import evaluate_predictions, sample_high_divergence
from .score import score_post, score_posts, trajectory_summary

__version__ = "0.2.1"

__all__ = [
    "score_post",
    "score_posts",
    "trajectory_summary",
    "flags_technical_keyword",
    "vader_sentiment_label",
    "classify_technical_first",
    "TECHNICAL_KEYWORDS",
    "ENHANCED_AUTOMATED_CORPUS",
    "TPSGDS542_CORPUS",
    "LABELING_GUIDE",
    "LABELING_PROCESS_NOTES",
    "sample_high_divergence",
    "evaluate_predictions",
    "__version__",
]


def __getattr__(name: str):
    # build_classifier/train_classifier/classify/save_classifier/load_classifier
    # and fetch_posts/to_scoreable_post pull in optional extras (scikit-learn,
    # requests). Deferred via __getattr__ so `import releasetrain_sentiment`
    # never requires those packages unless one of these names is actually used.
    #
    # The implementation module is named _classify.py, not classify.py, even
    # though the public function is named classify(): "from
    # releasetrain_sentiment import classify" does NOT go through this
    # __getattr__ at all if a real submodule named classify.py exists -
    # Python's import system tries importing "releasetrain_sentiment.classify"
    # as a submodule FIRST for any "from package import name" statement,
    # before ever consulting a package's __getattr__ (PEP 562 does not
    # override this). With a submodule literally named classify.py, that
    # proactive submodule import would always win, silently handing the
    # caller the submodule object instead of the classify() function -
    # confirmed live: `from releasetrain_sentiment import classify` returned
    # <module ...> instead of <function ...> until the submodule was renamed.
    import importlib

    if name in (
        "build_classifier",
        "train_classifier",
        "classify",
        "save_classifier",
        "load_classifier",
    ):
        _classify_module = importlib.import_module(f"{__name__}._classify")
        return getattr(_classify_module, name)
    if name in ("fetch_posts", "to_scoreable_post"):
        _fetch_module = importlib.import_module(f"{__name__}.fetch")
        return getattr(_fetch_module, name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
