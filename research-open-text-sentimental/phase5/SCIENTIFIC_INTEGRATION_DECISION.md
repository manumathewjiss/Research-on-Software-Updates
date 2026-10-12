# Phase 5 scientific integration decision (9 October 2026)

## Coauthor direction

Professor Berhe asked to retain the sentiment research from the ICMLA draft, specifically to ask whether sentiment helps identify troubleshooting posts about software updates. He also proposed examining the cadence of recent software-update risk posts. These are related but distinct questions: troubleshooting purpose, predicted update risk, and sentiment are different variables.

## What the completed experiment establishes

The frozen, grouped, development-only comparison is in `sentiment_reanalysis/RESULTS.md`. On 2,050 Reddit-URL, reviewed, update-related development posts, text-only TF-IDF plus logistic regression had macro-F1 0.8319 with a threshold selected inside training folds. Adding a title-and-body VADER compound feature yielded 0.8331. The paired difference was +0.0012 (bootstrap 95% interval -0.0115 to +0.0146). VADER alone yielded 0.5335. Thus the available experiment does **not** support a claim that VADER materially improves troubleshooting detection. It also does not prove sentiment is universally useless; this is a specific representation, task, corpus, and development evaluation. The protected tests were not scored.

The historical 542-post author/community VADER comparison reproduces the saved full-corpus divergence difference (0.3710 versus 0.2872, p=0.0092). Yet 205 author tracks use title-only fallback, stored comments cover only about 59% of recorded comment counts, class-specific divergence comparisons after separating title-only tracks have p=0.0766 and p=0.0598, and author-slope/early-late tests are not significant. Present this as a limited historical exploratory finding, not proof of a sentiment cadence through a conversation and not a current-label finding.

## ReleaseTrain documentation audit

The [official documentation](https://releasetrain.io/?view=docs) describes `/api/reddit/query/update-related` as filtering nested `metadata.labeled` and `metadata.predicted` fields. It describes `/api/reddit/query/positive` as documents where `metadata.predicted.positiveScore > 0.5`. It describes `/api/reddit/stats/by-month` as monthly counts for a **labeled training distribution**, while `/api/reddit/stats/summary` is a range summary of total, risky, latest-update, and CVE counts. These descriptions do not state that `positiveScore` is VADER sentiment or that `risky` is the same as the paper's troubleshooting class.

Read-only live API responses on 9 October 2026 were inconsistent in scope: `/api/reddit/count` returned `totalRedditPosts=21470`, `redditCount=12669`, `stackoverflowCount=49`, and `serverfaultCount=20`; `/api/reddit/stats/summary` without dates returned `total=21965`, `risky=3763`, `aboutLatestUpdate=12074`, and `aboutCve=14060`; `/api/reddit/query/update-related?isLabeled=false&isUpdateRelated=true&limit=1&page=1` returned `pagination.total=3763`. The first sampled post carried `metadata.predicted.isUpdateRelated=true`, `metadata.labeled.isUpdateRelated=null`, and `metadata.predicted.positiveScore=0.5946`; it also had a separate `sentiment` object. A dated summary query for 2026-01-01 through 2026-10-09 returned zero, despite a sampled post dated 2026-10-09. These are signs that route totals and date filters cannot be used interchangeably without an endpoint/schema audit. The professor's “3%” should be attributed as his preliminary estimate until its numerator, denominator, time range, and risk definition are documented.

## Paper decision

Preserve the current ICSC manuscript and the historical ICMLA PDF. A sound revision can state the coauthor's sentiment question and report the **negative incremental result** transparently. It may include the historical divergence only with its coverage and title-fallback limitations. The stronger current contribution remains the distinction between detecting a troubleshooting discussion and deciding what engineering action its evidence supports.

Do not claim that sentiment improves classification, that a time cadence has been demonstrated, or that roughly 3% is a verified prevalence. Do not combine the live risk API pool with the reviewed S2 labels. A risk-post cadence study needs a stable sampling frame, documented risk rule, complete date coverage, a numerator and denominator for each time interval, and validation of a human sample. That is a separate study, not a result of the present paper.

## Immediate manuscript path

1. Share this result with Professor Berhe and ask whether he endorses reporting the negative VADER comparison in the current paper while retaining the diagnostic/triage contribution.
2. If endorsed, revise a copy of the manuscript: one research question on incremental sentiment value, one compact methods/results subsection with the paired comparison, and a conservative discussion of the historical 542-post finding. Keep the fresh test and qualitative findings visible; do not selectively hide lower scores.
3. Verify exact page budget, all table values, and coauthor approval before replacing the Overleaf submission draft.

The first decision is scientific scope and coauthor agreement, not another model search.
