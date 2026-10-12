# Fresh test: fixed model result

**Status:** complete one-time evaluation of the previously fixed classifier. The test labels were frozen before scoring in `frozen_joint_labels/freeze_manifest.json`. Raw predictions and full numeric results are in `results_fixed_model/`. The corrected workbooks are the authoritative input. The user reports that Manu and Professor Berhe wrote the labels together, so this is a **joint review** and there is no independent agreement statistic.

## Test population

- A broad API query returned 3,718 update-related **candidates**, not confirmed update posts. After overlap and duplicate exclusions, 864 were new to this study; 500 were sampled without consulting classifier scores.
- Joint review found 344 posts that were both software-related and update-related: 277 troubleshooting and 67 other update discussion. The 67 other-update posts are a small comparison class. These posts have new Reddit IDs relative to the earlier corpus, but many were written before October 2026; this is an unseen-ID test, not wholly prospective collection.
- The classifier was given the human-established S2 scope. These results do not measure an automatic scope detector.

## Fixed configuration

Title plus body; TF-IDF word unigrams and bigrams; logistic regression with class weights balanced, `C=4`, and the saved decision threshold `0.5877137791150834`. The model was fitted on the revised 2,080-post development set (1,686 troubleshooting, 394 other update). No choice was changed using the fresh test.

## Main result

| Measure | Fixed model | Majority baseline | Fixed keyword baseline |
|---|---:|---:|---:|
| Macro-F1 | **0.792** | 0.446 | 0.474 |
| Troubleshooting F1 | **0.916** | 0.892 | 0.552 |
| Other-update F1 | **0.667** | 0.000 | 0.396 |

The fixed model's confusion matrix, with rows as true class and columns as predicted class, is:

| True class | Predicted other update | Predicted troubleshooting |
|---|---:|---:|
| Other update (67) | 46 | 21 |
| Troubleshooting (277) | 25 | 252 |

Accuracy is 0.866 and balanced accuracy is 0.798. A 1,000-resample bootstrap gives a 95% interval of **0.731–0.845** for macro-F1; other-update F1 is **0.562–0.755** and troubleshooting F1 is **0.891–0.940**. These intervals describe sampling uncertainty conditional on the study's labels and collection process; they do not incorporate annotation uncertainty.

The fresh-test macro-F1 is lower than the revised development grouped validation result of 0.835 and the earlier 159-post reserved result of 0.863. The three sets differ in source, labels, and composition, so this is evidence of limited transfer, not a controlled estimate of why the score changed.

## Subgroups and errors

- The title-and-body subgroup has 338 posts and macro-F1 0.793. Only six fresh-test posts are title-only, so their macro-F1 0.667 is too unstable for a firm test-set conclusion.
- Fifty-four test posts were published in October 2026 (14 other, 40 troubleshooting); their macro-F1 is 0.807. The remaining 290 posts have macro-F1 0.787. These small and unequal subgroups do not establish a time trend.
- Twenty-one other-update posts were predicted troubleshooting. Some include technical terms, upgrade questions, or strongly worded product criticism. Twenty-five troubleshooting posts were missed; some describe UI changes, brief symptoms, or update effects without familiar troubleshooting cues. These are descriptive observations from the saved error list, not a complete taxonomy of all 46 errors.

## Interpretation

The fixed text model carries useful signal for this reviewed, API-collected S2 population and exceeds both simple baselines. The comparison class remains harder: its F1 is 0.667 with 67 examples. The strongest safe claim is about screening **already identified software-update discussions** in this collected corpus. The result cannot be described as Reddit-wide prevalence, fully automatic update discovery, or independent two-reviewer validation.

No extra test posts are required to report this result with its limits. Additional human review would be needed only for a new, explicitly stronger claim (for example, independent annotation reliability or a fully prospective test); it should not be added after observing scores to make the current test look better.
