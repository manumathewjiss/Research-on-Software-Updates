# Diagnostic-detail pilot: first-pass analysis

**Status:** 2026-10-07. This is Manu's single-reviewer feasibility pilot, not independent agreement, a random sample of the corpus, or a finished research result. The submitted workbook is preserved unchanged in `submissions/2026-10-07-manu/`; `intake_summary.json` contains exact counts. No original Phase 2 or Phase 3 label was changed.

## Intake checks

- All 50 pilot IDs match the original sample, and every title/body matches exactly.
- `troubleshooting_check` is complete for all 50; every accepted troubleshooting row has all nine field answers; every row has an explanation.
- Manu marked 47 `yes`, one `no` (`D20261007-031`), and two `unclear` (`D20261007-039`, `D20261007-050`). These three are **flags to review against the Phase 2 rules**, not automatic label corrections. Two `unclear` rows involve missing or inaccessible image evidence.
- The sampling deliberately oversampled old/GDS-source and body-missing posts. None of the proportions below estimates prevalence in the 1,658 eligible Reddit troubleshooting development posts.

## What the pilot answers looked like

Among the 47 rows Manu marked as troubleshooting:

| Draft field | Present | Not observed | Unclear | Not applicable |
|---|---:|---:|---:|---:|
| Named software/product | 42 | 5 | 0 | 0 |
| Identifiable release/update | 21 | 2 | 24 | 0 |
| Environment | 36 | 11 | 0 | 0 |
| Specific symptom | 45 | 0 | 2 | 0 |
| Trigger/steps | 40 | 0 | 7 | 0 |
| Error evidence | 6 | 36 | 5 | 0 |
| Attempted fix | 25 | 22 | 0 | 0 |
| Result after attempt | 25 | 0 | 0 | 22 |
| Explicit help request | 33 | 14 | 0 | 0 |

These counts show that the workbook can be completed. They do **not** validate the field definitions by themselves.

## Three codebook repairs before scaling

1. **Release identification:** `release_or_update` was `unclear` on 24/47 accepted posts, usually because a post said “after updating” without naming the release. Rename the field `identifiable_release` and state plainly that an unnamed “latest update” is *not observed as an identifiable release*, while the update relationship remains a separate Phase 2 judgment. Reserve `unclear` for text that points to an unavailable screenshot/link or a genuinely ambiguous name. This makes `unclear` a missing-evidence answer rather than a frequent synonym for unnamed.
2. **Reproduction context:** `trigger_or_steps` was `present` on 40/47, including several title-only posts that merely said “after an update.” Separate the **event before the failure** from an **action or condition that reproduces it**. The latter should require an action/condition such as opening a screen, waking the device, or installing a package; “since updating” alone belongs in the update context field and does not establish reproducible steps. The 40 present judgments are preserved as first-pass answers and would need re-review under the new definition.
3. **Remedy versus diagnosis:** all 25 posts with `attempted_fix=present` also have `result_after_attempt=present`; the remaining 22 are exactly `not_observed`/`not_applicable`. Some examples describe account migration, creating a fresh test project, or taking another screenshot. These can be setup or diagnostic checks rather than attempts to remedy a known failure. Rename to `attempted_remedy` with an explicit criterion (action intended to fix or work around the failure). Keep a separate `diagnostic_check` field only if it proves useful in a short second pilot; otherwise capture checks in notes. `result_after_attempt` may be redundant and can be omitted from the main taxonomy if it does not contribute a distinct finding after revision.

No workbook answers should be automatically recoded from these proposals. A masked review of selected rows under the revised guide can show whether its distinctions are usable by one reviewer and how decisions change from the first guide. Because the guide changes, this is **not a within-reviewer consistency estimate** and is not agreement between independent people. A later masked repeat using the *same finalized guide* would be needed to assess within-reviewer consistency.

## Next gate

Prepare codebook v0.2 with the three repairs. Re-review a small masked subset after a delay, emphasizing unnamed updates, “after update” triggers, and setup-versus-remedy examples. If the distinctions still fail, simplify the taxonomy before a larger sample. Once definitions stabilize, draw a probability-based main sample and record its inclusion probabilities for any prevalence estimates.
