# Development error counts for the inner-threshold title+body model

Primary predictions are `pred_title_body` in `phase5/expanded_study/results/predictions.jsonl`. That field is the grouped inner-threshold title+body model. Its macro-F1 on the 2,050 development posts is **0.8319320360990539**.

This replaces the earlier count that used `y_pred_tfidf_lr` from `phase3/reddit_only_sensitivity/results/grouped_oof_predictions.jsonl`. That older field uses the continuity threshold 0.5877137791150834 and has macro-F1 **0.8363107912443574**. Those older counts are only in `SENSITIVITY_APPENDIX.md` and `sensitivity_continuity_threshold.json`.

Confusion matrix for `pred_title_body`, rows true other-update then troubleshooting:

|  | predicted other | predicted troubleshooting |
| --- | ---: | ---: |
| other update (392) | 289 | 103 |
| troubleshooting (1,658) | 112 | 1,546 |

False positives are 103/392 other-update posts (0.263). False negatives are 112/1,658 troubleshooting posts (0.068). No post text and no identifiers are stored in the count files.

Slices use the development snapshot for body, source pool, subreddit, and text. Class mix differs across slices, so a higher error rate in one slice is not a cause.

## Empty body

303 posts have an empty body: 177 other-update and 126 troubleshooting.

| body | n | FP / other | FN / troubleshooting |
| --- | ---: | --- | --- |
| empty | 303 | 17/177 (0.096) | 40/126 (0.317) |
| present | 1,747 | 86/215 (0.400) | 72/1,532 (0.047) |

## Source pool

The pool name is the stored collection route, not a gold label.

| pool | n | other / troubleshooting | FP / other | FN / troubleshooting |
| --- | ---: | --- | --- | --- |
| oct5_query_tps | 1,561 | 163 / 1,398 | 66/163 | 71/1,398 |
| oct5_query_gds | 289 | 66 / 223 | 27/66 | 32/223 |
| phase1_gold_file | 200 | 163 / 37 | 10/163 | 9/37 |

## Length

Character length is the stored title, a newline, and the stored body. Bins were fixed before the rates were computed.

| characters | n | other / troubleshooting | FP / other | FN / troubleshooting |
| --- | ---: | --- | --- | --- |
| 0–100 | 281 | 158 / 123 | 15/158 | 39/123 |
| 101–300 | 331 | 66 / 265 | 23/66 | 23/265 |
| 301–800 | 754 | 53 / 701 | 25/53 | 25/701 |
| 801+ | 684 | 115 / 569 | 40/115 | 25/569 |

## Lexical cues

Incident and discontent word lists are the frozen descriptive lists. They are not causes.

| cue cell | n | other / troubleshooting | FP / other | FN / troubleshooting |
| --- | ---: | --- | --- | --- |
| incident only | 1,249 | 125 / 1,124 | 44/125 | 55/1,124 |
| discontent only | 46 | 13 / 33 | 3/13 | 3/33 |
| both lists | 164 | 30 / 134 | 15/30 | 5/134 |
| neither list | 591 | 224 / 367 | 41/224 | 49/367 |

## Subreddit

22 communities have at least 20 posts. The other 94 communities are 275 posts: TN 80, FP 10, FN 19, TP 166.

Android is 64 other-update and 1 troubleshooting (FP 4, FN 1). applehelp is 3 other-update and 193 troubleshooting (FP 3, FN 1). Those mixes dominate the community rates.

Full cells are in `counts.json`.
