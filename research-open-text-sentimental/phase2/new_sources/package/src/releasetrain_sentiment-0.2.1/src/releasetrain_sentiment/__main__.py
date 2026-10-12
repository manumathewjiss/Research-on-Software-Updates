"""Allows `python -m releasetrain_sentiment` as an alternative to the
`releasetrain-sentiment` console script (e.g. when the scripts directory
isn't on PATH)."""

from .cli import main

if __name__ == "__main__":
    raise SystemExit(main())
