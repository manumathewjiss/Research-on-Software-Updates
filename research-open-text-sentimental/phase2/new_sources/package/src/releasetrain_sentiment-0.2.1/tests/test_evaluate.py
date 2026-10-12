import pytest

from releasetrain_sentiment import evaluate_predictions, sample_high_divergence


def test_sample_high_divergence_sorts_descending():
    posts = [
        {"post_id": "a", "category": "TPS", "divergence": 0.1},
        {"post_id": "b", "category": "TPS", "divergence": 0.9},
        {"post_id": "c", "category": "TPS", "divergence": 0.5},
    ]
    result = sample_high_divergence(posts, n=2)
    assert [p["post_id"] for p in result] == ["b", "c"]


def test_sample_high_divergence_filters_by_category():
    posts = [
        {"post_id": "a", "category": "TPS", "divergence": 0.9},
        {"post_id": "b", "category": "GDS", "divergence": 0.9},
    ]
    result = sample_high_divergence(posts, n=30, category="GDS")
    assert [p["post_id"] for p in result] == ["b"]


def test_evaluate_predictions_perfect_match():
    predicted = ["TPS", "GDS", "TPS"]
    actual = ["TPS", "GDS", "TPS"]
    result = evaluate_predictions(predicted, actual)
    assert result["precision"] == 1.0
    assert result["recall"] == 1.0
    assert result["f1"] == 1.0
    assert result["support"] == 2


def test_evaluate_predictions_known_values():
    predicted = ["TPS", "GDS", "TPS", "GDS"]
    actual = ["TPS", "GDS", "GDS", "GDS"]
    result = evaluate_predictions(predicted, actual)
    assert result["precision"] == 0.5
    assert result["recall"] == 1.0
    assert result["support"] == 1


def test_evaluate_predictions_no_positive_actuals_has_zero_recall_not_a_crash():
    predicted = ["GDS", "GDS"]
    actual = ["GDS", "GDS"]
    result = evaluate_predictions(predicted, actual)
    assert result["recall"] == 0.0
    assert result["precision"] == 0.0
    assert result["f1"] == 0.0
    assert result["support"] == 0


def test_evaluate_predictions_rejects_mismatched_lengths():
    with pytest.raises(ValueError):
        evaluate_predictions(["TPS"], ["TPS", "GDS"])
