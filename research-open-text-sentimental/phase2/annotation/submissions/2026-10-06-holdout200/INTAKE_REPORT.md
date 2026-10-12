# Reserved 200-post review intake

The two submitted workbooks in this folder are exact copies of the files supplied by Manu. They contain 200 rows each. The anonymous ids, order, title, body, shown replies, and availability notes match the prepared reserved sample. All answer fields are complete and use allowed values. No old, pilot, or previously reviewed post appears in this set.

The two workbooks have identical choices for `about_software`, `update_related`, `discussion_type`, and `confidence` on all 200 rows. All 200 written reason sentences differ. Manu clarified that **one draft was written together**. These are jointly agreed labels. Do not report an independent agreement statistic for this set. Their consensus labels are now stored as `reserved_test_consensus` in the combined master and remain excluded from training and model selection.

## Descriptive counts in the submitted workbooks

| Field | Counts |
|---|---|
| About software | yes 192; no 6; unclear 2 |
| Update related | yes 161; no 37; unclear 2 |
| Discussion type | troubleshooting 166; other 17; dissatisfaction 9; not applicable 8 |
| Confidence | high 135; medium 39; low 26 |

Under the strict `about_software=yes` and `update_related=yes` scope, 159 posts remain: 135 troubleshooting, 15 other, and 9 dissatisfaction. A constant troubleshooting prediction would be correct for 135/159 (84.9%) in that strict subset. This test sample is source-stratified, with 100 posts from each keyword-defined API pool, and is not a prevalence estimate for Reddit. It contains only 24 strict-scope non-troubleshooting posts, so negative-class estimates will be imprecise.

Among the 100 posts sampled from the API's `gds` candidate pool, 78 are marked troubleshooting in the submitted workbooks. The API pool names are not verified labels.

## Next steps

1. Keep the 200 joint labels frozen and excluded from training and model selection. Describe their joint review process accurately.
2. Build training data from the other reviewed 400 and additional checked posts, especially the 493 old posts awaiting Phase 2 labels. Add or separately evaluate more non-troubleshooting update discussions so performance is not hidden by the high troubleshooting rate.
3. Run the preselected baselines and models once on the frozen reserved set. Report technical-class precision, recall, F1, nontechnical-class performance, and uncertainty, with the 84.9% constant-positive reference.

**SHA-256:** Manu workbook `15126deb2c04799480252eb4a158094efa62b4436f66a50dbf74624ffa70ba17`; Berhe workbook `78dac2773212781370693eff3d048421472313628c11fb65ba4acb412fc7b976`.
