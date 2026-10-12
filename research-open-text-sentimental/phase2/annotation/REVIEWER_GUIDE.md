# Reviewer guide (Phase 2 pilot)

**Who this is for:** Reviewer A and Reviewer B only  
**Fill:** your sheet in `phase2/annotation/pilot/`  
**Do not open:** `pilot_id_mapping.csv`, `ANALYST_ONLY_EXAMPLES.md`, Phase 1 label files, or old validation CSVs

Work alone. Do not compare answers until both sheets are finished. Do not ask a chatbot to fill the sheet for you.

This guide uses **made-up** examples only. They are not from the pilot set.

---

## 1. Your sheet

| Reviewer | File |
|----------|------|
| A | `phase2/annotation/pilot/reviewer_A_sheet.csv` |
| B | `phase2/annotation/pilot/reviewer_B_sheet.csv` |

Each row shows:

- `pilot_id` — anonymous id  
- `title`  
- `post_body` — may be empty  
- `discussion_context` — up to five short replies when available  
- `text_availability_note`  

You fill:

- `about_software`  
- `update_related`  
- `discussion_type`  
- `confidence`  
- `reason`  

There is no answer key in your file.

---

## 2. Fields and allowed values

### `about_software`

| Value | Meaning |
|-------|---------|
| `yes` | The main topic is software (app, OS, service, tool, plugin, firmware/settings treated as software, or a problem that looks software-caused) |
| `no` | The main topic is not software |
| `unclear` | You cannot tell from the text you have |

### `update_related`

| Value | Meaning |
|-------|---------|
| `yes` | Connected to a software update, upgrade, release, patch, version change, or something that broke/changed after one |
| `no` | Not connected to an update/release in that way |
| `unclear` | You cannot tell |

Fill `update_related` on every row.  
A normal software help question with **no** update/release link should be `about_software=yes` and `update_related=no`.

### `discussion_type`

| Value | Meaning |
|-------|---------|
| `technical_troubleshooting` | Main purpose is to identify, diagnose, ask how to fix, or give a concrete fix for a software problem |
| `general_dissatisfaction` | Main purpose is criticism or frustration **without** a real troubleshooting purpose |
| `other` | About software, but neither of the above (news, praise, announcements, neutral tips) |
| `na` | Use when `about_software` is `no` or `unclear` |

Rules:

- If `about_software` is `yes`, choose `technical_troubleshooting`, `general_dissatisfaction`, or `other` (not `na`).  
- If `about_software` is `no` or `unclear`, set `discussion_type` to `na`.  
- Do **not** call news or praise “dissatisfaction.”

### `confidence`

`high` · `medium` · `low`

### `reason`

One short sentence in your own words.

---

## 3. Decision tree

```
1. Read title → body → replies shown.
2. about_software?
   - mainly software → yes
   - clearly not software → no
   - cannot tell → unclear
3. update_related?
   - tied to update/upgrade/release/change-after-update → yes
   - clearly not → no
   - cannot tell → unclear
4. discussion_type?
   - if about_software is no or unclear → na → go to step 5
   - if about_software is yes:
       - main ask is diagnose/fix a software problem (even if angry) → technical_troubleshooting
       - main ask is complain/criticize with no repair path → general_dissatisfaction
       - news, praise, announcement, neutral talk → other
5. Set confidence. If you almost guessed, use low.
6. Write a one-line reason.
```

---

## 4. Mixed complaints and technical reports

- Angry + versions + “how do I fix this?” → usually `technical_troubleshooting`.  
- “This app sucks” with no failure details → usually `general_dissatisfaction`.  
- One bug word inside a rant, with no diagnosis path → still usually `general_dissatisfaction`.  
- Release notes / “version X is out” → usually `other`, even if comments complain.  
- If the original post is still stuck and asking how to apply a fix → `technical_troubleshooting`.

Ask: *Would a support person treat the original post as an active ticket to diagnose?*  
If yes → troubleshooting. If it is mainly mood or news → the other types.

---

## 5. Missing body or replies

- Empty body → use title and any replies.  
- No replies → use title and body.  
- Only a vague title → prefer `unclear` on the field you cannot judge, and/or `confidence=low`.  
- For this pilot, judge the **saved text in the sheet**. Do not open live Reddit to recover deleted text unless the study leads ask for a later pass.

---

## 6. Synthetic practice examples (not in the pilot)

These posts are invented. Practice the fields; do not memorize them as a key.

| Made-up title / situation | about_software | update_related | discussion_type |
|---------------------------|----------------|----------------|-----------------|
| “CloudNotes 4.2 crashes when I export PDF; log attached” | yes | unclear or yes if they blame 4.2 | technical_troubleshooting |
| “CloudNotes keeps changing buttons for no reason, I hate it” (no failure to fix) | yes | yes if about recent changes; else no/unclear | general_dissatisfaction |
| “CloudNotes 4.2 release notes: dark mode and export fixes” | yes | yes | other |
| “How do I write a formula in SpreadsheetApp?” (no update mentioned) | yes | no | technical_troubleshooting or other (tips); if asking to fix broken formula behavior → troubleshooting |
| “My shelf of robot figures after rearranging the cabinet” | no | no | na |
| “Coin price go up; dyno update was wild” (finance slang, not an app) | no | no | na |
| Title only: “Help???” with no body/replies | unclear | unclear | na |

---

## 7. Independence

- Do not edit the other reviewer’s file.  
- Do not open `pilot_id_mapping.csv` or `ANALYST_ONLY_EXAMPLES.md`.  
- Prefer honest `unclear` / `low` over guessing.

---

## 8. When you are done

1. Save your CSV.  
2. Tell Manu which letter you used.  
3. Wait for the planned agreement analysis. Do not reconcile disagreements by chatting first.
