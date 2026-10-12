# Proposed independent annotation reliability study

**Status: both 200-post workbooks returned and archived as reported independent first passes. Manu confirmed that neither reviewer discussed answers or saw the other sheet before both files were saved.** See `reliability_packet/submissions/2026-10-07-independent/AGREEMENT.md` and `INTAKE_RESULTS.md`. The blank packet and original completed workbooks remain preserved. The files cannot independently verify the review sequence or exclude earlier familiarity with some development posts.

## Question

Can two trained reviewers independently apply the current scope, discussion-type, and diagnostic-detail definitions consistently on held-out development records?

## Sample and exclusions

- **Drawn:** 200 posts from the audited Reddit-only development snapshot using seed `ICSC-RELIABILITY-20261007-v1`. The sample excludes all 200 reserved, all 500 fresh-test, all 250 earlier diagnostic-sample, and all 30 Stack Overflow development records. Reproduce with `build_reliability_sample.py`; see `reliability_packet/MANIFEST.json`.
- Stratified using previous labels **only for selection**: exactly 80 S2 troubleshooting, 60 S2 other update, 40 software/non-update, and 20 outside software. Source pools were cycled within each stratum, yielding 67 TPS-pool, 68 GDS-pool, and 65 Phase 1 records. Stratum and source pool are hidden from reviewers.
- The sample is intentionally balanced toward difficult classes. Do not estimate corpus prevalence from its unweighted class counts.
- The selected sample intentionally avoids all 250 prior diagnostic cases. Thus field agreement is measured on different development posts, not a reannotation of those 237 retained cases.

## Workflow

1. **Done:** `reliability_packet/REVIEWER_GUIDE.md` version 1.0 has synthetic examples and the A022/A049 boundary; its hash is in the manifest.
2. **Done:** Reviewer A and B have separate XLSX files with identical ID/title/body/reply inputs and empty answer fields. Source pool, previous labels/reasons, diagnostic fields, model scores/predictions, and the other reviewer's answers are hidden. The analyst mapping is outside the reviewer packet.
3. **User-reported done:** both reviewers labeled separately and submitted first-pass files without discussing or seeing each other's answers beforehand. Earlier exposure to sampled posts was not individually recorded.
4. For every post, fill `about_software`, `update_related`, `discussion_type`, `confidence`, and a brief reason. Fill the eight diagnostic-detail fields for posts the reviewer considers troubleshooting. Mark a field `not_observed` only relative to the saved title/body; use `unclear` when the text is insufficient.
5. **Done:** agreement was computed from the archived first-pass files before any reported discussion. There were no categorical or diagnostic disagreements, so no adjudication file is required. Preserve both first-pass files exactly as received.

## Reporting

- For each main field: exact agreement, a confusion table, and Cohen's kappa. Include `unclear` as a category. The submitted answers are perfectly identical, so a bootstrap of observed pairs would give a degenerate interval that does not establish perfect future agreement; no such interval is reported. The raw tables permit excluding mutually unclear cases if needed.
- For each diagnostic field: positive and negative counts, agreement, kappa, and unclear counts. A rare field may yield an unstable kappa; give raw counts and avoid one overall diagnostic agreement score.
- Report disagreements by source/body stratum descriptively. Do not compare annotator scores with model scores until agreement is frozen.
- Report consensus/adjudication separately. A 100% final-consensus rate is not independent agreement.
- If Manu is a reviewer after earlier labeling work, report that prior exposure. A new independent pass relative to another reviewer does not erase earlier familiarity with the corpus.

## Completion criterion

This study is complete for the submitted sample: the sampling manifest, two original first-pass files, pre-discussion agreement analysis, and limitations text are saved. No adjudication file is needed because no categorical or diagnostic disagreement was submitted. Agreement measures consistency between these two reviewers on this selected set; it does not establish label correctness or Reddit-wide reliability.
