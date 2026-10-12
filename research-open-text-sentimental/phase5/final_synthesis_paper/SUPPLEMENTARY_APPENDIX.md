# Supplementary appendix

Internal notes for review. This file is not part of the compiled manuscript and is not in the Overleaf ZIP. It repeats saved denominators and comparisons. It does not add a model, a score, or a causal claim.

## Populations not repeated as new results

- Combined collection: 3,362 records in `phase2/combined_dataset/master_records.json`. This is not a verified-Reddit census.
- Primary sentiment and purpose development: 2,050 Reddit-URL rows. The development slice also contains 30 non-Reddit URL records (28 troubleshooting, 2 other update). Those 30 have no stored comment and are excluded from the primary scores.
- Reserved file: 200 rows, all `reddit.com`. Scored S2 subset: 159 (135 troubleshooting, 24 other update).
- Fresh S2 file: 344 (277 troubleshooting, 67 other update), outside the 3,362 collection, all `reddit.com`.
- Secondary cohort: 542 rows inside the collection, with assigned labels 86 technical problem statements and 456 general dissatisfaction. Not pooled with the 2,050 task.

## Development text baselines on the same 2,050 posts

From `phase5/sentiment_paper/results/stage_c_development_models.json`. These are text comparisons, not sentiment gains.

| Comparison | Macro-F1 |
| --- | ---: |
| Logistic regression, inner threshold | 0.8319320360990539 |
| Linear SVM, same TF–IDF, default margin | 0.8203397212543554 |
| Keyword-first heuristic | 0.6847478991596638 |
| Naive Bayes, not class-balanced | 0.5512380235530256 |

Naive Bayes confusion on classes `[other update, troubleshooting]` is `[[43, 349], [0, 1658]]`. The fixed-threshold continuity macro-F1 often stored near 0.8363 is a different cutoff from the inner-threshold 0.8319 used for the VADER comparison. Do not substitute one for the other.

Fresh text-only baselines from `phase3/fresh_test_20261007/results_fixed_model/metrics.json`: majority macro-F1 0.44605475040257647; fixed keyword 0.47390158551864175; model 0.7915151515151515. Other-update F1 on that test is 0.6666666666666666. Reserved other-update F1 is 0.7659574468085106.

## Sentiment intervals

Title/body on 2,050, hybrid minus text: point +0.0011980545326599756. Post-level 95% interval −0.011518135801304513 to +0.01458336073276919. Duplicate-group interval −0.012563484358767363 to +0.01537774769958068 (`phase5/sentiment_paper/manuscript/analysis/group_bootstrap.json`, 1,000 resamples, seed 42, 2,016 groups, 32 multi-post groups covering 66 posts). Both intervals include zero.

Full thread on 797 posts: text macro-F1 0.8659 versus same text plus sentiment columns 0.8390. Difference −0.026828994614003676. Group interval −0.05147666973972438 to −0.0048932408920277694, which excludes zero. That subset has 790 groups and only 7 multi-post groups (14 posts). Both-role coverage on the 2,050 posts is 466 (22.7%), below the predeclared 50% bar. The lower score is subset-limited and retrospective. It is not a general claim that sentiment features harm classification.

A comparison that puts comment-derived sentiment next to title/body text, without putting the comment text in both models, is not an identifying test and is not used as evidence in the paper.

On the 1,726-post troubleshooting-versus-dissatisfaction pair, text macro-F1 is 0.658 and the compound changes it by +0.0104; that interval includes zero. Mean compounds are −0.0644 and −0.0680.

Empty title/body facts on the 2,050 posts: 303 empty bodies and 237 exact-zero compounds. VADER returns 0.0 for an empty document.

## Comment coverage

Nonempty stored comments: 797 of 2,050 (560 troubleshooting, 237 other update). No stored comment: 1,098 of 1,658 troubleshooting and 155 of 392 other update. Author replies: 362 and 112. Community comments: 554 and 235. Both roles: 356 and 110.

## Diagnostic extras

From `analysis.json`. Of 250 sampled posts, 24 had no saved body; 20 of those 24 were confirmed troubleshooting (`by_body.title_only.n` 20) and 217 had a body. Reproduction context is present in 2 of 20 and 106 of 217. Attempted remedy is present in 2 of 20 and 116 of 217. Mean present fields among the 237 is 4.84 of eight. Grouped development predictions joined to these 237 posts show 16 misses: 8 of 20 title-only and 8 of 217 with a body. That join uses development predictions only. Fields were not coded on the fresh test.

Closed word lists on the 2,050 posts, fixed before counting, are descriptive. Incident terms occur in 1,258 of 1,658 troubleshooting posts and 154 of 392 other-update posts. Discontent-only cells are 33 and 13 posts. This is not a masking experiment.

## Thirty cases

Same first action in 21 of 30; different in 9. Both chose investigation in 10, clarification in 6, monitoring in 1, and no update-focused action in 4. One reader selected investigation 16 times and the other 11; monitoring was selected 5 times and 1 time. Six main-case identifiers also appear in the 237. Pilot cases are excluded. Counts are not a population rate and were not crossed with VADER.

## Not comparable, and not for the manuscript

A saved BERT run (`tps_gds_classification/outputs/bert/metrics.json`) fine-tunes `bert-base-uncased` on `text_raw` after undersampling the 542-post label system to 261 rows (86 and 175), then evaluates 40 rows. Test macro-F1 is 0.6354166666666667. That is a different label system, a different split, and a different model from the fresh text-only score 0.792. The two numbers are not a comparison.

A separate 324-post automated-sentiment file is a third sample with its own comment-count filter. It is neither the 542-row secondary cohort nor the 2,050-row development set. Its scores are not comparable to the purpose-test scores above.

## Limits already binding the paper

No independent gold for the full collection. No field-level agreement for the 237. No resolution labels. Comment snapshots are partial. Class proportions are not prevalence. One lexicon was prespecified. The fresh and reserved scores are separate fits. No analysis connects valence, purpose, diagnostic fields, and first action as one pipeline.
