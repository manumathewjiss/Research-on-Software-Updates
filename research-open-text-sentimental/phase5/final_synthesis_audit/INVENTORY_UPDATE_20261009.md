# Inventory update, 9 October 2026

Status: inspection only. No model was fit. `main.tex` was not edited.

The 6-page compiled paper is frozen at `phase5/final_synthesis_paper/baseline_20261009/` (`main.tex` sha256 `e9dac64a20d27c449bc8a0be50ab4f1b08aa9a4b536bc44cc299b20111a32b0b`, `main.pdf` sha256 `c17a918724e3d5d0277bf9c3d213eea94a6b27b759cb2c8a24dfb36b45988f86`). Datasets, past experiment outputs, and the live `main.tex` were left in place.

This note treats the pasted expansion request as a wish list. Saved files are evidence. They are not instructions to rerun or to rewrite claims.

## What this inspection did not open

The prior inventory (`REPOSITORY_INVENTORY.md`) already counted generated environments. This pass did not recurse into them and did not re-read dependency files.

| Excluded tree | Files | Size | Why excluded |
| --- | ---: | ---: | --- |
| `phase3/experiment_v1/.venv` | 38,921 | 1,128 MB | Phase 3 sklearn environment |
| `tps_gds_classification/.venv` | 39,985 | 1,081 MB | Historical classification environment |
| `phase4/manuscript_icsc2027/.venv` | 4,540 | 183 MB | Manuscript rendering environment |
| `phase5/sentiment_reanalysis/vendor` | 219 | 4.3 MB | Vendored VADER 3.3.2 |
| Bytecode caches | about 49 | small | Generated `__pycache__` |

No `node_modules` and no notebooks were recorded in that inventory. BERT checkpoints under `tps_gds_classification/outputs/bert/` are research artifacts, not an environment, but they are about 3.07 GB of weights. They were not reloaded.

## Frozen evaluation rules for any later fit

Use only the 2,050 Reddit-URL development rows and the saved duplicate groups in `phase3/reddit_only_sensitivity/results/grouped_oof_predictions.jsonl`. Outer split: stratified group folds, 5, shuffle, seed 42, character five-gram Jaccard at least 0.92. Inner threshold: three grouped folds, seed 42, grid 0.20–0.80 step 0.05, chosen by mean inner macro-F1, then other-update F1, then closeness to 0.5. Outer labels never choose the cutoff. Vectorizer and scaler fit on the training fold only. Paired difference: augmented minus text, 1,000 bootstrap resamples, seed 42.

Do not rescore `reserved_test.jsonl` (159 S2 rows) or `s2_test_344.jsonl`. Do not attach sentiment to them. Do not use ReleaseTrain `metadata.predicted`, keyword features, candidate route, or precomputed API sentiment as predictors or as labels. The 30 non-Reddit URL records stay out of the primary set. The 542-row assigned labels stay a different task. The 324-post comment-filtered file stays a third sample.

A new development score must reproduce the saved title-and-body inner-threshold macro-F1 0.8319320360990539 before any added feature is interpreted. The fixed-threshold continuity score near 0.8363 is a different cutoff.

## Requested comparisons

| Request | Already saved? | Justified next? |
| --- | --- | --- |
| 1. More sentiment tools than VADER | No fair comparison on the 2,050 task. VADER compound versus the same title/body text is saved: 0.8319 versus 0.8331, interval includes zero (`stage_a_title_body.json`). Full-thread text versus the same thread plus VADER columns is lower on 797 posts. SentiStrength-SE is a citation, not a run. TextBlob, DistilBERT, RoBERTa, Cardiff Twitter RoBERTa, and BERTweet were not scored on this task. | One additional lexicon on the same 2,050 protocol is justified, because the paper currently speaks only for VADER. A seven-model sweep is not. Transformer sentiment models are justified only after the lexicon replication matches, and only on development folds. |
| 2. A modern classifier | Partial and not interchangeable. Frozen `all-MiniLM-L6-v2` plus logistic regression versus TF–IDF on **2,136** posts gives +0.0059 macro-F1, interval includes zero (`phase3/semantic_comparator/RESULTS.md`). Undersampled BERT macro-F1 0.635 is 40 rows of the 542-label task (`outputs/bert/metrics.json`). ModernBERT was considered in `phase4/expansion_investigation/EXPANSION_DECISION.md` and not trained. | Do not fine-tune ModernBERT, RoBERTa, DistilBERT, or DeBERTa for this paper. The fresh test is no longer an untouched selection target. The saved MiniLM result already says a frozen encoder does not reliably beat TF–IDF, but its population is 2,136 rather than 2,050. Recomputing that one frozen encoder on the exact 2,050 rows is the only justified classifier check. |
| 3. One coherent story | The current paper already states that tone, purpose, and first action are not interchangeable. No saved result joins them as one pipeline. | Do not invent a joint model. Writing can connect the existing blocks. A new experiment cannot create a pipeline result that was never measured. |
| 4. Practical workflow figure | Missing as an evaluated workflow. Figure 1 is a branch diagram and forbids a sentiment-to-action arrow. | A use sketch may be drawn later only if it is labeled unevaluated. It is not an experiment. |
| 5. Ablation: title, body, title+body, title+body+sentiment | The last cell exists (VADER on title+body). Title-only **subgroup** scores exist for posts that lack a body. They are not an input ablation. Examples: semantic comparator `title_only` n=135, macro-F1 0.691 on the 2,136 set; experiment follow-up `title_only` n=138. No saved body-only model. | Yes. This is the smallest new fit that answers where the purpose signal sits. Same 2,050 groups and rules. Reproduce 0.8319 on title+body first. |
| 6. Error analysis | Provisional analyst codes exist for 46 fresh-test errors (`provisional_error_codes.csv`): 25 misses and 21 false alarms. The planned 92-row blind review was not completed (`ERROR_REVIEW_GUIDE.md`). Codes were assigned after scores were known. | Do not run a new coder study in this sequence. The saved codes can be described later as provisional. They are not a new taxonomy and must not be retuned. |
| 7–9. Diagnostic discussion, discussion, figures | Counts for the 237 are saved. The 30-case explanations are saved. New figures were not drawn. | Writing and figure work, after any new numbers exist. No new field coding. |
| 10. SHAP, LIME, or feature importance | No research-owned SHAP or LIME result was found outside environment trees. | A short list of logistic-regression coefficients from the training folds of the reproduced TF–IDF model is enough. Do not run SHAP on the reserved or fresh tests. |
| 11. Literature 2023–2026 | The bibliography already has several 2023–2026 software-engineering papers. A new search was not done in this pass. | Search later. Do not add a citation that has not been opened. |

## Population conflict to leave unresolved

`semantic_comparator/RESULTS.md` uses 2,136 posts (1,733 troubleshooting, 403 other update). The primary Reddit-URL development set is 2,050 (1,658 and 392). The mixed development file is 2,080. These are not the same denominator. Do not quote the MiniLM table as a 2,050 result.

## Leakage risks if the wish list is run carelessly

- Scoring the reserved or fresh tests again, or choosing a transformer because of those scores.
- Putting comment sentiment beside title/body text while the comment words are only in one arm.
- Using the title as an author-comment fallback.
- Feeding diagnostic codes, reviewer actions, or candidate-route fields into the classifier.
- Treating the 542-row BERT score as a competitor to fresh macro-F1 0.792.
- Publishing verbatim post titles from the error file.
- Drawing a workflow arrow that implies sentiment causes an engineering action.

## Minimal sequence for Codex

Do these in order. Stop when a step fails its own check. Do not start the manuscript edit in the same step.

1. Confirm the baseline hashes above still match before writing any result file.
2. On the 2,050 rows only, fit title-only, body-only, and title+body under the frozen grouped protocol. The title+body macro-F1 must match 0.8319320360990539 within rounding before the other two cells are reported.
3. Add one lexicon score, TextBlob polarity, to that same title+body string. Use the saved VADER comparison as the template: one column, training-fold scaling, paired bootstrap. If the interval includes zero, stop the sentiment expansion.
4. Only if step 3 is done: rerun the already used frozen MiniLM encoder on these 2,050 rows, not on 2,136, with the same folds. Do not fine-tune it. If its paired interval includes zero, do not add ModernBERT, RoBERTa, DistilBERT, or DeBERTa.
5. From the reproduced title+body model, export the largest-magnitude coefficients by class. That is the explainability artifact. No SHAP.
6. Leave the fresh-test error codes, the 237 field table, the 30 cases, and both protected tests unchanged.

Anything else on the wish list is writing, a figure labeled unevaluated, or a later literature check. It is not part of this experiment sequence.
