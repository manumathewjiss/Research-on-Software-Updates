# Intake of completed 100-post pilot sheets

**Correction received:** Manu later supplied a different Berhe file and identified the initial one as the wrong file. The initial byte-identical Berhe file is preserved as `Berhe_Blind_Review_100_Posts_SUPERSEDED_DUPLICATE.csv`. The corrected `Berhe_Blind_Review_100_Posts.csv` differs from Manu's sheet in all 100 reason sentences and five field judgments. See `PILOT_AGREEMENT_RESULTS.md` for the agreement analysis. The initial-file warning below is retained as intake history, not as the status of the corrected pair.

Received 2026-10-06. The two submitted CSV files were copied here without edits. Both contain 100 rows and have all five judgment fields filled. Their pilot IDs and ordering match the original pilot.

## Provenance

Manu stated in this conversation that Manu and Professor Berhe reviewed the posts independently and each typed into a separate file. The submitted CSV files are nevertheless byte-for-byte identical, including all 100 free-text reason fields (SHA-256 `17a2fa5ba9cc92f4358974986a67e39a1e4bbafe2425f93622faaa5d5eb78f62`). This record can preserve the authors' statement, but the files alone cannot demonstrate separate independent judgments. A computed 100% agreement or Cohen's kappa of 1 would be a property of duplicate files, not independently verifiable rater agreement.

## Recorded labels

The two files have the same counts, so the following describes their shared contents rather than two separate distributions:

| Field | Counts |
|---|---|
| About software | yes 87; no 12; unclear 1 |
| Update related | yes 54; no 38; unclear 8 |
| Discussion type | technical troubleshooting 63; general dissatisfaction 4; other 20; not applicable 13 |
| Confidence | high 66; medium 33; low 1 |

Allowed-value and required-field checks passed. One row marks the main topic as not software while also mentioning a software update (pilot row 59, a phone trade-in question). This is possible under the two-field protocol and should be reviewed when the scope rule is finalized; it is not automatically an error.

The pilot intentionally oversampled difficult cases. These counts do not estimate prevalence in Reddit or in the ReleaseTrain endpoint results.

## Next checks

1. If available, inspect original independent records or revision history and preserve them as received. The authors report separate reviews, but the two submitted files do not provide independent evidence of that process.
2. Avoid reporting agreement statistics from the two identical submitted files.
3. Resolve ambiguous scope cases and record a final label decision without overwriting either submitted file.
4. Use the pilot to refine the task definition. Do not train a final model or cite agreement statistics from these duplicate files.
