# Single-review consistency audit: initial result

The submitted 120-row workbook was copied intact into this directory. `analyze_completed.py` verified every blind ID, the saved title/body/reply text, the allowed answer values, and that all five answer fields were filled. It made no change to the Phase 2 master, revised development, or tests. Numeric details are in `analysis.json`; all 22 differing rows are in `disagreements.csv`.

This is **one new blind review compared with mixed-provenance earlier recorded decisions**. It is neither agreement between two independent reviewers nor a natural-prevalence sample. The sample deliberately contains 50 previously recorded troubleshooting posts, 30 other update posts, 20 software non-update posts, and 20 nonsoftware posts. It excludes the 200 reserved posts, the fresh 500, and the 237 diagnostic cases that had joined predictions.

## Completeness and comparison

| Field | Same as earlier record | Different | Raw match rate in this selected sample |
| --- | ---: | ---: | ---: |
| Software related | 114/120 | 6 | 95.0% |
| Update related | 107/120 | 13 | 89.2% |
| Discussion type | 110/120 | 10 | 91.7% |
| All three together | 98/120 | 22 posts differ on at least one field | 81.7% |

The match rates describe this **stratified check only**. Some posts differ on more than one field, so field-difference counts do not add to 22.

## Key finding: update boundary

The strongest mismatch is in the 20 posts previously recorded as software-related but **not** update-related: only 8 retain that update decision; the new review marks 12 as update-related. All 50 previously recorded troubleshooting posts in the sampled S2 stratum retain their update decision, as do all 30 other-update posts. This pattern is consistent with the broadened rule that an author may *suspect or ask whether* an update caused an issue. It is not proof that all 12 earlier decisions were wrong.

On a text-only inspection, several new `yes` judgments have an explicit author connection—for example `A048` asks whether firmware versions explain packet loss, `A061` describes failure after application updates, and `A107` says the apps have failed since watchOS 26. Others are boundary cases: `A021` lists the latest iOS and an update among attempted remedies, `A033` gets an update suggestion from a developer reply rather than an author claim, and `A090` says updating Edge did **not** fix an existing problem. These should be adjudicated against the exact rule before any dataset correction. The new answer is an observation, not automatic ground truth.

An exploratory phrase screen of the 728 Reddit development posts with an earlier `manu_assisted_review`, `about_software=yes`, and `update_related=no` found 208 with at least one broad update-connection phrase in title/body/saved replies. This is only a **candidate count**, not 208 confirmed errors. A phrase can refer to a remedy, unrelated context, or another person's comment. The screen suggests a bounded review is feasible if the rule discrepancy persists after adjudication.

## Other boundaries

- In the 30 prior other-update posts, discussion type matches on 26; four change type or scope. In the 50 prior troubleshooting posts, discussion type matches on 49.
- Six posts differ on whether the main topic is software. Examples include a vague title (`A041`), a computer-restoration progress post where “update” means progress (`A053`), and a network-loss report with uncertain software cause (`A085`).
- Some disagreements come from a thin saved snapshot (`A041`, `A089`, `A094`) or from whether a resolved incident/tutorial still counts as troubleshooting (`A022`, `A049`, `A073`, `A086`). These cases need the written rule applied consistently; no class was changed here.

## Research consequence and next action

Do **not** merge these new answers into the master or retrain yet. First adjudicate the 22 differing rows with a rule-level decision, recording both the old and new judgments. In particular, settle whether attempted updating, a third-party reply about a version, and an update used as a fix count as an update connection. Then apply the locked rule consistently to the earlier software/non-update development stratum, using a targeted candidate screen and a random audit of unflagged rows so the screen's misses can be estimated. Only after the corrected population is frozen should new modeling be considered. The earlier scores remain valid historical results for the earlier population, with that population stated accurately.
