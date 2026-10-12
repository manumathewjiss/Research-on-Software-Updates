# Semantic comparator result

**Created:** 2026-10-08T05:01:18.999031+00:00

This is one development comparison. It does not score the reserved or fresh tests, and it is not evidence of a new architecture or of independent generalization.

## Question and setup

Does a frozen `all-MiniLM-L6-v2` sentence embedding separate troubleshooting from other software-update discussion more reliably than the existing title-and-body TF-IDF logistic regression, on the audited Reddit-only development posts?

Population: **2136** posts, **1733** troubleshooting and **403** other update. Both models use the saved outer folds. Each outer training split chooses its own threshold from three inner grouped folds on the grid 0.20, 0.25, 0.30, 0.35, 0.40, 0.45, 0.50, 0.55, 0.60, 0.65, 0.70, 0.75, 0.80. The encoder is not fine-tuned. Semantic head: logistic regression `C=1`, class-balanced. TF-IDF head: `C=4`, class-balanced.

## Outer-fold result

| Model | macro-F1 | balanced acc. | other P/R/F1 | trouble P/R/F1 | confusion [[0,1]] |
|---|---:|---:|---|---|---|
| TF-IDF LR | 0.8385 | 0.8463 | 0.719/0.762/0.740 | 0.944/0.931/0.937 | `[[307, 96], [120, 1613]]` |
| MiniLM + LR | 0.8444 | 0.8353 | 0.773/0.720/0.746 | 0.936/0.951/0.943 | `[[290, 113], [85, 1648]]` |

Paired bootstrap, MiniLM minus TF-IDF, 1000 resamples: macro-F1 **+0.0059** (95% CI -0.0160 to +0.0292; includes zero: True). Other-update F1 **+0.0057** (95% CI -0.0305 to +0.0436).

The frozen MiniLM representation does not reliably beat the existing TF-IDF model on these development folds. The paired interval for the macro-F1 difference includes zero.

## Source pool and text availability

### Source pool

| Source | n | TF-IDF macro-F1 | MiniLM macro-F1 | TF-IDF other F1 | MiniLM other F1 |
|---|---:|---:|---:|---:|---:|
| oct5_query_gds | 289 | 0.750 | 0.806 | 0.618 | 0.690 |
| oct5_query_tps | 1644 | 0.779 | 0.796 | 0.606 | 0.637 |
| phase1_gold_file | 203 | 0.828 | 0.780 | 0.937 | 0.893 |

### Text availability

| Availability | n | TF-IDF macro-F1 | MiniLM macro-F1 |
|---|---:|---:|---:|
| title_and_body | 1165 | 0.795 | 0.813 |
| title_body_comments | 669 | 0.785 | 0.818 |
| title_only | 135 | 0.691 | 0.747 |
| title_plus_comments | 167 | 0.809 | 0.729 |

Outside the dominant TPS pool, MiniLM is higher on the GDS pool (289 posts) and lower on the Phase 1 pool (203 posts). That is not a consistent gain away from the main source.

## Truncation and cost

MiniLM keeps 256 word-pieces. **512 / 2136** posts (24.0%) are longer than that before truncation: 417 / 1733 troubleshooting (24.1%) and 95 / 403 other update (23.6%). Median length is 129 word-pieces.

CPU wall time 50s, of which encoding took 13s and the TF-IDF fits took 6s. Model revision `1110a243fdf4706b3f48f1d95db1a4f5529b4d41`.

The refit TF-IDF probabilities match the saved Reddit-only out-of-fold scores (max absolute gap 0.000e+00). Applying the historical 0.588 cutoff to those same scores gives macro-F1 0.843. The table above uses the inner-fold thresholds instead, so it is the fair comparison, not a reprint of that older cutoff.

## What this does not show

These folds reuse the audited development posts. A higher or lower development score is not a new test result. The reserved and fresh tests were not opened.

