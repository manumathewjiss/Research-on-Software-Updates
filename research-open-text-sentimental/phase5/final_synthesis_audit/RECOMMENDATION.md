# Recommendation

Do not draft a merged manuscript yet. One standalone ICSC paper is possible, and the files already support it, but only as a separation paper.

Use three verified blocks and stop there:

- Text-only purpose classification, with reserved macro-F1 0.863 and fresh macro-F1 0.792 both visible (`RESULT_VERSION_RECONCILIATION.json`).
- VADER as a negative result on that task, with the 542-post TPS/GDS analysis kept historically separate (`phase5/sentiment_paper/RESULTS.md`).
- The 237-post diagnostic coding and the 30-case reading as a limit on what a purpose label does not decide (`phase4` PDF).

Do not add the BERT checkpoint, the 324-post cohort, dashboard prototypes, or another model class. More unused artifacts would not make the paper stronger.

The critical flaw to keep out of the draft: nothing in the repository shows that sentiment, the classifier, diagnostic fields, and reviewer actions form one pipeline. Write them as separate descriptions whose connections were tested and did not hold, or were never jointly measured.

Internal provenance stays in the audit. The public paper can cite ReleaseTrain as the retrieval service and the saved dates, and it should keep calling the 542 labels corrected or assigned rather than gold.
