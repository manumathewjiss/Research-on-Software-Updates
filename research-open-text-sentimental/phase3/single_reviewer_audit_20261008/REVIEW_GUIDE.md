# Single-review consistency check

Use the workbook `Manu_Blind_Consistency_Review_120.xlsx`. It contains 120 posts with no previous labels, source pool, model scores, or predictions. This is a second judgment by one reviewer, made without seeing the previous answer. It can measure consistency with the previous review record after the workbook is returned. It **cannot** measure agreement between two independent reviewers.

## What to fill

For every row, fill the five yellow columns: `about_software`, `update_related`, `discussion_type`, `confidence`, and `reason`. Leave the post text and audit ID unchanged. Save the workbook with your answers and send that completed copy back.

Some posts are longer than the visible row height. Click the `post_body` or `saved_reply_context` cell and read the complete contents in Excel's formula bar before deciding.

| Field | Values | Rule |
| --- | --- | --- |
| `about_software` | `yes`, `no`, `unclear` | Is the main subject an app, operating system, online service, software tool, firmware, or software setting? |
| `update_related` | `yes`, `no`, `unclear` | Is the post connected to an update, patch, release, version change, or upgrade? |
| `discussion_type` | `technical_troubleshooting`, `general_dissatisfaction`, `other`, `na` | Choose the post's main purpose from the saved text. Use `na` when `about_software` is `no` or `unclear`. |
| `confidence` | `high`, `medium`, `low` | How sure are you of the decision? |
| `reason` | One short sentence | Explain the decisive clue or ambiguity. |

**Update connection:** mark `update_related=yes` when the author explicitly says, suspects, or asks whether an update, patch, release, or upgrade caused or affected the issue. The author does not have to prove causation. Mentioning an unrelated version number without a stated connection may be `no` or `unclear`.

**Discussion type:** `technical_troubleshooting` means the main purpose is identifying, diagnosing, fixing, or sharing a concrete fix for a software problem. `general_dissatisfaction` is primarily criticism or frustration without a real troubleshooting purpose. `other` includes news, praise, release notices, neutral advice, and other software discussion. A problem report can be angry and still be troubleshooting. A technical word in a complaint is not enough by itself.

Read the title, body, and saved reply context provided. Judge the saved snapshot only. Do not open live Reddit, old labels, analyst mapping, model results, or source-pool files while filling the workbook. If text is too thin, use `unclear` where appropriate and `low` confidence; do not guess to match an imagined answer key. Do not use a chatbot to fill the answers.

The sample deliberately includes several kinds of posts rather than their natural proportions. Do not interpret its category totals as prevalence in the full collection.
