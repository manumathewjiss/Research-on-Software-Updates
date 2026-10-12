# Diagnostic-detail pilot: draft codebook v0.1

**Status:** provisional instructions for a 50-post feasibility pilot. This is not a validated taxonomy or a completed annotation study. No answer has been filled in. Review only the saved **title and original post body** shown in the workbook; do not follow links or read replies. The sample intentionally overrepresents short posts and the old/GDS candidate pools, so it cannot estimate population prevalence.

## Why these fields

Software-maintenance literature has long separated a report's existence from its diagnostic information. The [Bettenburg et al. study of bug-report quality](https://www.st.cs.uni-saarland.de/publications/details/bettenburg-tr-2008/) found that developers value steps to reproduce, stack traces and test cases, while users often struggle to provide them. App-review work such as [INFAR](https://www.microsoft.com/en-us/research/publication/infar-insight-extraction-from-app-reviews/) analyzes user feedback for software insights. Our pilot adapts this idea to informal software-update posts, where short text and missing context may limit what is observable. These references motivate candidates; they do not validate the exact field list below.

## General answer rule

For each field choose:

- `present`: the title/body explicitly gives the detail. Brief but concrete wording counts.
- `not_observed`: the detail is not visible in the saved title/body. This does **not** prove it was absent from the original live thread.
- `unclear`: text gestures toward the detail but you cannot tell what it is, or needed information appears only in an unavailable image/link.
- `not_applicable`: use only for **result_after_attempt**, when no attempted fix or diagnostic action is described; otherwise avoid it.

Do not infer a version from a subreddit, date, device fashion, or your knowledge of the product. Do not use comments, API pool, model output, or the old labels. A symptom can be present even if the post is angry. A request for help is a separate field from a symptom.

## First, check that the post belongs in this pilot

The posts were drawn from existing troubleshooting labels, but the label may be wrong. Set `troubleshooting_check` to `yes`, `no`, or `unclear` based on the original post's main purpose. `yes` means it reports a current software failure, seeks diagnosis or repair, or offers a concrete repair to a specific problem. If `no` or `unclear`, add a brief note and leave the diagnostic fields blank. Do not change the Phase 2 label in this workbook; this is a review flag for later adjudication.

## Candidate fields

| Workbook column | Mark `present` when | Keep separate from |
|---|---|---|
| `software_product` | A specific app, OS, service, tool, or software component is named. | Device model and subreddit name. |
| `release_or_update` | A version, named release, patch, or identifiable update is stated. “After updating” with no identified release is `unclear` for this field. | Merely saying the problem is new. |
| `environment` | Device, hardware model, operating system, browser platform, configuration, or other setup relevant to the failure is specified. | The affected software itself. |
| `specific_symptom` | A concrete wrong behavior is described: e.g., “login shows a blank screen,” not just “the update sucks.” | Emotion, severity adjectives, or an unlocated “issue.” |
| `trigger_or_steps` | A user action, condition, or sequence that produces the problem is described. It need not be a full reproducible test case. | The symptom itself. |
| `error_evidence` | A quoted error message/code, log, trace, diagnostic output, or described screenshot evidence is given. An inaccessible image link without description is `unclear`. | A generic word such as “error” without its content. |
| `attempted_fix` | The author describes a repair or diagnostic action already tried. | Asking others what to try. |
| `result_after_attempt` | The author states what happened after an attempted fix, including “it did not help.” Use `not_applicable` if no action was attempted. | The original symptom. |
| `help_request` | The author explicitly asks for help, a fix, explanation, or workaround. | Merely describing a failure or venting. |

Use `evidence_or_note` for a short quote or explanation when an answer is uncertain or a boundary case. You do not need nine separate quotes for every row; mark enough evidence to make difficult decisions auditable.

## Synthetic examples, not sampled posts

- “After updating App A to 4.2 on Phone B, tapping Sync closes the app. Reinstalling did not help. Any fix?” has product, release, environment, symptom, trigger, attempted fix, result and help request. It has no quoted error evidence.
- “The latest update ruined everything” has no specific symptom. The release is unclear because the update is not identified.
- “Error 503 when saving settings after Patch 6; log says database timeout” has a symptom and error evidence. It does not state an attempted fix.

## Pilot decision rules

1. Label all 50 posts yourself from the saved text. Do not ask an assistant or model to fill answers.
2. Note fields that are hard to distinguish and any posts that are not truly troubleshooting. This is the purpose of the pilot; ambiguity is useful evidence.
3. After the 50 are complete, we will inspect field frequencies and your boundary notes, revise the codebook **before** a larger sample, and draw a masked re-review subset later to measure your own consistency. That would be **within-reviewer consistency**, not independent inter-annotator agreement.
4. Do not publish completeness rates from this deliberately enriched pilot. A later probability sample and appropriate weighting are needed for prevalence estimates.
