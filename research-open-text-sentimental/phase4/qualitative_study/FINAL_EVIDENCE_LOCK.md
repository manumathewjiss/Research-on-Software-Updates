# Evidence lock before manuscript drafting

**Status:** Scientific results and their limits are fixed for drafting. This file does not substitute for the private institutional, permission, and reviewer-process record.

| Component | Frozen evidence | Permitted manuscript claim | Boundary |
|---|---|---|---|
| Collection | `phase3/icsc_full_paper/EVIDENCE_LEDGER.md` | 3,362 unique combined records were collected and reviewed through mixed-provenance Phase 2 decisions. | Thirty records have Stack Overflow URLs; do not call all 3,362 Reddit posts. Do not describe all decisions as independent double annotation. |
| Historical fixed classifier | `phase3/revised_development_v2/MANIFEST.json`; `phase3/experiment_v1/RESULTS.md`; `phase3/fresh_test_20261007/RESULTS_FIXED_MODEL.md` | The fixed title/body TF-IDF logistic-regression model used 2,080 revised S2 development posts. It scored macro-F1 0.863 on 159 reserved S2 cases and 0.792 on 344 fresh S2 cases. | The fresh-test other-update class had 67 cases and F1 0.667. Scope was human-established, so this is not an end-to-end Reddit discovery system. Do not attribute the test scores to later audited development snapshots. |
| Diagnostic information | `phase3/diagnostic_results/RESULTS.md` | Among 237 confirmed troubleshooting posts in the diagnostic sample, 40 contained error evidence, 108 reproduction context, and 118 an attempted remedy. | These are observed fields in saved text, not proven developer usefulness or issue-resolution outcomes. |
| Development sensitivities | `phase3/icsc_full_paper/EVIDENCE_LEDGER.md`; `phase3/semantic_comparator/RESULTS.md` | The Reddit-only, balancing, and MiniLM comparisons test robustness on development data. | They do not supersede the frozen reserved/fresh evaluations. MiniLM's paired confidence interval includes zero; do not claim a reliable gain. |
| Main qualitative study | `phase4/qualitative_study/MAIN_INTAKE.json`; `phase4/qualitative_study/MAIN_ANALYSIS.md`; `phase4/qualitative_study/CLAIM_EVIDENCE_MATRIX.md`; original workbooks in `main_submissions/` | Across 30 purposefully selected intact posts, two reported independent external reviewers chose the same first action on 21 and different actions on nine. Their reasons show that similar evidence can support different action thresholds and that missing distinctions can change the first action. | This is an exploratory multiple-case finding. There is no correct-action key, field-removal intervention, population prevalence estimate, or causal effect. Reviewer independence and absence of outside lookup are Manu-reported process facts. |

## Qualitative source lock

- Reviewer A workbook SHA-256: `2df49763093f78c4ef4c6e7d5755debc622d500b50af14481546d9d01f651780`.
- Reviewer B workbook SHA-256: `024cd641e4ae137f4fcbf9538e984d0bb33853d3679e6265c3f8b207209c9a47`.
- The six pilot cases are not included in the 30-case main results.
- Historical discussion-purpose labels are not keys for first-action decisions.

## Before public manuscript wording

1. Archive the actual institutional human-participant determination, saved-text sharing basis, reviewer qualifications, and consent/process record in a private location. Manu reported that institutional and sharing questions were confirmed; Codex has not inspected the underlying documents. Do not put identifying reviewer paperwork in the public repository.
2. Recheck every manuscript number and quoted or paraphrased post example against the source files above. Apply the documented text-sharing arrangement to examples.
3. Preserve the two submitted reviewer workbooks unchanged. No additional reviewer labeling, model training, or new data collection is required for this frozen study.
