# Expanded development study

Development-only comparisons on the frozen 2,050 Reddit-URL rows. This directory does not edit the manuscript and does not rescore the reserved or fresh tests.

## How to read the outputs

- `RESULTS.md` — scores, intervals, truncation, and what was not tested.
- `MANIFEST.md` and `MANIFEST.json` — package versions and snapshot pointers.
- `results/metrics_table.csv` — one row per arm, with post-level paired intervals.
- `results/predictions.jsonl` — one row per development post, including `reddit_id`. Keep this file internal.
- `results/group_bootstrap.json` — group intervals from those saved predictions. Script: `group_bootstrap_saved.py`.
- `error_analysis/RESULTS.md` — error slices for `pred_title_body` (macro-F1 0.8319320360990539).
- `error_analysis/SENSITIVITY_APPENDIX.md` — older continuity-threshold counts (macro-F1 0.8363107912443574).
- `LITERATURE_NOTE.md` — Cassee 2024 and Wang 2026 for a later rewrite. The current manuscript cites neither.

## Run that produced the model outputs

`run_expanded.py` finished 2026-10-10 01:01:45 UTC. Reproduction passed before the other arms were interpreted. Do not rerun it to refresh this note; the JSON files are the record.

Python 3.14.7 and scikit-learn 1.9.1 come from `phase3/experiment_v1/.venv`. VADER 3.3.2 is the vendored package under `phase5/sentiment_reanalysis/vendor`. TextBlob 0.20.1 and NLTK 3.10.3 are under `vendor/` here. Contextual scoring used torch 2.14.1 and transformers 5.19.0. MiniLM encoding used sentence-transformers 6.1.0.

## Prediction fields

`pred_title_body` is the reproduced inner-threshold text model. `pred_title` and `pred_body` are the ablation. Sentiment-only and title+body-plus-score fields exist for VADER, TextBlob, and the contextual RoBERTa. `pred_minilm` is the frozen embedding head. `y_true` is the development troubleshooting label, not a sentiment label.
