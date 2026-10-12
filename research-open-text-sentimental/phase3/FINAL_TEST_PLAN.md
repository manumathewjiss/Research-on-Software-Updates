# Next task: fresh confirmatory test

Status: design proposal, 2026-10-07. No new test posts have been collected or labeled yet.

## Locked development version

`revised_development_v2/development_v2.jsonl` is the new development snapshot. It preserves the original experiment and applies Manu's two label corrections while excluding four uncertain posts. After the two previously identified near-duplicate exclusions, the S2 development set has 2,080 posts: 1,686 troubleshooting and 394 other update discussion. The exact input and output hashes are in `revised_development_v2/MANIFEST.json`.

Keep the final model specification fixed: title plus body TF-IDF logistic regression, `C=4`, class weighting and preprocessing as in experiment_v1, with the saved probability threshold `0.5877137791150834`. Train on the revised development set only after the new test protocol is locked. Do not use old reserved-test performance to change this specification.

## Build a genuinely new test set

1. Collect a new, dated snapshot of Reddit posts that was not in the 3,362-post Phase 2 master or the earlier 200-post reserved set. Prefer a later collection period and multiple software communities. Record the query or source, retrieval date, Reddit ID, post date, title, body, and missing-text status. Professor Berhe's API may supply **candidate posts**, never labels. Add a broader update-discussion query or independently sampled update posts so the new test is not just troubleshooting-keyword hits.
2. Deduplicate by Reddit ID and inspect exact and near-duplicate title+body overlap against all existing development and old reserved posts. Exclude repeats from the new test before labeling. Record counts and IDs.
3. Sample without consulting model predictions. Aim for roughly **250 in-scope software-update posts**, including at least **75 other-update posts** so that the minority class can be assessed. If extra negative candidates are deliberately sampled, record the sampling strata and do not present resulting class proportions as Reddit prevalence. Keep an unsampled collection manifest to show what was eligible.
4. Give Manu and Professor Berhe the same task guide and **separate blind sheets**. Each independently records `about_software`, `update_related`, and `discussion_type` from the saved text. Do not show API pool, old labels, model suggestions, model scores, or the other person's answers. Record initial agreement. Then discuss disagreements and save a separate adjudicated label file. Mark insufficient-text cases uncertain; do not force them into a class.
5. After labels, exclusions, and model specification are frozen, score the new S2 test **once**. Report both class precision/recall/F1, macro-F1, confusion matrix, uncertainty intervals, and breakdowns by source and text availability. Keep the old reserved-test result as a separate historical result; do not blend it with this test or call it newly untouched.

## Immediate division of work

- **Codex / Cursor:** set up collection and deduplication scripts, manifests, blank blind review sheets, and validation checks. No labels or predictions in reviewer sheets.
- **Manu and Professor Berhe:** independently label the new test candidates and resolve disagreements after initial sheets are saved.
- **Codex:** check agreement, lock the test file, review the one-shot evaluation, and decide what the manuscript can claim.

Do not start a new sentiment or clustering experiment until this confirmatory classification result is settled.
