# Sentiment reanalysis results

**Created:** 2026-10-09T21:17:26.664964+00:00
**Code version:** `sentiment-reanalysis-v1`

Verified on the saved development folds. The 159-row reserved test and the 344-row fresh test were not read or scored. Phase 1 files, labels, Phase 3 outputs, the manuscript, and Overleaf were not modified.

## Question

Does VADER compound sentiment from the saved title and body add useful information beyond the frozen TF-IDF logistic regression for troubleshooting versus other update discussion?

## Primary population

Reddit-URL S2 development rows and exact grouped outer folds from phase3/reddit_only_sensitivity n=2050: 1658 troubleshooting and 392 other update. Five grouped outer folds. TF-IDF uses word unigrams and bigrams, `min_df=2`, `max_features=20000`, `sublinear_tf`, logistic regression `C=4`, `class_weight='balanced'`, `liblinear`.

The reproduced text scores match the saved grouped out-of-fold scores within 0.000e+00 (tolerance 1e-06). Fixed-threshold prediction mismatches: 0.

VADER is one compound score of the raw title and body. Empty text returns 0.0. Empty title: 0. Empty body: 303. Both empty: 0. Exact-zero compounds, including genuine neutral text: 237. Mean compound is -0.0644 on troubleshooting and 0.1941 on other update. No comments, source, community, identifiers, timestamps, or review fields enter the classifier. The historical keyword-first VADER rule is not used.

The compound is standardized inside each training fold. Inner thresholds use three grouped folds of the outer training split only, on the grid 0.20 through 0.80 by 0.05. The selection rule is mean inner macro-F1, then mean inner other-update F1, then proximity to 0.50. Outer labels are not used to choose cutoffs.

## Primary scores

| Arm | macro-F1 | other P/R/F1 | trouble P/R/F1 | balanced acc. | confusion [[0,1]] |
|---|---:|---|---|---:|---|
| Text, saved threshold 0.5877137791150834 | 0.8363 | 0.725/0.747/0.736 | 0.940/0.933/0.936 | 0.8403 | `[[293, 99], [111, 1547]]` |
| Text, inner threshold | 0.8319 | 0.721/0.737/0.729 | 0.938/0.932/0.935 | 0.8348 | `[[289, 103], [112, 1546]]` |
| VADER compound only, inner threshold | 0.5335 | 0.246/0.245/0.245 | 0.822/0.822/0.822 | 0.5335 | `[[96, 296], [295, 1363]]` |
| Text plus VADER, inner threshold | 0.8331 | 0.733/0.727/0.730 | 0.936/0.937/0.936 | 0.8322 | `[[285, 107], [104, 1554]]` |
| Majority on the same folds | 0.4471 | 0.000/0.000/0.000 | 0.809/1.000/0.894 | 0.5000 | `[[0, 392], [0, 1658]]` |

Fair paired difference, hybrid minus text: macro-F1 **+0.0012** (95% bootstrap interval -0.0115 to +0.0146; includes zero: True). Other-update F1 **+0.0010** (-0.0199 to +0.0226; includes zero: True). Troubleshooting F1 **+0.0014** (-0.0039 to +0.0070; includes zero: True). Bootstrap: 1000 post-level resamples, seed 42.

A positive point estimate whose interval includes zero is not counted as an improvement.

Prediction changes between inner-threshold text and hybrid: **82**. Counts by change and true class: `{"hybrid_corrects_text_error_y1": 29, "hybrid_corrects_text_error_y0": 14, "hybrid_adds_error_y1": 21, "hybrid_adds_error_y0": 18}`. Titles in `results/reddit_2050/changed_errors.jsonl` are illustrations, not validated explanations.

Supplementary threshold-free average precision for troubleshooting: text 0.9819, sentiment-only 0.8642, hybrid 0.9792. This is not a second model-selection result.

## Smaller class

Other-update support is 392. Inner-threshold text F1 is 0.7289 (precision 0.721, recall 0.737). Hybrid F1 is 0.7298 (precision 0.733, recall 0.727). Sentiment-only F1 is 0.2452.

## Mixed-source sensitivity

Revised S2 development snapshot, near-duplicate IDs 1t0wme9 and 1wrqch6 excluded, saved diagnostic grouped folds. Includes 30 so_ records with conflicting source metadata. n=2080: 1686 troubleshooting and 394 other update. Conflicting-source `so_` records included: 30 (class counts {"1": 28, "0": 2}).

Reproduced text scores match the saved mixed grouped scores within 0.000e+00. Fixed-threshold mismatches: 0.

| Arm | macro-F1 | other P/R/F1 | trouble P/R/F1 | balanced acc. | confusion [[0,1]] |
|---|---:|---|---|---:|---|
| Text, saved threshold | 0.8347 | 0.709/0.761/0.734 | 0.943/0.927/0.935 | 0.8442 | `[[300, 94], [123, 1563]]` |
| Text, inner threshold | 0.8353 | 0.715/0.756/0.735 | 0.942/0.929/0.936 | 0.8429 | `[[298, 96], [119, 1567]]` |
| VADER compound only, inner threshold | 0.5356 | 0.243/0.279/0.260 | 0.826/0.797/0.811 | 0.5382 | `[[110, 284], [342, 1344]]` |
| Text plus VADER, inner threshold | 0.8362 | 0.744/0.723/0.734 | 0.936/0.942/0.939 | 0.8326 | `[[285, 109], [98, 1588]]` |
| Majority | 0.4477 | 0.000/0.000/0.000 | 0.811/1.000/0.895 | 0.5000 | `[[0, 394], [0, 1686]]` |

Hybrid minus text macro-F1 **+0.0009** (95% interval -0.0142 to +0.0151; includes zero: True). Other-update F1 **-0.0013** (-0.0254 to +0.0222; includes zero: True). This sensitivity is separate from the Reddit-URL primary result.

## Historical 542-post author/community check

This section uses the Phase 1 trajectory code and the saved C1′ table. It is not merged into the 2,050-row classifier. Comments are not available as a complete field for that classifier population, and the historical labels are the old TPS/GDS gold labels.

Recomputed trajectory metrics for 542 posts. Mismatches against `c1_prime_metrics.csv` at rounding tolerance 0.0005: **0**. Title-only author fallback: **205** (24 historical TPS, 181 historical GDS). Body present and no author comment: **38**. Mean author-comment count, excluding the title fallback: 1.4926.

On the 542 labeled posts, stored comments cover 0.5935 of the recorded `num_comments` field (10416 stored / 17549 recorded; 396 posts short). Empty comment bodies: 0.

Full raw pools, matching the Phase 2 coverage definition: TPS stored/recorded = 0.5521 (56 of 74 posts short); GDS stored/recorded = 0.5947 (368 of 500 posts short).

Saved full-set means: author 0.0091 vs 0.1911 (Welch p 4.71754e-05); community 0.1683 vs 0.1940 (Welch p 0.331788); absolute divergence 0.3710 vs 0.2872 (asymptotic Mann-Whitney p 0.00922073). Author-more-negative rates 0.6977 vs 0.5373.

Title-only author tracks (24 TPS / 181 GDS): divergence 0.3664 vs 0.2651, asymptotic Mann-Whitney p 0.076635.

Author tracks with a body or author comment (62 TPS / 275 GDS): divergence 0.3727 vs 0.3018, asymptotic Mann-Whitney p 0.0597802. Author means in that subset: 0.0769 vs 0.2607.

Author slope Welch p 0.274128; author early-versus-late Welch p 0.425444. Community slope Welch p 0.0832853 (asymptotic Mann-Whitney p 0.0261275). Author slope and author early-versus-late shift do not differ between the historical classes. A cumulative sentiment plot is not treated as evidence of change over time.

The published full-corpus report remains the historical reference for the rounded Table II figures. These recomputed tests use the saved metric columns and an asymptotic Mann-Whitney test. They do not create a current-label result.

## Recommendation

Hybrid minus text macro-F1 is +0.0012 and the 95% interval (-0.0115 to +0.0146) includes zero, so title-and-body VADER does not add a reliable gain. Sentiment-only macro-F1 is 0.5335, well below the text model at 0.8319. Retain the current paper without a new claim that this sentiment feature improves troubleshooting detection. This run does not edit the paper.

**Choice:** `retain_current_paper_without_new_sentiment_claims`.

No manuscript file was edited and no submission claim is made.

## Limitations

- Development out-of-fold scores are not a held-out test estimate.
- The other-update class is much smaller than the troubleshooting class.
- VADER's zero value mixes empty text and neutral text.
- Inner threshold selection uses development labels inside the outer training split. It does not use the outer fold.
- The 542-post analysis depends on partial stored comment threads and a title fallback.

## Files

- `results/reddit_2050/pooled_metrics.json`
- `results/reddit_2050/pooled_predictions.jsonl`
- `results/reddit_2050/fold_<k>_metrics.json` and `fold_<k>_predictions.jsonl`
- `results/mixed_2080/` with the same layout
- `results/historical_542_audit.json`
- `MANIFEST.json`
