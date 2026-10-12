"""Command-line interface for releasetrain-sentiment.

A thin wrapper around the package's own functions - no scoring,
classification, or fetch logic lives here, only argument parsing and
JSON I/O, so the CLI can never drift in behavior from the Python API
(see README.md for the equivalent `import releasetrain_sentiment` calls).

Installed as the `releasetrain-sentiment` console script; also runnable
as `python -m releasetrain_sentiment`.
"""

from __future__ import annotations

import argparse
import json
import sys
from typing import Any

from . import (
    __version__,
    classify_technical_first,
    flags_technical_keyword,
    score_posts,
    trajectory_summary,
    vader_sentiment_label,
)


def _read_json_input(path: str | None) -> Any:
    """Read a JSON post or list of posts from a file, or stdin when no
    file is given (or "-" is given explicitly)."""
    if path and path != "-":
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    return json.load(sys.stdin)


def _cmd_score(args: argparse.Namespace) -> int:
    data = _read_json_input(args.input)
    was_single = not isinstance(data, list)
    posts = [data] if was_single else data

    results = score_posts(posts)
    output = [{"items": items, "trajectory": trajectory_summary(items)} for items in results]
    if was_single:
        output = output[0]

    json.dump(output, sys.stdout, indent=2 if args.pretty else None)
    sys.stdout.write("\n")
    return 0


def _cmd_keyword_check(args: argparse.Namespace) -> int:
    for text in args.text:
        print(f"{flags_technical_keyword(text)}\t{text}")
    return 0


def _cmd_label(args: argparse.Namespace) -> int:
    for text in args.text:
        vader = vader_sentiment_label(text)
        technical_first = classify_technical_first(text)
        print(f"{text}\n  vader={vader}  technical_first={technical_first}")
    return 0


def _cmd_classify(args: argparse.Namespace) -> int:
    # Imported lazily (not at module top) since this pulls in the
    # [classify] extra (scikit-learn, joblib) - a plain `score`/
    # `keyword-check`/`label` invocation should never need it installed.
    from . import classify as classify_fn
    from . import load_classifier

    pipe = load_classifier(args.model)
    for text, label in zip(args.text, classify_fn(pipe, args.text)):
        print(f"{label}\t{text}")
    return 0


def _cmd_fetch(args: argparse.Namespace) -> int:
    # Imported lazily - pulls in the [fetch] extra (requests).
    from . import fetch_posts, to_scoreable_post

    kwargs = {"api_url": args.api_url} if args.api_url else {}
    raw_posts = fetch_posts(**kwargs)
    if args.limit is not None:
        raw_posts = raw_posts[: args.limit]
    posts = [to_scoreable_post(p) for p in raw_posts]

    text = json.dumps(posts, indent=2 if args.pretty else None)
    if args.out:
        with open(args.out, "w", encoding="utf-8") as f:
            f.write(text)
    else:
        print(text)
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="releasetrain-sentiment",
        description="Author-vs-community sentiment trajectory scoring for Reddit software-update discussions.",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    sub = parser.add_subparsers(dest="command", required=True)

    p_score = sub.add_parser("score", help="Score a post (or JSON array of posts) and print its trajectory summary")
    p_score.add_argument("--input", "-i", help="JSON file to read (default: stdin; '-' also means stdin)")
    p_score.add_argument("--pretty", action="store_true", help="Indent the JSON output")
    p_score.set_defaults(func=_cmd_score)

    p_kw = sub.add_parser("keyword-check", help="Check text(s) against the technical-keyword contamination list")
    p_kw.add_argument("text", nargs="+", help="One or more texts to check")
    p_kw.set_defaults(func=_cmd_keyword_check)

    p_label = sub.add_parser(
        "label", help="Print the standard VADER label and the technical_first baseline label for text(s)"
    )
    p_label.add_argument("text", nargs="+")
    p_label.set_defaults(func=_cmd_label)

    p_classify = sub.add_parser(
        "classify", help="Classify text(s) with a saved TPS/GDS model (requires: pip install releasetrain-sentiment[classify])"
    )
    p_classify.add_argument("--model", "-m", required=True, help="Path to a model saved with save_classifier()")
    p_classify.add_argument("text", nargs="+")
    p_classify.set_defaults(func=_cmd_classify)

    p_fetch = sub.add_parser(
        "fetch", help="Fetch recent posts from a live ReleaseTrain API (requires: pip install releasetrain-sentiment[fetch])"
    )
    p_fetch.add_argument("--api-url", help="Override the default ReleaseTrain /api/reddit URL")
    p_fetch.add_argument("--limit", type=int, help="Only keep the first N posts")
    p_fetch.add_argument("--out", "-o", help="Write JSON to this file instead of stdout")
    p_fetch.add_argument("--pretty", action="store_true")
    p_fetch.set_defaults(func=_cmd_fetch)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
