# Pilot sample quality report

**Last repaired:** 2026-10-05  
**Builder:** `phase2/build_pilot_sample.py --from-mapping`  
**Seed (original draw):** `20261005`  
**n:** 100 unique posts preserved from the prior pilot draw  
**Human labels:** none filled

---

## 1. Files

| Path | Audience |
|------|----------|
| `REVIEWER_GUIDE.md` | Reviewers |
| `PILOT_INSTRUCTIONS.md` | Pointer to the reviewer guide |
| `pilot/reviewer_A_sheet.csv` | Reviewer A |
| `pilot/reviewer_B_sheet.csv` | Reviewer B (identical blank copy) |
| `pilot/pilot_id_mapping.csv` | Analysts only |
| `ANALYST_ONLY_EXAMPLES.md` | Analysts only (real-post tentative notes) |
| `../TASK_DEFINITION.md` | Authors/analysts (research design) |
| `PILOT_ANALYSIS_PLAN.md` | Analysts |

---

## 2. Repair checks (this pass)

| Check | Result |
|-------|--------|
| Same 100 `(pilot_id, reddit_id, sheet_order)` pairs preserved | Yes |
| Reviewer A sheet == Reviewer B sheet | Yes |
| Answer fields blank | Yes (`about_software`, `update_related`, `discussion_type`, `confidence`, `reason`) |
| No source pool / old label / keyword / sentiment columns on sheets | Yes |
| Retired combined `scope` column removed from sheets | Yes |
| Reviewer-facing docs contain no pilot reddit ids | Verified for `REVIEWER_GUIDE.md`, `PILOT_INSTRUCTIONS.md`, `README.md`, and cleaned `TASK_DEFINITION.md` |
| Reviewer-facing docs contain no pilot titles (≥12 chars) | Verified |
| Real-post tentative examples moved to analyst-only file | Yes |

---

## 3. Sample composition (unchanged selection)

| Source | n |
|--------|---|
| Phase 1 gold file | 49 |
| Oct 5 `/query/tps` candidates | 33 |
| Oct 5 `/query/gds` candidates | 18 |

Text availability (saved snapshot): title+body+replies 33; title+replies 37; title+body 28; title only 2.

API pools remain **candidates only** in the mapping file.

---

## 4. Reviewer sheet columns

`pilot_id`, `sheet_order`, `title`, `post_body`, `discussion_context`, `text_availability_note`, `about_software`, `update_related`, `discussion_type`, `confidence`, `reason`

---

## 5. Limitations (unchanged)

Quotas oversample hard cases; not a prevalence sample. Comment trees are incomplete. Title-only rows may produce more `unclear` answers. Regenerating with `--resample` would change the set; use `--from-mapping` to refresh sheets only.
