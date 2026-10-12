# Internal provenance

This directory is the local eight-page IEEEtran review draft. It is not a submission, and it is not publicly archived. The compiled manuscript has no data-availability section and does not cite the public project repository, because the phase 2–5 files behind these results were not verified to be on that remote. Nothing in this directory promises distribution on request.

Local files, all unpublished:

- `main.tex`, `references.bib`, `main.pdf`
- `FIGURE_SOURCES.md`, `SUPPLEMENTARY_APPENDIX.md`, `WHY_THIS_PAPER_IS_STRONGER.md`
- `REPRODUCIBILITY.md`
- `figures/diagnostic_visibility.csv` and `figures/purpose_scores.csv` (local mirrors; not required to compile)
- `overleaf_upload.zip` (the two manuscript source files only)

Compile steps and saved-result paths are in `REPRODUCIBILITY.md`. Figures are TikZ in `main.tex`. Do not refit models or rescore tests.

The ten-task final-stage record is `../final_improvement/FINAL_RESEARCH_IMPROVEMENT_REPORT.md`. The stage adds matched title/body VADER ablations, fold-wise coefficient inspection, revised figures, and a unified interpretation. Its development-only outputs are in `../final_improvement/results/`. No new score is inserted into the protected reserved or fresh test rows.

## Study-design ID check

The 237 diagnostic rows and the 30 main cases are separate samples. Six main-case identifiers also occur in the 237; one pilot identifier does too. The fresh 344 identifiers are outside the 3,362-record collection and do not overlap the diagnostic sample or the reserved 159. The reserved 159 do not overlap the 2,050 Reddit-URL development rows. All 542 secondary-cohort identifiers are inside the combined collection and use a different label system.

## Artifact status

https://github.com/SE4CPS/Research-on-Software-Updates is the existing public project remote. It is recorded here only so a later check can see what was not claimed. The phase 2–5 result files used for this draft are local. The Overleaf ZIP contains `main.tex` and `references.bib`. It does not contain data, identifiers, or these internal guides.

## Test URL check (9 October 2026)

Scored rows were joined by `reddit_id` / `redditId`. No model was fit.

| Scored set | n | URL source | Host |
| --- | --- | --- | --- |
| Reserved S2 (`s2_in_scope` true) | 159 | All 159 are in `phase2/combined_dataset/master_records.json` and in the saved fresh-collection pages. Hosts match. | `reddit.com` 159, other 0 |
| Fresh S2 | 344 | None of the 344 are in the 3,362-record combined collection. URLs come from `phase3/fresh_test_20261007/raw/`. | `reddit.com` 344, other 0 |

The reserved file has 200 rows, all `reddit.com`. Only the 159 S2 rows are the scored reserved test (135 troubleshooting, 24 other update). The fresh file is the 344-row S2 test (277 troubleshooting, 67 other update). Neither scored test contains the 30 non-Reddit URL records that sit in the development slice of the combined collection.

Primary sentiment results remain the 2,050 Reddit-URL development rows. The combined collection is still 3,362 records, not a verified-Reddit census.

## Text-only scores (not rescored)

- Reserved macro-F1 0.8626835204522258, quoted 0.863. Source: `phase3/icsc_full_paper/RESULT_VERSION_RECONCILIATION.json`.
- Fresh macro-F1 0.7915151515151515, quoted 0.792. Majority 0.44605475040257647. Fixed keyword 0.47390158551864175. Source: `phase3/fresh_test_20261007/results_fixed_model/metrics.json`.
- Development title and body 0.8319320360990539, title 0.750534, body 0.781424, VADER 0.533519 alone and 0.833130 with text, TextBlob 0.552128/0.834445, contextual 0.783792/0.835524, MiniLM 0.847561. Source: `phase5/expanded_study/results/metrics_table.csv`. Grouped intervals for the three augmented sentiment arms and for MiniLM include zero (`phase5/expanded_study/results/group_bootstrap.json`). The continuity-threshold score 0.8363107912443574 is not the inner-threshold score.
- The abstract states the fresh 0.792, the sentiment interval in words, and the 9-of-30 disagreement. Reserved and ablation numbers are in the results, not the abstract.

## AI-assistance disclosure

The acknowledgment names OpenAI Codex for scientific planning, source audit, outline and review comments, and literature checking, and Cursor for substantive drafting, LaTeX, tables, and figures, including placement of the saved development comparisons. It cites the IEEE Open page "Author Guidelines for Artificial Intelligence (AI)-Generated Text" (16 April 2024). Neither tool is described as the source of human review labels or engineer choices. The phase4 manuscript was left unchanged. Final author verification of the wording is still pending.
