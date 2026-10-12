# Final research improvement record

This directory contains development-only experiments added after the protected
reserved and fresh evaluations were frozen. It must not be used to retune on
either protected test set.

## Population and protocol

- `phase3/reddit_only_sensitivity/development_reddit_only.jsonl` and its saved
  grouped out-of-fold fold IDs define the 2,050 Reddit-URL development rows
  (1,658 troubleshooting, 392 other update; 2,016 duplicate groups).
- `phase5/expanded_study/results/predictions.jsonl` supplies the previously
  saved title-only, body-only, and title-and-body comparisons with thresholds
  selected inside outer training folds.
- `run_phase_a.py` scores VADER on exactly the text seen by the respective
  title-only or body-only arm. It also records TF--IDF training-fold
  coefficients. `matched_vader_ci.py` computes paired duplicate-group
  intervals against the matching text arms.
- `run_task2_roberta.py` is the predeclared fine-tuned RoBERTa comparison.
  One inner grouped split within each outer training fold chooses epoch count
  and threshold. A fresh model is then fit on the full outer training fold.
  The script has a one-fold smoke mode and five-fold mode. A one-fold result is
  a feasibility check, not a model comparison. The five-fold run uses the
  cached `roberta-base` revision `e2da8e2f811d1448a5b465c236feacd80ffbac7b`,
  seed 42, batch size 8, learning rate `2e-5`, and a 256-token limit. The
  limit truncates 442 of 2,050 development posts.

## Current results

The matched VADER arms have development macro-F1 0.750843 (title) and
0.786073 (body), versus 0.750534 and 0.781424 for the matching text-only
arms. Their paired group intervals for the increments include zero. The
title-and-body plus VADER arm reproduces the earlier 0.833130 result against
0.831932 for title and body alone.

The official SentiStrength-SE v1.5 distribution was downloaded from the
authors' laboratory and scored on all 2,050 development posts with the same
grouped, nested-threshold protocol. Its signed positive-plus-negative
strength alone scores 0.464797 macro-F1; added to title/body text it scores
0.834083 versus 0.831932 for text, a grouped interval for the increment of
−0.004188 to +0.008859. The sentiment tool sees raw title and body (embedded
line breaks replaced by spaces); TF--IDF retains its locked cleaned text.
Inputs, checksums, predictions, and group interval
are in `run_se_sentiment.py` and `results/sentistrength_se_*`. The official
`pySenti4SD` repository was inspected at commit
`5ed11f1f9bf42c113db064278fe7decaf07587c4`. Its pretrained Java and
distributional semantic files are tracked in DVC, including an 835,369,209
byte `dsm.bin` with DVC MD5 `395cb470cacd6e584508d108945b67d3`.
The bounded DVC pull did not materialize those files. The corpus has no
independent sentiment gold labels, and no Senti4SD result is claimed.

The full five-fold RoBERTa development comparison is saved in
`results/task2_summary.json` and `results/roberta_predictions.jsonl`:
macro-F1 0.839113 versus 0.831932 for the matched TF--IDF model. The
duplicate-group paired 95% interval for the +0.007181 difference is
−0.015974 to +0.028589, which includes zero. RoBERTa's other-update recall is
lower (0.709 versus 0.737). Neither protected test was scored for this arm.

## Reproduction

1. Use a fresh Python environment with versions recorded by the experiment.
2. Run `run_phase_a.py`, then `matched_vader_ci.py` on development only.
   The SentiStrength-SE result requires the official v1.5 ZIP (SHA-256
   `b3244714dc82381833ae55c4722e0e7dcc5dc1522353f65bbb937a9e2d9daaa9`),
   Java, and `run_se_sentiment.py` pointing at its unpacked folder. Its
   bundled JAR and dictionary are not committed to this research repo.
3. For RoBERTa, run `run_task2_roberta.py --smoke` before considering
   `--all-folds`. Keep the exact cached base-model revision, seed, and saved
   fold IDs. Do not use the reserved or fresh test labels for model selection.
4. Read the final report for task-by-task status and interpretive limits.

The repository's `phase5/final_synthesis_paper/` contains the manuscript. The
baseline before this improvement stage is preserved as `baseline_main.tex`
here. No data or saved protected-test predictions were changed.
