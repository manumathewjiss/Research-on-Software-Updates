# Final research improvement report

This report records the ten requested tasks against the frozen Phase 2 labels and protected evaluations. The primary development population is the saved 2,050 Reddit-URL, update-related records (1,658 troubleshooting; 392 other update) with 2,016 duplicate groups. All new model checks below use the saved five grouped outer folds and select thresholds inside each training fold. The 159-post reserved test and 344-post fresh test were not reopened, tuned on, or overwritten for this improvement stage.

## Task 1 — Software-engineering sentiment model

**Objective.** Test whether a sentiment tool designed for software-engineering language changes the conclusion reached with general-purpose valence tools.

**What was done / files.** Inspected the [official `pySenti4SD` source](https://github.com/collab-uniba/pySenti4SD) at commit `5ed11f1f9bf42c113db064278fe7decaf07587c4` and its DVC model manifest. Also inspected [SentiCR](https://github.com/senticr/SentiCR) and the [SentiSE](https://github.com/amiangshu/SentiSE) research source. Then obtained the [official SentiStrength-SE v1.5 distribution](https://laser.cs.uno.edu/Projects/Projects.html) directly from the authors' laboratory: ZIP SHA-256 `b3244714dc82381833ae55c4722e0e7dcc5dc1522353f65bbb937a9e2d9daaa9`; JAR SHA-256 `d5b1b4a6fc819723e6bc64ad4e7282a3a347ad73e4cb2a076c6587811de509c3`. `run_se_sentiment.py` and `results/sentistrength_se_predictions.jsonl` record the executable call, row IDs, strengths, and out-of-fold predictions. The primary [SentiStrength-SE paper](https://doi.org/10.1016/j.jss.2018.08.030) and distribution are cited in `../final_synthesis_paper/references.bib`.

**Experiment / result.** The official SentiStrength-SE JAR and bundled software-engineering dictionary scored all 2,050 frozen development raw title/body documents, preserving their saved order and IDs. The tool returns positive and negative strengths; their signed sum is one polarity feature. Newline and tab characters within a post were replaced by spaces because the command-line scorer accepts one document per line. TF–IDF still uses its locked cleaned text. With exactly the existing nested grouped folds and training-only scaling, the SE sentiment score alone reached macro-F1 **0.464797** (other-update F1 **0.057**). Adding it to the title/body text model reached **0.834083** versus **0.831932** for text alone, a +0.002151 difference with paired duplicate-group 95% bootstrap interval **−0.004188 to +0.008859**. The interval includes zero. Detailed metrics and provenance are in `results/sentistrength_se_metrics.json`. No protected test was scored. A later exploratory subgroup calculation (`analyse_se_sentiment_groups.py`, `results/sentistrength_se_subgroup.json`) found mean signed strength −0.027 for troubleshooting and −0.794 for 68 dissatisfaction posts, a trouble-minus-dissatisfaction difference +0.767 (group interval +0.481 to +1.055). VADER's corresponding mean difference is +0.004 (interval −0.188 to +0.192). The scales differ, and neither tool has a human sentiment gold standard here; the point is that the descriptive contrast depends on the tool.

**Paper change / scientific impact.** Related Work, Methods, Results, Table V, Discussion, Threats, Abstract, Conclusion, and bibliography now include this domain-specific tool and its exploratory disagreement with VADER on the dissatisfaction slice. It did not reliably improve purpose classification on this sample. **Status: COMPLETE** for the requested SE-specific comparison. The score is still not an independent assessment of sentiment correctness: the development posts have no human sentiment gold labels, and a software-engineering interaction lexicon may not transfer perfectly to Reddit update reports. Senti4SD remained unscored because its 835,369,209-byte `dsm.bin` and other DVC-tracked pretrained artifacts were not retrieved; its DVC remote redirected unauthenticated access to login. SentiCR/SentiSE were not substituted without a comparable pretrained scorer. Thus the paper does not generalize the null increment to every SE sentiment system.

## Task 2 — Fine-tuned modern transformer classifier

**Objective.** Compare a task-fine-tuned RoBERTa-base purpose classifier with the fixed title/body TF–IDF logistic regression on exactly the same development population and folds.

**What was done / files.** `run_task2_roberta.py` records the model revision `e2da8e2f811d1448a5b465c236feacd80ffbac7b`, seed 42, 256-token limit, learning rate $2\times10^{-5}$, batch size 8, maximum three epochs, inner grouped epoch/threshold selection, and outer-fold refit. `results/task2_config.json` records the full-run configuration. The script uses only development rows; it has no protected-test input. A fresh isolated environment was prepared because the older local training environment stalled while loading evicted package files. Of 2,050 development inputs, 442 exceed the 256-token limit and are truncated. This can omit evidence late in a body.

**Experiment / result.** A one-fold smoke run was completed before the full five-fold comparison. Its saved predictions were verified against the identical fold assignment and then reused in the full run. All 2,050 out-of-fold predictions across five outer folds are now saved, with 2,050 unique IDs and no protected-test input. RoBERTa macro-F1 is **0.839113**; the matched TF–IDF logistic regression is **0.831932**. The difference is **+0.007181**, with paired duplicate-group 95% bootstrap interval **−0.015974 to +0.028589** (1,000 draws). The interval includes zero. RoBERTa other-update precision/recall/F1 is **0.768/0.709/0.737** versus **0.721/0.737/0.729** for TF–IDF. Its confusion matrix, with other update as class 0, is `[[278,114],[84,1574]]`. Relative to TF–IDF, it corrects 119 errors and introduces 102. Fold training choices were 1, 1, 2, 1, and 2 epochs; training-only thresholds were 0.80, 0.35, 0.50, 0.75, and 0.40. Per-fold durations including inner selection and refit were 837, 714, 1,185, 1,160, and 1,226 seconds. The saved evidence is `results/task2_summary.json`, `results/roberta_predictions.jsonl`, and `results/task2_config.json`. No reserved or fresh test was opened.

**Paper change / scientific impact.** Methods, purpose-detection Results, the purpose-score table, Discussion, Threats, and the RoBERTa citation now describe the completed fine-tuned comparison. This adds a genuine modern classifier control beyond the frozen MiniLM encoder. Its development point estimate is higher, but the uncertainty interval overlaps zero, minority-class recall is lower, thresholds vary by fold, and 22% of inputs are truncated. It has no protected-test confirmation and should not be called the new best model. **Status: COMPLETE.**

## Task 3 — One coherent contribution

**Objective.** Explain how informal update discussions become useful engineering evidence without claiming an evaluated end-to-end triage system.

**What was done / files.** Reworked the title, abstract, Introduction, four research questions, Discussion, and Conclusion in `../final_synthesis_paper/main.tex`; retained the underlying empirical studies and their different denominators.

**Experiment / result.** This is synthesis, not an additional experiment. The measured distinctions are: purpose can be detected on a fresh test, valence is a weak extra purpose feature under the tested tools, diagnostic facts are variably visible, and two reviewers can choose different first actions from the same intact post.

**Paper change / scientific impact.** The central contribution is an empirical boundary between recognizing a report and deciding what to do with it. The paper explicitly rejects a causal or deployed-pipeline interpretation. **Status: COMPLETE.** The evidence remains observational and the studies use different subsets.

## Task 4 — Matched input ablations

**Objective.** Separate title, body, and sentiment contributions using matched records and grouped folds.

**What was done / files.** `run_phase_a.py`, `matched_vader_ci.py`, `results/metrics_table.csv`, and `results/matched_vader_group_ci.json`; Tables in `../final_synthesis_paper/main.tex`.

**Experiment / result.** Title-only macro-F1 is 0.750534 and title plus title VADER is 0.750843 (difference +0.000309; duplicate-group 95% bootstrap interval −0.014425 to +0.015729). Body-only is 0.781424 and body plus body VADER is 0.786073 (difference +0.004649; interval −0.005449 to +0.013527). Title/body is 0.831932 and title/body plus VADER is 0.833130 (difference +0.001198; grouped interval −0.012563 to +0.015378). All increments have intervals containing zero. Empty bodies were retained.

**Paper change / scientific impact.** The input ablation table and Results now show that most signal is in text, with no reliable extra gain from these VADER columns. **Status: COMPLETE.** These are development checks; no new reserved/fresh evaluation was done.

## Task 5 — Explainability

**Objective.** Show what the linear purpose classifier uses without presenting feature weights as causal explanations.

**What was done / files.** `run_phase_a.py` saved the top 25 coefficients per class from each training fold in `results/fold_coefficients.json`; a compact term figure and interpretation were added to `../final_synthesis_paper/main.tex`.

**Experiment / result.** Incident/help words including *error*, *fix*, *tried*, and *issue* recur on troubleshooting lists; release/update words including *released*, *features*, *improved*, and *updates* recur on other-update lists. Platform/product terms also appear. The figure uses recurrence across folds rather than one potentially idiosyncratic fit.

**Paper change / scientific impact.** The finding supports a lexical-purpose interpretation and reveals a potential community/source shortcut. Coefficients are associations with historical labels, not proof the model understands a defect. **Status: COMPLETE.** No claim is made that this is local, counterfactual, or causal explainability.

## Task 6 — Redesign Figure 1

**Objective.** Make the sample flow and separate analyses legible.

**What was done / files.** Redrew Figure 1 as vector TikZ in `../final_synthesis_paper/main.tex` with collection, human review, development/test separation, purpose/sentiment checks, diagnostic sample, and intact-post reviewer cases.

**Experiment / result.** Visual/documentation task; no new inference. The 3,362 master, 2,050 primary development records, 159 reserved records, separate 344 fresh records, 237 confirmed diagnostic posts, and 30 cases are labeled in their appropriate branches.

**Paper change / scientific impact.** Reduces denominator confusion and visually avoids implying a tested sequential pipeline. **Status: COMPLETE.** Branches can overlap and are not population estimates.

## Task 7 — Figure review

**Objective.** Improve grayscale readability, consistent captions, and appropriate visual encoding.

**What was done / files.** Reviewed the rendered eight-page PDF and revised the source figures in `../final_synthesis_paper/main.tex`, including the valence comparison, diagnostic-field bar chart, term recurrence, Figure 1, and the conceptual framework.

**Experiment / result.** No new dataset result. The figures are vectors from manuscript code; no generated data points. The valence caption identifies the dissatisfaction-only comparison and the diagnostic caption marks unclear decisions separately.

**Paper change / scientific impact.** Figures communicate different denominators and descriptive versus inferential comparisons more directly. **Status: COMPLETE.** The revised source was uploaded to the Overleaf project and compiled there to eight pages with zero reported errors and zero warnings; benign underfull-box messages appear as informational log entries.

## Task 8 — Summary framework

**Objective.** Summarize the four descriptions without depicting an implemented action pipeline.

**What was done / files.** Added a vector conceptual framework in Discussion of `../final_synthesis_paper/main.tex`: purpose, valence, diagnostic facts, and reviewer first action are parallel readings of an intact post.

**Experiment / result.** Conceptual figure only. Its conclusion is the measured non-equivalence of those descriptions; it is not an evaluated software system.

**Paper change / scientific impact.** Gives the paper one memorable scientific structure and limits the interpretation through the caption. **Status: COMPLETE.** It does not identify causal effects.

## Task 9 — Future work

**Objective.** State specific next tests that follow from observed limits.

**What was done / files.** Rewrote Future Work in `../final_synthesis_paper/main.tex` around prospective engineering triage, independent reviewer scale, transfer to GitHub/Jira/Stack Overflow, monitoring delay/missingness, and verified language-model suggestions.

**Experiment / result.** No result is attributed to future work.

**Paper change / scientific impact.** Separates next-study hypotheses from current findings. **Status: COMPLETE.** Transfer and deployment are presently untested.

## Task 10 — Conclusion

**Objective.** End with a scientific claim that follows from all four analyses.

**What was done / files.** Rewrote Conclusion and tightened the Abstract in `../final_synthesis_paper/main.tex`.

**Experiment / result.** The conclusion cites the frozen fresh-test macro-F1 0.792, null reliable VADER increment on development, varying diagnostic visibility, and nine divergent first actions in 30 intact cases.

**Paper change / scientific impact.** The takeaway is the measured boundary between recognizing a troubleshooting report and knowing what action its evidence supports. **Status: COMPLETE.** It does not claim the proposed triage aid has been built or tested.

## Integrity and submission checks

- Phase 1 and Phase 2 label files, reserved predictions, and fresh predictions were not modified by these experiments.
- New ablation predictions and confidence intervals are saved under `results/` with their scripts.
- The local IEEEtran paper compiles as eight US-letter pages. Its remaining TeX messages are underfull spacing warnings, not undefined references, overfull text, or missing figures.
- The current Overleaf project was refreshed from the final `../final_synthesis_paper/main.tex` and `../final_synthesis_paper/references.bib`, including RoBERTa. Its PDF visibly contains the RoBERTa row and result, has eight pages, and its compile panel reports errors 0 and warnings 0.

## Checklist

| Task | Status | Decisive evidence or limit |
|---|---|---|
| 1 SE sentiment model | **COMPLETE** | Official SentiStrength-SE scored on 2,050 matched folds; no reliable increment |
| 2 Fine-tuned transformer | **COMPLETE** | Five saved grouped folds, 2,050 predictions, paired interval includes zero |
| 3 Unified contribution | **COMPLETE** | Revised Abstract, Introduction, Discussion, Conclusion |
| 4 Ablations | **COMPLETE** | Saved matched predictions and grouped intervals |
| 5 Explainability | **COMPLETE** | Five-fold coefficient recurrence and caveated figure |
| 6 Figure 1 | **COMPLETE** | New data-flow vector figure |
| 7 All figures | **COMPLETE** | Eight-page rendered figure review |
| 8 Summary framework | **COMPLETE** | Parallel-lens figure with non-pipeline caption |
| 9 Future work | **COMPLETE** | Specific prospective tests, no invented results |
| 10 Conclusion | **COMPLETE** | Evidence-bounded scientific takeaway |

The unscored Senti4SD alternative stays visibly qualified. The completed RoBERTa result does not justify a superiority claim or reusing protected tests for model selection.
