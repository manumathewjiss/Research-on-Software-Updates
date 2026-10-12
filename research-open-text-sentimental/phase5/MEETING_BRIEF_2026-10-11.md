# Discussion brief for Professor Berhe — 11 October 2026

Internal preparation for the Tuesday meeting. This is a read-only synthesis of saved research outputs, not a manuscript revision or a new experiment.

## Main question for the meeting

What contribution should lead the revision: a carefully bounded result about sentiment and troubleshooting purpose, a descriptive analysis of comments over time, or an evaluated connection to the ReleaseTrain prototype? The saved data support the first; the other two need narrower wording or additional validation.

## What the current results actually say

The primary development set contains **2,050 posts with Reddit URLs**: 1,658 reviewed as troubleshooting and 392 as other software-update discussion. Its grouped, title-and-body text model has macro-F1 **0.8319**. VADER alone has macro-F1 **0.5335**; adding VADER to the same text model gives **0.8331**, a gain of only **0.0012** with a duplicate-group 95% interval from **−0.0126 to +0.0154**. This does not establish an improvement from VADER. Three other tested sentiment scores also had no reliable additional gain over the text model. Source: `phase5/sentiment_paper/RESULTS.md` and `phase5/final_improvement/FINAL_RESEARCH_IMPROVEMENT_REPORT.md`.

The comparison group changes the descriptive sentiment result. Mean title/body VADER compound is **−0.0644** for troubleshooting versus **+0.1941** for all other update discussion (difference **−0.2585**). Within the **68 posts specifically labeled general dissatisfaction**, the mean is **−0.0680**, almost the same as troubleshooting; the difference is **+0.0036**, with a wide interval spanning zero. That smaller comparison should not be presented as proof of equivalence. An exploratory SentiStrength-SE comparison instead marks those 68 dissatisfaction posts more negative than troubleshooting. There is no human sentiment gold label to decide which tool best represents sentiment. Source: `phase5/sentiment_paper/RESULTS.md` and `phase5/final_improvement/FINAL_RESEARCH_IMPROVEMENT_REPORT.md`.

The protected fresh test remains **macro-F1 0.7915 on 344 posts**. These new development analyses have not rescored that test. Do not imply that a development comparison proves fresh-test improvement. Source: `phase5/sentiment_paper/RESULTS.md`.

## True-positive and false-positive averages requested by Professor Berhe

These values are **new descriptive summaries of the already-saved 2,050 development predictions** in `phase5/expanded_study/results/predictions.jsonl`; no model was refit. The positive class is troubleshooting. The model score is the saved `score_title_body`, and the sentiment score is saved title/body `vader_compound`. Neither is a measure of problem severity. These averages are conditional on the reviewed label and model prediction, not population estimates.

| Outcome | Meaning | Count | Mean model score | Mean VADER compound |
|---|---|---:|---:|---:|
| True positive | Reviewed troubleshooting; predicted troubleshooting | 1,546 | 0.851 | −0.073 |
| False positive | Reviewed other update; predicted troubleshooting | 103 | 0.714 | +0.087 |
| True negative | Reviewed other update; predicted other update | 289 | 0.298 | +0.232 |
| False negative | Reviewed troubleshooting; predicted other update | 112 | 0.472 | +0.060 |

These are exploratory descriptions. The false-positive group contains varied posts, including positive release experiences and posts whose reviewed category is arguable. The average alone cannot explain why the model erred. The model scores are not demonstrated to be calibrated probabilities.

## Four candidate cases for Professor Berhe's requested table

**Illustrative cases selected to show contrasts, not the four highest-scoring posts.** Check the saved snapshot and wording again before publication. In any public table, paraphrase source text and avoid exposing addresses, handles, or full body text. All four are from the same development prediction file and the same `phase3/reddit_only_sensitivity/development_reddit_only.jsonl` snapshot.

| Outcome | Reddit ID / source link | Why selected | Model score | VADER |
|---|---|---|---:|---:|
| True positive | [`1rrji0f`](https://reddit.com/r/homeassistant/comments/1rrji0f/help_home_assistant_inaccessible_in_brave_browser/) | After an update, author reports lost access in normal browser mode but successful access in private mode, plus attempted remedies. The text is a clear help request even though VADER is strongly positive. | 0.988 | +0.964 |
| True positive | [`1qs5jqm`](https://reddit.com/r/immich/comments/1qs5jqm/issue_after_updating_to_25x/) | After an update, author reports image-loading errors, a failed thumbnail-regeneration attempt, and an HTTP 500 error. VADER is negative. | 0.989 | −0.506 |
| False positive | [`1tfbgzv`](https://reddit.com/r/Ubiquiti/comments/1tfbgzv/significant_lower_memory_usage_after_updating_to/) | Author reports lower memory use after an update and asks whether others see the improvement. Reviewed as other update discussion, but model calls it troubleshooting. VADER is positive. | 0.834 | +0.867 |
| False positive | [`1th5jal`](https://reddit.com/r/AndroidQuestions/comments/1th5jal/one_ui_is_destroying_the_experience_on_my_galaxy/) | Strong complaint about overheating and freezing after recent updates, reviewed as general dissatisfaction. Model calls it troubleshooting and VADER is very negative. **Boundary case:** concrete symptoms make the reviewed distinction contestable; present it as ambiguity, not an obvious labeling error by the model. | 0.916 | −0.953 |

The example table should say whether its scores come from out-of-fold **development** predictions; it must not imply they are fresh-test cases. If Professor Berhe prefers four least-ambiguous examples, replace the final boundary case after a case-level review rather than silently changing its label.

## Comments and cadence

Only **797 of 2,050** development posts have a nonempty stored comment. Author replies are stored for 474; community comments for 789; both roles for **466 (22.7%)**. Stored comments cover only **37.9% of recorded comment counts**. A full-thread model uses later, timestamped comments retrospectively, not information available when the post first appeared. The earlier 542-post sentiment gap and the present author/community summaries do not establish a general time trend or that a reply fixed an issue. Source: `phase5/sentiment_paper/RESULTS.md` and manuscript Methods/Discussion.

For the meeting: ask whether Professor Berhe wants a **descriptive, coverage-qualified timeline** from the saved comments, or whether he has a more complete archived comment dataset. Do not promise a cadence result until its completeness and exact time definition are checked.

## Prototype and reproducibility

Professor Berhe reports that the earlier VADER work is in the ReleaseTrain prototype. Treat that as a deployment context, not as proof that the current classifier, sentiment comparison, or risk cadence was validated online. Ask which code version, VADER input, score definition, and data snapshot the prototype uses, and whether its output can be reproduced from a public repository. Add a GitHub link only after checking that the repository contains the cited code, dependency instructions, and shareable data or a documented access route. Do not imply all reviewed labels or full Reddit text are public if they are not.

## Paper structure and decisions

The current manuscript already has Abstract, Introduction, Related Work, Methods, Results, Discussion, and Conclusion; it also has Sources and Populations, Threats, and Future Work. The requested structure is therefore mainly an ordering/presentation check, not a missing-section problem. Source: `phase5/final_synthesis_paper/main.tex`.

Decide with Professor Berhe:

1. Which **one sentence** states the contribution beyond “sentiment does not improve F1”?
2. Should the comment result remain a limited secondary finding or become a central question only after a stronger cadence analysis?
3. Are the four example cases acceptable, especially the contested dissatisfaction case?
4. What exact prototype and repository are reproducible and appropriate to cite?
5. Once those are agreed, does the title need changing? Avoid locking it before the claim is settled.
