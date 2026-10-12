# Sentiment-centered paper blueprint (working; evidence gates apply)

## Main claim to investigate

Sentiment in a software-update conversation may describe the author's experience, but its value for identifying technical troubleshooting must be measured against the actual words and context of the post. This is a question, not a promised positive finding.

## Candidate paper questions

1. **Purpose:** Within reviewed software-update posts, how well do post text and sentiment separately identify troubleshooting? The negative class for current S2 is *other update discussion*, not historical GDS.
2. **Incremental value:** Does sentiment add reliable predictive information to a text classifier when evaluated on the same grouped folds and, after model freeze, protected tests?
3. **Conversation:** Among posts with saved comments, how do author and community sentiment differ by discussion purpose, and how sensitive are these patterns to title-only fallbacks, missing comments, bots, and technical vocabulary?
4. **Outcome, conditional:** If and only if credible human-reviewed labels can be established, do observable author replies indicate that a proposed solution worked? Otherwise describe proposal/acknowledgment patterns without calling them resolution.

## Study architecture

- Historical 542-post snapshot: reproduce ICMLA findings, correct method descriptions, and explicitly audit comment coverage and time claims.
- Reviewed Phase 2 collection: retain its scope/purpose distinctions and frozen tests; measure title/body sentiment incrementally on the existing development folds. The first VADER compound experiment found no reliable gain.
- Conversation subset: join archived Reddit IDs to archived raw snapshots, quantify who has stored comments and replies, and analyze only what those snapshots actually show. Do not interpret missing comments as no replies.
- ReleaseTrain: document the API candidate-selection process and risk-score definitions. Do not train on route names or treat the live risk collection as human labels. Do not use the claimed 3% as a fact until its calculation is reproducible.
- Current diagnostic coding and two-reviewer case study: retain only where they directly help explain why technical purpose and sentiment cannot by themselves establish the next engineering action. Otherwise move to a separately positioned paper, since an eight-page manuscript cannot give two unrelated studies adequate space.

## Preliminary saved-data gate (Cursor audit; verify final report)

The first join audit finds 2,050 Reddit-URL S2 development posts, of which 797 have at least one stored comment and 474 have an original-poster reply. Stored comments are only about 38% of the recorded `num_comments` total in the 2,080-row S2 development snapshot. The missingness differs by class: 560/1,686 troubleshooting posts and 237/394 other-update posts have a stored comment. Therefore any comment-based comparison is a selected subset, not a representative result for all reviewed posts.

Only 68 of the 2,080 S2 development posts have the revised `general_dissatisfaction` type. The other 326 negative-class posts are `other`. A current-model result cannot honestly be titled TPS-versus-GDS merely by renaming the negative class. The historical 542-row TPS/GDS task and the revised S2 task need separate denominators and labels.

The audit has not identified any human-confirmed resolution outcome field. We cannot state that a user reply helped the original poster rectify an issue without new outcome review.

## Development result after a matched full-thread comparison

Cursor's corrected development run on the 797 comment-available Reddit-URL S2 posts gives macro-F1 **0.866** for TF-IDF on the saved title, body, and comments, versus **0.839** for the same text plus VADER-derived role sentiment features (difference −0.027; post-bootstrap 95% interval −0.049 to −0.004). This is a retrospective, selected-subset comparison, and the uncertainty procedure should be checked against duplicate groups. It does not support a claim that sentiment adds predictive value beyond the words of the same conversation. The 2,050-post pre-discussion comparison also had no reliable gain (+0.001, interval spanning zero). These are development findings, not protected-test scores.

On the restricted current task of 1,658 troubleshooting posts versus 68 confirmed general-dissatisfaction posts, initial VADER means were −0.064 and −0.068: almost identical. This directly challenges a simple claim that negative tone distinguishes technical troubleshooting from dissatisfaction. The restricted sample is highly imbalanced and should remain exploratory.

## Required evidence before manuscript lock

- Stable mapping between reviewed IDs and saved comment snapshots, with coverage by class and source.
- A fair same-fold comparison of text, sentiment, and text-plus-sentiment, with duplicate grouping and training-only feature fitting.
- Error analysis showing what changes because of sentiment, including whether VADER misreads technical words such as 'crash' or 'error'.
- If comparing sentiment tools, a human-checked sentiment sample from this Reddit corpus or a clearly qualified comparison of unvalidated proxy scores.
- Protected-test evaluation only after the final feature design is frozen; report both initial and fresh test results.
- Claims about resolution require an explicit outcome definition and human review of complete-enough threads. A reply suggesting a fix and an author saying it worked are different observations.
- An accurate source account for the 30 conflicting-source records; do not state that all 3,362 URLs are verified Reddit URLs.

## Possible contribution even if sentiment does not lift F1

A rigorous negative finding can still be useful if it explains **why** a general social-media sentiment score is insufficient for technical-purpose detection, verifies that with reviewed update posts, and contrasts post-level polarity with conversation roles and diagnostic context. It should not be sold as a new sentiment classifier or a validated risk-cadence detector.

## What would stop this rewrite

If saved comments match too few reviewed posts, if conversation coverage is strongly class-dependent, or if no human basis exists for interpreting sentiment scores, then a broad claim about author/community cadence would not be supported. We would retain the narrower post-level comparison and the current engineering-decision paper rather than force a sentiment-centered submission.
