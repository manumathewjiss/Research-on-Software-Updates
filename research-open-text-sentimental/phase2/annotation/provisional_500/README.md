# Five batches of 100 posts for Manu's review

The five `batch_*_review.csv` files contain **500 different posts** that had no Phase 2 review when sampled. Each batch has 50 posts from the original 542-post file, 25 from the October 5 general-discussion query, and 25 from the October 5 troubleshooting query. The source pools only control sampling; they are not correct answers. The 200 reserved test posts are absent.

Open one batch at a time. For **every row**, read the title, post body, and any saved replies, then compare your judgment with the five `proposed_*` fields. Use the current [reviewer guide](../REVIEWER_GUIDE.md) for `about_software`, `update_related`, and `discussion_type`. The suggestions came from text rules and a small model trained on the 400 already-reviewed development posts. Expect errors, especially for software scope, general dissatisfaction, mixed posts, and the meaning of “update.” They are not confirmed labels.

In `decision`, write:

- `accept` if you read the post and agree with **all three** proposed label fields;
- `revise` if any proposed field is wrong, then fill **all three** `final_*` fields and explain your correction in `reviewer_note`;
- `uncertain` if you cannot decide from the saved text, with the reason in `reviewer_note`.

For `accept`, leave the `final_*` cells blank. The intake step will copy the accepted proposed values into the confirmed fields and preserve the review decision. For `revise`, do not leave any `final_*` field blank. `reviewed_at` is an optional date/time record. Save the file under a new name so the original batch stays intact. Return each completed batch when ready; they can be processed separately. Do not copy down `accept` without reading each post.

The workbook delivered to Manu has the same five batch tables, plus a short instruction tab. The CSVs are plain-text backups. `provisional_labels.json` records the proposals. `ANALYST_ONLY_MAPPING.json` and `sampling_manifest.json` preserve provenance and sampling details; they are not needed while reviewing.

The proposal method uses the original post's title and body, plus the subreddit. It does **not** use the old two-class label, API source-pool name, reserved-test answers, or replies. Replies are displayed for your judgment. An internal check on the 400 development posts showed that the model struggled especially with the rare general-dissatisfaction class. The final mixed rule/model proposals have not been independently evaluated. This is an assisted review workflow, not an independent blind annotation study. Any paper description must reflect the completed human decisions and the actual review process.

`proposed_confidence` is only a rough flag for your attention, **not** a measured probability. Review high, medium, and low proposals alike.
