# Phase 4 qualitative study package

**Status:** Pilot completed; Manu reports that institutional/data-use requirements and final privacy/case review are satisfied. Main blank workbooks are released to the same two external reviewers. The supporting determination/permission documents have not been reviewed by Codex.

## Files for the investigator

- `ANALYST_ONLY_CASE_SELECTION.csv`: 30 main and six pilot cases, historical labels, URLs, selection reasons, and source text. Never send this file to reviewers.
- `SELECTION_VALIDATION.json`: frozen-input hashes and checks for IDs, scope, domain, duplicates, and test overlap.
- `WORKBOOK_MANIFEST.json`: reviewer-specific order, count, and workbook hashes.
- `packet_source.json`: minimal text source used for packet generation; keep internal.
- `ANALYST_ONLY_RELEASE_REVIEW.md`: investigator decisions on flagged pilot and boundary cases; never send to reviewers.

## Files for reviewers, after participation approval

- Give `REVIEWER_GUIDE.md` and only `Reviewer_A_PILOT_6_BLANK.xlsx` to Reviewer A.
- Give `REVIEWER_GUIDE.md` and only `Reviewer_B_PILOT_6_BLANK.xlsx` to Reviewer B.
- The pilot is complete with no guide change. Give `Reviewer_A_MAIN_30_HOLD_UNTIL_PILOT.xlsx` only to Reviewer A, and `Reviewer_B_MAIN_30_HOLD_UNTIL_PILOT.xlsx` only to Reviewer B. The filenames preserve the original gate; the gate has now been met.

The selection is purposeful and development-only. Historical categories and selection reasons are hidden from reviewer workbooks. The reviewers see the same intact title/body text in different orders and have blank answer fields.

## Participation record

Manu reports that he and Professor Berhe approved all 30 cases (including `1ud1j0h`), the University of the Pacific requirements and text-sharing permission were confirmed, and the pilot reviewers answered independently without confusing instructions. Preserve supporting institutional/permission records privately. The main reviewers should remain independent and save first passes before discussion.

The main blank workbooks contain **no reviewer decisions**. Pilot submissions are preserved separately in `pilot_submissions/` and summarized in `PILOT_INTAKE.md`.
