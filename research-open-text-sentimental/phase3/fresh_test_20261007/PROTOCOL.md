# Fresh-to-study model test: frozen review protocol

**Status:** Candidate collection and blind review assignment complete on 2026-10-07. No human answers, model predictions, or new test scores have been filled. The earlier model specification in `../FINAL_TEST_PLAN.md` remains fixed.

## Candidate collection and sample

The professor's broad read-only `GET /api/reddit/query/update-related?isLabeled=false&isUpdateRelated=true` route returned 3,718 unique records across eight pages. Raw responses, response dates, URLs, and hashes are preserved in `raw/`. The API's update-related output is a **candidate filter**, not a human label. Of the 3,718 records, 2,842 Reddit IDs already occurred in the 3,362-record Phase 2 master. Of the remaining 876 IDs, 12 near-identical text duplicates were excluded using normalized title+body character-5-gram Jaccard ≥0.92, leaving 864 candidates. `excluded_duplicates.json` records the excluded IDs and matches. No old master ID occurs in the 864.

From the sorted 864 IDs, `select_review_sample.py` drew 500 by simple random sampling without replacement using seed 20261007. The inclusion probability in this candidate frame is 500/864. There are 45 posts dated October 5, 2026 or later; the rest are older posts newly added to this study. Thus this is an **unseen-ID test**, not a wholly prospective future-period test. The selected posts span 66 subreddits and nine have no saved body. The sample was drawn without consulting the prior task labels or the troubleshooting model.

## Human review

The 500 masked IDs are assigned to two reviewers: 100 appear on both sheets and 200 only on each respective sheet. Each workbook therefore has 300 rows. The 100 shared rows were randomly selected and hidden as a set from the reviewers. Both reviewers should use `TEST_REVIEW_GUIDE.md`, read only saved title/body, and preserve their first independent answers before discussing any case. If the review is joint, record it as joint rather than independent agreement.

Record `about_software`, `update_related`, `discussion_type`, `confidence`, and `reason` for each assigned row. API predicted labels, source categories, old labels, and model scores are absent from the workbooks. After both completed files are returned, validate every row, compute initial agreement on the 100 shared IDs if they were independently reviewed, and record any reconciliation in a separate file. The final test population is posts judged `about_software=yes` and `update_related=yes`; its size and class mix are **not known yet**. Do not force `unclear` cases into a class or discard difficult rows silently.

## One-shot model evaluation

Freeze the reviewed test labels and exclusions before scoring. Fit the fixed title+body TF-IDF logistic-regression specification on `../revised_development_v2/development_v2.jsonl` using the existing development protocol and threshold. Score the finalized new S2 test only once. Report both classes, macro-F1, confusion matrix, uncertainty intervals, source/text-availability breakdowns, and the number of excluded scope-unclear posts. If the test has fewer than roughly 75 non-troubleshooting update posts, report the limitation rather than selecting favorable results or silently adding cases after seeing predictions. The original 159-post reserved test is a separate historical result and is not merged with this one.

The candidate source is one API's predicted-update pool, so this evaluation does not establish Reddit-wide prevalence or automatic discovery from the full Reddit stream. Reviewers' independent status and label provenance must be stated exactly as completed.
