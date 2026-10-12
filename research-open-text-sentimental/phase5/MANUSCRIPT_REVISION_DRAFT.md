# Candidate manuscript revision — for coauthor review

This is a separate writing draft. It does not replace the current Overleaf manuscript. Its sentiment result is based on development folds only; it must not be described as a new held-out result.

## Suggested research question

**RQ4.** Does title-and-body sentiment add useful information beyond lexical text features when identifying troubleshooting posts within reviewed software-update discussions?

This is narrower and testable. The distinct question about the frequency or sentiment cadence of ReleaseTrain risk posts has not been evaluated and is not included as a result.

## Revised abstract candidate

Software-update discussions contain fault reports, reactions, advice, and general conversation. Detecting a troubleshooting post is useful, but it does not establish which engineering response the available evidence supports. We study this distinction in a reviewed collection of 3,362 candidate posts. Within update-related posts, a title-and-body text classifier is evaluated on an initial reserved test and a separate fresh test. We also code visible diagnostic information and analyze how two independent software-engineering reviewers explain first-pass decisions for 30 intact posts. To revisit the sentiment question from our earlier work, we compare the text classifier with VADER sentiment alone and with a text-plus-sentiment model on fixed, grouped development folds. Sentiment alone performs poorly, and adding one VADER score yields no reliable improvement over text features. The earlier author–community sentiment gap can be reproduced, but incomplete comment capture and title-only fallbacks limit its interpretation. The case study shows that reviewers can cite similar evidence yet select different first actions. Together, the findings show that discussion purpose, emotional tone, visible diagnostic evidence, and engineering response are related but distinct. Sentiment provides descriptive context in this corpus; it does not replace purpose detection or determine a first-pass decision.

## Methods insert: incremental sentiment comparison

We evaluated whether sentiment supplies information beyond post text for the revised two-class task. The primary comparison used 2,050 reviewed development posts with Reddit URLs that were judged to concern software and an update; 1,658 were troubleshooting and 392 were other update discussion. Exact and near-duplicate groups remained within the same fold. We reused the saved five outer folds and the existing word-unigram/bigram TF-IDF logistic regression. VADER supplied a single compound score computed from the saved title and body, excluding comments and metadata. We compared sentiment alone and text plus sentiment against the text model. Sentiment scaling and threshold selection occurred within each training fold. Outer-fold labels were not used to set thresholds. We did not use the protected reserved or fresh test sets to choose this feature.

## Results insert: incremental sentiment comparison

With thresholds selected within training folds, text alone achieved macro-F1 0.832; VADER alone achieved 0.534; and text plus VADER achieved 0.833. The paired difference between the combined and text-only models was +0.001 (95% bootstrap interval −0.012 to +0.015). This interval includes plausible small gains and losses, so the experiment does not establish a useful incremental benefit from the VADER compound score. A mixed-source development sensitivity analysis led to the same conclusion. These results concern a specific post-level sentiment representation; they do not show that every possible sentiment signal is uninformative.

## Discussion insert: historical conversation sentiment

The earlier 542-post analysis found greater absolute author–community sentiment divergence in posts labeled technical problem solving than in posts labeled general discontent (0.371 versus 0.287). We reproduced this saved result, but 205 author tracks use the title because no author body or comment was available, and stored comments cover about 59% of recorded comment counts. When title-only tracks are considered separately, the class differences are less conclusive. Tests of author sentiment slope and early-to-late change also do not establish different temporal trajectories. We therefore treat the divergence as exploratory description of that historical collection. It is not evidence that sentiment cadence predicts current troubleshooting labels or that sentiment caused a particular engineering decision.

## Required corrections before this text enters a paper

- Check the sentence in the current paper asserting that every one of the 3,362 records came from Reddit. The preserved source audit identifies 30 `so_` records with non-Reddit URLs in the development snapshot. Describe the sampling frame accurately rather than concealing this discrepancy.
- Keep both existing protected-test results, including the lower fresh-test estimate.
- Do not claim the ReleaseTrain `positiveScore` field is a VADER score, or interpret its `risky` count as troubleshooting prevalence without documentation.
- If the journal/conference page limit cannot hold RQ4 and its limitations clearly, retain the current paper and prepare the sentiment analysis as a separate follow-up rather than compressing it into a misleading claim.
