# Literature positioning for the sentiment-centered rewrite

This note identifies research we should engage with in the revised paper. It is a source check, not a claim that a new experiment has been completed.

1. **VADER and what it measures.** Hutto and Gilbert's [2014 VADER paper](https://eegilbert.org/papers/icwsm14.vader.hutto.pdf) designs a rule-based sentiment method for social-media text. Its output estimates emotional valence, not whether a post contains a software fault, an update connection, or a successful fix. Our manuscript must keep those targets separate.

2. **Technical vocabulary can distort general sentiment tools.** Islam and Zibran's [SentiStrength-SE study](https://doi.org/10.1016/j.jss.2018.08.030) reports domain-specific difficulties and evaluates a software-engineering-specific dictionary on manually labeled Jira comments. This motivates checking words such as error, failure, and bug as possible sentiment confounders in our Reddit data. It does not imply that a tool validated on Jira will work on Reddit without evaluation.

3. **Tool choice changes SE sentiment conclusions.** The [extended replication study of SE-specific sentiment tools](https://doi.org/10.1007/s10664-021-09960-w) cautions that general-purpose sentiment tools can be unreliable on technical communication. The [benchmark study](https://arxiv.org/abs/1803.06525) and [negative-results study](https://doi.org/10.1007/s10664-016-9493-x) are relevant checks against treating one VADER polarity number as ground truth. If we compare another sentiment model, we need human sentiment judgments on our own sample to tell whether it measures emotional tone correctly.

4. **Comments and outcomes are separate research targets.** Ramírez-Mora et al.'s [issue-description-and-comment study](https://arxiv.org/abs/2006.01358) evaluates resolution outcomes in issue trackers where outcome labels exist. Our saved Reddit snapshots do not yet establish whether a proposed fix worked. We may analyze reply content and self-reported resolution only after defining and validating that label, and we must distinguish no visible confirmation from unresolved.

5. **Questions during resolution matter.** Huang et al.'s [issue-report questions study](https://danielcalencar.github.io/journal%20papers/2018/09/22/emse-18.html) gives a nearby rationale for studying clarification requests. It does not support claiming that negative sentiment causes engineers to ask for clarification.

## Precise gap we can test

In reviewed software-update Reddit posts, does sentiment of the initial report, author follow-ups, and available community replies add information about **discussion purpose** beyond the words of the post? The post-level VADER answer so far is no reliable gain. The richer conversation comparison depends on comment coverage and temporal provenance. A separate descriptive question can ask how author and community sentiment differ, but the historical 542-post gap must be reported with title-only and missing-comment limitations.

## Terminology guardrail

The current revised S2 label is **troubleshooting versus other update discussion**. The historical label is **TPS versus GDS**. “Other update discussion” is not synonymous with “general dissatisfaction.” A paper that says TPS/GDS while training on S2 labels would misdescribe the task. If we want a genuine TPS-versus-general-dissatisfaction result, we must restrict to posts with those confirmed discussion-type labels and report the resulting population and class counts.
