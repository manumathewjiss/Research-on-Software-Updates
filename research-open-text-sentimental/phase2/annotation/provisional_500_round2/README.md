# Next five review batches: 6 through 10

These five sheets contain **500 different posts** that had not entered a Phase 2 review batch. They contain the remaining 243 posts from the original dataset, the remaining 57 posts from the October 5 general-query pool, and 200 posts sampled from the larger October 5 troubleshooting-query pool. The four uncertain posts from the previous workbook are not repeated here. The 200 reserved test posts are excluded.

For **each row**, read the title, body, and saved replies. Use the [reviewer guide](../REVIEWER_GUIDE.md) to judge `about_software`, `update_related`, and `discussion_type`. In `decision`, write:

- `accept` when all three proposed labels are correct;
- `revise` when any label is wrong, then fill **all three** `final_*` fields and explain the correction in `reviewer_note`;
- `uncertain` when the saved text is insufficient, with an explanation in `reviewer_note`.

Save a new copy of the workbook after each batch. Every row requires your judgment, including medium-confidence rows. The proposed labels are **automatic review aids**, not confirmed labels. The system was trained on 400 earlier development reviews and 496 posts from Manu's first assisted review; it did not use the reserved test labels. Because the model predicts general dissatisfaction rarely, check complaints and mixed complaint/bug reports carefully. The query-pool names are sampling sources, not labels.

One long post, `B7-011`, was shortened to fit in an Excel cell. The full saved body is in `B7-011.txt` in this folder. If the displayed text is insufficient, read that file before deciding or mark the row uncertain.

The five CSVs are plain-text copies of the workbook tables. `ANALYST_ONLY_MAPPING.json`, `provisional_labels.json`, and `sampling_manifest.json` preserve how posts were selected and proposed. Do not treat the previous assisted review or these proposals as independent blind annotations in the paper.

After all 500 posts in this workbook receive resolved labels, **1,762 posts will still be untouched**, plus **four** uncertain posts from the prior workbook. Thus **1,766 posts** will still need a decision if no new uncertainties arise in this batch.
