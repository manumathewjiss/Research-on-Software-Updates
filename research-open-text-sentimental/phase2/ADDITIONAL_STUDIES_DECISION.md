# Decisions on additional research questions

**Status:** design recommendation, not a completed experiment. The 300-post expansion sheets collect only the core labels. Results must not be claimed until the relevant review and analysis are finished.

## Recommended main paper

Study whether posts in software-update discussions are actionable troubleshooting requests. Compare a keyword screen, simple text baselines, and stronger text models on the same reviewed posts. Report a practical ranking measure (for example, how many true requests appear in the first 10 or 20 results) as well as technical-class precision, recall, and F1. Decide the exact update-focused inclusion rule after the 300-post review and recheck of the old corpus.

## 1. Information completeness: add as a focused secondary contribution

This is the strongest proposed extension because it builds naturally on identifying troubleshooting posts. It asks whether the **original post** contains enough diagnostic detail for a support person to understand the failure. It is distinct from a claim that a developer actually acted on the post.

After core labels are finalized, draw a documented subset of **confirmed troubleshooting posts** from both the old and new data. Have two reviewers inspect the **title and original post body only**, not the replies, for these observable fields:

| Field | Operational question |
|---|---|
| `version_or_release` | Is a product version, named release, or update identified? |
| `environment` | Is the device, operating system, browser, or relevant setup identified? |
| `specific_symptom` | Is the failure described more specifically than a generic negative judgment? |
| `error_evidence` | Is an error message, log, code, screenshot description, or other diagnostic evidence present? |
| `trigger_or_steps` | Is the action or situation that produces the failure described? |
| `attempted_fix` | Does the author say what they already tried? |

Each field should be `present`, `absent`, or `unclear/not visible`. Do **not** reduce these to one arbitrary score before checking agreement. A post can be useful without every field, and a version number alone does not make it useful. If we want to claim real usefulness, ask a developer or maintainer to rate a subset independently and test whether these fields predict their judgment.

Potential paper question: **Does a troubleshooting detector find diagnostically informative reports, or merely posts with bug words?** This directly strengthens the practical story.

## 2. Community resolution: exploratory until full conversations are verified

This is scientifically interesting, but the saved API responses often contain only part of a thread. No original-poster confirmation in a snapshot means **unknown outcome**, not necessarily “unresolved.” A suggested fix in a reply is also not proof it worked.

If pursued, first audit comment completeness and timestamps. On a subset with adequate saved comments, distinguish:

1. Solution proposed in replies.
2. Original poster explicitly confirms a fix worked.
3. Original poster explicitly says the issue remains.
4. Outcome unknown from the saved text.

Two reviewers should agree on those rules before labeling. This can be an exploratory analysis or a later paper. Do not add a resolved/unresolved label to all 300 posts now.

## 3. Emerging issue clusters: separate later study

Finding repeated Wi-Fi or crash reports after a release could be valuable, but it requires enough posts per product/release, reliable dates and version links, duplicate control, and manual checking that grouped posts describe the **same issue**. The current API candidate pools and 300-post annotation are not by themselves a validated incident stream. A clustering result without a human-checked issue set would be hard to interpret.

Keep the fields needed for later work (post id, product/community, date, version references) in analyst data. Do not make clustering a central claim in the present paper unless a separate dataset and evaluation can be completed.

## Overall priority

1. Core task definition, reviewed labels, and fair new-post evaluation.
2. Diagnostic information completeness on confirmed troubleshooting posts.
3. A measured practical screening result.
4. Community-resolution analysis only where outcome evidence is adequate.
5. Emerging-issue detection as a follow-on project.

Sentiment is optional error analysis. Keep it only if a focused review shows it explains real distinctions after accounting for technical vocabulary and title-only posts.
