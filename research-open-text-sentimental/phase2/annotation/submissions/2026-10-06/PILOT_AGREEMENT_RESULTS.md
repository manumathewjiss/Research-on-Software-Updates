# Human pilot agreement — corrected Berhe submission

The corrected Berhe sheet supersedes the byte-identical file initially supplied under that name. The initial file is preserved as `Berhe_Blind_Review_100_Posts_SUPERSEDED_DUPLICATE.csv`. Manu states that both authors reviewed the posts separately. These calculations use the two distinct completed files as submitted.

All 100 rows and required fields are complete in both files. Pilot IDs match, allowed values are valid, and discussion type is `na` exactly where `about_software` is not `yes`. Both files include distinct reason text for every row.

| Judgment | Posts compared | Exact matches | Agreement | Cohen’s κ |
|---|---:|---:|---:|---:|
| About software | 100 | 100 | 100.0% | 1.000 |
| Connected to an update | 100 | 96 | 96.0% | 0.927 |
| Discussion type, both software=yes | 87 | 86 | 98.9% | 0.972 |
| Troubleshooting versus other software discussion | 87 | 86 | 98.9% | 0.971 |

There are five field-level disagreements across five posts: four concern `update_related`, and one concerns `discussion_type`. The disagreements and both reviewers’ reasons are in `DISAGREEMENTS_TO_RESOLVE.csv`. Its final-decision fields are empty pending author resolution. Do not overwrite either reviewer’s original answers.

The pilot intentionally oversampled hard cases and used saved, sometimes incomplete text. Agreement does not establish the prevalence of classes in the source population, nor does it prove that the labels are valid beyond this pilot. Any manuscript description should name the sampling method, the two reviewers, the guide, and this limitation.

Counts in the two files differ slightly: Manu marked 54 update-related posts and 63 troubleshooting posts; Berhe marked 55 and 64. The unresolved rows should not enter a final adjudicated dataset until a resolution is recorded.

`CONSENSUS_95_FOR_ANALYSIS.csv` contains the 95 posts where both reviewers gave exactly the same values for the three research fields. It is a derived analysis table, not a replacement for the submitted sheets. It includes 46 posts from Phase 1 and 49 new API candidates; only the latter can form a genuinely new-post evaluation set. The five disagreements remain excluded pending author resolution.
