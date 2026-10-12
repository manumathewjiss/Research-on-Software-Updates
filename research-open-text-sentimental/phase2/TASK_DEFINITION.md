# Phase 2 task definition (research design)

**Status:** repaired pilot definition (2026-10-05)  
**Does not change** Phase 1 labels.  
**Reviewers should use** `phase2/annotation/REVIEWER_GUIDE.md`, not this file, while labeling.

This document is for authors and analysts. It states the operational fields, how mixed cases work, and how a final paper might use the fields. Real corpus examples with tentative answers live only in `phase2/annotation/ANALYST_ONLY_EXAMPLES.md` (analyst-only).

---

## 1. What we are measuring

For each Reddit post snapshot, humans separately judge:

1. **Is the discussion about software?**  
2. **Is it connected to a software update, upgrade, release, or a change that followed one?**  
3. **If it is about software, what is the main discussion type?** technical troubleshooting, general dissatisfaction, or other.

These are separate judgments. A software support question is **not** automatically an update discussion.

---

## 2. Fields

### 2.1 `about_software`

| Value | Meaning |
|-------|---------|
| `yes` | Main topic is software, an app/OS/service/tool, configuration of software, or a failure plausibly caused by software |
| `no` | Main topic is not software (toys, pure finance, politics, lifestyle, etc.) |
| `unclear` | Cannot tell from the saved text |

Firmware / phone settings count as software when the thread treats them as software behavior or software settings. Pure physical hardware with no software angle is usually `no`.

### 2.2 `update_related`

| Value | Meaning |
|-------|---------|
| `yes` | Connected to a software update, upgrade, new release, patch, version bump, or a problem/change that followed one |
| `no` | About software (or not), but **not** tied to an update/release/change-from-update |
| `unclear` | Cannot tell whether an update/release is involved |

Fill this field even when `about_software=no` (usually `no` or `unclear`). Do not set `update_related=yes` only because the word “update” appears in an unrelated way (for example, updating a toy display).

### 2.3 `discussion_type`

Fill a content type only when `about_software=yes`. Otherwise use `na`.

| Value | Meaning |
|-------|---------|
| `technical_troubleshooting` | Main purpose is to identify, diagnose, ask how to resolve, or offer a concrete resolution for a software problem |
| `general_dissatisfaction` | Main purpose is criticism or frustration without a substantive troubleshooting purpose |
| `other` | About software, but neither of the above (news, praise, announcements, neutral tips, strategy talk) |
| `na` | Use when `about_software` is `no` or `unclear` |

**Never map `other` to dissatisfaction.**

### 2.4 `confidence` and `reason`

- `confidence`: `high` | `medium` | `low`  
- `reason`: one short sentence

---

## 3. Mixed complaints and technical reports

1. Read title, then body, then shown replies.  
2. Judge `about_software` and `update_related` first. They do not depend on tone.  
3. If `about_software` is not `yes`, set `discussion_type=na`.  
4. If `about_software=yes`, ask what the **original post’s main purpose** is:  
   - Concrete failure + diagnosis/fix ask → `technical_troubleshooting` even if the writer is angry.  
   - Rant/criticism with no real repair path → `general_dissatisfaction` even if a bug word appears once.  
   - News, changelog, praise, showcase, neutral discussion → `other`.  
5. Replies can clarify, but a joke thread under a bug report does not erase the bug report, and one technical comment under a news post does not turn the whole post into troubleshooting.

---

## 4. How a final paper can use these two scope fields

None of these options is locked yet. The pilot measures whether humans can fill the fields reliably.

| Paper scope option | Keep rows where | Positive / main class (example) | Use of `update_related` |
|--------------------|-----------------|----------------------------------|-------------------------|
| **S1. Broad software triage** | `about_software=yes` | `technical_troubleshooting` vs (`general_dissatisfaction` ∪ `other`) | Reported as a descriptor; not required for inclusion |
| **S2. Update-focused triage** | `about_software=yes` **and** `update_related=yes` | same binary or three-way types | Required inclusion filter |
| **S3. Two-stage filter** | stage 1: `about_software`; stage 2 optional: `update_related` | troubleshooting among the filtered set | Second-stage gate |
| **S4. Three-way among update threads** | `about_software=yes` and `update_related=yes` | troubleshooting vs dissatisfaction vs other | Required |

Phase 1 treated many non-troubleshooting posts as one “GDS” bin. S1–S4 all avoid silently calling news or praise “dissatisfaction.”

---

## 5. What this pilot does not do

- Does not copy Phase 1 `corrected_label`  
- Does not treat API `/query/tps` or `/query/gds` as labels  
- Does not ask for sentiment or author–community divergence  
- Does not allow model-filled “human” sheets  

---

## 6. Author decisions still open

1. After agreement results exist, lock S1, S2, S3, or S4 (or a variant).  
2. Confirm firmware / settings default (this draft: software when treated as software behavior).  
3. Confirm “is X dead?” with no defect → `other` unless the main thrust is affective ranting.  
4. Confirm reviewers judge the **saved sheet snapshot only** (no live Reddit lookup) for this pilot.
