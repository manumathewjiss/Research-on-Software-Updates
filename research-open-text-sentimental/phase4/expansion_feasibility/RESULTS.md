# Expansion feasibility: the 21,920-post update-related pool

Decision: **Option A. Freeze the dataset.**

This note is a feasibility study. It is not a paper result, not a new gold set, and not a reason to retrain.

Reviewed on 8 October 2026. The live index returned 21,920 unique posts (pages 1–43 of 500, page 44 of 420, `hasNext` false). The total had moved from 21,708 earlier the same day, so the figure is the census, not a permanent population size.

## What was reviewed, and why it stopped

The pool is an unreviewed index. It is not 21,920 update discussions.

| Slice | Posts |
| --- | ---: |
| Index | 21,920 |
| Already in the 3,362 master | 2,832 |
| In the fresh 500 | 499 |
| In the reserved 200 | 198 |
| Unseen (not in master, fresh, or reserved) | 18,589 |
| Unseen with an empty body | 757 |
| Unseen with a body | 17,832 |

API `predicted.isUpdateRelated` on the unseen posts: true 396, false 8,494, missing 9,699. A non-null human `labeled.isUpdateRelated` exists on 3 unseen posts, all predicted true. The predictor is a sampling stratum only. It was not treated as a label.

Pre-registered wave, seed 20261008, written in `wave1_ids.json` before any body was fetched:

- Every unseen non-empty post with predicted update true, or a non-null labeled flag: 386 posts. This is the entire high-prior slice.
- 120 predicted-false and 120 predicted-none posts, stratified by era (before 24 April 2025, inside the study window, after the 5 October 2026 master cutoff).

Total reviewed: **626**. All 626 bodies were recovered.

Stopping rule, applied after human verification: stop if the predicted-false and predicted-none samples have no verified expansion-worthy posts and no new troubleshooting category appears three times. Both conditions hold. Reading further toward 2,000 would resample the same index. The predicted-true slice is already exhausted.

## How labels were proposed

`annotate_wave1.py` proposes labels from title and body only. It does not use subreddit, source, or the API prediction as a feature. A post is an expansion candidate only when the text has a software cue, at least two strong update words (update, upgrade, patch, firmware, rollback, downgrade), troubleshooting language, a concrete symptom, and at least two diagnostic fields from codebook v1.0. A lone “version” or “release” is uncertain, not an update. Thin bodies and single update cues are flagged.

The rubric is not ground truth. It marked 18 posts expansion-worthy and 16 more as needing review. Every one of those 34 was read. Decisions and reasons are in `wave1_human_verification.jsonl`.

Human check of the rubric: 12 of the 18 automatic keeps were rejected, and 7 of the 16 flagged posts were promoted. Net verified useful posts: **13, all inside the predicted-true slice.** The predicted-false and predicted-none samples contributed **zero**.

## 1. Review statistics

| Quantity | Value |
| --- | ---: |
| Posts reviewed | 626 |
| Predicted-true slice, fully read | 386 |
| Predicted-false sample | 120 |
| Predicted-none sample | 120 |
| Rubric expansion-worthy | 18 (2.9%) |
| Rubric uncertain flags | 442 |
| Human-verified useful | 13 (2.1% of 626; 3.4% of the 386) |
| Wilson 95% interval, 13/386 | 2.0% to 5.7% |
| Verified useful in the 240 low-prior posts | 0 |

Useful means: software, a real update incident, troubleshooting, a concrete symptom, and enough technical detail to add a case of the kind the diagnostic study already analyzes.

## 2. Label distributions

Rubric proposals on all 626, before the human pass:

| Question | Yes | No | Uncertain |
| --- | ---: | ---: | ---: |
| Software-related | 409 | 217 | — |
| Update-related | 427 | 178 | 21 |
| Troubleshooting language | 367 | 259 | — |

Those yes-counts are deliberately loose. “Troubleshooting language” fires on ordinary help posts. The human pass is the distribution that matters: 13 verified useful, 21 rubric candidates rejected, and the remaining 592 not advanced because they missed the update incident, the symptom, or the diagnostic detail.

## 3. Diagnostic evidence

The 13 verified posts do contain real evidence. They do not contain a new evidence pattern.

| Post | What the text actually supplies |
| --- | --- |
| 1wyqgfx | Ubuntu 24.04 to 26.04, `/lib32` failure, kernel panic, Live USB recovery |
| 1wzne0h | Frozen ComfyUI workload, RTX 5090 full power-off, stack update as the change that stopped it |
| 1uueif0 | Fedora, KDE Plasma 6.7, NVIDIA 595.80, secondary-monitor black region, config removal |
| 1p1wvs5 | Chrome, Windows 11, Ryzen and 5600 XT, YouTube stutter, hardware-acceleration toggle |
| 1x0emfp | Chrome 155.0.8059.40, Windows 10, passwords and bookmarks tied to sign-in |
| 1uh1n9n | ComfyUI after update plus an NVIDIA driver update, “can't run” and Access Denied |
| 1x0twgw | ComfyUI after a Windows update, SAC workaround |
| 1wzvhj6 | PowerToys 0.101, features and shortcuts reset by successive updates |
| 1wzohes | Contact Form 7 6.2 auto-update crashes PHP 8.2 |
| 1ucz1ox | Firefox YouTube quality drop, absent in Chrome, extension list |
| 1ucuoux | Fedora 44, black screen after Discover update |
| 1s2kv7x | Fedora, black screen after update, akmod message, virtual-console recovery |
| 1si0nu9 | Immich local web UI spins after an update; public URL and mobile app still work |

Two of these, the Ubuntu recovery and the ComfyUI power-off, are individually strong. Two Fedora black screens are the same incident type. The rest are short reports with a version or a workaround.

## 4. New troubleshooting categories

No new category occurs three times.

What recurred is the inventory the study already has: OS upgrade or update leaves the machine unbootable or on a black screen; a browser misbehaves after an update; an application fails to launch after an update. ComfyUI accounts for three of the 13, and the master already contains 170 ComfyUI posts. Fedora, Chrome, Firefox, WordPress, and Immich are likewise already in the master (181, 362, 121, 85, and 104).

Rejected lookalikes, kept so the boundary stays visible: Group Policy `gpupdate`, “fully updated” as a description of the environment, changelogs, project announcements, and hardware upgrades.

## 5. Representative examples

Useful, and already the paper's genre:

- “Ubuntu 24.04 > 26.04 LTS upgrade failed on /lib32 and left system unbootable” (`1wyqgfx`).
- “Black screen after update” on Fedora 44 (`1ucuoux`).
- “Comfyui after updating… This App can't run on your PC” (`1uh1n9n`).

Richest new text, still one case:

- RTX 5090 full-system power-off on a frozen MiniMax workload, no longer reproduced after a ComfyUI-side update (`1wzne0h`).

Not useful, despite update vocabulary:

- Stickied Raspberry Pi helpdesk (`1vr69o1`).
- “gpupdate /force applies user policies, but not computer ones” (`1wzv7nz`).
- ComfyUI v0.32.0 changelog (`1vmygp5`).

## 6. Diversity

Unseen posts span 408 subreddits and dates from 2010-07-13 to 2026-10-08, against 154 subreddits in the master. That is collection diversity, not scientific diversity. The verified useful posts sit in communities the master already represents. The long tail of the 17,832 unseen bodies was probed with 240 posts drawn from the strata the API does not mark as update-related. None survived review.

Era quotas in the low-prior sample followed the pool: most mass is inside the study window, with a smaller after-cutoff slice and a thin pre-2025 slice. No era produced a verified useful post outside the predicted-true slice.

## 7. Would this strengthen Phase 4?

Phase 4 step 1 already screened the reviewed Reddit troubleshooting set and provisionally found 27 plausible passage-removal posts and 6 borderline posts. The new pool adds at most two further passage-shaped reports (`1wyqgfx`, `1wzne0h`) and one weaker display case (`1uueif0`). Two more posts of a type the inventory already contains do not change the passage-removal design, the reviewer materials, or the go/no-go that was left to a human count rather than to a threshold of 60.

## 8. Dataset expansion

**Option A. Freeze the dataset.**

The seven study questions:

1. Useful yield is 2.1% of posts read, and 3.4% of the entire predicted-update slice (13/386; 95% interval 2.0–5.7%).
2. No new troubleshooting category appears.
3. Diagnostic patterns are the same ones already coded: version, environment, symptom, error text, attempted remedy. One hardware A/B is richer than the median post and is still a single case.
4. Community coverage in the verified slice does not extend the master.
5. Phase 4 does not gain a new design or a new evidence class.
6. Retraining is not justified. Thirteen additional positives, drawn from the same failure modes, cannot move a classifier trained on roughly 1,700 troubleshooting posts by a scientifically meaningful amount. The hard negatives this wave exposed (`gpupdate`, “fully updated,” changelogs) are the negative class the current model was built to refuse.
7. Collecting more of this index is not justified. The only stratum with any verified yield has already been read in full.

Options B and C fail the same test. Expanding everything adds thousands of non-update posts. Expanding “only ComfyUI” or “only OS black screens” adds duplicates of categories whose subreddits are already in the master.

## 9. Modern model comparison

Do not run another model comparison.

The frozen MiniLM comparison already tested the hypothesis that a sentence embedding separates troubleshooting from other update discussion better than the locked TF-IDF logistic regression. The paired macro-F1 difference was about +0.006 and the confidence interval included zero. This wave does not propose a new decision boundary, a new label, or a slice where bag-of-words is the wrong representation. A further transformer, instruction model, or larger embedding would add complexity without a hypothesis that these 13 posts can support.

No model was trained for this study. The reserved 159 and the fresh 344 were not scored.
