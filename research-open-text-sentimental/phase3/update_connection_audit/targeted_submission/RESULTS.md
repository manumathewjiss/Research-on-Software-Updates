# Targeted update-connection audit: completed intake

## Status and provenance

Manu returned a completed 254-post workbook. The submitted workbook is archived unchanged beside this report. The 22 earlier adjudication decisions are preserved separately; `A049` uses Manu's later chat correction to `update_related=yes`, while `A022` remains `no`. `final_decisions_resolved.json` is the authoritative 22-decision overlay. The earlier Phase 2 master, revised development v2, reserved test, and fresh test were not overwritten.

Validation: 254 unique review IDs; each ID, title, saved body, and saved reply context matches the blank packet exactly; all answer fields are filled with permitted values; each row obeys the software/type consistency rule. All 254 IDs and all 22 adjudication IDs belong to development, with no overlap between packets or with the 200 reserved test rows. The 500 fresh-test IDs also have no overlap with the revised development snapshot.

## Decisions

The 254 targeted rows were **previously reviewed**, then selected for this extra blind recheck. They are not 254 newly collected posts. All had a prior `update_related=no` in revised development v2. The new review records 80 `yes`, 172 `no`, and two `unclear`. Software scope is 234 `yes`, three `no`, and 17 `unclear`. Discussion types are 198 troubleshooting, 30 other, six general dissatisfaction, and 20 `na`.

Among 204 phrase-flagged candidates, 77 were marked update-related, 125 not update-related, and two unclear. Among 50 randomly selected from the unflagged frame, three were marked update-related and 47 not. These are results of an enriched audit sample, **not corpus prevalence estimates**. The three of 50 show that the phrase screen was not exhaustive. The audit does not imply that all unreviewed or unflagged records are correct.

The 80 newly update-related targeted posts comprise 69 troubleshooting, nine other, and two general dissatisfaction. Applying them plus the resolved 22 decisions to the full 3,151-row development snapshot changes its raw S2 count from 2,082 to 2,168. After retaining the original two near-duplicate exclusions, the model-eligible S2 count changes from **2,080 (1,686 troubleshooting, 394 other update)** to **2,166 (1,761 troubleshooting, 405 other update)**. The change is +86 overall: the 254-post packet adds 80 S2 rows and the 22 adjudications add a net six. The 30 Stack Overflow development records remain identifiable and are excluded from Reddit-only results.

## Development-only fixed-model check

The pre-existing title+body TF-IDF logistic-regression configuration was applied without retuning: balanced class weights, `C=4`, threshold `0.5877137791150834`. Five stratified grouped folds keep exact/near duplicate text together. Vectorization is fit within each training fold. Neither the reserved nor the fresh test was scored.

| Population | n | Troubleshooting | Other update | Model macro-F1 | Other-update F1 | Troubleshooting F1 | Majority macro-F1 | Keyword macro-F1 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Audited mixed development | 2,166 | 1,761 | 405 | 0.841 | 0.742 | 0.940 | 0.448 | 0.651 |
| Audited Reddit-only development | 2,136 | 1,733 | 403 | 0.843 | 0.746 | 0.940 | 0.448 | 0.650 |

The historical mixed-development grouped macro-F1 was 0.835 and historical Reddit-only grouped macro-F1 was 0.836. These are different populations with rebuilt folds, so the new numbers are **not** a paired improvement or proof that the audit improved generalization. The qualitative development finding remains: text features outperform the two simple baselines on the reviewed S2 development population.

## Implications for the paper

The already reported reserved and fresh test scores belong to the **historical fixed model trained on the earlier development snapshot**. They must not be presented as scores of a model refit on the audited 2,166-post population. The corrected development snapshot and grouped check are a subsequent sensitivity analysis. A model refit on the corrected population would be a different model; any scoring on already viewed test sets would be post hoc, not a new untouched confirmation.

Next: reconcile one final dataset-flow table, keep the original frozen-test result with its exact training population, and report the audited development sensitivity separately. Then complete the manuscript's methods, error analysis, limitations, and final evidence check. No further large human labeling batch is required for this paper as currently scoped; further review would support a new, stronger claim rather than repair this bounded audit.
