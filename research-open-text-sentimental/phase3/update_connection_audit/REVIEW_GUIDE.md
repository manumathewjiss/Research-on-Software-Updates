# Update-connection review

## Order

1. Complete **Adjudicate_22_Differences.xlsx** first. It shows the old and new recorded answers. Fill the yellow `final_...` columns and `final_reason`. You may agree with either earlier answer or choose a different permitted answer. Read all saved text; do not rely on the short reason alone.
2. Return that workbook. The rule will be locked and any unclear wording resolved before the larger packet is reviewed.
3. Only then complete **Targeted_Update_Connection_254_Blind.xlsx**. It contains 204 phrase-flagged candidates and a random sample of 50 unflagged posts; which group a post came from is hidden. Fill the five yellow answer columns. Previous labels are not shown.

## Working rule

Mark `update_related=yes` when the original post is substantively about a software update, upgrade, patch, new release, or version change. This includes release announcements, advice about whether or how to update, a failed update process, and an issue the author says, suspects, or asks whether an update caused or affected. The author does not need to prove that the update caused the issue. Retrospective accounts of an upgrade breaking software also count.

Mark `no` when a version number is only background, “update” means a progress report rather than a software change, or someone else alone introduces an update in a reply. An update tried as a generic fix for an otherwise unrelated problem is not enough by itself. In the author-confirmed A022 example, installing firmware is recommended to prevent a pre-existing defect; this was judged `no` because the update did not cause or change the reported issue. In A049, submitting a new app version changed the Play Console review outcome; this was judged `yes`. These two decisions are specific boundary examples, not automatic keyword rules. Use `unclear` when the saved text does not establish the connection.

For `discussion_type`, use `technical_troubleshooting` for a concrete software problem being diagnosed, fixed, or reported with a concrete fix; `general_dissatisfaction` for criticism without a troubleshooting purpose; `other` for announcements, praise, advice, and other software discussion; and `na` when software scope is `no` or `unclear`.

Use the title, saved body, and saved reply context. A long cell may show only its beginning; click it and read the complete formula-bar text. Do not open live Reddit while reviewing. Leave the post IDs and text unchanged. These workbooks do not update the master or the historical model results.

The packets exclude the reserved and fresh tests. The 22 differences do not repeat in the targeted 254 rows. The 204 phrase flags are candidates, **not** confirmed mistakes, and the random 50 check whether the screen misses connections.
