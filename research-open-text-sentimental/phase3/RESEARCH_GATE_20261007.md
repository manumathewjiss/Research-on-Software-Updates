# Research gate after corrected joint reviews

**Status:** The planned core analyses are complete. The user asked to finish the research before drafting the new paper. This file states what the completed work supports and what is still a choice rather than silently calling the study finished.

## Completed evidence

1. **Data and labels:** Phase 1 preserved; 3,362-record combined corpus audited; revised S2 development snapshot has 2,080 posts (1,686 troubleshooting, 394 other update). The corrected 250-post diagnostic workbook and two corrected fresh-test workbooks are archived. The user reports that Manu and Professor Berhe wrote the fresh labels together. There is no independent reviewer-agreement estimate from these sheets.
2. **Fresh classifier test:** The 500 unseen-ID candidates were screened before scoring. Joint review found 344 in-scope update posts (277 troubleshooting, 67 other). Frozen labels were hashed before the one-time fixed-model evaluation. Fresh macro-F1 is 0.792 (bootstrap 95% interval 0.731–0.845); other-update F1 is 0.667; troubleshooting F1 is 0.916. The fixed model exceeds majority and fixed-keyword baselines. See `fresh_test_20261007/RESULTS_FIXED_MODEL.md` and `results_fixed_model/metrics.json`.
3. **Diagnostic study:** Among 250 sampled reviewed troubleshooting posts, 237 were confirmed troubleshooting, four were marked no, and nine unclear. In the 237 confirmed cases, release information was observed in 122, reproduction context in 108, error evidence in 40, and an attempted remedy in 118. Rates and Wilson intervals are in `diagnostic_results/RESULTS.md` and `analysis.json`. The 13 scope flags were not written back into development labels.
4. **Error link:** Fixed-model grouped development predictions missed 16 of those 237 confirmed cases. Eight of 20 title-only posts were missed versus eight of 217 posts with bodies. This is exploratory and cannot establish causality. Diagnostic fields were not labeled on the fresh test, so no direct fresh-test detail/error join exists.
5. **Development stress:** The predeclared July 1, 2026 chronological holdout (1,629 train, 451 later development posts) has macro-F1 0.776, with 55 other-update posts in the later set. Holding out each of 18 development communities with at least five of each class yields pooled macro-F1 0.830 on 1,395 held-out records. Source mix and class mix change with time/community; these results are stress checks rather than universal generalization evidence. Full numbers: `diagnostic_results/development_stress_tests.json`.

## Claims ready for a manuscript

- The revised software/update scope and three discussion types correct the original binary-class wording. The negative class is **other update discussion**, including dissatisfaction and neutral/other topics.
- For this collected, reviewed corpus, post text distinguishes troubleshooting from other update discussion better than majority or a fixed keyword rule. Fresh macro-F1 is 0.792, with a weaker and less precise other-update class.
- In the sampled confirmed troubleshooting posts, observable diagnostic details are uneven: specific symptoms are common by design, while explicit error evidence and reproduction context are much less common.
- Short posts with no saved body are associated with more development classifier misses in this diagnostic sample. This is exploratory, not causal.

## Limits that must appear with these claims

- The API candidate pool is not a random sample of Reddit. The fresh test uses new IDs, but most posts were published before the final collection date. The classifier is evaluated after human S2 scope selection; it is not an end-to-end Reddit monitor.
- Current corrected test and diagnostic labels were jointly reviewed according to the user, so no independent agreement can be estimated from them. The earlier files named `AI_Assisted` were withdrawn; their cell values match the corrected files, and the label-generation account is user-reported rather than established from file metadata.
- The diagnostic checklist measures what is visible in saved text. It does not measure developer utility, resolution, or whether missing information existed elsewhere in a thread.
- The sample's 13 no/unclear troubleshooting checks are review discrepancies relative to the earlier development labels. The reported field rates condition on 237 confirmed posts. Do not silently relabel development or change the fresh-test population after scoring.
- The negative fresh-test class has 67 posts. Its F1 interval is roughly 0.562–0.755. That is adequate for a qualified test result, while narrower generalization claims would require more evidence.

## Remaining research choices

There is **no required bulk labeling batch** for the current, qualified study. The planned diagnostic analysis, fixed fresh test, error analysis, and development stress tests are done. The next action is an author-level evidence review: agree on the paper's exact question, decide whether the current joint annotation evidence is sufficient for the intended ICSC full-paper claim, and approve the limitations above. If the paper wants to claim *reliable human identification of each diagnostic field*, a genuinely independent annotation exercise on newly assigned posts would be needed; the joint sheets cannot provide that statistic. A practitioner usefulness claim would require a separate practitioner study. Those are additional research contributions, not corrections to the completed scores.

Once the authors choose the claim level, manuscript drafting can begin. Preserve the frozen test as a one-time result; do not tune its model or threshold to improve the reported score.
