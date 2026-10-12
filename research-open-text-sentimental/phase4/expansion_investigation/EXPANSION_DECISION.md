# Final expansion investigation: 21K broad ReleaseTrain pool

**Decision: Option A — retain the frozen dataset and model, and begin writing.** This is a scientific stopping decision, not a claim that the 21K pool has no interesting posts. The observed pool is a different, much broader candidate frame; the current study already has a newly reviewed 500-post test from its update-positive subset; and the existing semantic comparator has not shown a reliable gain. No paper result or confirmed label has been changed by this investigation.

## Sources and snapshot

- On 2026-10-08 the unfiltered `GET https://releasetrain.io/api/reddit/query/update-related?limit=500&page=...` initially reported 21,813 records. During download its live total became 21,814. The 44 offset pages returned 21,814 rows and 21,813 unique Reddit IDs: one duplicate ID caused by a shifting live collection. This is a dated inventory, not a stable API release. Page hashes and server dates are in `BROAD_INVENTORY.json`.
- Of the downloaded rows, 9,592 had no `metadata.predicted.isUpdateRelated`, 8,495 were `false`, and 3,727 were `true`. These are server fields, not human labels. The `true` count matches the filtered route used for the fresh test at this time.
- 2,832 rows overlap the Phase 2 master and 499 overlap the 500-post fresh review. After excluding both sets, 18,483 rows remain. These are candidate rows, not 18,483 newly eligible software-update discussions. The one offset-page duplicate means row and ID counts should not be used interchangeably.
- The separate `/tps` and `/gds` keyword routes returned 2,430 and 460 unique IDs respectively during this investigation. Their server descriptions call them recall-oriented keyword screens and explicitly warn of false positives. Their sum is not the 21K collection, and their categories are not human labels.
- The Phase 2 master dates range from 2025-01 through 2026-10. The broad-pool pilot contains older material back to 2014, although most sampled records are from 2026. This is another reason to treat the broad route as a different sampling frame.

## Reproducible desk pilot

`collect_broad_inventory.py` drew a seed-20261008 simple random sample of 200 unique IDs absent from the Phase 2 master and the fresh 500-post review. The sample is saved in `pilot_200_candidates.jsonl`, with empty human fields. It contains 200 unique IDs, 86 communities, seven posts without saved body text, and a median saved body length of 821 characters. Its API prediction fields are: 105 missing, 92 false, three true. These proportions estimate only server metadata in this sampled *new-ID* frame; they do not estimate human-confirmed software-update or troubleshooting prevalence.

A Codex desk screen read titles and relevant body passages. Examples show genuine positives **and** scope contamination:

| Pilot ID | Provisional interpretation | Why it matters |
|---|---|---|
| E082 | Software/update troubleshooting candidate | Automatic protection disappeared between app versions 103 and 104; author rebuilt an older commit under a new version code and compared outcomes. Rich diagnostic contrast. |
| E120 | Software/update troubleshooting candidate | A Fedora update command produced a repeated offline-transaction warning and command errors. |
| E181 | Software/update troubleshooting candidate | Author states an iMessage delivery failure began after a macOS update and supplies an error. API prediction is false. |
| E044 | Borderline software/update candidate | Author asks whether a model/backend update explains changed cloud usage; the actual change is uncertain. |
| E166 | Software release discussion, not an observed fault | Author asks how a forthcoming Immich release's people-sharing behavior works. |
| E090 | Release announcement, not troubleshooting | Eclipse release link with almost no diagnostic text. |
| E007 | Software troubleshooting, update connection **not established** | Chrome menu problem existed before the browser was updated; that update was attempted afterward and did not fix it. |
| E025 | Software troubleshooting, update connection **not established** | Mail sync problem predates or spans several OS versions; updating was tried as a remedy. |
| E054 | Software outage troubleshooting, not clearly an update effect | Login/integration issue follows an outage, which is not itself evidence of a software update. |
| E094 | Software help, not an update effect | Screen Time was accidentally re-enabled. |

These are **illustrative Codex judgments only**, not a completed annotation of 200 rows or an estimate of class balance. We cannot honestly give the percentage of useful posts, troubleshooting posts, new discussion types, or rich diagnostic posts from this pilot without human review. The observed mix and API metadata are sufficient to reject the assumption that 21K means 21K eligible additions.

## What a publishable human pilot would require, if expansion were later reopened

1. Freeze the 200 sampled IDs and saved title/body snapshots before annotation. Do not expose the API prediction, source pool, prior classifier score, or Codex suggestion to reviewers.
2. Have two people independently label **all 200** with the finalized `about_software`, `update_related`, and `discussion_type` rules, including `unclear`; preserve both first passes and resolve differences separately. This is the minimum I would use to make a credible quantitative claim about this new frame. A 200-post simple random sample has a worst-case approximate 95% margin of error of about ±7 percentage points for a proportion, before label uncertainty and API selection bias. A smaller overlapping subset could assess reliability but would weaken the prevalence estimate.
3. Among human-confirmed update troubleshooting posts, independently apply the existing diagnostic codebook to a random subset **only if enough cases exist**. Do not compare richer detail on API-selected versus old posts without matching text availability, community and time period.
4. Report the sampling frame and an uncertainty interval for eligibility and class proportions. Keep enriched or targeted cases separate from the random sample; do not mix them into prevalence estimates.

This full human pilot was **not conducted** here. We recommend not assigning it now because the expected contribution to the current paper is weak relative to the existing fresh test and qualitative study.

## Scientific comparison with the present study

**Classifier.** The current fixed model already had an unseen-ID test from 500 randomly sampled candidates in the API's update-positive filtered route. Of those 500, joint review found 344 eligible S2 posts and 67 other-update cases. The fixed model achieved macro-F1 0.792, and other-update F1 0.667 (`phase3/fresh_test_20261007/RESULTS_FIXED_MODEL.md`). Adding broad-route posts would mostly add *scope-screening* negatives or unlabeled material, while the current model is explicitly conditional on human-established S2 scope. To use the broad frame as a model test, we would need a new end-to-end scope detector and a new estimand. That is a different research question.

**Qualitative study.** The intact-post study purposefully selected 30 diverse, reviewed development cases and obtained separate first actions and explanations from two reviewers. Extra unreviewed broad posts do not repair its two-reviewer limitation or create a causal test. Adding them would require a new sampling rationale and further reviewer work.

**Scientific contribution.** The strongest current contribution is the distinction among discussion purpose, observable diagnostic evidence, and first engineering action. Simply increasing N from a broad and mostly unverified pool does not strengthen that distinction. The old and broad frames also differ in date range, source completeness and selection rule, making a single pooled dataset difficult to interpret.

**Reviewer perception.** Transparent limits, frozen tests, and an honest small human study are more defensible than advertising 21K posts while training on a much smaller selected subset or assigning API membership as a class. The current paper should state its actual collection and selection frame.

## Modern model decision

The audited Reddit-only development comparator already tested a frozen MiniLM sentence representation against the TF-IDF logistic-regression baseline on the same 2,136 posts and outer folds. MiniLM macro-F1 was 0.8444 and TF-IDF 0.8385; the paired difference was +0.0059 with a 95% interval from −0.0160 to +0.0292. No reliable gain was shown, and the reserved/fresh tests were not used for that comparison (`phase3/semantic_comparator/RESULTS.md`). MiniLM truncated 24% of posts at 256 word-pieces, which suggests one possible long-context question but is not proof of a performance gain.

If a new model experiment were scientifically necessary, the most focused candidate would be a *single* longer-context encoder such as ModernBERT-base, compared with the fixed TF-IDF baseline using identical title/body inputs, duplicate-grouped outer folds, training-only threshold selection, class-wise F1, source slices, text-length slices, paired uncertainty intervals, and compute cost. The already viewed reserved and fresh tests could not honestly be called untouched confirmation after selecting on them. A new frozen external test would be needed for a strong generalization claim. There is no current evidence that this work would change the paper's central conclusion or justify reopening the frozen model.

## Decision and stop rule

Choose **Option A**. Add **zero** broad-route posts to the current training set, do **no** additional model training for this paper, and begin writing from the frozen evidence ledger. Do not present the 200-post sample as human labels or as a research result. Preserve it as a documented feasibility check.

Reopen expansion only for a future, explicitly different question—such as end-to-end discovery of update-linked problems from a broad stream—with its own sampling frame, scope annotation and untouched test. No result in this inventory forces that change for the present manuscript.
