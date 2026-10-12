# Phase 4 feasibility, step 1: passage-removal pool

**Date:** 2026-10-08
**Code version:** `phase4-feasibility-step1-v1`

This is a screening inventory. It does not approve posts, start a pilot, or decide whether the experiment should proceed.

## Question

Does the latest reviewed development set contain Reddit troubleshooting posts from which one genuine author passage can be removed while the shorter post still names the product, the concrete issue, and a minimal update connection?

## What was used

- Latest reviewed development file listed in `MANIFEST.json`.
- Master `url` for the domain check.
- Every ID in the original reserved-test file and every ID in the 500-post fresh-test file.

Passage choice uses the author title and body only. Replies, source pool, model scores, sentiment, and test outcomes are not inputs to the decision.

## Filters

1. `about_software=yes`, `update_related=yes`, and `discussion_type=technical_troubleshooting`.
2. Master URL domain is Reddit.
3. Drop reserved-test IDs and all fresh-test IDs.
4. Drop title-only records, blank bodies, unreadable text, and obvious emails, phone numbers, or credential-like secrets.
5. Duplicate rule from the earlier development audit: exact normalized title+body, plus Jaccard character 5-grams at least 0.92. A duplicate is kept in the audit with its representative ID. Only the representative is screened.
6. A removable passage must be a rollback outcome, a contrast of versions, an explicit before/after working-state contrast, or a device contrast tied to an update. A bare version or a generic “after the update” is not enough. The passage also cannot be the only update connection.

## Provisional labels

`plausible`, `borderline`, and `reject` are Cursor suggestions. None is human-reviewed or approved.

## Counts

See `flow.json`. Provisional plausible: **27**. Borderline: **6**. Reject among screened representatives: **1517**.

Plausible cases span **16** communities and the evidence types in `flow.json`. A count above 60 does not mean the experiment is feasible. Codex and Manu still have to inspect the passages and make the go/no-go decision.

## Limits

The passage finder is a rule, not a reading of every post. It can miss a good passage and it can mark a weak one as plausible. Shortened text was checked only for a remaining symptom cue and a remaining update mention, not for natural prose. Privacy detection covers obvious patterns only.
