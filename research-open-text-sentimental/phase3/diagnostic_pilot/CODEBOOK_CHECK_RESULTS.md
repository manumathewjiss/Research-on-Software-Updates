# Revised codebook: 15-post check

**Status (2026-10-07):** Manu's completed workbook is archived unchanged in `submissions/2026-10-07-manu-codebook-check/`. The 15 masked IDs, saved titles/bodies, allowed answers, and required notes were validated. Blank post bodies round-tripped as blank spreadsheet cells. The first 50-post workbook and all Phase 2 labels remain unchanged.

This is a deliberately selected check of difficult cases from the first 50 posts. It is **not** a fresh 15-post sample, a prevalence estimate, independent agreement, or a within-reviewer consistency measure. The rules changed between the two passes.

## Results

- Troubleshooting check: 13 yes, one no, one unclear. The earlier `unclear` for `D20261007-050` became yes (`C20261007-005`); the earlier no for `D20261007-031` and unclear for `D20261007-039` remained so. These are review flags, not automatic corrections to the study dataset.
- Among the 13 yes posts: identifiable release 7 present / 6 not observed; reproduction context 10 present / 3 not observed; attempted remedy 7 present / 6 not observed. Other field counts are available in `answers.json`.
- The new release field avoided using `unclear` as a synonym for an unnamed update in these 13 cases. Two boundary judgments still need a written rule: `C20261007-007` calls “Win 11 update” an identifiable release, although no patch/version is named; `C20261007-003` uses an uncertain February-or-March update cycle as a dated release.
- `C20261007-005` has an inaccessible screenshot and was marked troubleshooting yes from its text. Keep the missing visual evidence separate from whether the text itself establishes a concrete symptom.

## Gate before scaling

Clarify the `identifiable_release` rule for a named OS plus unnamed update and for broad or uncertain update cycles. Then freeze a versioned guide. Draw a new probability-based diagnostic sample from the eligible Reddit-only S2 troubleshooting development population; the enriched 50-post pilot should not be used to estimate field prevalence. The planned main sample is roughly 200–300 **new** posts, with its final size based on desired precision and sampling strata. A separate fresh, untouched classification test is also still planned; the current design targets roughly 250 in-scope posts and may require screening more candidates.

Paper framing, related work, dataset provenance, and existing model methods can be drafted now. Final diagnostic distributions and confirmatory model claims must await those two studies.
