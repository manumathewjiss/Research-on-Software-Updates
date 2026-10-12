# Analysis plan for the 120-post single-review check

## Purpose

Compare one new blind review with the earlier recorded Phase 2 decisions. This is a consistency and boundary audit. The earlier records have mixed review provenance, so the comparison is **not** independent inter-annotator agreement and should not be described as Manu-versus-Berhe agreement or as intra-rater reliability.

## Before opening answers

- The sample and prior-label mapping are frozen in `sampling_manifest.json` and `ANALYST_ONLY_MAPPING.json`.
- The reviewer sees only the blind workbook and `REVIEW_GUIDE.md`; no previous labels, source pool, model score, or prediction.
- The 120 rows are deliberately stratified by earlier labels (50 troubleshooting, 30 other update, 20 software non-update, 20 nonsoftware). These are **sample quotas**, not class prevalence.

## After receiving the completed workbook

1. Verify exactly 120 unique `audit_id` values and no altered title/body/context values. Validate allowed answers and record any blanks. Keep the original completed workbook intact.
2. Compare the new answers with the earlier record separately for `about_software`, `update_related`, and `discussion_type`. Report raw agreement counts and a confusion table for each field. Report the same within each sampling stratum, with denominators. Do not pool the three fields into one impressive number.
3. List every disagreement with blind ID and both answers for author inspection. Do not overwrite either review. Distinguish clear rule conflicts, thin saved text, and source/context differences. For a small, jointly discussed adjudication set, save a **third** final decision record instead of silently replacing a prior value.
4. If computing chance-corrected agreement, label it as agreement between a new review and the earlier *record* under stratified sampling. Do not call it independent two-rater reliability. Because the sample was deliberately balanced across old classes, do not extrapolate the resulting agreement rate to the natural corpus without sampling weights and uncertainty.
5. Report what the recheck supports and what remains unknown. A high match would strengthen confidence in the operational rule within this sample, but would not prove validity or independence for the full corpus.

No model training, threshold choice, or historical test-label change should use these answers until the audit is complete and documented.
