# Pilot analysis plan

**Status:** plan only. Do **not** compute agreement until both human reviewers finish.  
**Reviewer guide:** `REVIEWER_GUIDE.md`  
**Sheets:** `pilot/reviewer_A_sheet.csv`, `pilot/reviewer_B_sheet.csv`  
**Private map:** `pilot/pilot_id_mapping.csv`  
**Research options:** `../TASK_DEFINITION.md`  
**Analyst examples (closed during labeling):** `ANALYST_ONLY_EXAMPLES.md`

No Cursor-generated labels count as human validation.

---

## 1. When analysis may start

1. Reviewer A and B each saved a completed sheet.  
2. Every row has `about_software`, `update_related`, and `confidence`.  
3. If `about_software=yes`, `discussion_type` is one of `technical_troubleshooting` | `general_dissatisfaction` | `other`.  
4. If `about_software` is `no` or `unclear`, `discussion_type` is `na`.  
5. Analysts have not edited either reviewer’s judgments.

Incomplete sheets go back to the reviewer. Do not impute labels.

---

## 2. Primary agreement metrics

Join on `pilot_id` only.

### 2.1 Software judgment (all rows)

- Exact agreement and Cohen’s κ on `about_software` (`yes` / `no` / `unclear`)

### 2.2 Update-connection judgment (all rows)

- Exact agreement and Cohen’s κ on `update_related` (`yes` / `no` / `unclear`)

Also report agreement on the **joint** pair `(about_software, update_related)`.

### 2.3 Discussion type (software intersection)

Keep rows where **both** reviewers set `about_software=yes`. On that subset:

- Exact agreement and κ on `discussion_type` (three content classes)  
- Collapsed binary: `technical_troubleshooting` vs (`general_dissatisfaction` ∪ `other`)

### 2.4 Optional filtered subsets (for paper-scope planning)

Without choosing the paper yet, also report collapsed troubleshooting agreement on:

| Subset | Definition |
|--------|------------|
| Broad software | both say `about_software=yes` |
| Update-focused | both say `about_software=yes` **and** `update_related=yes` |

This shows whether S1 vs S2 in `TASK_DEFINITION.md` is realistic.

### 2.5 Uncertainty

- Rows with any `unclear` on software or update fields  
- Rows with any `confidence=low`  
- Among disagreements, how often at least one side was low / unclear

---

## 3. Disagreement review

Blind-to-source table first:

`pilot_id`, A/B `about_software`, A/B `update_related`, A/B `discussion_type`, reasons, title from sheet

Then analysts may add source/stratum from the mapping.

Bucket disagreements, for example:

1. Software vs not software  
2. Update-related vs ordinary software support  
3. News/announcement vs troubleshooting  
4. Rant vs bug report  
5. Thin / missing text  
6. Hardware vs software  
7. Rule wording is unclear  

Read all software-field disagreements, all update-field disagreements, and at least 20 discussion-type disagreements (or all if fewer).

---

## 4. Rule revision

| Problem | Action |
|---------|--------|
| Software boundary unclear | Sharpen `REVIEWER_GUIDE.md` with one synthetic example |
| Update field too hard | Clarify that ordinary software help with no release link is `update_related=no` |
| Three-way type weak, binary strong | Prefer collapsed troubleshooting task for the larger pass |
| Missing text drives errors | Record as data limit; do not force guesses |

Large rule changes need a written note and a re-label of disagreed rows, not a silent full overwrite.

---

## 5. Go / no-go (proposed discussion thresholds)

| Signal | Encouraging | Caution | Redesign |
|--------|-------------|---------|----------|
| `about_software` κ | ≥ 0.70 | 0.50–0.69 | < 0.50 |
| `update_related` κ | ≥ 0.60 | 0.40–0.59 | < 0.40 |
| Three-way type κ (both software=yes) | ≥ 0.60 | 0.40–0.59 | < 0.40 |
| Collapsed troubleshooting κ | ≥ 0.70 | 0.55–0.69 | < 0.55 |

If `update_related` agreement is weak but software + type are strong, the larger pass can still use **S1** (broad software) and treat update linkage as secondary.

---

## 6. What not to do

- Do not treat Phase 1 `corrected_label` as pilot truth.  
- Do not treat API pools as truth.  
- Do not train models on pilot labels before the go/no-go write-up.  
- Do not compute these metrics until both humans finish.  
- Do not give reviewers `ANALYST_ONLY_EXAMPLES.md` during labeling.

---

## 7. Later deliverable (only after humans finish)

`phase2/annotation/pilot/PILOT_AGREEMENT_RESULTS.md` with completeness, κ tables, disagreement buckets, rule revisions, and S1/S2/S3/S4 recommendation.
