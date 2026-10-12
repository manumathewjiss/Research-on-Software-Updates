# Review instructions: 300 additional posts

These are **300 new posts** from the saved October 5 API downloads. Manu and Professor Berhe each have a separate sheet containing the same posts in the same order. All answer cells are blank. The API groups are hidden and are **not** correct answers.

## Open your own file

| Reviewer | File |
|---|---|
| Manu | `Manu_Blind_Review_300_Posts.csv` |
| Professor Berhe | `Berhe_Blind_Review_300_Posts.csv` |

Use the rules below. Work separately and save separate completed files. After both are complete, compare answers and resolve disagreements together. Keep both original completed files unchanged.

Do not open `ANALYST_ONLY_ID_MAPPING.csv` while reviewing. It contains the API source group, Reddit id, and other details that could influence a judgment. Judge **only the saved text in your sheet**; do not look up live Reddit posts. The shown replies are limited and may not be a complete conversation.

## Fill these five columns on every row

| Column | Allowed answers | Decision |
|---|---|---|
| `about_software` | `yes`, `no`, `unclear` | Is the main topic an app, operating system, software service, software tool, configuration, or software-like firmware/settings? |
| `update_related` | `yes`, `no`, `unclear` | Is there a clear connection to a software update, release, patch, upgrade, version change, or change after one? A general help request with no such connection is `no`. |
| `discussion_type` | `technical_troubleshooting`, `general_dissatisfaction`, `other`, `na` | What is the original post mainly trying to do? Use `na` if `about_software` is `no` or `unclear`. |
| `confidence` | `high`, `medium`, `low` | How sure are you from the saved text? |
| `reason` | One short sentence | State the main evidence for your decision in your own words. |

For `discussion_type` when `about_software=yes`:

- `technical_troubleshooting`: identifies, diagnoses, asks how to fix, or provides a concrete fix for a software problem. An angry tone does not cancel a genuine technical request.
- `general_dissatisfaction`: mainly criticism or frustration without a substantive diagnosis or fix purpose.
- `other`: news, release announcements, praise, neutral discussion, tips, or any other software discussion that is neither of the above. **Do not call `other` dissatisfaction.**

Read the title, body, and shown replies, then judge the **original post's main purpose**. Replies may clarify the original request, but one technical reply does not turn a news announcement into a troubleshooting post. When the text is too thin, use `unclear` for the field you cannot judge and/or `confidence=low` rather than guessing.

**Made-up examples (not sampled posts):**

- “After CloudNotes 4.2, export crashes; what log should I check?” → software `yes`, update `yes`, troubleshooting.
- “CloudNotes 4.2 is out today; here are the release notes” → software `yes`, update `yes`, `other`.
- “CloudNotes keeps redesigning the menu and I hate it” → software `yes`, update `yes` only if a release/change is clear, general dissatisfaction.
- “How do I repair a broken formula in SpreadsheetApp?” with no update link → software `yes`, update `no`, troubleshooting.
- “My robot figure shelf after rearranging it” → software `no`, update `no`, `na`.

## Before and after the 300 rows

1. Resolve the five disagreements from the completed 100-post pilot together and record the final decisions in `../submissions/2026-10-06/DISAGREEMENTS_TO_RESOLVE.csv`. If that discussion changes a rule materially, write the revised rule in this guide before either person begins the 300-post pass.
2. Fill only your own sheet. Leave `review_id`, `sheet_order`, and post text unchanged. Save the file with the same CSV columns and all 300 rows.
3. Exchange no answers until **both** sheets are complete. Then run agreement checks, discuss differences, and make a separate final-label file. Never overwrite the two original reviews.

This pass asks for the **core discussion labels only**. Information completeness and conversation outcomes need different instructions and are planned as a later, smaller review of appropriate posts. Do not add those judgments to `reason` unless they naturally explain the core label.
