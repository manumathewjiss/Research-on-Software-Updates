# Independent review guide for the 200-post reliability sample

**Version 1.0, issued 2026-10-07. No answers have been filled.** This combines the current Phase 2 discussion rules, the later update-connection boundary decisions, and diagnostic guide v1.0. If a rule changes after review begins, record the version change; do not silently rewrite either first-pass sheet.

**Which file:** Reviewer A fills `Reviewer_A_Independent_200_Blank.xlsx`; Reviewer B fills `Reviewer_B_Independent_200_Blank.xlsx`. The same 200 posts appear in the same order. Fill only the yellow answer columns, E through Q. Save a new completed copy with your own name or letter in the filename. Do not edit the ID, title, body, or reply columns.

## What the reviewers will do

Each reviewer receives a separate sheet with the same 200 randomly assigned IDs, saved title, saved body, and saved reply context. Work alone on the entire sheet. Do not see the previous labels, collection pool, model outputs, the other reviewer's answers, or live Reddit pages. Return the first completed version before discussing any post. If you remember reviewing a sampled post before, tell the analyst after submitting your first pass; this does not invalidate the sheet, but it must be disclosed.

For **every** row, answer `about_software`, `update_related`, `discussion_type`, `confidence`, and `reason`. Allowed values:

| Field | Allowed values | Meaning |
|---|---|---|
| `about_software` | `yes`, `no`, `unclear` | Is the main topic software, an app/OS/service, firmware, software settings, or software behavior? Pure hardware with no software angle is `no`. |
| `update_related` | `yes`, `no`, `unclear` | Is the original post substantively connected to a software update, patch, upgrade, new release, or version change? |
| `discussion_type` | `technical_troubleshooting`, `general_dissatisfaction`, `other`, `na` | Main purpose of the original post. Use `na` only if software scope is `no` or `unclear`. |
| `confidence` | `high`, `medium`, `low` | Confidence in the overall row; use `low` for a borderline decision. |
| `reason` | short text | A short explanation grounded in the saved text. |

### Scope boundaries

- `technical_troubleshooting`: a concrete software failure or an attempt to diagnose, fix, or report it. Frustration does not erase a concrete problem.
- `general_dissatisfaction`: mainly criticism without a substantive troubleshooting purpose.
- `other`: announcements, neutral questions/advice, praise, feature observations, or other software discussion. Never treat `other` as dissatisfaction by default.
- The author does **not** need to prove an update caused the problem. If they explicitly state, suspect, or ask whether an update caused or changed it, mark `update_related=yes`.
- An update tried as a generic fix for an otherwise unrelated existing problem is usually `no`. In the previously adjudicated A022 boundary, a preventive firmware update was recommended for an existing defect and the decision was `no`. In A049, submission of a new app version changed the review outcome and the decision was `yes`. These are boundary principles, not keyword shortcuts.
- A version number given only as background does not by itself establish an update connection. A reply alone mentioning an update does not change the original post's update connection.
- A software help question can be `about_software=yes` and `update_related=no`.

## Diagnostic details

Only if **you** choose `technical_troubleshooting`, mark each of the following eight fields `present`, `not_observed`, or `unclear`: `software_product`, `identifiable_release`, `environment`, `specific_symptom`, `reproduction_context`, `error_evidence`, `attempted_remedy`, `help_request`. Otherwise leave all eight blank.

For these eight fields, use **only the original title and body**. Replies may inform the three scope/type fields but cannot supply a diagnostic detail missing from the original post. `not_observed` means absent from the saved text, not absent in reality. Use `unclear` for explicitly referenced but inaccessible evidence or genuinely ambiguous wording.

| Field | Mark `present` for | Do not count |
|---|---|---|
| `software_product` | Named affected app, OS, service, tool, or component | Device alone |
| `identifiable_release` | Distinct version/build, patch, release name, or unambiguous dated cycle | Generic “latest update” |
| `environment` | Device model, OS/platform, host, deployment context, or relevant configuration | Merely repeating the affected product |
| `specific_symptom` | Concrete wrong behavior | “Bad update” alone |
| `reproduction_context` | Action or condition under which failure occurs | “Since updating” when it is only timing |
| `error_evidence` | Error code/message, log, trace, diagnostic output, or described visible evidence | The generic word “error” |
| `attempted_remedy` | Fix/workaround the original poster actually tried | A suggestion to try something later |
| `help_request` | Explicit request for explanation, diagnosis, fix, or workaround | Mere presence of a question mark |

## Synthetic examples

- “After version 4.2, opening Settings crashes; reinstalling did not help.” → software `yes`, update `yes`, troubleshooting. Product/release/symptom/context/remedy are visible; an error code is not.
- “Version 4.2 is available. Should I install it?” → software `yes`, update `yes`, `other`; asking for preventive advice is not itself a current failure.
- “The latest redesign is ugly and annoying.” → software `yes`, update `yes` if the redesign is expressly tied to the release; `general_dissatisfaction` if criticism is the main purpose.
- “A patch might prevent this old defect from happening again.” → assess whether the patch changed the reported issue. A preventive suggestion alone is not enough.

## Submission and later analysis

Do not exchange answers or discuss individual posts before both first-pass sheets are saved. The analyst calculates initial agreement from those immutable files. Afterwards, disagreements can be discussed in a **separate adjudication file**. Final consensus must never be reported as initial agreement. The earlier jointly reviewed sheets also must not be described as independent first passes.
