# Review the reserved 200 new posts

Manu and Professor Berhe each have a separate workbook with the **same 200 posts**. Fill your own workbook independently, without comparing answers or seeing source pools, old labels, sentiment scores, or model suggestions. After both workbooks are finished, we will compare and resolve differences in a separate record. Keep both completed workbooks unchanged.

Judge only the saved title, original post body, and limited reply snippets in the workbook. Do not look up live Reddit posts. The saved replies may be incomplete. Read the original post's **main purpose**; replies may clarify it, but one technical reply does not turn a news post into a troubleshooting request.

Fill all five yellow columns on every row:

| Field | Allowed answers | Rule |
|---|---|---|
| `about_software` | `yes`, `no`, `unclear` | Main topic is an app, operating system, service, tool, software configuration, or software-like firmware/settings. |
| `update_related` | `yes`, `no`, `unclear` | The original post explicitly connects a problem or discussion to an update/release/version change, **including asking or suspecting whether an update caused it**. The cause need not be proved. Use `no` when no such connection is expressed. Use `unclear` when saved text is too thin to decide. A version mentioned only as background is not automatically an update link. |
| `discussion_type` | `technical_troubleshooting`, `general_dissatisfaction`, `other`, `na` | Main purpose of the original post. If `about_software` is `no` or `unclear`, use `na`. |
| `confidence` | `high`, `medium`, `low` | Your certainty from the saved text. |
| `reason` | One short sentence | The text clue supporting your answer. |

`technical_troubleshooting` means identifying, diagnosing, asking how to fix, or offering a concrete fix for a software failure. An angry bug report can still be troubleshooting. `general_dissatisfaction` means criticism or frustration without a real diagnosis or fix purpose. `other` includes news, announcements, praise, neutral tips, and other software discussion. Do **not** put neutral posts into dissatisfaction.

Made-up examples:

- “After CloudNotes 4.2, export crashes. What should I check?” → software `yes`, update `yes`, troubleshooting.
- “Did the CloudNotes 4.2 update cause my export failures?” → software `yes`, update `yes`, troubleshooting, even though the cause is uncertain.
- “CloudNotes 4.2 release notes are out” → software `yes`, update `yes`, `other`.
- “CloudNotes is awful” without a specific problem or fix request → software `yes`, update `no` or `unclear` depending on the text, dissatisfaction.
- “The dice on my shelf look great after I updated the display” → software `no`, update `no`, `na`.

Use `unclear` and/or `confidence=low` when the saved text does not support a firmer answer. Do not guess from the API pool name; it is not shown in your workbook. Do not ask an assistant to fill this reserved set. When finished, return your completed workbook without changing the post text, ids, order, or column names.
