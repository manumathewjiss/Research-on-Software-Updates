# Questions for Manu (experiment_v1)

Only items that cannot be closed from the package alone.

## 1. Label adjudication (blocking for hard manuscript claims)

Please review `results/label_quality_flags.jsonl` (48 rows). Heuristic flags only — no auto-corrections were applied.

Priority themes:

- Posts labeled **troubleshooting** that read like rants with weak tech/repair cues.
- Posts labeled **other** / **general_dissatisfaction** that still ask for a fix or report a break.
- Very thin title-only / near-empty body rows.

**Decision needed:** Keep labels as-is for v1 reporting, or schedule a correction pass? If many labels flip, treat the current reserved-test score as exploratory and reserve a new untouched test set for confirmatory numbers.

## 2. Near-duplicate exclusions

Protocol excluded development `1t0wme9` and `1wrqch6` (near-dups of reserved posts; Jaccard ≥ 0.92 on char 5-grams). Exact reserved copies were already removed in the package.

**Decision needed:** Confirm this exclusion rule is acceptable for the paper methods text.

## 3. Claim strength

Development and reserved sets are reviewed labels of mixed origin (`manu_assisted_review`, `joint_review`, `pilot_post_discussion`, `reserved_test_consensus`), not a fresh independent blind panel.

**Decision needed:** What wording do you want for “gold” vs “reviewed study labels” in the manuscript?

## 4. Scope of next experiment (optional)

Out of scope for this run, but needs a call for Phase 3 follow-ups:

- Train a scope detector (`about_software` / `update_related`) separately?
- Allow `discussion_context` in a clearly labeled secondary experiment?
- Rebalance or resample so source pool is less entangled with class?

No answer required to keep the v1 baseline numbers on file; answer before rewriting ICMLA/ICSC claims.
