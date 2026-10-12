# Codex screening of the 100-post pilot

Prepared 2026-10-05 from the saved, blind pilot text. This is an **AI analytical review**, not human annotation or independent validation. The two human reviewer sheets remain empty. These figures describe a deliberately selected set of difficult examples and must not be used to estimate category prevalence in Reddit.

## Provisional judgments

| Field | Counts |
|---|---:|
| About software | yes 87; no 12; unclear 1 |
| Connected to an update | yes 53; no 25; unclear 22 |
| Discussion type | technical troubleshooting 63; general dissatisfaction 4; other software discussion 20; not applicable 13 |
| Confidence | high 56; medium 38; low 6 |

The full row-by-row reasons are in `AI_SCREENING_NOT_HUMAN.csv`. The most important observation is how uncommon *general dissatisfaction* is under the revised definition, even in a sample that deliberately included complaint-like posts. This suggests the original TPS/GDS name does not fit the current negative class. It does **not** establish a population rate.

## Diagnostic checks

- Among 49 sampled Phase 1 posts, this AI review disagrees with the old binary label on 16 when troubleshooting is treated as the positive class. These are prompts for human review, not corrections to the old labels.
- The 18 sampled posts from the new `/query/gds` pool include 16 judged as troubleshooting in this review. That subsample intentionally favored technically worded and ambiguous cases. Do not generalize 16/18 to the entire endpoint.
- The 33 sampled posts from the new `/query/tps` pool include 30 judged as troubleshooting in this review. That pool is keyword selected; its membership is not ground truth.
- Twenty-two update-connection judgments were unclear. Saying that an app has the latest version, or that the user tried updating it, does not prove the problem began with an update. This question needs a strict rule if the final paper claims to study update effects.

## Cases that should shape the research definition

1. A post can be about software without being about an update, such as a Laravel test failure or a VS Code color setting problem.
2. A post can mention an update while mainly asking about hardware purchase or trade-in value. Scope should follow the main purpose of the post.
3. A release announcement and an article about a future update are neither troubleshooting nor dissatisfaction.
4. A technical issue report may lack the exact keywords in the API's TPS query. The `/query/gds` pool contains clear examples.
5. A frustrated writer may still be asking for a fix. Tone should not determine the troubleshooting label.

## Research use

Use this screening to revise rules, identify hard cases, and plan further analysis. Do not report agreement statistics from it, merge it into the gold corpus, or train a final model using these labels without an explicit protocol that calls them AI-generated provisional labels. If human review cannot be arranged, the paper must describe the label limitation and remove claims of independent human validation.
