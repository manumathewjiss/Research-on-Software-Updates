# Reported independent first-pass agreement

Manu reports that the two reviewers completed the 200-post first passes separately, without discussion or seeing the other person's completed answers before both files were saved. The workbooks themselves cannot verify the review sequence. Earlier familiarity with some development posts remains possible.

The submitted category and diagnostic answers are identical for every eligible item; all 200 free-text reasons differ in wording. This is **perfect agreement in these files**, not proof that either answer is correct or that future reviewers will agree perfectly. The sample was deliberately stratified and is not a prevalence sample.

| Field | Eligible posts | Exact agreement | Cohen's kappa |
|---|---:|---:|---:|
| `about_software` | 200 | 1.000 | 1.000 |
| `update_related` | 200 | 1.000 | 1.000 |
| `discussion_type` | 200 | 1.000 | 1.000 |
| `confidence` | 200 | 1.000 | 1.000 |
| `software_product` (troubleshooting only) | 118 | 1.000 | 1.000 |
| `identifiable_release` (troubleshooting only) | 118 | 1.000 | 1.000 |
| `environment` (troubleshooting only) | 118 | 1.000 | 1.000 |
| `specific_symptom` (troubleshooting only) | 118 | 1.000 | 1.000 |
| `reproduction_context` (troubleshooting only) | 118 | 1.000 | 1.000 |
| `error_evidence` (troubleshooting only) | 118 | 1.000 | 1.000 |
| `attempted_remedy` (troubleshooting only) | 118 | 1.000 | 1.000 |
| `help_request` (troubleshooting only) | 118 | 1.000 | 1.000 |

No disagreement adjudication is needed for these submitted categorical answers. Raw category counts and confusion tables are in `AGREEMENT.json`; `unclear` is retained as a category. A bootstrap of perfectly identical observed pairs would return a degenerate interval and would not establish perfect agreement beyond this sample, so no such interval is presented.

**Interpretation limits:** This is agreement between the two reported separate first passes on selected development records. It does not validate the correctness of labels or the reserved/fresh test labels. The exact agreement is unusual and should be described transparently, including the user-reported independent workflow and the fact that prior corpus exposure cannot be ruled out from the files alone.
