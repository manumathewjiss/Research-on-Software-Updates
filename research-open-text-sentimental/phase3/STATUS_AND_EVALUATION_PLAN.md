# Phase 3: turn the reviewed corpus into defensible evidence

Status: 2026-10-07. Plan below; first locked baseline is complete under `experiment_v1/` (`DATA_AUDIT.md`, `PROTOCOL.md`, `RESULTS.md`, `RUN.md`).

## What is ready

- The rebuilt Phase 2 master has 3,362 unique Reddit IDs. Of these, 3,357 have a recorded final Phase 2 decision and five remain unresolved. Exclude the five from supervised experiments. The source is `../phase2/combined_dataset/master_records.json`; the last submitted workbook and its checks are archived at `../phase2/annotation/submissions/2026-10-07-final-remaining-768/`.
- Label provenance differs: 2,757 decisions came from Manu's assisted review, 100 pilot decisions were finalized after discussion, 300 expansion decisions were joint, and 200 reserved-test decisions were joint. These are reviewed decisions, not 3,357 independent annotations. The pre-discussion 100-post pilot agreement is documented separately in `../phase2/annotation/submissions/2026-10-06/PILOT_AGREEMENT_RESULTS.md`.
- The 200-post reserved set was chosen before the bulk suggested labels. Keep it out of training, model choice, threshold choice, prompt revision, and feature selection. Report its joint-label provenance plainly.

## Recommended main question and population

Study **software-update discussion** as the main paper population: `phase2_about_software=yes` and `phase2_update_related=yes` (the S2 definition in `../phase2/TASK_DEFINITION.md`). Within that population, predict whether a post is `technical_troubleshooting`. The negative class is **other update discussion**, including general dissatisfaction and other discussion; it must not be called “general dissatisfaction.” This gives a meaningful two-class task without pretending that news or product discussion is dissatisfaction.

Current counts before any duplicate handling: 2,246 S2 posts (1,826 troubleshooting, 344 other, 76 general dissatisfaction). Development: 2,087 (1,691 / 329 / 67). Reserved test: 159 (135 / 15 / 9). The three-way label can be described and explored, but general dissatisfaction has only nine reserved-test examples, too few for a strong primary three-way performance claim.

## Immediate task: lock an evaluation-ready snapshot

1. **Check label and text quality.** Audit a stratified sample of accepted assistant suggestions, revised cases, both API pools, and the old 542. Record corrections with provenance in a new file; never overwrite Phase 1. Keep the five unresolved excluded. Report what was checked and what was corrected. Do not equate an accepted suggestion with an independent human annotation.
2. **Guard against duplicate leakage.** There are zero duplicate Reddit IDs, but normalized title plus body has 46 duplicate-text groups involving 97 rows across the full corpus. Two groups cross between development and the reserved test, including one pair within the proposed S2 task: `1u3zzcs` (development) and `1u3zf6d` (reserved). Another pair, `1so7xen` / `1so7xx4`, crosses the split but its two records have different update-related judgments. Before fitting a model, remove or group development copies that match reserved posts; keep the reserved set unchanged. Inspect near duplicates as well. Document the rule and affected counts.
3. **Check source bias.** The API pools are keyword screens, not class labels. Source and class are strongly related: in S2, the old pool has 37 troubleshooting of 202, the API GDS pool 294 of 380, and the API TPS pool 1,495 of 1,664. Report performance by source and compare title/body-only models to any model that uses source clues. Never feed `source_pool`, old labels, review status, or review reasons into the classifier.
4. **Freeze the protocol.** Record the exact included IDs, scope, label map, duplicate treatment, train/validation split, reserved-test IDs, preprocessing, model choices, metric definitions, and random seeds. Use development data for all choices. Open the reserved-test results once, after those choices are fixed.

## Experiments after the protocol is fixed

1. Compare majority and keyword-screen baselines with simple text models (for example TF-IDF plus logistic regression), using title only and title plus body. Add comments only as a separately named setting because comments may be missing or arrive after the original post. Consider a transformer only if its cost and gain justify it.
2. Report troubleshooting precision, recall and F1, macro-F1, confusion matrix, and precision among the top ranked posts. Include uncertainty intervals where feasible. Show results by source pool and text availability. Do not select a winner from test-set scores.
3. Reassess Phase 1 sentiment and conversation claims. Keep only results supported by correctly matched text availability and valid tests. Do not carry forward the old “best model” or trajectory claims unchanged.
4. If the main result is sound, add one focused secondary study: **information completeness** of genuine troubleshooting posts. Define observable fields such as version, device/OS, symptom, error message, steps/context, and attempted fix; annotate a manageable sampled subset with a separate guide and quality check. This can show whether a detected post gives enough detail to investigate a problem. Resolution and emerging-issue clustering should remain later projects unless complete comments and dates support them.

## When to start rewriting the paper

Start the new manuscript after the target, protocol, duplicate handling, and baseline results are frozen. Then write the contribution around the revised task and evidence. Include the ICMLA paper as prior work and clearly state what data, labels, methods, and findings changed. Acceptance cannot be promised; this sequence addresses the main scientific weaknesses before submission.
