# Combined Phase 2 candidate dataset

`master_records.json` contains **3,362 unique Reddit posts** from the saved Phase 1 file and Professor Berhe's October 5 API downloads. `phase2/build_combined_dataset.py` rebuilds it from the preserved source files.

| Source | Unique posts in master |
|---|---:|
| Original Phase 1 dataset | 542 |
| New API posts after removing nine overlaps with Phase 1 | 2,820 |
| **Total** | **3,362** |

Phase 2 labels currently exist for **3,357 posts**: 100 pilot posts (final decisions after discussion), 300 expansion posts reviewed jointly, 200 reserved-test posts reviewed jointly, and 2,757 posts from Manu's assisted-review workbooks. **Five posts** remain uncertain because the saved material is insufficient. **No untouched posts remain** in the current 3,362-post corpus. Empty Phase 2 fields mean *unresolved*, not a negative class.

The **200** reserved-test posts are marked `reserved_test_consensus` in the current master. They were selected before generating model suggestions and must stay out of model training and model selection. Their final label file is `../annotation/heldout_200/final_consensus.json`; the two submitted workbooks are preserved in `../annotation/submissions/2026-10-06-holdout200/`. Manu clarified that one draft was written together, so these files cannot be used to calculate independent agreement. The other posts have now been reviewed; five remain unresolved.

`phase1_legacy_label` preserves the original two-class judgment on old posts. It is not automatically converted into `phase2_discussion_type`. API `source_pool` values identify how a post was found and are not verified labels.

The 300 expansion labels were agreed together, so they do not supply an independent agreement score. The 100-post pilot's pre-discussion agreement is recorded separately in `../annotation/submissions/2026-10-06/PILOT_AGREEMENT_RESULTS.md`. The first five post-discussion changes are recorded in `../annotation/submissions/2026-10-06-update/INTAKE_AND_NEXT_STEPS.md`; the later review and its additional revisions are recorded in `../annotation/submissions/2026-10-06-second-review/REVISION_REPORT.md`.

`blind_review_old_493.json` preserves the original 493-post blank review snapshot. `blind_review_old_remaining.json` is now empty because every original post has entered a Phase 2 review batch. Completed review files are preserved under `../annotation/submissions/`; the combined master is rebuilt from them, leaving the Phase 1 source data intact.

The master is a **candidate corpus**, not a 3,362-post gold-standard dataset. Only reviewed and adjudicated rows may be counted as confirmed labels in a paper. The first 500-post workbook has 314 accepted proposals, 182 revised rows, and four uncertain rows. The second has 341 accepted, 157 revised, and two uncertain. The 1,000-post workbook has 758 accepted and 242 revised rows. The final 762-post batch has 564 accepted and 198 revised rows; one earlier uncertain case was resolved and five remain uncertain. The 2,757 resolved assisted rows are marked `manu_assisted_review`. This is assisted verification, not independent blind annotation. Provisional model or assistant suggestions are stored separately and do not enter the confirmed-label columns until checked by a person.
