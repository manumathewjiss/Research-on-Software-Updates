# Fresh model-test review guide

**Use with the two blank reviewer workbooks.** Each has 300 posts: 100 are assigned to both reviewers, and 200 are assigned to only that reviewer. The shared rows are hidden so that the initial decisions remain independent. Read only each saved title and original post body. Do not open live Reddit, the collection metadata, old labels, model scores, or the other reviewer's answers. An empty body means use the title alone. Do not guess what an inaccessible screenshot shows.

Reviewers A and B should each fill their own file before comparing answers. If you instead discuss posts while filling the files, tell the analyst: those are **joint decisions**, not independent agreement. Save both original completed files before discussing disagreements; a separate agreed-label file can be created later.

For every row, fill these five fields:

| Field | Allowed answers | Rule |
|---|---|---|
| `about_software` | `yes`, `no`, `unclear` | Is the main topic an app, OS, service, tool, firmware/settings treated as software, or a plausible software failure? Pure physical hardware or unrelated uses of “update” are no. |
| `update_related` | `yes`, `no`, `unclear` | Is the post connected to a software update, upgrade, release, patch, version change, or a problem/change that followed one? A normal software help request with no update link is no. Fill this even if `about_software` is no. |
| `discussion_type` | `technical_troubleshooting`, `general_dissatisfaction`, `other`, `na` | If `about_software` is no/unclear, use `na`. Otherwise classify the **main purpose** of the original post. See below. |
| `confidence` | `high`, `medium`, `low` | How certain are you from the saved text? Use low rather than forcing a guess. |
| `reason` | Short sentence | State the key evidence or why the case is uncertain. |

`technical_troubleshooting` reports a concrete software malfunction or asks how to diagnose, fix, or work around one. An angry bug report can still be troubleshooting. `general_dissatisfaction` mainly criticizes or complains without a substantive troubleshooting purpose. `other` covers news, praise, announcements, feature showcases, and neutral discussion. **Do not call `other` dissatisfaction.**

Synthetic examples (not taken from the test set):

- “After CloudNotes 4.2, export freezes; how can I fix it?” → software yes, update yes, troubleshooting.
- “CloudNotes 4.2 is out; here are the release notes.” → software yes, update yes, other.
- “I dislike the new CloudNotes layout.” → software yes, update yes if the change is tied to the release, general dissatisfaction if the main purpose is criticism.
- “CloudNotes export freezes, but no update is mentioned.” → software yes, update no, troubleshooting.
- “Updated my model-train collection shelf.” → software no, update no, `na`.

The test set will be determined from these human decisions **before** its model predictions are examined. Use `unclear` for insufficient text. API predictions and keyword screens are only collection routes; they are not labels.
