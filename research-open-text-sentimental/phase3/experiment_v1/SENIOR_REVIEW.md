# Review of experiment_v1 (2026-10-07)

## What the saved run supports

The saved protocol preceded the run, the model was chosen using development out-of-fold (OOF) predictions, and the reserved test was scored once in the saved code. The reported reserved confusion matrix `[[18,6],[5,130]]` gives macro-F1 0.863 and troubleshooting F1 0.959 for 159 already-scoped posts. This is encouraging evidence for this collected, reviewed corpus. The 24 reserved negative examples make the negative-class estimate uncertain. Labels have mixed provenance; the reserved labels were jointly decided, not independently blinded.

The comparison with majority and keyword baselines is on **development**, not on the reserved test. Say that explicitly. The reserved test checks the chosen model's performance; it is not a reserved-test demonstration of a baseline gap.

## Important validation issue

The original Cursor task asked for duplicate groups to stay together, but the frozen protocol and `run_experiment.py` use `StratifiedKFold` on individual rows. In the 2,084 eligible development records, there are 25 exact normalized title+body duplicate groups (52 rows). Twenty groups (42 rows) are split across folds under the saved seed. A model may therefore train on the same text it is asked to predict in another fold. The OOF macro-F1 of 0.841 may be optimistic. This does not establish leakage into the reserved test, whose exact and detected near-duplicate development copies were removed.

One three-post exact-text group has conflicting labels: `1wxl2u9` and `1wxl3ma` are marked other update, while `1wxl35m` is marked troubleshooting. These should be adjudicated from the saved post text and the labeling guide; do not silently choose a label by majority vote. There may be other near-duplicate groups within development.

## Next work before manuscript results

1. Have Manu review the 48 heuristic label flags and the three conflicting duplicate records. Record keep/change/uncertain decisions with reasons. Flags are suggestions, not proof of mistakes. Do not overwrite the original review files.
2. Run **development-only** grouped validation with exact and sensible near-duplicate groups kept in one fold. Keep the v1 model, threshold, and reserved-test results as the original record. A grouped validation is a sensitivity check; do not use it to change the already tested model and then reuse the same reserved test as if untouched.
3. Report development metrics by source pool and title/body availability, and compare the corrected validation result with v1. If results change substantially or many labels flip, treat the existing reserved-test result as exploratory and design a new untouched evaluation set for a confirmatory claim.
4. Only then decide whether to add the information-completeness secondary study and begin the manuscript rewrite.

No new model family or sentiment experiment is needed to close these immediate issues.
