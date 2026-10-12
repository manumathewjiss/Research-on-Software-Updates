# Completed 200-post first-pass review: intake result

**Status:** both completed workbooks were validated and archived unchanged. Manu clarified that both reviewers completed separate first passes without seeing or discussing each other's answers before both files were saved. This process is reported by Manu; the files alone cannot independently verify it. Initial agreement is analyzed in `AGREEMENT.md` and `AGREEMENT.json`.

## Validation

- Both files contain the same 200 unique review IDs in the same order. IDs, title, original body, and saved reply text match the blank packet exactly.
- Every row has valid `about_software`, `update_related`, `discussion_type`, `confidence`, and a nonempty reason. For all 118 posts marked troubleshooting in both files, all eight diagnostic fields have allowed answers. Diagnostic fields are blank for the remaining 82 rows.
- All categorical and diagnostic answers match across A and B. The 200 reason cells differ in wording. Both original files are preserved next to this report. The package contains no reserved or fresh-test records.
- The Phase 2 master, audited development snapshot, model files, and test results were **not** changed by this intake.

## Matching first-pass decisions on this selected sample

| Field | Counts |
|---|---|
| Software scope | 181 yes, 18 no, 1 unclear |
| Update connection | 138 yes, 62 no |
| Discussion type | 118 troubleshooting, 51 other, 12 general dissatisfaction, 19 not applicable |
| Confidence | 96 high, 78 medium, 26 low |

This sample was deliberately stratified using prior labels (80 previous S2 troubleshooting, 60 previous S2 other update, 40 software/nonupdate, 20 nonsoftware). These counts are **not** estimates of corpus or Reddit prevalence.

## Differences from the earlier development labels

Twenty-nine unique posts differ on at least one of the three substantive fields. The field-level counts are 20 discussion-type changes, 13 update-connection changes, and three software-scope changes; some posts changed on multiple fields. Within the selected 200, eight previously in-scope posts moved out of S2 and six previously out-of-scope posts moved into S2. Among type changes, eight move from general dissatisfaction to troubleshooting, three move in the reverse direction, and several involve `other` or `na`.

These are possible development-label corrections, not a population error rate. The first label and the new independent first passes are both fallible, and the reviewers may have encountered records before. A **new versioned development-only snapshot** now applies the matching first-pass decisions while preserving the earlier snapshot. After the two original near-duplicate exclusions, it has 2,164 S2 posts (1,762 troubleshooting and 402 other update); its Reddit-only subset has 2,134 (1,734 troubleshooting and 400 other update).

A grouped five-fold check on the new snapshot, using the same fixed TF-IDF logistic-regression settings and threshold, gives macro-F1 **0.832** on mixed development and **0.838** on Reddit-only development. The Reddit-only majority and keyword baselines give 0.448 and 0.649. The earlier audited-development Reddit-only score was 0.843 on 2,136 posts. The populations and folds changed, so 0.838 versus 0.843 is **not a paired change estimate**. The qualitative development finding remains. No reserved or fresh-test record was scored. Machine-readable output: `independent_review_dev_grouped_validation.json`.

## Diagnostic fields

The 118 posts marked troubleshooting in both files have complete detail fields. For example, 31 have `error_evidence=present` and 54 have `reproduction_context=present`; `error_evidence=unclear` for 12. Because this is a selected reliability sample, do not add these rates to the separate random 250-post diagnostic study as if they were one random sample.

## Next research decision

Under the user-reported separate first-pass workflow, this sample has exact agreement on every categorical and diagnostic field (Cohen's kappa 1.0 where computed). This measures agreement, **not** label correctness. All 200 reasons differ in wording. The exact match is unusual and must be reported transparently with its provenance and prior-exposure limitations. The historical 0.792 fresh-test score still belongs only to the model fitted on the earlier 2,080-post training population.
