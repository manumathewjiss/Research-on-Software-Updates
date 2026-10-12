# Phase 2 research audit

**Date of this audit:** 2026-10-05  
**Phase 1 baseline left unchanged:** manuscript PDF, `tps_gds_classification/data/`, `data/c1_prime/`, `evaluation/outputs/`, and `analysis/outputs/`.  
**This audit did not** retrain models, change labels, or rewrite the paper.  
**Status words used below:** **verified** means a file, code path, or recomputation shows it; **suspected** means the evidence points that way and a remaining check could change the size of the effect; **unknown** means the project files do not record the fact.

The submitted manuscript is the 5-page PDF dated 2026-07-23 in its PDF metadata. A text extract is in `phase2/sources/icmla_manuscript.txt`. The ICMLA reviews (Paper 483) are in `phase2/sources/icmla_reviews.txt`. Counts below were recomputed by `phase2/audit_dataset.py` and saved in `phase2/audit_computations.json`.

There is no project `AGENTS.md`. The git repo is the parent folder `Research-on-Software-Updates`, branch `open-text-sentimental-sync`, commit `2a57869`. A full `git status` did not finish in several minutes, so the dirty-file list is **unknown**. This audit only added files under `phase2/`.

---

## Plain-language conclusion

The 542-post count, the 86 / 456 split, the main cross-validation table, and the published divergence averages are real saved results. The story built on top of those numbers is weaker than the paper says.

The labels mix several kinds of posts into one “general discontent” bin, including news, toy collecting, and some actual bug reports. The 80-post check compared a second rating with an answer key that was sitting in the same spreadsheet, and that check disagreed with the sentiment buckets 67.5% of the time. That disagreement is in the project files and is absent from the paper. The sentiment gap is mostly “the original poster’s text is less positive,” and it gets weaker if posts whose only author text is the title are separated from posts with a real author comment. Naive Bayes is the best full-thread model in the five-fold averages. It is not the best result in the project: title-only logistic regression scores higher, and a held-out test that existed before the PDF was built has logistic regression ahead of Naive Bayes.

The new ReleaseTrain endpoints are a different candidate list, not a larger set of confirmed labels. Downloading more of them will not, by itself, fix the paper.

---

## Priority findings

### P1. The 80-post “human validation” does not show that an independent person confirmed the labels

**Status: verified for the file design and the 32.5% figure; unknown for who filled the sheet.**

The paper (page 4 and Table V) says an independent annotator agreed with the gold labels on 91.2% of 80 threads, Cohen’s κ = 0.688. Those two numbers match `analysis/outputs/human_validation/summary.json` (`label_accuracy_vs_gold` 0.9125, `cohens_kappa` 0.688195991091314) and the confusion counts 10 / 3 / 4 / 63.

The same summary records `divergence_agreement_rate` 0.325. The report `analysis/outputs/human_validation/human_validation_report.md` says exact bucket agreement is 32.5% (26/80). The manuscript text extract does not mention 32.5%. The project’s own guide said divergence agreement of at least 65% was the bar for the trajectory claim to be defensible (`documentation/HUMAN_VALIDATION_GUIDE.md`, lines 62–66). The saved result is below that bar.

What the 32.5% is: each post was put into one of three buckets. The automatic bucket is “aligned” when the absolute author–community gap is under 0.15, otherwise “author more negative” or “community more negative” (`scripts/analyze_human_eval.py`, lines 100–104 and 191–212). On the 80 rows, the human rating is “aligned” 66 times. The automatic rating is “author more negative” on 23 of those 66, and “community more negative” on 20 of them (`phase2/audit_computations.json`, field `human.div_confusion`). The people-or-process who filled the sheet mostly did not see the author-more-negative pattern the paper reports.

The spreadsheet the script reads is `data/human_eval/human_eval_template_80.csv`. It contains `gold_corrected_label`, `gold_label_name`, `vader_divergence`, and `vader_author_more_negative` in the same file as the human columns. The exporter writes those answer columns before anyone labels (`scripts/export_human_eval_template.py`, lines 84–98). The guide tells the filler not to change the gold column and, for seven “edge” posts, tells them the gold label (`documentation/HUMAN_VALIDATION_GUIDE.md`, lines 17 and 31–43). κ here is agreement with that gold column. It is not agreement between two annotators who each labeled from scratch.

`ANNOTATION_GUIDELINES.md` lines 146 and 123 say a single annotator labeled much of the corpus and that inter-annotator agreement was future work. The 542-row file `tps_gds_classification/data/updated_labeled_dataset_unique.csv` has a `notes` column that is empty on all 542 rows. No file records a name, a date per decision, or a second labeler for the 542.

At least these saved notes in the 80-row file describe a different class from the human label stored on that same row:

| reddit_id | Human label | What the note says |
|-----------|-------------|--------------------|
| `1nuwiid` | GDS | Technical troubleshooting of a Chrome/YouTube blank-video issue |
| `1nznnb8` | GDS | Strong technical troubleshooting of a ComfyUI workflow |
| `1nv3m8j` | GDS | Technical troubleshooting of ComfyUI 3D generation |
| `1nwgz8q` | GDS | Clear Chrome video-playback support thread |
| `1o1cbch` | GDS | TPM detection failure with troubleshooting suggestions |
| `1nww0mp` | GDS | VMware upgrade and recovery troubleshooting |
| `1oiwr33` | GDS | Immich duplicate/cache problem with a diagnosed cause |
| `1nqu3ag` | TPS | Article sharing, not troubleshooting a concrete issue |
| `1pf32mo` | TPS | News and criticism, not active troubleshooting |
| `1nw9rwz` | GDS | Upgrade advice and performance troubleshooting |

Row `1ozp5qj` (r/angular, title “I still can't get used to it”) has a note about Android widgets. That note does not match the title or subreddit. **Suspected** copy or generation error. **Unknown** whether a person typed the 80 notes while looking at Reddit.

**Implication:** 91.2% and κ = 0.688 support “a second column often matches the gold column.” They do not support “an independent annotator confirmed the corpus” or “people agree with the sentiment-divergence buckets.”

**Repair:** A new labeling pass on a fresh sample, with the gold label and the VADER numbers hidden, by two people, with agreement computed between those two people. Keep the current 80-row file as a Phase 1 record of what was submitted.

### P2. “GDS” is a leftover bin, and the old API score is a poor stand-in for troubleshooting

**Status: verified.**

`corrected_label` on the unique file is 86 ones and 456 zeros. Unique `reddit_id` count is 542. The non-unique file has 574 rows and 32 duplicate ids. Those 32 duplicates disagree on `label_current` and agree on `corrected_label` (`phase2/audit_computations.json`, `labels.conflicting_duplicate_labels`). Deduplicating by keeping the first row does not create two gold labels for one post.

API candidate versus gold, from the unique file:

| API `label_current` | Gold GDS (0) | Gold TPS (1) |
|---------------------|--------------|--------------|
| 0 (GDS pool) | 397 | 71 |
| 1 (TPS pool) | 59 | 15 |

Disagreements: 71 + 59 = 130, which is 24.0%. The paper’s 24% sentence matches this count. Of the 86 gold TPS posts, 71 were taken from the pool the API had marked 0.

The saved raw responses show what that pool split actually was (`tps_gds_classification/data/raw/tps_response.json` and `gds_response.json`, fetched `2026-03-27T17:05:26.619683+00:00`):

- TPS request echo: `minComments=3`, `minScore=0.3`, `limit=500`, 74 posts returned, `total` 74.
- GDS request echo: `minComments=3`, `maxScore=0.5`, `limit=500`, 500 posts returned, `total` 500.
- Every TPS-pool post has `metadata.predicted.positiveScore` ≥ 0.3065. Every GDS-pool post has `positiveScore` ≤ 0.4982.
- The 32 duplicates are exactly the posts in the overlap band 0.3–0.5, and they appear in both responses.
- Reddit upvote `score` is a different field. Eight TPS-pool posts and 32 GDS-pool posts have Reddit score 0, so the filter is not “higher upvotes.”
- `metadata.predicted.isUpdateRelated` is false for all 500 GDS-pool posts, and true for only 42 of 74 TPS-pool posts.

The dataset JSON meta records the request URLs with `limit=2000` (`tps_gds_classification/data/tps_gds_dataset.json`, `meta.endpoints`), while the saved response `filters.limit` is 500. The GDS file contains exactly 500 rows. **Suspected:** the GDS pool was cut off at the server limit. **Unknown:** how many additional posts a higher limit would have returned in March 2026.

Platform `category` on the gold set (`audit_computations.json`, `lexical_title_vader.category_by_gold_label`): gold GDS includes 58 Positive, 66 Neutral, and 11 Negative. Gold TPS includes 9 Positive, 19 Neutral, and 5 Negative. Most rows have category `None`. Platform `tag` on gold GDS includes News (49), Photography / Poses (25), New Purchases (17), Rumour (6), and Software Release (5).

The written definition in `ANNOTATION_GUIDELINES.md` lines 35–43 and 93–95 puts announcements, politics, finance, and fandom into GDS, and says a pure release note is usually GDS. The paper’s abstract describes GDS as general frustration without technical detail. Those are different definitions. The guidelines’ own GDS examples `1misnpf`, `1mlixg3`, `1mhlyz0`, `1mul6k9`, and `1mid4hg` are not in the 542-row file. The TPS examples in that same table are in the file and match `corrected_label` 1.

Subreddits in the 542 (70 names). Largest: Android 87, transformers 83, Bitcoin 56, chrome 42, linux 25. Dates on the raw posts: GDS pool `2025-01-28T14:50:47` through `2026-03-26T20:52:44`; TPS pool `2025-09-23T11:18:17` through `2026-03-27T12:12:53`. The paper does not report this window. Reviewer 4 asked for it.

**Implication:** The 24% figure shows that `positiveScore` thresholds do not recover the gold labels. It does not show that a discontent detector failed. The new API’s own GDS description says the same thing in public: positiveScore stays high on update-related posts and does not separate the two classes (`phase2/new_sources/api/gds_response.json`, `criteria.description`).

**Repair:** Write one definition and apply it to every post. A useful split is “the main request is to diagnose or fix a software problem” versus “everything else,” and then say so. News, toy posts, and crypto opinion should be excluded or given their own label, not called discontent. Keep the current CSV as the Phase 1 label snapshot.

### P3. The divergence result is a level difference in the author’s text. The “over time” claim is not supported, and the significant p-value weakens when title-only author tracks are split out

**Status: verified for the published numbers and for the split; suspected for how much technical wording explains the rest.**

Saved full-corpus report `analysis/outputs/c1_prime_divergence/divergence_report_full.md`:

| Measure | TPS (n=86) | GDS (n=456) | Test in that file |
|---------|------------|-------------|-------------------|
| Mean absolute divergence | 0.371 | 0.2872 | Mann–Whitney p = 0.009221 |
| Author more negative | 69.77% | 53.73% | Mann–Whitney p = 0.006007 |
| Author mean sentiment | 0.0091 | 0.1911 | Welch p = 4.7e-05 |
| Community mean sentiment | 0.1683 | 0.194 | Welch p = 0.332 |
| Author trend (slope) | 0.0433 | 0.0026 | Welch p = 0.274 |
| Author early-versus-late shift | 0.0031 | −0.0084 | Welch p = 0.425 |

The paper’s Table II (0.371 vs 0.287, p = 0.009, 69.8% vs 53.7%, p = 0.006, d = 0.33, CI [0.023, 0.146]) matches this file. Cohen’s d in code is `(mean_tps − mean_gds) / sqrt((var_tps + var_gds) / 2)` (`analysis/c1_prime_stats.py`, lines 43–50), which weights the small TPS group equally with the large GDS group.

Community averages do not differ. Slope and early-versus-late shift do not differ. The significant pieces are “TPS author text is less positive” and “the absolute gap is larger.” The conclusion’s sentence that the separation stayed higher throughout thread progression goes beyond those tests.

How the author track is built (`trajectory/build.py`, lines 62–82): use the post body if it exists, then original-poster comments, and if that list is still empty use the title’s sentiment as the only author point. Recomputation on the raw JSON: **205 of 542** posts are in that title-only case (24 TPS, 181 GDS). Another 38 have a body and no author comment. Mean number of author comments is 1.49. `trajectory_eligible` is true for all 542 because the title fallback counts as one author point (`data/c1_prime/c1_prime_metrics.csv`; `trajectory_notes` is `ok` on every row).

Audit split of the saved divergence column (normal approximation to Mann–Whitney; on the full 542 this approximation returns p ≈ 0.00921, matching the saved 0.009221):

| Subset | TPS / GDS | Mean divergence | Approx. MW p |
|--------|-----------|-----------------|---------------|
| Title is the only author text | 24 / 181 | 0.366 vs 0.265 | 0.076 |
| Body or at least one author comment | 62 / 275 | 0.373 vs 0.302 | 0.060 |

In the title-only subset, community means are 0.148 (TPS) and 0.151 (GDS). In the real-author subset, author means are +0.077 (TPS) and +0.261 (GDS): both positive, TPS less so. **Verified:** the published p = 0.009 is the pooled set. **Verified:** neither half reaches 0.05 under this approximation.

Title wording: VADER compound on titles averages −0.148 for gold TPS and +0.060 for gold GDS. A short technical-word mask (`error`, `bug`, `fix`, `crash`, `install`, `broken`, `issue`, `problem`, `update`, `upgrade`, `dependency`, `config`) moves the TPS title mean to −0.062 and leaves the GDS mean at +0.060. Those words appear in 51.2% of TPS titles and 23.0% of GDS titles. **Suspected:** technical wording explains part of the title gap and not all of it. This was a diagnostic, not a new experiment in the paper.

Figure 5 is a different calculation from Table II (`scripts/render_sentiment_trajectory_figure.py`). It always starts the author average with title plus body (lines 88–94 and 122), plots a cumulative absolute gap, and smooths the drawn line with a 5-point average (lines 220–228) while the shaded band uses the unsmoothed curve. Saved meta `analysis/outputs/paper_figures/fig_results_sentiment_trajectory_meta.json`: end mean gap 0.358 (TPS) vs 0.268 (GDS); end author means −0.046 vs +0.162; end community means 0.171 vs 0.194. A cumulative average keeps a negative opening visible for the rest of the plot even when later comments are similar. Comment order in that figure parses timestamps (lines 52–74). The metric builder sorts `created_utc` as text (`trajectory/build.py`, lines 41–42 and 57). On this snapshot every timestamp matches `YYYY-MM-DDTHH:MM:SS` (0 unparsed), so the text sort is chronological here. **Verified** for this file. **Unknown** for any future export with a different time format.

Author identity: metric code treats a comment as the author’s if `is_submitter` is true or the author name matches (`trajectory/build.py`, lines 72–74). The figure returns false immediately when `is_submitter` is false and does not check the name (`render_sentiment_trajectory_figure.py`, lines 77–85). On the saved raw comments, `is_submitter` and the author-name check disagreed 0 times, so the two rules match on this snapshot.

Stored comments are fewer than Reddit’s `num_comments`: 55.2% of counted comments are stored in the TPS response (56 of 74 posts short) and 59.5% in the GDS response (368 of 500 posts short). Empty comment bodies: 0. The paper’s “complete comment tree” means every comment inside the JSON, which is a partial thread. Bot text matching “I am a bot” appears in 4 TPS-pool posts and 44 GDS-pool posts and is included in both classification text and sentiment.

**Repair:** Report author means and community means side by side. State that slope and early-late shift were not significant. Recompute the gap on posts with at least one real author comment, and report that subset even if the p-value rises above 0.05. Say that 205 author tracks are the title alone. Keep Figure 5 only if its caption describes cumulative means and smoothing.

### P4. “Naive Bayes is the best model” is true for one table and false for the project as a whole

**Status: verified.**

Table I in the paper matches the **fold averages** in `evaluation/outputs/paper_cv_full/summary.json` (run `2026-05-25T23:27:57Z`, 542 posts, 86 TPS, 5 stratified folds, seed 42, no undersampling; `run_metadata.json`). TF-IDF is fit inside each training fold (`evaluation/runner.py`, lines 96–105; `evaluation/models/logistic_regression.py`, lines 29–53; `evaluation/models/naive_bayes.py`, lines 27–44). That is the right place to fit it. Test-fold text is not used to build the vocabulary.

The same JSON stores a second set of scores, `bootstrap_oof`, computed on the pooled out-of-fold predictions (`evaluation/metrics.py`, lines 76–115). The paper’s caption says “OOF” and the printed point values are the fold averages. For precision-recall area those two summaries differ:

| Model | Fold-average PR-AUC (printed) | Pooled out-of-fold PR-AUC |
|-------|-------------------------------|---------------------------|
| Naive Bayes | 0.411 | 0.359 |
| Logistic regression | 0.431 | 0.369 |
| RoBERTa | 0.391 | 0.302 |

RoBERTa fold-average macro-F1 is 0.591; the pooled value is 0.617. One of the five RoBERTa folds has TPS-F1 of 0 (`evaluation/outputs/paper_roberta_5fold/roberta/summary.json`, second fold). Saved settings match the paper: `roberta-base`, length 256, batch 8, learning rate 2e-5, 2 epochs, device `mps` (same file, `params`). A 3-fold RoBERTa run exists (`evaluation/outputs/paper_roberta_3fold/`) with TPS-F1 mean 0.117 and is not in the paper. **Unknown** whether the epoch count and length were chosen before looking at these scores.

Held-out test saved `2026-05-26T21:04:59Z`, before the July manuscript (`evaluation/outputs/held_out_test/summary.json`): 82 test posts, seed 42. Logistic regression macro-F1 0.685 and TPS-F1 0.455; Naive Bayes 0.612 and 0.375. McNemar p = 0.027 for Naive Bayes versus logistic regression. The manuscript extract does not report this split.

Title-only logistic regression, full 542 (`evaluation/outputs/ablations/ablations_v1/ablation_table.csv`): macro-F1 0.758 ± 0.060, TPS-F1 0.580 ± 0.101. That is higher than Naive Bayes on full text (0.659 and 0.463). The paper’s Table III matches this CSV, including D2–D5. The conclusion still says Naive Bayes had the best minority-class tradeoff among all evaluated approaches. That sentence conflicts with Table III.

Logistic regression applies class balancing twice: `class_weight="balanced"` and `sample_weight` from `compute_sample_weight("balanced")` (`evaluation/models/logistic_regression.py`, lines 30 and 46–53). scikit-learn multiplies those two weights. Naive Bayes uses only the sample weight. **Unknown** how much this changes the comparison, because this audit did not refit the models. The paper’s method text says “class-balanced weights,” which does not describe the double application.

The VADER rule is keyword-first (`evaluation/models/vader_rules.py`, lines 48–55): any technical cue returns TPS, except the branch `compound < -0.6` and no cue, which returns GDS. The ±0.15 band is used only when no cue is present, and the final default is GDS. The paper’s sentence about “strongly negative sentiment but no technical indicators” describes one branch. Reviewer 7’s description of keyword exemption matches the `if tech: return 1` branch. High TPS recall 0.896 and precision 0.202 in Table I match this rule.

The older 40-example undersampled comparison in `tps_gds_classification/outputs/model_comparison.md` (GDS cut to 175, 261 rows) is a different experiment. Table I does not use those numbers.

**Repair:** One results table with fold mean, fold standard deviation, and pooled out-of-fold score for every metric, including title-only runs for Naive Bayes, RoBERTa, and the rule baseline. Report the held-out split that is already on disk. Refit logistic regression with a single balancing method before calling any model best. Describe the VADER rule as keyword-first.

### P5. Trajectory features and the “software subset” do not carry the claims the paper makes for them

**Status: verified.**

On the full 542, adding trajectory features to full-thread logistic regression raises TPS-F1 from 0.352 to 0.423 and macro-F1 from 0.632 to 0.647, and lowers PR-AUC from 0.431 to 0.366 (`ablations_v1/ablation_table.csv`, D3 versus D4). The paper reports the F1 rise and not the PR-AUC drop.

On the Tier-A subset the same D4 run does not help (`evaluation/outputs/ablations/ablations_tier_a/ablation_table.csv`):

| Setting | Full 542 macro-F1 | Tier-A macro-F1 | Full TPS-F1 | Tier-A TPS-F1 |
|---------|-------------------|-----------------|-------------|---------------|
| D3 full thread | 0.632 | 0.622 | 0.352 | 0.348 |
| D4 plus trajectory | 0.647 | 0.591 | 0.423 | 0.337 |
| D1 title only | 0.758 | 0.695 | 0.580 | 0.469 |

Table IV prints Tier-A Naive Bayes (0.703 and 0.535), which matches `evaluation/outputs/paper_cv_tier_a/summary.json` (n = 304, TPS 53, GDS 251, `2026-05-26T21:03:03Z`). It also prints D1 and D3. It omits D4. The sentence that primary findings stay stable on the software subset is true for Naive Bayes F1 and for the divergence direction (Tier-A means 0.412 vs 0.307, Mann–Whitney p = 0.0125, `divergence_report_tier_a.md`). It is false for “trajectory features improve TPS detection.”

Tier A is the allowlist in `evaluation/config.py`, lines 20–51. It has 304 posts. Android alone is 87 (28.6%). The allowlist includes Nest, IBM, and Oracle. It excludes Fedora (5), Ubuntu (3), homeassistant (4), ansible (3), ios (3), windows (4), MicrosoftEdge (8), and google (9), which are software communities in this file. r/transformers (83) and r/Bitcoin (56) are outside Tier A. **Verified** counts. **Unknown** whether this list was the intended definition of “software-focused,” because no design note records who chose it.

**Repair:** Publish D4 on Tier A. Either justify the allowlist post by post or define software by a written rule and apply it again. Keep the full 542 table as the mixed-community result.

### P6. The new endpoints and the PyPI package are candidate tools, not a bigger labeled corpus

**Status: verified from downloads on 2026-10-05. The package was read and not executed.**

Saved responses and the page log are under `phase2/new_sources/api/`. Collection times are the HTTP `Date` headers in `pagination_manifest.json`.

| Endpoint | What the server says it returns | Rows saved | Pagination | Dates |
|----------|----------------------------------|------------|------------|-------|
| `/api/reddit/query/tps` | Update-related posts whose title or body matches a troubleshooting phrase list. The description says this is a recall-oriented heuristic for later human labeling, and to expect false positives. | 2,378 unique ids, 5 pages (500+500+500+500+378) | `hasNext` became false on page 5. Header `X-Page` stayed `1` on later pages; the cursor was what advanced. | 2025-04-24 to 2026-10-05 |
| `/api/reddit/query/gds` | Update-related posts with none of those phrases. The description says positiveScore was tested and does not separate GDS from TPS. | 451 unique ids, one page | `hasNext` false, 451 < limit 500 | 2025-04-25 to 2026-10-05 |

The two new pools share 0 ids. They share 9 ids with the old 542 (8 in the new TPS pool, of which 6 are old gold TPS and 2 are old gold GDS; 1 in the new GDS pool, old gold GDS). These are mostly new posts.

Every new TPS row has `features.matchedKeywords`. `features.isUpdateRelatedSource` on the inspected row is `"predicted"`. Comments are present on 809 of 2,378 TPS rows and 118 of 451 GDS rows. Stored comments are about 32% and 29% of `num_comments`. Bodies are present more often than in the March 2026 files (67 empty bodies in the new TPS pool).

Illustrations, not a measured error rate: new GDS titles include “Firefox 157.0 has some serious memory leaks” and “Firefox not loading sites…”. New TPS titles include “Successful Upgrade to 26.04.1 (with glitches)” and “Need urgent advice on iCloud,” with the keyword match recorded in `features.matchedKeywords` (title or body). The largest new TPS communities are applehelp (356), chrome (230), Fedora (162), and comfyui (135).

`releasetrain-sentiment` 0.2.1 was downloaded from PyPI (uploaded 2026-10-03) into `phase2/new_sources/package/src/` and not imported. Differences from this repo’s methods:

- `score.py` `trajectory_summary` averages author **comments only**. If there are no author comments, the author average is 0. The post title is scored and then left out of the average (lines 166–176). This repo’s C1′ metric includes the body and, when needed, the title (`trajectory/build.py`, lines 62–82).
- `fetch.py` `to_scoreable_post` reads `selftext` or `description`, not `author_description`, which is the body field in the saved JSON (lines 45–49).
- `fetch.py` calls `https://releasetrain.io/api/reddit`, not `/query/tps` or `/query/gds`.
- `baseline_vader.py` says it was reconstructed from Reviewer 7’s paragraph, not from `evaluation/models/vader_rules.py`. Its keyword list is shorter, `fix` matches any word that starts with those letters, and `classify_technical_first` returns TPS for non-negative text with no keyword (lines 84–99). The repo rule returns GDS in that case (`vader_rules.py`, lines 48–55).
- `_classify.py` is TF-IDF plus multinomial Naive Bayes with `max_features=20000`, no `sublinear_tf`, and no class weights (lines 60–65). The paper’s Naive Bayes uses 12,000 features, sublinear TF, and balanced sample weights.
- `corpus.py` leaves the 542-post subreddit list, dates, and labeler as `None` (lines 73–88) and leaves `LABELING_PROCESS_NOTES` as a TODO (lines 128–131).

**Implication:** A model trained on these endpoints would be training on keyword membership unless new human labels are collected. The package’s own text says the 542-post file was not available when it was built. Citing the package as a reproduction of Table I would be incorrect.

---

## Claim check against saved results

| Manuscript claim | Status | Where the number lives |
|------------------|--------|------------------------|
| 542 threads, 86 TPS, 456 GDS | Verified | `updated_labeled_dataset_unique.csv`; `paper_cv_full/run_metadata.json` |
| About 24% of platform labels differ from corrected labels | Verified count. The platform field is `positiveScore` pool membership, not a TPS/GDS judgment | Crosstab above; raw `filters` |
| Text is title + body + up to 10 highest-scored comments | Verified in code | `text_preprocessing.py` `top_comments`, `combine_text`; fetch `max_comments` default 10. Histogram of `comments_included` peaks at 10 (301 of 574 JSON rows) |
| Five-fold Table I numbers | Verified as fold averages | `paper_cv_full/summary.json`, `paper_roberta_5fold/roberta/summary.json` |
| Naive Bayes best minority-class tradeoff among all approaches | Verified only inside Table I. False once Table III and the held-out file are included | `ablations_v1/ablation_table.csv`; `held_out_test/summary.json` |
| Title-only is the strongest representation | Verified for logistic regression | Ablation D1 |
| Trajectory features raise TPS-F1 from 0.352 to 0.423 | Verified on the mixed 542. False on Tier A (0.348 to 0.337) | `ablations_tier_a/ablation_table.csv` |
| Divergence 0.371 vs 0.287, p = 0.009 | Verified on all 542 | `divergence_report_full.md` |
| Gap stays larger across thread progress | Not supported by slope or early-late tests. Figure uses a cumulative, smoothed gap | `divergence_report_full.md`; figure script lines 122–139 and 220–228 |
| Tier A n = 304, NB 0.703 / 0.535, divergence p = 0.012 | Verified | `paper_cv_tier_a/run_metadata.json`; `divergence_report_tier_a.md` |
| Independent annotator, 91.2%, κ = 0.688 | Numbers verified. Independence unknown and unlikely from the file layout | `human_validation/summary.json`; exporter lines 84–98 |
| Learned models beat the VADER rule | Verified on macro-F1 in Table I | `paper_cv_full/summary.json` |

---

## Evaluation checks that came out clean

These were checked because they are common ways a result becomes too optimistic.

- Vocabulary is fit on the training fold only. Verified in `evaluation/runner.py` and `evaluation/models/logistic_hybrid.py` (`TfidfVectorizer.fit` on the training texts, then transform).
- The 32 double-fetched posts do not have two different `corrected_label` values.
- Cleaned text is empty for 0 JSON rows. Titles are empty for 0 gold rows. URLs and subreddits are present for all 542.
- Comment timestamps in the March 2026 files are ISO strings, so a text sort matches time order on this snapshot.
- `is_submitter` and the author name agreed on the stored comments.

Four titles are repeated across different ids (`dear rubyists: shopify isn’t your enemy`, the Firefox 145.0 title, `true`, and `lol` on four ids). They were not removed before cross-validation. **Unknown** whether copies fell in different folds. The practical risk looks small next to P1–P5.

---

## What to do next

Do these five things before any new model and before saying that a larger download improves the paper.

1. **Freeze Phase 1.** Leave the PDF, the 542 labels, and the output folders as the record of what ICMLA reviewed.
2. **Rewrite the label rule in one paragraph, then relabel with two people who cannot see the old label or the sentiment score.** The current GDS bin and the 32.5% bucket disagreement have to be settled before a new accuracy number means anything.
3. **Rebuild the divergence section around author text versus community text, with the title-only posts separated.** Report the non-significant slope and early-late tests. The pooled p = 0.009 can stay as a Phase 1 result with that limitation stated.
4. **Rebuild the results table from the files already on disk:** fold mean, fold spread, and pooled score; title-only for every model; the held-out split; Tier-A with and without trajectory features. Refit logistic regression with one weighting method.
5. **If new posts are collected, use the October 2026 endpoints only as a candidate list.** Budget a labeling sample. The 2,378 keyword hits are not 2,378 troubleshooting labels. The package baseline is not the experiment in this repo.

### Retain

- The practical question: some update threads ask for a fix, and many do not.
- The 542-row file as a Phase 1 label snapshot, with the provenance limits above.
- The demonstration that a `positiveScore` cutoff does not match those labels (130 disagreements; 71 of 86 gold TPS came from the low-score pool).
- Stratified folds, macro-F1, and TPS-F1. Accuracy stays high if a model always says GDS (0.841 in Table I).
- The code path that fits TF-IDF inside the training fold.

### Repair

- The class definition, the guideline examples that are not in the corpus, and the empty `notes` column.
- The 80-row validation: hide the answer key, use two people, and publish the 32.5% divergence result that is already computed.
- The divergence write-up: author mean, community mean, title-only subset, and the non-significant time tests.
- Table I’s “OOF” wording, the missing standard deviations, the omitted held-out file, and the double class weight.
- The VADER baseline description so it matches `vader_rules.py`.
- Figure 5’s caption so it matches the cumulative, smoothed curve.
- Tier A: publish the D4 row and either defend or replace the allowlist.
- The package, if it will be cited: point `baseline_vader.py` at `evaluation/models/vader_rules.py`, and fill `corpus.py` from the counts in this audit rather than from guesses.

### Replace

- “Naive Bayes is best among all evaluated approaches.”
- “An independent annotator confirmed the labels,” until a blinded two-person pass exists.
- “Sentiment divergence changes over the life of the thread,” as a tested result.
- “Trajectory features improve detection,” as a result that survives the software subset.
- Any plan that treats `/query/tps` and `/query/gds` as gold labels.
- Any plan that treats a larger keyword download as evidence the findings will get stronger.
