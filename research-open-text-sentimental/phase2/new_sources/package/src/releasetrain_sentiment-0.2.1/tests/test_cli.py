import json
import tempfile
from pathlib import Path

import pytest

from releasetrain_sentiment.cli import build_parser, main


def make_post():
    return {
        "title": "Update broke my build",
        "description": "Nothing compiles since 3.2.0",
        "comments": [
            {"text": "Known issue, fix coming soon", "author": "dev1", "is_author": True},
            {"text": "Same here, very annoying", "author": "user2", "is_author": False},
        ],
    }


def test_build_parser_requires_a_subcommand():
    parser = build_parser()
    with pytest.raises(SystemExit):
        parser.parse_args([])


def test_version_flag_prints_the_package_version(capsys):
    with pytest.raises(SystemExit) as exc:
        main(["--version"])
    assert exc.value.code == 0
    assert "releasetrain-sentiment" in capsys.readouterr().out


def test_score_from_stdin_prints_items_and_trajectory(capsys, monkeypatch):
    import io

    monkeypatch.setattr("sys.stdin", io.StringIO(json.dumps(make_post())))
    code = main(["score"])
    assert code == 0
    output = json.loads(capsys.readouterr().out)
    assert "items" in output and "trajectory" in output
    assert len(output["items"]) == len(make_post()["comments"]) + 1


def test_score_from_a_file_handles_a_list_of_posts(capsys):
    posts = [make_post(), make_post()]
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "posts.json"
        path.write_text(json.dumps(posts), encoding="utf-8")
        code = main(["score", "--input", str(path)])
    assert code == 0
    output = json.loads(capsys.readouterr().out)
    assert isinstance(output, list)
    assert len(output) == 2


def test_keyword_check_prints_true_false_per_text(capsys):
    code = main(["keyword-check", "That redesign was a massive error", "I am so tired of this update"])
    assert code == 0
    lines = capsys.readouterr().out.strip().splitlines()
    assert lines[0].startswith("True\t")
    assert lines[1].startswith("False\t")


def test_label_prints_both_the_vader_and_technical_first_label(capsys):
    code = main(["label", "I am so tired of this update"])
    assert code == 0
    out = capsys.readouterr().out
    assert "vader=" in out
    assert "technical_first=" in out


def test_classify_with_a_saved_model_prints_a_label_per_text(capsys):
    from releasetrain_sentiment import save_classifier, train_classifier

    texts = ["crash on launch every time", "app freezes after the update", "I'm so tired of this update", "another pointless update, ugh"]
    labels = ["TPS", "TPS", "GDS", "GDS"]
    pipe = train_classifier(texts, labels)
    with tempfile.TemporaryDirectory() as tmp:
        model_path = Path(tmp) / "model.joblib"
        save_classifier(pipe, model_path)
        code = main(["classify", "--model", str(model_path), "the app crashed again"])
    assert code == 0
    out = capsys.readouterr().out.strip()
    label, text = out.split("\t", 1)
    assert label in ("TPS", "GDS")
    assert text == "the app crashed again"
