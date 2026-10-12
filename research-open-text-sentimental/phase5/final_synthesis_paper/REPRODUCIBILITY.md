# Reproducibility guide

This file is internal and unpublished. The manuscript does not contain a data-availability section and does not cite https://github.com/SE4CPS/Research-on-Software-Updates. Phase 2 through phase 5 files used for the draft are local. They are not publicly archived. This guide does not promise copies on request.

Related local notes, also unpublished: `FIGURE_SOURCES.md`, `SUPPLEMENTARY_APPENDIX.md`, and `WHY_THIS_PAPER_IS_STRONGER.md`. The file `overleaf_upload.zip` is a manuscript bundle only.

## Compile

From `phase5/final_synthesis_paper/`:

`/opt/homebrew/bin/tectonic -X compile main.tex`

Figures are TikZ inside `main.tex`. No external figure file is required. Do not refit models or rescore the reserved or fresh tests. The development title-and-body score 0.8319320360990539 is the inner-threshold result in `phase5/expanded_study/results/reproduction_title_body.json`. The continuity-threshold score 0.8363107912443574 is a different prediction field and is not the number in the manuscript.

## Saved inputs

Paths are relative to `research-open-text-sentimental/`.

- Reserved text-only macro-F1 0.8626835204522258, quoted 0.863: `phase3/icsc_full_paper/RESULT_VERSION_RECONCILIATION.json`.
- Fresh text-only macro-F1 0.7915151515151515, quoted 0.792; majority 0.44605475040257647; fixed keyword 0.47390158551864175: `phase3/fresh_test_20261007/results_fixed_model/metrics.json`.
- Development ablation and sentiment arms, including title 0.750534, body 0.781424, VADER 0.533519/0.833130, TextBlob 0.552128/0.834445, contextual 0.783792/0.835524, and MiniLM 0.847561: `phase5/expanded_study/results/metrics_table.csv`.
- Group intervals for those arms: `phase5/expanded_study/results/group_bootstrap.json`. Augmented sentiment intervals and the MiniLM interval include zero. Title-only and body-only intervals do not.
- Matched title-only and body-only VADER additions: `phase5/final_improvement/results/metrics_table.csv`; paired duplicate-group intervals: `phase5/final_improvement/results/matched_vader_group_ci.json`. The matching scripts are `phase5/final_improvement/run_phase_a.py` and `phase5/final_improvement/matched_vader_ci.py`.
- The official SentiStrength-SE v1.5 ZIP from `https://laser.cs.uno.edu/resources/ProjectData/SentiStrength-SE_v1.5.zip` has SHA-256 `b3244714dc82381833ae55c4722e0e7dcc5dc1522353f65bbb937a9e2d9daaa9`. Its packaged JAR and `ConfigFiles` lexicon were used by `phase5/final_improvement/run_se_sentiment.py`; the saved scores, grouped out-of-fold predictions, settings, and interval are in `phase5/final_improvement/results/sentistrength_se_*`. This is a developer-domain sentiment tool applied without Reddit-specific sentiment gold labels.
- The exploratory 68-post dissatisfaction comparison between VADER and SentiStrength-SE is calculated by `phase5/final_improvement/analyse_se_sentiment_groups.py` and saved in `phase5/final_improvement/results/sentistrength_se_subgroup.json`. It was examined after the tool comparison and does not select any model or threshold.
- The five-fold coefficient recurrence used for the term figure: `phase5/final_improvement/results/fold_coefficients.json`. These are training-fold associations, not local or causal explanations.
- The completed software-engineering-specific sentiment comparison and the fine-tuned RoBERTa protocol are recorded in `phase5/final_improvement/FINAL_RESEARCH_IMPROVEMENT_REPORT.md`. RoBERTa configuration, five fold records, predictions, and grouped interval are in `phase5/final_improvement/results/task2_config.json`, `task2_summary.json`, and `roberta_predictions.jsonl`. Its development macro-F1 is 0.839113 against 0.831932 for the matched text baseline; the paired interval for the difference includes zero. No protected test was scored for this arm.
- Inner-threshold confusion TN 289, FP 103, FN 112, TP 1546, and the 303 empty-body denominators: `phase5/expanded_study/error_analysis/counts.json`.
- Public paraphrases used in the paper: `phase5/expanded_study/error_analysis/PUBLIC_CASE_TABLE.md`. The manuscript does not include post identifiers.
- Earlier VADER-only development file, same title-and-body pair: `phase5/sentiment_paper/results/stage_a_title_body.json`.
- Earlier group bootstrap for the VADER pair: `phase5/sentiment_paper/manuscript/analysis/group_bootstrap.json`.
- Discussion-type means: `phase5/sentiment_paper/manuscript/analysis/valence_by_discussion_type.json`.
- Diagnostic field counts and the body split: `phase3/diagnostic_results/analysis.json` (`conditional_field_rates`; `body_missing_n` 24 of 250; `by_body.title_only.n` 20; reproduction present 2 of 20 and 106 of 217).
- Thirty-case selection: `phase4/qualitative_study/ANALYST_ONLY_CASE_SELECTION.csv`. Six of the 30 main-case identifiers also appear in the 237 diagnostic rows.
- Figure-to-field map: `FIGURE_SOURCES.md`.

## Test URL check

Reserved S2 rows (159) are in `phase2/combined_dataset/master_records.json` and all have `reddit.com` URLs. Fresh S2 rows (344) are absent from that collection; their URLs in `phase3/fresh_test_20261007/raw/` are also `reddit.com`. Neither scored test includes the 30 non-Reddit URL records.
