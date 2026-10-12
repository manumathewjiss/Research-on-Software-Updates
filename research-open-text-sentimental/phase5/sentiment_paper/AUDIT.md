# Join and coverage audit

**Created:** 2026-10-09T21:36:20.313731+00:00

Reviewed IDs were joined to the March 2026 raw responses, the October 5 saved API pages, and the saved fresh-test collection pages by `redditId`. No live thread was fetched. No model was fit. The reserved and fresh files were used only to count coverage. They were not scored.

S2 negative class is other update discussion (s2_target 0), not historical GDS and not discussion_type general_dissatisfaction. Those populations are reported separately.

## Snapshot rule

Combined-collection IDs use the October 5 saved API response if present, otherwise the March 2026 raw response. Fresh-test IDs are outside the master and use phase3/fresh_test_20261007/raw pages. Snapshots are not concatenated and threads are not refetched.

Master posts: 3362. March snapshot IDs: 542. October 5 snapshot IDs: 2829. October 5 route counts, which are candidate files rather than labels: `{"oct5_tps_candidate": 2378, "oct5_gds_candidate": 451}`.

## Coverage by split

| Split | n | Joined any saved snapshot | Nonempty stored comment | Author reply | Community comment | Both roles | Title only | Stored/recorded comments |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| development_s2 | 2080 | 2080 | 797 | 474 | 789 | 466 | 303 | 0.379 |
| development_not_s2 | 1071 | 1071 | 601 | 363 | 597 | 359 | 286 | 0.555 |
| reserved | 200 | 200 | 55 | 28 | 54 | 27 | 29 | 0.331 |
| fresh_s2 | 344 | 344 | 141 | 95 | 140 | 94 | 6 | 0.393 |
| master_not_in_development_snapshot | 11 | 11 | 7 | 3 | 7 | 3 | 8 | 0.617 |

The reserved file has 200 rows: 159 are S2 (135 troubleshooting, 24 other update discussion) and 41 are outside S2. The fresh file is the 344-row S2 test (277 troubleshooting, 67 other update discussion). Development S2 contains 2,050 `reddit.com` rows and 30 `stackoverflow.com` rows.

## S2 development classes

These counts use `s2_target`. Class 0 is other update discussion.

| S2 class | n | Nonempty comment | Author reply | Community comment |
|---|---:|---:|---:|---:|
| Troubleshooting | 1686 | 560 | 362 | 554 |
| Other update discussion | 394 | 237 | 112 | 235 |

Reddit-URL modeling rows with saved folds: **2050** (1658 troubleshooting, 392 other update). Joined to a saved snapshot: 2050. At least one nonempty stored comment: 797 (troubleshooting 560, other update 237). Author reply: 474. Community comment: 789. Both roles: 466. Title only: 303.

## Historical TPS/GDS, separate from S2

Gold file posts in the master join: 542 (TPS 86, GDS 456). March snapshot join: 542. Historical corrected_label is the ICMLA TPS/GDS gold file. It is not the revised S2 label.

## Restricted discussion-type population

On the 2,050 Reddit S2 rows, `technical_troubleshooting` versus `general_dissatisfaction` contains **1726** posts: 1658 troubleshooting-type and 68 general-dissatisfaction. This is not a substitute for the S2 population. Development S2 discussion-type counts: `{"technical_troubleshooting": 1686, "other": 326, "general_dissatisfaction": 68}`.

## Outcome labels

No human-confirmed resolution or outcome label was found. Saved replies cannot be described as evidence that a reply solved an issue. Absence of a confirmation is unknown outcome, not unresolved.

## Fields that can support text without using API categories

Saved API records can supply title, body, comment text, author flags, timestamps, num_comments, and URL domain. The same records also carry candidate-route names, metadata.predicted, metadata.labeled, keyword features, category, and precomputed sentiment. Those fields are API candidate signals, not reviewed S2 labels.

## Preserved fresh-test score

The existing fresh-test evaluation remains macro-F1 **0.7915** on 344 posts (other update 67, troubleshooting 277; confusion `[[46, 21], [25, 252]]`). This audit did not recompute it.

Fresh saved pages: comments key present for 340 of 344 posts and absent for 4. A missing comments key is not evidence of zero Reddit comments. Page-level omission is recorded separately from an empty comments list.

## Unverified ReleaseTrain question

phase2/new_sources/api/pagination_manifest.json records October 5 candidate pulls, not a prevalence. phase5/SCIENTIFIC_INTEGRATION_DECISION.md records inconsistent live route totals and states that the professor's 3% estimate has no documented numerator, denominator, time range, or risk definition in these files. It is not a result of this audit.
