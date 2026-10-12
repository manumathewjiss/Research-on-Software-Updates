# Final remaining review workbook

This workbook contains **all 768 posts still needing a decision** after Manu's first three assisted-review submissions:

- **762 untouched posts** in Batches 21–28. Batches 21–27 have 100 rows each; Batch 28 has 62.
- **Six previously uncertain posts** in a separate `Uncertain 6` tab. Their earlier reasons for uncertainty are shown. These six do not have new automatic suggestions.

For Batches 21–28, read every saved title, body, and available reply. Use the [reviewer guide](../REVIEWER_GUIDE.md). In `decision`, write `accept` if all three proposed labels are correct, `revise` if any is wrong, or `uncertain` if the saved text still does not support a decision. For `revise`, fill **all three** `final_*` fields and add a short explanation. For `uncertain`, leave final fields blank and explain why. Every row needs your judgment, regardless of the proposed confidence.

On `Uncertain 6`, there is no proposed answer to accept. Write `resolved` and fill all three final labels if you can decide from the saved snapshot, or `still_uncertain` and a note if you cannot. Keep unresolved cases out of confirmed-label counts; an honest uncertain decision is acceptable.

The 762 untouched posts all came from the professor's October 5 troubleshooting query. That query is a **candidate source, not a label**. The proposals used 400 earlier development reviews and 1,994 resolved decisions from Manu's assisted workbooks, excluding the reserved 200-post test set. They used title, the first 4,000 body characters, and subreddit; no API category or old label was used as an answer. The proposals are review aids, not independent blind annotations or confirmed research labels.

The eight batch CSVs and `uncertain_6_review.csv` provide plain-text versions of the workbook. `ANALYST_ONLY_MAPPING.json` and `sampling_manifest.json` preserve provenance. If every row in this workbook receives a resolved decision, no unreviewed or uncertain posts will remain in the current 3,362-post candidate corpus.
