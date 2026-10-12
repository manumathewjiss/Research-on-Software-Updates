# Final PI stopping decision before manuscript writing

**Decision date:** 2026-10-08. **Recommendation: Option A — freeze everything and begin writing.** No new labels, training, testing, or change to the 30-case qualitative study is authorized by this decision.

## Temporal honesty

The 21K API inventory and 200-ID random sample in `BROAD_INVENTORY.json` and `pilot_200_candidates.jsonl` were made **before** the present request to define stopping rules. They are exploratory and must never be described as a preregistered pilot. The criteria below govern whether to begin **any additional** sampling or human review now. Because the entry gate fails on already documented structural evidence, we stop before a new review stage. No human-confirmed proportions for the 21K frame are claimed.

## Objective continuation gate for any further 21K annotation

Continue only if **all** of the following are satisfied before assigning new reviewer work:

1. **Same construct:** A proposed sample must target the paper's S2 population—human-confirmed software **and** update discussion—without silently replacing the task with end-to-end discovery from an unfiltered stream. If studying the broad stream is itself the objective, that is a separate research question and requires a new protocol.
2. **New information:** The candidate source must offer a credible way to obtain a substantial number of *new* human-confirmed S2 records, particularly other-update cases or genuinely new triage situations, beyond the 500-post fresh review already sampled from the filtered update-positive route. API keyword/prediction membership alone is not evidence.
3. **Protected evaluation:** Any proposed model claim must have an untouched test population independent of all choices made after the reserved and fresh tests were examined. Development cross-validation alone cannot establish improved fresh-test generalization.
4. **Decision-relevant gain:** The planned work must test a material scientific claim, such as a previously absent evidence-to-action mechanism or a reliable, practically relevant model improvement. A target for a new model study would be at least +0.03 macro-F1 *and* +0.05 other-update F1 on an untouched test, with a paired uncertainty interval excluding zero; these are decision thresholds, not observed outcomes.
5. **Human validity:** Any numerical claim about the broad frame requires a probability sample with human verification and preserved first passes. An AI suggestion or API flag cannot become the reported label. An enriched set may find examples but cannot estimate prevalence without weighting.

The gate is deliberately conjunctive. Failing one condition is enough to stop further annotation for **this paper**. It does not assert that the unused posts are worthless.

## Evidence at the gate

| Criterion | Evidence now | Decision |
|---|---|---|
| Same construct | The unfiltered route returned ~21.8K records, including thousands with API update prediction false or absent and visibly unrelated discussions. The current classifier is conditional on human-established S2 scope. | **Fails** as a direct dataset extension. |
| New information | The filtered update-positive route already supplied the one-shot 500-post fresh review (344 S2, 67 other-update). The 200-ID random sample from the remaining broad new IDs has only three API-positive update predictions, although specific API-negative misses exist. The sample is not human-labeled. | No demonstrated material addition; a new screening study would be required. |
| Protected evaluation | Both reserved and fresh tests have been scored and discussed. | **Fails** for a newly selected model's confirmatory claim unless a new untouched test is collected. |
| Decision-relevant gain | The existing 30-case human study identifies conditional evidence-to-action reasoning. The MiniLM comparison's +0.0059 macro-F1 development difference has a 95% interval crossing zero. | No demonstrated benefit from reopening either part. |
| Human validity | The broad 200 is a blindable candidate sample with empty human fields. | No publishable class or diagnostic prevalence estimate exists for 21K. |

## Questions the broad inventory cannot answer yet

The number of **human-confirmed** troubleshooting posts among the 21K, whether their diagnostic field rates differ from the current 237-post diagnostic sample, and whether they contain *new* decision mechanisms are unknown. Reporting a percentage would require human annotation. Those unknowns do not require new reviewer work for the current paper, because the broad route fails the same-construct and protected-evaluation gates.

If this were pursued as a later study, begin with a fresh probability sample of 200 unseen IDs and two independent reviewers for all 200 S2 scope and discussion-type decisions. Keep their first passes; adjudicate separately; retain uncertain cases. This is a future-study specification, not work pending for the ICSC manuscript.

## Qualitative study and passage removal

The completed intact-post study has two independent first-pass reviewer submissions for 30 selected cases. Additional examples from a broader API frame would not change its reviewer count or establish action correctness. Replacing cases after examining responses would compromise the frozen design. Keep the current protocol.

The earlier passage-removal screen found only 27 provisional plausible cases among 1,550 screened development representatives. None was human-approved by that inventory, and the construct risk remains: removing a passage can change the natural meaning or more than one piece of evidence. The existence of additional broad posts is not evidence that this experimental design has become valid. Do not revive it for this paper.

## Modern models

1. **Already tested:** Frozen MiniLM embeddings plus logistic regression versus TF-IDF plus logistic regression on the same 2,136 audited Reddit-only development posts. Macro-F1 difference +0.0059, paired 95% interval −0.0160 to +0.0292. This tests whether semantic representation alone helps; the answer is not established as a meaningful gain.
2. **Most defensible next model, if the gate had passed:** A single fine-tuned longer-context encoder such as ModernBERT-base. Its hypothesis would be that contextual and longer-range cues reduce errors on long, ambiguous posts, especially the other-update class. Use the same title/body, grouped outer folds, nested threshold/model selection, source and length slices, paired confidence interval, and recorded compute. Test generalization only on a new untouched population. The existing fresh set is no longer an untouched selection target.
3. **Not justified now:** A suite of popular encoders, a large language model prompt benchmark, or additional hyperparameter searches. More architectures without a new causal or generalization question would dilute the paper's contribution and invite selection on development scores.

The current model is sufficient for the paper's purpose. Its fresh-test weakness on the other-update class should be reported, not optimized away after test inspection. No Cursor implementation task is needed.

## Final decision

**Option A.** Freeze the 3,362-record master, reviewed subsets, fixed classifier and evaluations, diagnostic analysis, and intact-post qualitative study. Start writing from `phase3/icsc_full_paper/EVIDENCE_LEDGER.md` and `phase4/qualitative_study/FINAL_EVIDENCE_LOCK.md`. The 21K snapshot and 200-ID sample remain an internal feasibility record only. The sole separate administrative item is preserving the underlying institutional, text-sharing and reviewer-process documents privately, as previously noted.
