#!/usr/bin/env python3
"""Score the frozen Reddit development set with official SentiStrength-SE v1.5.

The university-hosted distribution is external; pass the unpacked directory
explicitly. This script never reads reserved or fresh tests. The two signed
strengths are added to form one polarity score, matching the treatment in the
SA4SE replication package. An augmented arm uses the saved nested grouped
protocol and fits every scaler/vectorizer only on the outer training data.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

import numpy as np
from sklearn.metrics import f1_score

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
sys.path.insert(0, str(REPO / "phase5" / "expanded_study"))
import run_expanded as ex  # noqa: E402

OUT = HERE / "results"
SAVED = REPO / "phase5" / "expanded_study" / "results" / "predictions.jsonl"
EXPECTED_N = 2050
EXPECTED_BASE = 0.8319320360990539
OFFICIAL_URL = "https://laser.cs.uno.edu/resources/ProjectData/SentiStrength-SE_v1.5.zip"
ZIP_SHA256 = "b3244714dc82381833ae55c4722e0e7dcc5dc1522353f65bbb937a9e2d9daaa9"


def one_line(s: str) -> str:
    """The original executable scores one document per line."""
    return re.sub(r"[\t\r\n]+", " ", s).strip() or " "


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--distribution", type=Path, required=True)
    parser.add_argument("--java", type=Path, required=True)
    args = parser.parse_args()
    jar = args.distribution / "SentiStrength-SE_V1.5.jar"
    lexicon = args.distribution / "ConfigFiles"
    if not jar.is_file() or not (lexicon / "EmotionLookupTable.txt").is_file():
        raise SystemExit("official JAR or dictionary missing")
    if not args.java.is_file():
        raise SystemExit("Java executable missing")
    rows, y, folds, groups, population = ex.load_population()
    if len(rows) != EXPECTED_N:
        raise SystemExit(f"population changed: {len(rows)}")
    saved = ex.read_jsonl(SAVED)
    if [r["reddit_id"] for r in saved] != [r["reddit_id"] for r in rows]:
        raise SystemExit("saved baseline does not match population order")
    base = np.array([int(r["pred_title_body"]) for r in saved])
    if abs(f1_score(y, base, average="macro") - EXPECTED_BASE) > 1e-12:
        raise SystemExit("saved baseline score changed")
    texts = [ex.input_text(r, "title_body") for r in rows]
    # Sentiment tools see the raw title/body, as VADER does. TF--IDF retains
    # its locked URL-stripped, lowercase text cleaning inside ex.input_text.
    input_lines = [one_line(ex.raw_document(r)) for r in rows]
    cmd = [
        str(args.java), "-cp", str(jar), "uk.ac.wlv.sentistrength.SentiStrength",
        "sentidata", str(lexicon) + "/", "stdin", "UTF8",
        # Match the shipped GUI's default settings for these exposed options.
        "maxWordsBeforeSentimentToNegate", "5",
        "negatedWordStrengthMultiplier", "1", "mood", "1", "noDictionary",
    ]
    result = subprocess.run(
        cmd, input="\n".join(input_lines) + "\n", text=True,
        capture_output=True, timeout=180, cwd=args.distribution,
    )
    if result.returncode != 0:
        raise SystemExit(f"SentiStrength-SE failed: {result.stderr[:1000]}")
    outputs = result.stdout.splitlines()
    if len(outputs) != EXPECTED_N:
        raise SystemExit(f"sentiment output count mismatch: {len(outputs)}")
    pairs = np.empty((EXPECTED_N, 2), dtype=int)
    for i, line in enumerate(outputs):
        parts = line.strip().split()
        if len(parts) != 2:
            raise SystemExit(f"unexpected output at row {i}: {line[:100]!r}")
        pairs[i] = [int(parts[0]), int(parts[1])]
    if not np.all((pairs[:, 0] >= 1) & (pairs[:, 0] <= 5) & (pairs[:, 1] <= -1) & (pairs[:, 1] >= -5)):
        raise SystemExit("out-of-range sentiment strength")
    scores = pairs.sum(axis=1).astype(float)
    pred_only, proba_only, thr_only, seconds_only = ex.oof_sentiment(scores, y, folds, groups)
    pred_aug, proba_aug, thr_aug, seconds_aug = ex.oof_hybrid(texts, scores, y, folds, groups)

    # Reuse the already audited grouped paired-resampling implementation.
    import run_phase_a as phase_a
    interval = phase_a.group_interval(y, base, pred_aug, groups)
    records = [{
        "reddit_id": row["reddit_id"], "fold": int(folds[i]),
        "group_id": int(groups[i]), "y_true": int(y[i]),
        "positive_strength": int(pairs[i, 0]),
        "negative_strength": int(pairs[i, 1]), "polarity_sum": float(scores[i]),
        "pred_se_only": int(pred_only[i]), "pred_text_plus_se": int(pred_aug[i]),
        "pred_title_body": int(base[i]),
    } for i, row in enumerate(rows)]
    OUT.mkdir(parents=True, exist_ok=True)
    ex.write_jsonl(OUT / "sentistrength_se_predictions.jsonl", records)
    ex.write_json(OUT / "sentistrength_se_metrics.json", {
        "source_url": OFFICIAL_URL,
        "distribution_zip_sha256": ZIP_SHA256,
        "jar_sha256": hashlib.sha256(jar.read_bytes()).hexdigest(),
        "population": population,
        "input": "raw title+body in the saved row order, as in VADER; embedded newlines/tabs replaced by spaces for one-line scorer; TF-IDF retains its locked cleaning",
        "score": "positive strength plus negative strength, one scalar feature",
        "command_options": cmd[4:],
        "se_only": ex.metrics_at(y, pred_only),
        "text_plus_se": ex.metrics_at(y, pred_aug),
        "text_baseline_macro_f1": EXPECTED_BASE,
        "group_bootstrap_minus_text": interval,
        "thresholds_se_only": thr_only,
        "thresholds_augmented": thr_aug,
        "seconds_se_only": seconds_only,
        "seconds_augmented": seconds_aug,
        "protected_tests_opened": False,
    })
    print(json.dumps({
        "n": len(rows),
        "se_only_macro_f1": ex.metrics_at(y, pred_only)["macro_f1"],
        "aug_macro_f1": ex.metrics_at(y, pred_aug)["macro_f1"],
        "group_ci": interval["ci95"],
    }), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
