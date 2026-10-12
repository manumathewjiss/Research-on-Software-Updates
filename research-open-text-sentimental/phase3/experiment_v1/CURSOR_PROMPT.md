# Cursor task: run the Phase 3 baseline experiment

Work in `/Users/manumathewjiss/Documents/Research-on-Software-Updates/research-open-text-sentimental/`. Read `AGENTS.md` if present, `phase3/STATUS_AND_EVALUATION_PLAN.md`, this prompt, and `phase3/experiment_v1/MANIFEST.json`. Preserve Phase 1 and Phase 2 files; write all new code and results under `phase3/experiment_v1/`. Check Git status first. The two JSONL files in `phase3/experiment_v1/data/` are the experiment input. Do not rebuild them or silently change labels.

## Research question

Within software-update discussions, can post text identify **technical troubleshooting**? Use only rows where `s2_in_scope=true`. Target is `s2_target`: 1 means `technical_troubleshooting`, 0 means **other update discussion**. The negative class includes `other` and `general_dissatisfaction`; never describe all negatives as dissatisfaction. Preserve the three-way `discussion_type` for breakdowns only.

## Before training: data and leakage audit

1. Verify SHA-256 hashes and row counts against `MANIFEST.json`. Check unique IDs, missing title/body, class balance, scope consistency, and label distribution by `source_pool_audit_only` and `review_status_audit_only`. Report the real collection and labeling provenance. `source_pool_audit_only` is a collection route, not a label.
2. Check exact and near-duplicate **post text** between development and reserved test, including title-only similarity. The package already excludes two exact development copies of test posts. Report the similarity method, threshold, manual examples, and any further development IDs to exclude. Never remove or edit reserved-test rows. If you find plausible near duplicates, exclude their development copies under a documented rule before model fitting.
3. Make a bounded label-quality spot check on development records across source pools, review statuses, and predicted classes, but **do not relabel posts yourself or claim human corrections**. Flag questionable records in a separate CSV/JSONL for Manu to adjudicate. If serious systematic label problems appear, report them and pause the final test evaluation; continue with development-only diagnostics.
4. Write `DATA_AUDIT.md` and freeze a protocol in `PROTOCOL.md`: exact included/excluded IDs, text fields, target, split method, models, tuning grid, metric definitions, seeds, and chosen final evaluation procedure. Do this before reading reserved-test labels for performance or selecting a model. The reserved-test file may be used now only to detect text overlap and verify structural counts/hashes.

## Training and model selection: development only

1. Use a fixed, reproducible stratified development validation scheme. Keep duplicate or near-duplicate groups together. Consider source-aware validation as a stress test because collection source and label are strongly related. All preprocessing and vectorizer fitting must occur inside each training fold.
2. Compare at least: majority-class baseline, a transparent keyword baseline, TF-IDF word or character features plus logistic regression, and one other simple classifier such as linear SVM or Naive Bayes. Evaluate `title` only and `title + post_body` separately. Do not use `discussion_context` in the primary models. A later separate experiment may use it, with missing-comment availability reported.
3. Never feed `reddit_id`, `study_id`, `source_pool_audit_only`, `review_status_audit_only`, `subreddit`, `created_utc`, `text_availability`, `about_software`, `update_related`, `discussion_type`, or any label/proposal metadata as predictive features. For this first experiment, assume the S2 population is already selected; measuring the scope detector is a separate task.
4. Report confusion matrices and precision, recall, F1 for both classes, macro-F1, balanced accuracy, and precision among the top 10 and 20 scored troubleshooting posts. If probabilities are available, report average precision/PR-AUC and calibration cautiously. Include class supports and compare source pools/text availability. The reserved set is heavily troubleshooting-heavy, so raw accuracy and top-k precision alone are misleading.
5. Choose the final model and decision threshold using development data only. Save seeds, dependencies, parameters, out-of-fold predictions, and a machine-readable result table. Include uncertainty estimates appropriate to the sample size and do not claim statistically meaningful gains from tiny differences.

## One final reserved-test evaluation

Once `PROTOCOL.md` and the final choice are fixed, fit the chosen pipeline on all eligible development rows and evaluate once on eligible S2 reserved-test rows. Save the predictions with IDs, gold label, score, and prediction under `results/`. Report all metrics and the confusion matrix. Do not tune, switch models, change thresholds, or rewrite the protocol in response to reserved-test results. If you discover a flaw, record the result as exploratory and explain why a new untouched test set would be needed for a confirmatory claim.

## Deliverables

- `DATA_AUDIT.md`, `PROTOCOL.md`, and `RESULTS.md` in `phase3/experiment_v1/`.
- Reproducible training/evaluation code and a short `RUN.md` with exact commands.
- Machine-readable validation and reserved-test predictions, model settings, and package versions under `results/`.
- A brief `QUESTIONS_FOR_MANU.md` only for decisions that cannot be resolved from the files, especially questionable labels.

End with a plain-English verdict: what the classifier can currently support, where it fails, whether it improves on simple baselines, and what needs human review before the manuscript is rewritten. Do not fabricate human agreement, independent labels, model scores, or conference acceptance likelihood. Do not start a new sentiment or clustering study in this run.
