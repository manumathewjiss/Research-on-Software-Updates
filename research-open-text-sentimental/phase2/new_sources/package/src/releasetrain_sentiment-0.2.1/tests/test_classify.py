import tempfile
from pathlib import Path

from releasetrain_sentiment import classify, load_classifier, save_classifier, train_classifier


def test_train_and_classify_round_trip():
    texts = [
        "crash on launch every time",
        "app freezes after the update",
        "I'm so tired of this update",
        "another pointless update, ugh",
    ]
    labels = ["TPS", "TPS", "GDS", "GDS"]
    pipe = train_classifier(texts, labels)
    predictions = classify(pipe, ["the app crashed again"])
    assert predictions[0] in ("TPS", "GDS")


def test_save_and_load_classifier_round_trip():
    texts = ["crash on launch", "I hate this update"]
    labels = ["TPS", "GDS"]
    pipe = train_classifier(texts, labels)
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "model.joblib"
        save_classifier(pipe, path)
        loaded = load_classifier(path)
        assert classify(loaded, texts) == classify(pipe, texts)
