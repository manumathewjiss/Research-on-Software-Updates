# Paper comparison

Three study documents were read in full. Page counts are from the PDFs on disk.

| Document | Path | Pages | Decision it studies |
|---|---|---:|---|
| ICMLA manuscript | `Papers/Distinguishing_Technical_Problem_Solving_and_General_Discontent_in_Reddit_Software_Update_Discussions (3).pdf` | 6 | TPS vs GDS on 542 posts, plus author–community divergence |
| Beyond Troubleshooting Detection | `phase4/manuscript_icsc2027/overleaf/main.pdf` (same text as `output/pdf/ICSC_2027_Complete_Author_Review.pdf`) | 8 | Troubleshooting vs other update discussion; diagnostic fields; first-pass reviewer actions |
| Beyond Polarity | `phase5/sentiment_paper/manuscript/main.pdf` | 6 | Whether VADER adds information to that purpose task; historical 542 kept separate |

`research-open-text-sentimental/main.pdf` is not a study manuscript. It is a 10-page KES 2025 paper by other authors about LLM issue tickets. It was not used as evidence.

## What each paper asserts

**ICMLA.** Macro-F1 0.659 and TPS-F1 0.463 for multinomial Naive Bayes under stratified five-fold cross-validation. Divergence 0.371 vs 0.287, p = 0.009. The abstract says TPS filtering can help teams find troubleshooting discussions and that divergence adds insight into community response. Reviews in `phase2/sources/icmla_reviews.txt` (paper 483): one Accept and two Weak Rejects. Technical soundness was scored Poor by the first Weak Reject. `phase2/RESEARCH_AUDIT.md` later showed the keyword-first VADER rule, the title-only author fallback (205 posts), non-significant slope and early–late tests, and that the 80-row check was not an independent rating.

**Beyond Troubleshooting Detection.** Does not use sentiment. Reports text-only fresh macro-F1 0.792 after an earlier reserved test, weaker performance on other update discussion, missing reproduction context and error evidence in a 237-post coding, and divergent first actions in 30 cases. The abstract says these observations are exploratory and do not establish causal effects or downstream benefit. The reserved 0.863 score is easy to miss beside 0.792; the polarity paper states both.

**Beyond Polarity.** Does not rerun the fresh test. States both saved text-only scores. Development title/body sentiment difference +0.001 with an interval that includes zero. Fair full-thread comparison is lower by 0.027 on 797 posts. The 68 confirmed dissatisfaction posts do not reproduce the mean valence gap. ReleaseTrain is named as the retrieval service; TPS/GDS endpoints are candidate pools (27 March 2026 and 5 October 2026). No 3% claim.

## Overlap and conflict

Both IEEE drafts already refuse the ICMLA closing implication that a label, or a valence gap, tells an engineer what to do. They use different negative classes. The ICMLA negative class is general discontent. The current negative class is other update discussion, of which only 68 Reddit-URL development posts are typed `general_dissatisfaction`.

Numbers that must not be merged:

- ICMLA Naive Bayes macro-F1 0.659 is cross-validation on 542 TPS/GDS posts. Phase 3 Naive Bayes on the 2,050-post task is 0.551 and predicts troubleshooting for almost every post (`phase5/sentiment_paper/RESULTS.md`). Same algorithm name, different task.
- BERT test macro-F1 0.635 is a 40-row undersampled holdout (`tps_gds_classification/outputs/bert/metrics.json`). It is not comparable to 0.792.
- The 324-post automated cohort is a third sample (`README.md`, `DATA_CARD.md` C2).

A combined manuscript can cite the ICMLA paper as history and the audit as the reason the claim was narrowed. It cannot add the ICMLA model table, the BERT checkpoint, or the 324-post chart as further evidence that the current classifier or the sentiment features work.

## What a single ICSC paper could honestly contain

One narrative, already supported, in this order:

1. Purpose classification on the current label, with both text-only tests (0.863 reserved, 0.792 fresh).
2. Sentiment as a negative result on that same task, historical 542 reported separately.
3. Diagnostic visibility and the 30-case reading as a bound on what the purpose label does not decide.

That is one paper about separation. It is not a paper about a better model. Adding the unused checkpoints or the sibling prototypes would make the paper look broader without answering a new question.
