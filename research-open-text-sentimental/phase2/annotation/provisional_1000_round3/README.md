# Review batches 11 through 20

This workbook contains **1,000 different posts**, arranged in ten batches of 100. They were sampled at random from the 1,762 posts that had not yet entered a Phase 2 review batch. At this stage, every remaining untouched post came from the October 5 troubleshooting query. That query is a candidate source, **not a confirmed label**. The 200 reserved test posts and the six uncertain posts from earlier workbooks are excluded.

For **every row**, read the saved title, post body, and replies. Judge `about_software`, `update_related`, and `discussion_type` using the [reviewer guide](../REVIEWER_GUIDE.md). In `decision`, enter:

- `accept` if all three proposed labels are correct;
- `revise` if any proposed label is wrong, then fill **all three** `final_*` fields and explain the change in `reviewer_note`;
- `uncertain` if the saved text does not support a decision, with an explanation in `reviewer_note`.

Save a new copy of the workbook after each batch. The proposed labels are automatic review aids. A proposal becomes a confirmed decision only after you check that row. Check `update_related` especially carefully: in the previous 200 reviewed posts from this query pool, that proposal agreed with Manu's decision on 145 posts. Mentions of versions or updates do not always mean the discussion is about a software update.

The proposal models used the 400 earlier development reviews plus 994 resolved rows from Manu's two assisted-review workbooks. They used title, first 4,000 body characters, and subreddit. They did **not** use query-pool name, old labels, replies, or reserved-test answers. The model's `proposed_confidence` is only a rough attention flag, not a measured probability. These assisted reviews are not independent blind annotations.

The ten CSVs are plain-text copies of the workbook tables. `ANALYST_ONLY_MAPPING.json`, `provisional_labels.json`, and `sampling_manifest.json` preserve the selection and proposal details.

One post (`B20-017`) contained a nonprinting control character. Excel cannot store it, so the workbook display omits that one character; the original saved text remains in the CSV and master JSON.

If all 1,000 posts in this workbook receive resolved labels, **762 posts will remain untouched**, plus the **six** uncertain posts from prior workbooks. Thus **768 posts** will still need a decision if this workbook creates no new uncertain cases.
