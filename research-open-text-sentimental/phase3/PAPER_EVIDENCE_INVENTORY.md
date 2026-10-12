# Paper evidence inventory (working, 2026-10-07)

This is a planning record, not a manuscript or a new experiment. Historical datasets, labels, predictions, and test results remain unchanged. A result is suitable for the paper only with the population and limitations below.

| Candidate claim | Saved evidence | Status and allowed wording | Remaining check |
| --- | --- | --- | --- |
| Phase 2 collection contains 3,362 unique records | `../phase2/combined_dataset/master_records.json` | Verified count; **not** 3,362 Reddit posts | Dataset flow by source, date, exclusion, and review status |
| 30 Stack Overflow records are present | `SOURCE_DOMAIN_AUDIT.md`, `reddit_only_sensitivity/MANIFEST.json` | Verified; 30 are in revised development, none in the 200 reserved records | Make the manuscript dataset flow explicit |
| Excluding non-Reddit records preserves the development conclusion | `reddit_only_sensitivity/RESULTS.md`, `reddit_only_sensitivity/results/grouped_validation.json` | Reddit-only S2 development: 2,050 posts; grouped macro-F1 0.836 versus saved mixed v2 0.835. Fold assignments differ, so this is a sensitivity result, not a paired improvement. | Check exact method and describe the older tests as models trained on mixed-source development |
| Balanced weights are a reasonable retained choice | `balancing_study/RESULTS.md`, `balancing_study/results/` | At the saved threshold, balanced macro-F1 0.836, unweighted 0.764, oversampling 0.838 on identical Reddit-only grouped folds. When each arm is allowed a development-only threshold search, all are approximately 0.838–0.839; do not claim weights are intrinsically superior. | Keep historical model/threshold; treat threshold search as exploratory, not a new test result |
| Revised S2 development has 2,080 posts (1,686 troubleshooting, 394 other update) | `revised_development_v2/MANIFEST.json`, `revised_development_v2/development_v2.jsonl` | Verified for the revised development snapshot, not all Phase 2 records | Check domain-specific counts after Reddit-only exclusion |
| Text model beats simple baselines within S2 | `experiment_v1/RESULTS.md`, `experiment_v1/results/`, `diagnostic_results/RESULTS.md` | Supported for the reviewed S2 corpus; grouped development macro-F1 approximately 0.835 | Produce one version-consistent results table; avoid mixing v1 and revised v2 counts |
| Original reserved S2 test macro-F1 is 0.863 on 159 posts | `experiment_v1/RESULTS.md`, `experiment_v1/results/` | Historical scored result; 24 comparison-class posts; no longer untouched | Report exact model/data version and uncertainty |
| Fixed model macro-F1 is 0.792 on 344 fresh S2 posts | `fresh_test_20261007/RESULTS_FIXED_MODEL.md`, `fresh_test_20261007/results_fixed_model/` | Verified scored result; 277 troubleshooting, 67 other; examined test | Compare errors and source mix without tuning to this test |
| Troubleshooting posts often lack some diagnostic details in saved text | `diagnostic_results/RESULTS.md`, `diagnostic_results/analysis.json` | Descriptive result for 237 retained cases from a 250-post sample; not a developer-usefulness measure | Distinguish field presence from utility; separate help-request intent from technical detail |
| Sparse text is associated with some misses | `diagnostic_results/RESULTS.md`, grouped out-of-fold predictions | Exploratory association: 16 misses among 237 retained troubleshooting cases; 8 of 20 title-only cases missed | Check exact denominators and uncertainty; do not claim causation or fresh-test diagnostic evidence |
| Independent human agreement validates all Phase 2 labels | No complete independent first-pass record for the joint review | **Unsupported. Do not claim.** Joint decisions are documented as joint decisions | Optional new blinded reliability sample with first judgments saved separately |
| A new blind single-review check reproduces earlier recorded decisions | `single_reviewer_audit_20261008/submission/RESULTS.md`, `single_reviewer_audit_20261008/submission/analysis.json` | 120-post stratified check: all three fields match on 98; update field matches on 107. This is a single new review versus mixed-provenance prior decisions, not independent two-rater agreement. | Adjudicate 22 differences; investigate 12/20 previous software/non-update posts now marked update-related before freezing the study population |
| System reduces developer work or produces actionable reports | No practitioner outcome study | **Unsupported. Do not claim as a result.** | Either collect practitioner outcomes under a protocol or state as future motivation |

## Test-use rule

The 159-post reserved test and 344-post fresh test have both been scored. Do not use either to choose new balancing, preprocessing, model architecture, or decision threshold. Develop any new method within development data. If the paper needs a new confirmatory performance claim for that new method, collect a separate untouched test after freezing it.

## Immediate parallel work

1. Cursor: versioned Reddit-only grouped sensitivity analysis with the fixed existing model and baselines; no historical file edits. Save a manifest, counts, predictions, metrics, and a short interpretation.
2. Codex: reconcile claim wording, closest prior work, dataset flow, and the fresh-test error analysis plan from saved evidence.
3. Manu and Professor Berhe: no new bulk review now. A limited independent reliability sample is the next human task only after its sample and protocol are frozen.
