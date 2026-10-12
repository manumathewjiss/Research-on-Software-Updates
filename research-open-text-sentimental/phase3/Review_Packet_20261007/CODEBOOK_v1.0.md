# Diagnostic-detail review guide v1.0

**Frozen for the main diagnostic sample, 2026-10-07.** This guide follows the 50-post feasibility pilot and 15-post check. Keep their submitted answers unchanged. Any later rule change needs a new version and a recorded reason.

## What to read

Use only the saved post title and original body in the review sheet. Do not use the subreddit, collection route, old labels, model scores, comments, live Reddit page, or an inaccessible image. Mark a detail `present` only when visible in this text. `not_observed` means it is not visible in this saved snapshot, **not** that the real-world detail does not exist. Use `unclear` when the text explicitly points to evidence that cannot be read or when its meaning is genuinely ambiguous. A blank body does not automatically make every field unclear.

First answer `troubleshooting_check`: `yes`, `no`, or `unclear`. Choose `yes` if the post reports a concrete software failure, seeks to understand or fix one, or describes a technical malfunction. A direct question is not required. Choose `no` when the post is mainly news, general opinion, feature request, or another discussion without a concrete failure. Choose `unclear` when the saved text is insufficient. If `no` or `unclear`, leave all eight detail fields blank and explain why in `evidence_or_note`. This check flags possible source-label problems; it does not change the Phase 2 label automatically.

For each detail field choose `present`, `not_observed`, or `unclear`:

| Field | Mark `present` when the saved text explicitly gives | Boundary |
|---|---|---|
| `software_product` | The affected app, OS, service, tool, or software component. | A device alone is not software. |
| `identifiable_release` | A specific software version/build, numbered patch, distinct release name, or unambiguous dated release cycle relevant to the reported problem. | “Latest update,” “after updating,” or a generic “Windows update” has no identifiable release. “Windows 11” or “Firefox 145” counts as a named major/software version even if the exact patch is not known. If the post says “February **or** March update,” no unique cycle is identified; mark `not_observed`. Do not assume a named installed version is the cause of the failure. |
| `environment` | A device/hardware model, OS, browser/platform, host, deployment context, or relevant configuration. | Do not count the affected product name again as the environment. |
| `specific_symptom` | Concrete wrong behavior: e.g., login goes blank, install fails, or an app crashes on opening. | “Bad update” or “it broke” alone is too vague. |
| `reproduction_context` | An action or condition under which the wrong behavior occurs: e.g., opening Settings, waking from sleep, or attempting installation. | “Since updating” is timing only. It counts only if the failure occurs during the update action itself. |
| `error_evidence` | A specific error message/code, log, trace, diagnostic output, or written description of visible evidence. | Generic “error” is insufficient. If an image is referenced but its content is unavailable, use `unclear` when that image is the only indicated evidence. |
| `attempted_remedy` | Something the original poster actually tried to fix or work around the reported failure. | A proposed future fix, initial setup, diagnostic screenshot, or check is not a tried remedy. An outcome does not need to be stated. |
| `help_request` | An explicit request for diagnosis, explanation, fix, or workaround. | A report can still be troubleshooting without a direct request. |

Use `evidence_or_note` to quote a short phrase or explain a difficult boundary. Do not fill a separate overall “usefulness” score: the eight fields record observable information, not whether a developer could solve the problem.

## How results may be used

The main sample is drawn randomly from the 1,658 Reddit-only S2 troubleshooting development posts. It estimates field frequencies **for that reviewed corpus**, subject to the limits of its keyword-based collection and existing troubleshooting labels. It does not estimate all Reddit posts or prove that the details are useful to developers. The 50-post pilot was deliberately enriched and must not be added to the main sample as if it were random. If a pilot post is randomly selected again, review it under this guide as part of the main sample and keep both responses separately.

Manu is the current single reviewer. These annotations are not independent inter-annotator agreement. Any repeat using this same frozen guide must be labeled as a repeat by one reviewer, and initial and adjudicated decisions must remain separate if a second reviewer later participates.
