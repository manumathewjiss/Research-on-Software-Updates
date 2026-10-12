# Reviewer response matrix

Source: `phase2/sources/icmla_reviews.txt`, extracted from `Conference Management Toolkit - View review.pdf` (Paper 483, ICMLA 2026 main track). The local manuscript is the 5-page PDF extracted to `phase2/sources/icmla_manuscript.txt`.

Scores, so the matrix is not only the written comments:

| Reviewer | Originality | Soundness | Significance | Clarity | Recommendation |
|----------|-------------|-----------|--------------|---------|----------------|
| 4 | Fair | Poor | Fair | Fair | Weak reject |
| 7 | Very good | Very good | Very good | Excellent | Accept |
| 9 | Fair | Good | Fair | Good | Weak reject |

“Current evidence” is what the Phase 1 files already show. Nothing below is a completed new experiment.

---

## Reviewer 4

### R4-W1. Dataset is small (542 posts, 86 TPS), so the model comparison has limited statistical power

| | |
|--|--|
| **Current evidence** | **Verified.** Unique file has 542 ids, 86 `corrected_label=1`, 456 `corrected_label=0`. Five-fold test folds therefore contain about 17 TPS posts each. RoBERTa fold 2 has TPS-F1 of 0 (`evaluation/outputs/paper_roberta_5fold/roberta/summary.json`). Fold standard deviations on TPS-F1 are large (Naive Bayes 0.047, logistic regression 0.162, RoBERTa 0.189). |
| **Remaining work** | A larger **labeled** set, or a pre-registered statement that the contribution is a small benchmark plus a limitation. More unlabeled API rows do not add power. |
| **Done when** | A methods section states the TPS count used in each test fold, and any new corpus reports a labeled TPS count with a blinded labeling protocol. A keyword download is not counted as labeled data. |

### R4-W2. The practical claim (developers find troubleshooting threads faster) has no downstream test

| | |
|--|--|
| **Current evidence** | **Verified as absent.** The manuscript extract’s conclusion says future work will evaluate usefulness with software teams. There is no user study, ranking metric, or “was this useful to a developer” label in the repo. `releasetrain-sentiment` `evaluate.py` only provides a function stub for that test; it was not run, and it has no such labels. Reviewer 4 says this was “acknowledged in the limitations.” The extracted 5-page text has no heading “Limitations.” |
| **Remaining work** | Either drop the efficiency claim or run a small study: give people a mixed list and a TPS-ranked list and record time and how many true troubleshooting threads they open. |
| **Done when** | The abstract’s sentence about reducing manual effort is either removed or paired with a measured time or precision-at-k on labels that mean “a developer would act on this,” collected for that purpose. |

### R4-D1. Section III-A needs the subreddits and the time window

| | |
|--|--|
| **Current evidence** | **Verified and now measured.** 70 subreddits. Largest: Android 87, transformers 83, Bitcoin 56, chrome 42, linux 25 (`phase2/audit_computations.json`). Raw post times: GDS pool 2025-01-28 to 2026-03-26; TPS pool 2025-09-23 to 2026-03-27. Fetch timestamp on the raw JSON: 2026-03-27T17:05:26Z. The paper does not report these. |
| **Remaining work** | Put the window, the top communities, and the Tier-A rule in the corpus section. State that r/transformers and r/Bitcoin are inside the 542. |
| **Done when** | A reader can list the collection dates and the community mix without opening the JSON. |

### R4-D2. Table I should show fold standard deviations for every metric

| | |
|--|--|
| **Current evidence** | **Verified gap.** The paper prints a standard deviation for macro-F1 and TPS-F1 only. The JSON already has `*_std` for accuracy, precision, recall, and PR-AUC (`paper_cv_full/summary.json`, `paper_roberta_5fold/roberta/summary.json`). Pooled out-of-fold scores differ from the printed fold averages, especially PR-AUC (Naive Bayes 0.411 fold-average vs 0.359 pooled). |
| **Remaining work** | Reprint the table from those JSON fields. Label fold averages and pooled scores as two columns. |
| **Done when** | Every metric in the main table has a fold mean, a fold standard deviation, and the pooled out-of-fold value, copied from the saved JSON or from a rerun that matches it. |

### R4-D3. Report title-only performance for Naive Bayes, RoBERTa, and VADER, not only logistic regression

| | |
|--|--|
| **Current evidence** | **Verified that this is missing.** Title-only results exist only for logistic regression (`ablations_v1` D1: macro-F1 0.758 ± 0.060, TPS-F1 0.580 ± 0.101). That already beats full-thread Naive Bayes. No saved title-only run for Naive Bayes, RoBERTa, or the rule baseline. |
| **Remaining work** | Rerun those three on `text_title_only` with the same folds and seed. Do not tune on the result and then hide the worse runs. |
| **Done when** | A table has title-only and full-thread rows for all four systems, with the same metrics as Table I. |

### R4-D4. Manually read 30 high-divergence TPS threads and 30 high-divergence GDS threads to test the “bug words make VADER negative” idea

| | |
|--|--|
| **Current evidence** | **Not done.** The review text points to a “Major 3” lexical hypothesis. The exported review has two numbered weaknesses and does not contain a Major 3 paragraph. **Unknown** whether CMT cut text. A partial diagnostic is in this audit: TPS titles are more negative than GDS titles (−0.148 vs +0.060), and masking a short technical-word list moves the TPS title mean to −0.062. That is not the 30-versus-30 reading. The package function `sample_high_divergence` only sorts a list; it was not run on the 542. |
| **Remaining work** | Sort `c1_prime_metrics.csv` by `sentiment_divergence` within each gold class, export 30 + 30 with the title and author text, and have a person mark whether the gap comes from a bug word, from real frustration, or from a missing author comment. |
| **Done when** | A short table reports those three counts for 60 threads, and the divergence section cites it. |

### R4-D5. Turn the developer-usefulness limitation into a concrete study design

| | |
|--|--|
| **Current evidence** | The conclusion names “software engineering teams” and does not specify task, sample size, or measure. |
| **Remaining work** | Write the protocol: who, how many threads, what they see, what is recorded. Running it can be a later paper if the venue is told the claim is not yet tested. |
| **Done when** | The paper either includes results or describes a protocol specific enough that another lab could run it, and the abstract no longer states the untested benefit as a result. |

---

## Reviewer 7

### R7-W1. The `technical_first` rule treats words like error, crash, and fix as proof of TPS, so the baseline is a weak picture of VADER

| | |
|--|--|
| **Current evidence** | **Verified in code.** `evaluation/models/vader_rules.py` lines 48–55: if the compound score is under −0.6 and there is no technical cue, predict GDS; if any cue matches, predict TPS; otherwise predict GDS. The cue list is much longer than the three words in the paper (lines 16–28), including `issue`, `problem`, `update`, `install`, and `how do i`. Table I recall 0.896 and precision 0.202 match a rule that fires often. The ±0.15 band is not the main switch. The PyPI file `baseline_vader.py` is a reconstruction from this review, and its decision rule differs (non-negative text with no keyword becomes TPS). |
| **Remaining work** | Describe the real rule. Add a second baseline that is ordinary VADER sentiment with no keyword override, so readers can see what the lexicon does alone. |
| **Done when** | The method section quotes the actual branch order, and the results table has both the keyword rule and a no-keyword VADER row. |

### R7-W2. Labeling criteria are thin, and developer teams do not appear to have been asked

| | |
|--|--|
| **Current evidence** | `ANNOTATION_GUIDELINES.md` does define TPS and GDS and gives decision rules (sections 2–3). It also files announcements, politics, and fandom under GDS (section 7), which is broader than “discontent.” The `notes` column is empty for all 542 gold rows. No file names a developer team or a labeler. **Unknown** who applied `corrected_label`. |
| **Remaining work** | One operational definition. A record of who labeled, with a second person on a shared subset. If developers are not involved, say the labels are researcher labels. |
| **Done when** | The paper states the rule, the labeler role, and the agreement between two blinded people. Empty notes are no longer the only record. |

### R7-D1. Figure 2 does not show that `text_raw` is title, body, and up to ten comments

| | |
|--|--|
| **Current evidence** | **Verified in code, not in the figure text.** `tps_gds_classification/scripts/text_preprocessing.py` lines 30–47 and `fetch_tps_gds_dataset.py` `build_record`. The manuscript says Figure 2 shows this. Reviewer 7 says the picture does not. The figure image was not re-audited pixel by pixel. |
| **Remaining work** | Redraw the figure with the three text pieces, the ten-comment cap, the model list, and the author/community split. |
| **Done when** | A reader can reconstruct the input of each model from the figure alone. |

### R7-D2. Name the API, and say how the data were labeled and by whom

| | |
|--|--|
| **Current evidence** | **Partly verified.** Collection code calls `https://releasetrain.io/api/reddit/query/filter` with `minComments`, `minScore` / `maxScore`, and `limit` (`fetch_tps_gds_dataset.py` lines 42–56 and 199–210). The saved responses show the score is `metadata.predicted.positiveScore`, not Reddit upvotes. Who assigned `corrected_label` is **unknown**. The 80-row sheet’s author is **unknown**, and that sheet shows the gold label to the filler. |
| **Remaining work** | Corpus section: endpoint, date fetched (2026-03-27), filters, dedup of the 32 overlap posts, and the labeler answer from the team. |
| **Done when** | Those facts are in the paper, and any unknown labeler item is explicitly marked unknown rather than described as an independent annotator. |

---

## Reviewer 9

### R9-W1. TPS/GDS looks like a renaming of existing bug-report and feedback categories. The paper should say why those categories are not enough

| | |
|--|--|
| **Current evidence** | The manuscript cites Iqbal et al. (reference 13) and still says prior work rarely separates troubleshooting from dissatisfaction. The guideline definition of GDS also includes news, politics, finance, and fandom (`ANNOTATION_GUIDELINES.md` lines 35–43). The corpus contains those posts (Bitcoin 56, transformers 83, News tag 49 among gold GDS). That is a different task from “bug versus feature request,” and the paper does not spell out the difference. **Verified** that the comparison is thin. **Unknown** whether a tighter definition would still be new after a real literature pass. |
| **Remaining work** | A related-work subsection that takes bug-report classification, Reddit requirements mining, and issue categorization one paper at a time and says what TPS/GDS adds or refuses to add. |
| **Done when** | The introduction’s novelty sentence is limited to a difference that the related-work section has actually argued, and the label rule matches that sentence. |

### R9-W2. Introduction and related work use broad novelty claims without the closest papers

| | |
|--|--|
| **Current evidence** | The extract says existing studies “rarely” model author–community interaction for this split (manuscript pages 1–2). Reviewer 9’s examples (software discussion classification, requirements mining, bug reports) are mostly absent aside from the one Iqbal citation. This audit did not do a new literature search, so the size of the gap is the reviewer’s judgment plus the citation list in the PDF. |
| **Remaining work** | Replace “rarely” and “most studies” with citations or delete the wording. |
| **Done when** | Every novelty sentence in the introduction points to a paragraph that discusses the nearest papers. |

### R9-W3. Related work misses software-engineering classification and stays on general sentiment and social media

| | |
|--|--|
| **Current evidence** | The reference list in the extract is dominated by sentiment surveys, VADER, Reddit health and education mining, one support-ticket paper, one complaint-topic paper, Iqbal et al., and one transformer-versus-classical classification paper. |
| **Remaining work** | Add the bug-report and feedback-classification papers the reviewer named, and any closer ones found in a proper search. |
| **Done when** | Related work has a subsection whose topic is software feedback classification, not only sentiment. |

### R9-W4. The experiments only compare classifiers inside this project. There is no external method

| | |
|--|--|
| **Current evidence** | **Verified.** Table I is majority class, Naive Bayes, logistic regression, RoBERTa, and the local VADER rule. No published bug-report classifier is run on these 542 posts. An external tool may not use the TPS/GDS label set, so a direct number may be impossible. The paper does not say that. |
| **Remaining work** | Either run one public issue classifier and map its labels in a documented way, or explain why the label sets cannot be aligned and keep the internal comparison clearly labeled as internal. |
| **Done when** | The evaluation section contains that comparison or that explanation, and does not call the internal table a comparison to prior systems. |

### R9-D1. Figure 1 branching arrows are awkward

| | |
|--|--|
| **Current evidence** | Presentation comment. Not rechecked in a drawing tool. |
| **Remaining work** | Redraw. |
| **Done when** | The camera-ready figure uses one reading order and the reviewer comment no longer applies. |

### R9-D2. Figure 1 should use the abbreviations TPS and GDS after they are defined

| | |
|--|--|
| **Current evidence** | Presentation comment. |
| **Remaining work** | Edit the figure labels. |
| **Done when** | The figure uses TPS and GDS, and the first mention in the text spells them out. |

### R9-D3. Figure 1 is a high-level overview and uses a lot of space

| | |
|--|--|
| **Current evidence** | The paper already has Figure 1 and Figure 2. Reviewer 7 also asked Figure 2 to carry more technical detail. |
| **Remaining work** | Keep one pipeline figure and put the text construction, the score, and the author/community split on it. |
| **Done when** | One figure carries the pipeline detail and the other conceptual drawing is removed or reduced. |

### R9-D4. Figure 2 is a sequence of boxes and does not show data flow

| | |
|--|--|
| **Current evidence** | Same gap as R7-D1. The code path is documented; the figure, according to both reviewers, is not. |
| **Remaining work** | See R7-D1. |
| **Done when** | See R7-D1. |

### R9-D5. A reference to `c1_prime_metrics.csv` looks out of place unless the file is part of the public release

| | |
|--|--|
| **Current evidence** | The text extract of the local 5-page PDF does not contain the filename `c1_prime_metrics.csv`. The paper does say “C1′.” **Unknown** whether the name appears inside a figure image or in a copy the reviewer saw. The file exists at `data/c1_prime/c1_prime_metrics.csv`. The GitHub link in the manuscript points at this research tree. |
| **Remaining work** | If the file is cited, release it with the paper. If it is only an internal name, use “the per-thread metric table” in prose. |
| **Done when** | The camera-ready text and the released archive use the same filename, or the filename is gone from the paper. |

---

## Strengths the files do support

These are worth keeping when the ICSC paper is drafted. They are not repairs.

| Reviewer point | Evidence |
|----------------|----------|
| R4 strength: separating actionable reports from other update talk is a real problem | The task is coherent once the label rule is narrowed. The current GDS bin is the part that is not coherent (audit finding P2). |
| R4 strength: a 24% gap between the API pool and the corrected labels justifies manual labels | **Verified** 130/542. The gap is specifically `positiveScore` pool versus `corrected_label`, and 71 of 86 gold TPS came from the low-score pool. |
| R7 strength: the paper compares a rule, linear models, Naive Bayes, and RoBERTa | **Verified** in the saved runs. The “best model” sentence still has to be narrowed (audit finding P4). |
| R9 strength: the problem is practical and the paper is readable | Readability was not re-scored here. The practical claim is untested (R4-W2). |
