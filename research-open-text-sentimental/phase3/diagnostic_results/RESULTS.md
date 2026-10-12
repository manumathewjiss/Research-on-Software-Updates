# Diagnostic-detail study: current result

**Status:** analysis of the corrected 250-post review. Numeric results and grouped development predictions are in `analysis.json` and the accompanying JSONL files. The guide is `../diagnostic_pilot/CODEBOOK_v1.0.md`. The user reports joint human review; there is no independent field-level agreement statistic.

## Sample and scope

The 250 posts were a simple random sample from 1,658 Reddit-only, S2 troubleshooting records in revised development. The sample was chosen before the diagnostic answers. The reviewer retained the troubleshooting designation for 237 posts, marked four as not troubleshooting, and found nine unclear. Those 13 remain in the original development snapshot but are excluded from the **conditional diagnostic-field summary** below; this is a review discrepancy to report, not an automatic relabeling. Thus the field rates describe the 237 posts confirmed during this review, and conditioning on that judgment may affect representativeness.

Twenty-four of the sampled posts had no saved body; 20 of these were confirmed troubleshooting. Ten sampled posts overlapped the earlier feasibility pilot by chance; their main-study answers were recorded separately under the final guide. Excluding the nine overlapping posts among the 237 confirmed cases changes the field rates only slightly (`analysis.json`).

## Observable diagnostic information

| Detail in saved title/body | Present | Rate among 237 | 95% Wilson interval |
|---|---:|---:|---:|
| Software product | 218 | 92.0% | 87.8–94.8% |
| Identifiable release | 122 | 51.5% | 45.1–57.8% |
| Environment | 137 | 57.8% | 51.4–63.9% |
| Specific symptom | 237 | 100.0% | 98.4–100.0% |
| Reproduction context | 108 | 45.6% | 39.4–51.9% |
| Error evidence | 40 | 16.9% | 12.6–22.2% |
| Attempted remedy | 118 | 49.8% | 43.5–56.1% |
| Explicit help request | 168 | 70.9% | 64.8–76.3% |

`not_observed` means absent from the saved snapshot, not absent from the full live discussion or the actual incident. The sample was drawn from posts already labeled troubleshooting, so the 100% symptom result may partly reflect the task definition and should not be promoted as a surprising finding. The clearest descriptive gaps are error evidence and reproduction context. This field checklist does not measure whether a software developer can resolve a problem; no practitioner rating was collected.

Among confirmed troubleshooting posts, the mean number of present fields is 4.84 of eight. That count weights all fields equally for description only; it is not a validated utility score. Title-only posts show less recorded context: reproduction context is present in 2/20 and attempted remedy in 2/20, compared with 106/217 and 116/217 when a body is saved. Text availability is a major interpretation factor.

## Relationship to the detector

For an exploratory error analysis, the fixed classifier was scored out of fold on revised development using five stratified group folds. Exact and near-identical title/body records were grouped in the same fold. The grouped development macro-F1 is **0.835**, consistent with the prior validation result. The 237 diagnostic posts confirmed as troubleshooting were joined to these held-out predictions by Reddit ID; **16** were missed by the classifier.

- Title-only: 8 misses among 20 confirmed troubleshooting posts.
- Title plus body: 8 misses among 217.
- Reproduction context present: 3 misses among 108; not observed: 13 among 129.
- Attempted remedy present: 4 misses among 118; not observed: 12 among 119.

These comparisons are exploratory associations in a small error set. The title-only difference is especially large, but there are only 20 title-only confirmed cases. Other field comparisons overlap and were not preselected as separate hypothesis tests; do not claim that missing details **cause** a miss or that every individual field has a statistically established effect. The 250 diagnostic records come from development; they do **not** annotate the fresh 344-post test. Therefore this analysis connects diagnostic fields to development held-out errors, not to the fresh-test errors.

## Limits before manuscript claims

The study has one joint review record rather than two independent first passes. The 13 scope discrepancies should be described and can be inspected separately if authors want to revise the corpus; they must not be silently changed after model evaluation. The source corpus was assembled using an API selection process, so the estimates describe this reviewed Reddit-only corpus and do not estimate all Reddit troubleshooting posts.
