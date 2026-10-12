# Open questions

Only items the files cannot answer. Each one needs Manu or Professor Berhe. Everything else measured in this audit is in `phase2/RESEARCH_AUDIT.md`.

1. **Who assigned `corrected_label` on the 542 posts, and when?** The column `notes` is empty on every row of `updated_labeled_dataset_unique.csv`, `updated_labeled_dataset.csv`, and both manual-review CSVs. No file records a name or a date per decision.

2. **Did a second person label any of those 542 posts?** `ANNOTATION_GUIDELINES.md` says inter-annotator agreement was future work. The paper says an independent annotator reviewed 80 threads. Those can both be true only if the 80-row sheet is a different event from the original 542. The files do not say whether it was.

3. **Who filled `data/human_eval/human_eval_template_80.csv`, and did they look at `gold_corrected_label` and the VADER columns while rating?** The sheet contains those columns. The guide tells the filler the gold label for seven posts. Row `1ozp5qj` has a note about Android widgets on an r/angular post. The file does not name an author.

4. **Should GDS mean “anger or fatigue about an update,” or “any thread that is not troubleshooting”?** The guidelines put news, politics, finance, fandom, and release announcements into GDS. The abstract describes frustration without technical detail. Several gold-GDS notes in the 80-row file describe bug reports. The next paper needs one rule before relabeling.

5. **Is the Tier-A allowlist in `evaluation/config.py` the intended software set?** It keeps all 87 r/Android posts and drops Fedora, Ubuntu, homeassistant, ansible, and windows. Nobody recorded that choice in a design note.

6. **Were RoBERTa’s 2 epochs, sequence length 256, and learning rate 2e-5 locked before the reported five-fold run?** The saved run uses those values. A separate three-fold run is on disk and was not reported. The files do not say whether the settings were chosen by looking at scores.

7. **For the ICSC paper, which claim should stay if the others are cut?** The files support a small labeled benchmark and a weak author-versus-community level difference. They do not support a developer time-saving result, a change-over-time result, or “Naive Bayes is best overall.” The choice of what the next paper asserts is the authors’.

8. **Are `https://releasetrain.io/api/reddit/query/tps` and `/query/gds` the candidate source Professor Berhe wants for Phase 2, and is the keyword list frozen?** The copies saved on 2026-10-05 are keyword pools (2,378 and 451 posts), not human labels. They overlap the old 542 on 9 ids.

9. **May the 542-post file, comment text, and Reddit urls be released with an ICSC paper?** `DATA_CARD.md` says to follow Reddit’s terms and institutional review policy. This audit did not find an approval record.
