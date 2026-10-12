# Diagnostic-detail codebook v0.2 — proposed revision

**Status:** design proposal after the 50-post pilot. No pilot answer has been changed. Do not use this guide to reinterpret the first-pass workbook silently. Use it only for a separately recorded repeat review and, if it works, a later main study.

## Evidence source and answer values

Read the saved title and original body only. Do not infer from subreddit, API source, replies, inaccessible images, or external knowledge. For each field choose `present` (explicitly visible), `not_observed` (not visible in this snapshot), or `unclear` (text or image points to a detail but its value cannot be determined). A missing body is recorded separately and does not make all answers `unclear`.

First verify `troubleshooting_check` (`yes`, `no`, `unclear`). If `no` or `unclear`, explain why and do not complete detail fields. Review flags do not overwrite the Phase 2 label.

## Proposed core fields

| Field | `present` rule | Important boundary |
|---|---|---|
| `software_product` | Names the app, OS, service, tool, or component affected. | A device alone is not the software product. |
| `identifiable_release` | Names a version, numbered patch, dated release, or distinct release name. | “Latest update” or “after updating” without identification is `not_observed` here; update linkage is already a separate Phase 2 field. |
| `environment` | Names a device/hardware model, OS, browser platform, host, deployment context, or relevant configuration. | Do not count the affected app name again as environment. |
| `specific_symptom` | Describes concrete wrong behavior, such as a login screen going blank or an install failing. | “Bad update” or “it broke” alone is insufficient. |
| `reproduction_context` | States an action or condition under which the wrong behavior occurs, such as opening settings, waking from sleep, or attempting installation. | “After the update” only states timing; do not count it unless the failure occurs during the update action itself. |
| `error_evidence` | Gives a specific error message/code, log/trace, diagnostic output, or text describing visible evidence. | A generic “error” or an image link whose content is unavailable is not an observed error message; use `unclear` for inaccessible visual evidence. |
| `attempted_remedy` | Describes something the author tried **to fix or work around the reported failure**. | Creating the initial setup, checking a setting, or taking a diagnostic screenshot is not a remedy unless explicitly tried as a fix. |
| `help_request` | Explicitly asks someone to diagnose, explain, fix, or suggest a workaround. | A report can be troubleshooting even without a direct question. |

`result_after_attempt` is **not** in this proposed core list because the first pilot showed it duplicated `attempted_fix` perfectly. During a small repeat review, record any counterexamples in notes: remedy described but no outcome, or diagnostic check with an observed outcome. If many occur, we can restore a carefully defined outcome field.

The guide still needs a pilot check. A single reviewer's ability to fill fields once does not establish that these definitions are stable. Review a masked subset under this revised guide and record changes rather than replacing first-pass answers. Changes can reflect the new rules, so do not report them as a consistency score.
