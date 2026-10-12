# Sensitivity appendix: continuity-threshold predictions

This appendix is not the primary error analysis.

`y_pred_tfidf_lr` in `phase3/reddit_only_sensitivity/results/grouped_oof_predictions.jsonl` uses the continuity threshold 0.5877137791150834. On the same 2,050 posts its macro-F1 is **0.8363107912443574**.

|  | predicted other | predicted troubleshooting |
| --- | ---: | ---: |
| other update (392) | 293 | 99 |
| troubleshooting (1,658) | 111 | 1,547 |

Compared with the primary inner-threshold field `pred_title_body` (TN 289, FP 103, FN 112, TP 1,546), this older field has 4 fewer false positives and 1 fewer false negative. The two scores must stay separate: 0.83631 is not the reproduced inner-threshold score 0.8319320360990539.

The same slice definitions are stored in `sensitivity_continuity_threshold.json`. Do not quote those cells as the current error analysis.
