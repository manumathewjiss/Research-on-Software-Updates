# Fresh-test errors: bounded manuscript evidence

**Status:** exploratory single-analyst synthesis of already saved predictions and provisional codes. This is not the prospective blinded 92-post review specified in `ERROR_REVIEW_GUIDE.md`; that completion criterion remains unmet. No labels, predictions, threshold, or test scores were changed.

## Verified numerical result

The frozen fresh S2 test contains 344 posts: 298 correct predictions and 46 errors. Of the errors, 25 are troubleshooting posts predicted as other update discussion (false negatives); 21 are other update posts predicted as troubleshooting (false positives). Fourteen of 46 errors lie within 0.05 of the fixed threshold, compared with four of 46 selected matched correct posts. These selected groups do not establish that moving the threshold would improve the model. Source: `phase3/fresh_test_20261007/saved_error_analysis/README.md`, `all_46_errors.csv`, `matched_correct_examples.csv`, and `summary.json`.

## Exploratory reading, not a validated taxonomy

The saved provisional analyst codes assign six of 25 misses to specific malfunction descriptions, three to update-installation trouble, three to brief malfunction reports, three to resolved incident narratives, and three to configuration help. Among 21 false alarms, five ask for preventive update advice and four observe a feature or change. These are descriptions of a deliberately selected error set, not population rates or causal explanations. Source: `phase3/fresh_test_20261007/saved_error_analysis/provisional_error_codes.csv` and `provisional_coding_summary.json`.

Concrete examples show the boundary. One missed post describes a panel that cannot be resized after a Plasma upgrade (`T20261007-027`); another is a short report of screen glitches (`T20261007-102`). A false alarm asks about preventive firmware-updating advice (`T20261007-074`), and another observes smoother tab behavior (`T20261007-245`). Paraphrases reflect the saved title/body and should be checked against those records before publication. The matched correct posts show overlapping surface cues, so the examples should not be described as a discovered mechanism of model failure.

Twenty-two of the 46 errors were flagged by the analyst as possible task-boundary cases, **not confirmed wrong labels**. A newly added but apparently missing feature (`T20261007-181`) and missing cumulative updates after a management-system migration (`T20261007-473`) illustrate why discussion purpose can be arguable. The test labels stay frozen. Any later re-review must be reported separately and cannot silently replace this evaluation.

## Safe manuscript wording

> On the 344-post fresh test, the fixed classifier made 46 errors (25 missed troubleshooting posts and 21 false alarms). An exploratory reading of those errors found both concrete malfunction descriptions among misses and preventive update advice or feature observations among false alarms. Matched correct examples shared several of these surface cues. Thus, the error cases illustrate the limits of simple lexical interpretations; the qualitative codes were not independently validated and do not establish why the model made a given prediction.

## Still open

The 92-row blind error/control coding in `ERROR_REVIEW_GUIDE.md` was not completed. It is optional for a bounded paper if the exploratory status above is explicit. The 250-post diagnostic-field sample was drawn from development posts, so its fields cannot be used as measured explanations for fresh-test errors. The fresh test has only six title-only posts, too few for a stable title-only subgroup claim.
