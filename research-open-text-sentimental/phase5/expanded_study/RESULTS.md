# Development-only expansion results

All numbers below are from the finished run in `results/`. The models were not refit for this note. The population stayed the 2,050 Reddit-URL development posts, 1,658 troubleshooting and 392 other-update, on the saved grouped folds.

Reproduction of the title+body TF-IDF logistic regression with inner-fold thresholds passed: observed macro-F1 **0.8319320360990539**, absolute gap 0. Fold thresholds were 0.60, 0.55, 0.60, 0.55, 0.60.

No new arm was scored on the reserved 159 or fresh 344 tests. Sentiment scores have no independent gold labels on these posts. A sentiment-only arm is a classifier that sees only the sentiment number, not a check that the number matches a human sentiment judgment.

## Input ablation

Missing bodies stay empty. There are 303 empty bodies (177 other-update, 126 troubleshooting) and no empty titles.

| arm | macro-F1 | delta vs title+body | post-level 95% CI | group 95% CI |
| --- | ---: | ---: | --- | --- |
| title+body | 0.831932 |  |  |  |
| title only | 0.750534 | −0.081398 | [−0.106676, −0.055889] | [−0.107223, −0.056854] |
| body only | 0.781424 | −0.050508 | [−0.068454, −0.032205] | [−0.069097, −0.031893] |

Both title-only and body-only intervals exclude zero on both bootstrap definitions. Title and body each carry purpose signal, and neither replaces the other on this development set.

## Sentiment

| arm | macro-F1 | delta vs title+body | post-level 95% CI | group 95% CI | includes 0 |
| --- | ---: | ---: | --- | --- | --- |
| VADER only | 0.533519 | −0.298413 | [−0.328616, −0.265768] | [−0.330336, −0.266616] | no |
| title+body + VADER | 0.833130 | +0.001198 | [−0.011518, 0.014583] | [−0.012563, 0.015378] | yes |
| TextBlob only | 0.552128 | −0.279804 | [−0.311632, −0.248694] | [−0.312584, −0.248522] | no |
| title+body + TextBlob | 0.834445 | +0.002513 | [−0.008670, 0.014101] | [−0.008252, 0.015450] | yes |
| contextual only | 0.783792 | −0.048140 | [−0.076661, −0.020539] | [−0.078286, −0.017247] | no |
| title+body + contextual | 0.835524 | +0.003592 | [−0.020998, 0.026337] | [−0.021773, 0.027316] | yes |

Sentiment alone is below the text model. Adding any of the three scores to title+body changes macro-F1 by less than 0.004, and every paired interval includes zero. The group interval for title+body + VADER matches the earlier development group bootstrap for that same comparison.

The contextual model is frozen `cardiffnlp/twitter-roberta-base-sentiment-latest`. The score is P(positive) − P(negative). Neutral probability stays in the simplex and is not added. The cache `refs/main` at inspection time is snapshot `3216a57f2a0d9c45a2e6c20157c20c49fb4bf9c7`. The run did not pin a revision, so that hash is the cache main pointer, not a hash written into the run log.

**Truncation:** 188 of 2,050 texts have more than 512 tokens once special tokens are counted. Those 188 were truncated to 512 before the score was computed. The median length, including special tokens, is 134. No input was empty, so the empty-text score of 0.0 was unused. Truncation can drop later body text from the contextual score. It does not change the TF-IDF arms.

The loader reported unexpected `roberta.pooler.dense` weights. Transformers describes that as ignorable when the task head differs from the architecture that owned the pooler. The classification head is the sentiment head.

## Frozen MiniLM

`sentence-transformers/all-MiniLM-L6-v2`, snapshot `1110a243fdf4706b3f48f1d95db1a4f5529b4d41`, normalized 384-d embeddings, logistic regression head C=1, not fine-tuned. Macro-F1 **0.847561**. Delta versus title+body is **+0.015629**.

Post-level 95% interval: [−0.008995, 0.039023]. Group 95% interval: [−0.008604, 0.039266]. Both include zero. The point estimate is higher, and the development comparison does not establish a difference once resampling uncertainty is included. This is not the older MiniLM comparison on 2,136 posts.

## Error counts

Primary false-positive and false-negative slices for `pred_title_body` are in `error_analysis/RESULTS.md`. The continuity-threshold counts at macro-F1 0.83631 are only in `error_analysis/SENSITIVITY_APPENDIX.md`.

## Bootstrap definitions

`results/metrics_table.csv` intervals resample posts. `results/group_bootstrap.json` resamples the 2,016 saved `group_id` values with replacement and keeps every post in a drawn group together. There are 32 multi-post groups covering 66 posts. Both use 1,000 draws and seed 42, and both subtract the title+body prediction. Neither refits a model.

## What this file does not claim

Held-out tests were not read. There is no sentiment gold standard. Coefficients in `results/tfidf_coefficients.json` are associative weights from one development fit, not causes. The manuscript was not edited.
