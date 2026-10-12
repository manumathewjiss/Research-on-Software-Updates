# Phase 3 experiment_v1 protocol (frozen before reserved-test scoring)

**Frozen:** 2026-10-07  
**Based on:** `DATA_AUDIT.md`, `MANIFEST.json`, `results/development_exclusions.json`  
**Rule:** Do not change this protocol after looking at reserved-test model scores.

---

## 1. Population and target

| Item | Setting |
|------|---------|
| Population | Rows with `s2_in_scope=true` (software update discussions) |
| Positive class | `s2_target=1` (`discussion_type=technical_troubleshooting`) |
| Negative class | `s2_target=0` (other update discussion: `other` + `general_dissatisfaction`) |
| Negative wording | Never call all negatives “dissatisfaction” |
| Three-way type | Kept for breakdowns only, not primary training target |

## 2. Included / excluded IDs

### Included development

All `development.jsonl` rows with `s2_in_scope=true`, **except** the additional near-duplicate exclusions below.

Package already removed exact reserved copies: `1u3zzcs`, `1so7xen`.

### Additional development exclusions (this protocol)

| reddit_id | study_id | reason |
|-----------|----------|--------|
| `1t0wme9` | `C2-18544D2C491B` | near-duplicate of reserved `1t0wr91` (sim 0.9838) |
| `1wrqch6` | `C2-53269BF08151` | near-duplicate of reserved `1wrqmip` (sim 0.9487) |

Exclusion rule: Jaccard ≥ 0.92 on character 5-grams of normalized title+body vs any reserved S2 post. Reserved rows are never excluded.

### Included reserved test

All `reserved_test.jsonl` rows with `s2_in_scope=true` (n=159). Unchanged.

Expected S2 development after exclusions: 2084 (2086 − 2).

## 3. Text fields

| Setting | Fields |
|---------|--------|
| `title` | `title` only |
| `title_body` | `title` + newline + `post_body` (empty body allowed) |
| Not used in primary models | `discussion_context`, IDs, subreddit, timestamps, audit fields, labels |

Preprocessing for classical models: lowercase; optional URL stripping inside the vectorizer tokenizer / analyzer as implemented in `run_experiment.py`. Vectorizer **fit only on each training fold**.

## 4. Forbidden features

Never use as predictors: `reddit_id`, `study_id`, `source_pool_audit_only`, `review_status_audit_only`, `subreddit`, `created_utc`, `text_availability`, `about_software`, `update_related`, `discussion_type`, or any proposal/label metadata beyond the training target.

## 5. Validation scheme (development only)

- Stratified 5-fold CV on eligible S2 development rows  
- `random_state=42`  
- Stratify on `s2_target`  
- Same fold assignment for all models / text settings  
- Out-of-fold predictions saved for model choice  

Source-aware stress: after choosing the model, also report OOF metrics by `source_pool_audit_only` (analysis only).

## 6. Models

1. **Majority** — always predict the majority class in the training fold (troubleshooting).  
2. **Keyword** — predict troubleshooting if title/body matches a fixed troubleshooting-cue regex (transparent baseline; not trained).  
3. **TF-IDF + Logistic Regression** — word unigrams+bigrams, `min_df=2`, `sublinear_tf=True`, `max_features=20000`, class-balanced LR.  
4. **TF-IDF + Linear SVM** — same TF-IDF, `LinearSVC` with class weight balanced; decision scores via `decision_function`.

Each model runs under both `title` and `title_body`.

Light tuning on development OOF only:

- LR: `C ∈ {0.25, 1.0, 4.0}`  
- SVM: `C ∈ {0.25, 1.0, 4.0}`  

Choose `C` by highest OOF **macro-F1**; break ties by troubleshooting F1, then troubleshooting recall.

## 7. Metrics

Primary selection metric: **macro-F1** (OOF).

Also report: accuracy, balanced accuracy, precision/recall/F1 for both classes, confusion matrix, class supports, precision@10 and precision@20 among highest troubleshooting scores, average precision (PR-AUC) when scores exist. Bootstrap 95% CI on OOF macro-F1 and troubleshooting F1 (1000 resamples, seed 42). Breakdowns by source pool and text availability.

## 8. Final model selection and threshold

1. Select the best (model, text setting, C) by OOF macro-F1.  
2. Default decision threshold: 0.5 for probabilistic models; 0 for SVM decision_function. Optional threshold sweep on OOF is allowed **before** reserved test if needed to maximize macro-F1; record the chosen threshold.  
3. Refit the chosen pipeline on **all** eligible development rows.  
4. Evaluate **once** on eligible reserved-test S2 rows.

## 9. Seeds and environment

- Global seed: `42`  
- Python venv: `phase3/experiment_v1/.venv`  
- Record `pip freeze` into `results/environment.txt` at run time  

## 10. Reserved-test rule

After this protocol and the chosen configuration are written, reserved-test labels may be used for the single final evaluation only. No retuning, model switching, or protocol edits based on those scores. If a flaw is found, mark the result exploratory and require a new untouched test set for a confirmatory claim.

## 11. Label-quality note

`results/label_quality_flags.jsonl` lists heuristic concerns for Manu. This experiment proceeds with existing labels; it does not apply auto-corrections. Serious systematic problems would pause confirmatory claims.
