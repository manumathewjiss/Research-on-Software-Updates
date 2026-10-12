# Class-balancing comparison (Reddit-only development)

**Created:** 2026-10-08T02:16:11.011416+00:00
**Code version:** `balancing-study-v1`

Development check only. The 159-post reserved test and the 344-post fresh test were not read or scored.

## Population and folds

Reddit-only S2 modeling set from `reddit_only_sensitivity/development_reddit_only.jsonl`: **2050** posts, **1658** troubleshooting and **392** other update.

All three arms use the five grouped folds already saved in `reddit_only_sensitivity/results/grouped_oof_predictions.jsonl`. Exact and near-duplicate posts stay in the same fold. TF-IDF is fit on each fold's original training posts. Oversampling, when used, copies minority training rows after that fit and does not change the held-out posts.

The balanced arm agrees with the saved Reddit-only predictions on **1.0000** of posts (max absolute score gap 0.000e+00).

## Fixed threshold `0.5877137791150834`

This is the threshold saved with the original balanced model. It is applied here to every arm so the comparison is not mixed with a new cutoff.

| Arm | macro-F1 | balanced acc. | other P/R/F1 | trouble P/R/F1 | confusion [[0,1]] |
|---|---:|---:|---|---|---|
| Balanced class weights | 0.8363 | 0.8403 | 0.725/0.747/0.736 | 0.940/0.933/0.936 | `[[293, 99], [111, 1547]]` |
| No class weights | 0.7644 | 0.7172 | 0.897/0.446/0.596 | 0.883/0.988/0.933 | `[[175, 217], [20, 1638]]` |
| Random oversampling, no class weights | 0.8382 | 0.8313 | 0.757/0.717/0.737 | 0.934/0.946/0.940 | `[[281, 111], [90, 1568]]` |

Paired bootstrap of macro-F1 difference versus balanced weights (1,000 resamples):

- Unweighted − balanced: -0.0719 (95% CI -0.0980 to -0.0472; includes zero: False)
- Oversample − balanced: +0.0019 (95% CI -0.0066 to +0.0112; includes zero: True)

## Threshold exploration (development only)

A quantile search maximized out-of-fold macro-F1 separately for each arm. These cutoffs were **not** applied to either scored test and are not a replacement final model.

| Arm | Explored threshold | macro-F1 | balanced acc. | other F1 | trouble F1 |
|---|---:|---:|---:|---:|---:|
| Balanced | 0.4964 | 0.8381 | 0.8108 | 0.7314 | 0.9447 |
| Unweighted | 0.7081 | 0.8381 | 0.8108 | 0.7314 | 0.9447 |
| Oversample | 0.5762 | 0.8394 | 0.8286 | 0.7377 | 0.9412 |

## Tradeoff

Class weights and oversampling shift probability mass toward the smaller other-update class. At the saved threshold, dropping weights raises other-update precision and cuts its recall sharply, which lowers macro-F1. Oversampling stays close to class weights, with a small swap of other-update precision and recall. The saved cutoff was chosen for the balanced model, so the exploration block is the fairer comparison of each arm at its own operating point. After that search, the three arms are nearly the same.

## Recommendation

Keep the existing balanced-weight model and the saved threshold. At that cutoff, dropping class weights lowers macro-F1 by 0.072, mainly by missing other-update posts. That gap is large, but it is a cutoff mismatch: after each arm's own development threshold, macro-F1 differs by at most 0.001. Oversampling versus class weights is +0.002 at the saved cutoff, and that paired interval includes zero. Those differences are not large enough to replace the current configuration or to spend a new test set. This comparison was not scored on the reserved or fresh tests.

## Reproduce

```bash
phase3/experiment_v1/.venv/bin/python phase3/balancing_study/run_balancing_study.py
```

Hashes and settings: `MANIFEST.json`.
