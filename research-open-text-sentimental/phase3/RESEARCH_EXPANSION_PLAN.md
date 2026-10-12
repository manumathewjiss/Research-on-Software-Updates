# Research expansion plan for one regular paper

**Status:** design decision document, 2026-10-07. No new annotations, models, clusters, or practitioner ratings are claimed here. This plan does not optimize around the earlier deadline. All Phase 1–3 records remain preserved.

## Evidence inspected and decision boundary

I inspected the five-page ICMLA manuscript; the complete three-review CMT PDF and `phase2/REVIEWER_RESPONSE_MATRIX.md`; the Phase 1 code/data card and `phase2/RESEARCH_AUDIT.md`; the Phase 2 task guide, pilot agreement and combined-data manifest; and the Phase 3 protocol, model results, duplicate check, Manu's 51-row review, and revised-development manifest. This is an audit of the study design and saved results, not independent verification of every Reddit post's truthfulness.

The combined corpus has 3,362 unique posts: 542 Phase 1 and 2,820 newly deduplicated API candidates. The Phase 2 master records 3,357 resolved judgments and five unresolved posts. Label provenance is mixed: 100 pilot decisions finalized after two stated independent first passes, 300 joint expansion decisions, 200 joint reserved-test decisions, and 2,757 assisted reviews by Manu. The v2 S2 development analysis uses 2,080 posts (1,686 troubleshooting; 394 other update). Its grouped, development-only macro-F1 is 0.8347 for title+body TF-IDF logistic regression. The **original** model's one-shot reserved S2 result was macro-F1 0.863 on 159 posts, only 24 of them negative. These results answer a conditional question: classification **after** human S2 scope selection. They do not establish automatic discovery of update discussions or developer usefulness.

Available fields support careful generalization tests: all 2,080 revised S2 development posts have timestamps from 2025-01-28 to 2026-10-05 and cover 135 subreddits. A pre-2026-07 versus later split would yield 1,629 earlier and 451 later posts, with 339 and 55 negative cases respectively. Seventeen subreddits have at least five examples of each class. There is **no validated product identifier field**. Of the 2,080, 303 have no post body and 1,283 have no saved discussion context. API source and label are strongly entangled: the S2 candidate pools have different positive rates. Consequently, random splits alone are insufficient and comment-outcome analysis is unsafe.

For literature grounding, start with the primary [Bettenburg et al. bug-report quality study](https://www.st.cs.uni-saarland.de/publications/details/bettenburg-tr-2008/), [Devine et al. on unseen-app and cross-dataset feedback classification](https://arxiv.org/abs/2112.13497), [Gao et al. on insights from app reviews](https://www.microsoft.com/en-us/research/publication/infar-insight-extraction-from-app-reviews/), and [Isotani et al. on semantic duplicate bug-report detection](https://www.frontiersin.org/journals/computer-science/articles/10.3389/fcomp.2022.1032452/full). These show that bug-report quality, feedback classification, transfer, and duplicate discovery are established fields. Novelty cannot rest on renaming a bug-report task; it must come from the update-discussion setting, explicit scope/type distinction, diagnostic-detail representation, and carefully evaluated relationship between detection and detail. A full related-work search remains to be done before claiming a gap.

## Proposed central paper question

**How can software-update discussions be screened for troubleshooting, and what diagnostic information is present or missing in the reports that screening finds?**

Recommended RQs:

- **RQ1:** How accurately does post text distinguish troubleshooting from other update discussion after scope has been established?
- **RQ2:** How stable is that result across collection source, time, and held-out communities?
- **RQ3:** What diagnostic details appear in troubleshooting posts, and how consistently can humans identify them?
- **RQ4:** Are sparse diagnostic details associated with classification errors or lower model confidence? This is an association question, not a causal claim.

One later optional RQ may test ranking by troubleshooting and diagnostic detail **only if** a valid ranking population and relevance judgments are assembled. Product holdouts, issue clusters, emerging trends, and developer utility are not promised by the present data.

## Assessment of the twelve proposed directions

Effort is a rough **research-person-hour** range after this plan, excluding waiting for participants or API access. It is not a deadline estimate. A larger human annotation sample can make the effort substantially higher.

### 1. Task and dataset formulation — **Must have**

1. **Question:** What exactly counts as software-related, update-related, and troubleshooting, and what is left in the other class?
2. **Value:** Repairs the Phase 1 category error: non-troubleshooting is not automatically discontent. This is a meaningful data/task contribution if the decisions and sampling limits are transparent, not an unprecedented classifier label.
3. **Existing support:** 3,362 IDs, source metadata, 3,357 Phase 2 decisions, separate scope/type fields, the independent-first-pass 100 pilot, joint and assisted review records, and 5+4 later uncertainty exclusions.
4. **Needed:** A versioned Phase 2 data card, exact flow counts from raw pools to S2 development/test, definition examples that are not leaked into tests, and a publication/redistribution decision. No additional bulk labels are required for the current corpus.
5. **Method:** Flow diagram; class and source tables; disagreement/ambiguity analysis; separate initial agreement from adjudicated consensus; explicit split and exclusion rules.
6. **Measures:** Counts and proportions by source, time, community, text availability, label provenance; pilot agreement with exact denominator; uncertainty counts.
7. **Risks:** Keyword-selected sample is not Reddit prevalence; assisted review is not independent gold; original 542's labeler provenance remains partly unknown; scope was human-given in the classifier experiment.
8. **Effort:** 12–25 hours of auditing, writing, and coauthor verification.
9. **Placement:** Main paper methods/data contribution.

### 2. Troubleshooting detection and one semantic model — **High value, conditional**

1. **Question:** Does richer language representation identify hard cases better than the already strong lexical baseline?
2. **Value:** Tests a semantic hypothesis, especially implicit problem descriptions, mixed rants, and technical-word announcements. A transformer is valuable only if it changes error behavior or transfer, not because it is modern.
3. **Existing support:** Majority, fixed-keyword, TF-IDF LR/SVM, title versus title+body, grouped v2 development check; original one-shot reserved test.
4. **Needed:** One preselected model family, fixed hyperparameter budget, compute, and an evaluation plan that keeps old reserved scores out of new selection. Naive Bayes is optional for Phase 1 continuity; an LLM prompt baseline is unnecessary unless a specific zero/few-shot transfer question is asked.
5. **Method:** Same grouped development folds and text input; compare per-class errors and source/temporal stress; choose by development only. A changed finalist needs a fresh untouched final test for a confirmatory claim.
6. **Measures:** Per-class precision/recall/F1, macro-F1, paired uncertainty for model difference, confusion matrices, runtime/cost, error-category changes.
7. **Risks:** Small gains within sampling noise, pretrained contamination, hyperparameter search after seeing old test, duplicate leakage, and semantic-model advantage due to source artifacts.
8. **Effort:** 18–45 hours plus compute, depending on model and diagnostics.
9. **Placement:** Main paper only if it answers the semantic/generalization question; otherwise classical models suffice.

### 3. Generalization — **Must have, with feasible splits only**

1. **Question:** Does detection survive time and community changes rather than relying on source-specific vocabulary?
2. **Value:** Directly tests the main threat to the current random-split result and addresses reviewer novelty/soundness concerns.
3. **Existing support:** Complete post dates, 135 subreddit names, 17 with at least five of each class, and source-pool metadata. July-2026 cutoff yields 451 later S2 development posts but only 55 negatives. No validated product field.
4. **Needed:** A predeclared temporal cutoff and held-out-community selection based on counts, not scores; product normalization/annotation before any product holdout. Ideally a later or external collection with new labels for final confirmation.
5. **Method:** Development-only chronological train-earlier/test-later stress; group-aware held-out-community tests on feasible communities; compare majority, keyword, LR, and chosen semantic model. Report source distribution in each split. Do not conflate subreddit with product.
6. **Measures:** Both-class F1, macro-F1, precision/recall, support, interval estimates, performance change from grouped in-domain CV.
7. **Risks:** Time, community, API source, and class ratios move together; 55 later negatives constrain precision; leaving out a subreddit can change the task itself; product holdout is currently ungrounded.
8. **Effort:** 15–35 hours for time/community; another 25–60 hours if product identities are created and checked.
9. **Placement:** Main paper for time plus one justified community stress test. Product transfer only if IDs become reliable; otherwise future work.

### 4. Diagnostic-information taxonomy — **Must have**

1. **Question:** Which observable facts in an original post describe a software problem and its context?
2. **Value:** Moves beyond binary detection toward a semantic representation of update-related problems. It distinguishes identifying a report from understanding what it says.
3. **Existing support:** 1,686 confirmed S2 troubleshooting development records; original title/body text; Phase 2 guide; 303 S2 posts with missing bodies (all classes), allowing explicit missing-text handling.
4. **Needed:** Focused literature review; representative examples sampled across sources, communities, lengths and errors; draft codebook; a 40–60-post pilot; two separate first-pass human sheets; adjudication and revision. Avoid showing model suggestions to reviewers.
5. **Method:** Begin with a small, non-overlapping set of candidate fields: affected software/release, environment, symptom, trigger/steps, diagnostic evidence, attempted fix and observed outcome. Split or merge only when pilot examples show the distinction can be applied reliably. Record `present`, `absent`, `unclear/not visible` with evidence spans, rather than guessing.
6. **Measures:** Field-wise prevalence and agreement (percentage plus an appropriate chance-corrected or prevalence-aware statistic), disagreement examples, missing-text rate, codebook revision log.
7. **Risks:** Rare fields inflate agreement or yield unstable κ; product/version and environment may be confused; a field can be absent from the saved snapshot but present on Reddit; reviewer guide may leak examples.
8. **Effort:** 35–70 hours including literature, pilot, two reviews and adjudication.
9. **Placement:** Main new contribution. Do not call it developer usefulness without practitioner ratings.

### 5. Diagnostic completeness and its distribution — **Must have after taxonomy pilot**

1. **Question:** What details do troubleshooting authors provide, and what is missing?
2. **Value:** Gives a substantive empirical finding rather than just another classifier table.
3. **Existing support:** Revised S2 troubleshooting pool of 1,686 development posts; text and source/community/date descriptors. No diagnostic-field labels yet.
4. **Needed:** A documented stratified sample (initial planning range 200–300 posts), validated codebook, trained reviewers, double-coded quality subset, adjudicated field labels. Sample size should be set from pilot field frequencies and the intended precision, not a convenient round number.
5. **Method:** Sample across source pool, body availability, major communities, and time; estimate field prevalence with sampling weights if strata are disproportionate. Start with each field separately. A summed completeness score is secondary and requires a clear rationale; no arbitrary weights.
6. **Measures:** Per-field prevalence with intervals, co-occurrence patterns, field-count distribution if interpretable, sensitivity to title-only posts and sampling design.
7. **Risks:** Missing saved body can mimic low completeness; confidence intervals for rare details; checklist counts do not prove investigation value; nonrandom hard-case oversampling requires weights for prevalence claims.
8. **Effort:** 60–120 human review hours plus 20–35 analysis hours, depending on fields and double-coding fraction.
9. **Placement:** Main empirical contribution if pilot reliability is adequate.

### 6. Problem-type characterization — **Optional, narrow**

1. **Question:** What kinds of failures do the detected reports describe?
2. **Value:** Helps explain whether completeness differs by failure type and makes the diagnostic representation richer.
3. **Existing support:** Text of 1,686 revised S2 troubleshooting posts; no validated problem-type labels.
4. **Needed:** Derive a small hierarchical or multi-label codebook from related work and sampled posts; pilot for ambiguous multi-problem posts; possibly annotate the same diagnostic sample.
5. **Method:** Distinguish manifestation (crash, connectivity, wrong output) from lifecycle stage (install/update/rollback). Allow multiple types if needed. Use descriptive analysis first, not a new classifier by default.
6. **Measures:** Type prevalence, agreement, unclear/multiple-type rate, completeness by type with uncertainty.
7. **Risks:** Categories overlap; software-specific vocabulary may dominate; many types have tiny counts and invite false comparisons.
8. **Effort:** 25–60 hours incremental if added to the diagnostic sample.
9. **Placement:** One compact descriptive table if reliable and explanatory; otherwise appendix or later paper.

### 7. Classifier error analysis linked to details — **Must have**

1. **Question:** Which meaning distinctions produce false positives/negatives, and are sparse-detail reports harder to detect?
2. **Value:** Connects the detection and diagnostic studies into one coherent result; shows what the model has and has not learned.
3. **Existing support:** Grouped OOF predictions and original reserved predictions, text, source/availability fields; roughly 200 original development errors before label correction. The corrected v2 grouped sensitivity summary lacks saved per-post predictions and would need a development-only rerun under the same locked model.
4. **Needed:** A bounded, blinded error-coding sample; codebook for error categories; diagnostic-field labels on both correctly and incorrectly classified troubleshooting posts. Do not use model error status to redefine the gold label silently.
5. **Method:** Sample false positives, false negatives and matched correct cases from development OOF; two people code error reason on a subset; compare detail presence with error probability while adjusting or stratifying for body length, source pool and community.
6. **Measures:** Error-category frequencies with denominators, agreement, false-negative rates by detail field/count, confidence distributions and uncertainty intervals. Describe association, not causal effect.
7. **Risks:** Selecting only errors can inflate associations; model predictions influenced by text length and source; rare false negatives give unstable subgroups; post-hoc categories can overfit anecdotes.
8. **Effort:** 30–65 hours including coding and analysis.
9. **Placement:** Main paper, tightly paired with diagnostic completeness.

### 8. Recurring-issue clustering — **Better as future/separate work unless feasibility pilot succeeds**

1. **Question:** Can multiple posts be grouped because they report the same underlying software issue?
2. **Value:** Could turn individual reports into an issue-level view, but duplicate retrieval is already an active research area, so a new method/validated benchmark would be needed.
3. **Existing support:** 1,686 troubleshooting posts, dates, titles/bodies, and several exact/near duplicates. Product/release normalization is absent; identical text does not prove the same software failure across users.
4. **Needed:** Product/release and issue-identity labels on sampled pairs/clusters, enough positive repeated-issue pairs, and a clean temporal evaluation protocol.
5. **Method:** Feasibility sample first: manually judge whether plausible clusters represent the same issue. Only then compare lexical and embedding methods; evaluate grouping, not just display attractive example clusters.
6. **Measures:** Pair precision/recall, cluster purity/coverage or retrieval metrics with human issue-identity labels, analyst effort.
7. **Risks:** Most posts may be unique; mixed products with similar words; semantic embeddings group broad themes rather than identical incidents; collection is keyword-selected and may not reflect incident volume.
8. **Effort:** 50–120+ hours after feasibility, potentially much more for a defensible benchmark.
9. **Placement:** Future/separate paper unless early human feasibility shows abundant recurrent issues and clear evaluation.

### 9. Emerging-issue analysis — **Better as future/separate work**

1. **Question:** Do reports of a defined issue rise after a named release or during a specific window?
2. **Value:** Important release-monitoring problem if measured with a stable collection denominator.
3. **Existing support:** Post timestamps; update language; no validated release mapping, complete stream, or stable population denominator. The two API pools were selected by keywords/heuristics.
4. **Needed:** Continuous or repeated collection with fixed query coverage, release-event dates, product/release identities and issue labels, exposure/baseline denominators.
5. **Method:** Predefine issue and release windows; compare rates with historical baselines and negative-control periods; report association only.
6. **Measures:** Counts/rates with denominators, change estimates and intervals, false-alert rate, cluster precision.
7. **Risks:** API coverage or popularity changes create artificial spikes; duplicate posts; cross-product mixing; temporal association does not identify causation.
8. **Effort:** Multiple collection periods plus 70–150+ hours of labeling/analysis.
9. **Placement:** Future/separate work.

### 10. Ranking and prioritization — **High value only with the right evaluation pool**

1. **Question:** If an analyst checks a short list, which reports are surfaced and how much diagnostic detail do they contain?
2. **Value:** Makes the classification output more operational and answers part of reviewer 4's missing downstream evaluation, without claiming time saved.
3. **Existing support:** Scores and labels for the current S2 corpus; prior precision@10/20 was 1.0, but troubleshooting already forms about 81% of revised development and 85% of the old reserved S2 set. This ceiling makes top-k alone weak evidence.
4. **Needed:** A clearly defined, lower-prevalence screening queue or a prospective collection snapshot; graded relevance if using NDCG; diagnostic labels if ranking by detail. Do not mix human scope selection with an alleged end-to-end ranking system.
5. **Method:** Compare fixed keyword, LR score, and (if available) detail-aware ordering on the **same** queue; use independent labels and disclose how the queue was sampled. Evaluate what happens when K is fixed before results.
6. **Measures:** Precision@K and recall@K with baseline prevalence; mean average precision; NDCG only for validated graded relevance; field coverage among surfaced posts.
7. **Risks:** K metrics are uninformative in an 80% positive set; tuning on old reserved ranks; diagnostic count as a surrogate for actual utility; collection bias.
8. **Effort:** 15–35 hours if an appropriate labeled queue exists; 45–100+ if new collection and annotation are needed.
9. **Placement:** Main-paper demonstration only if meaningful queue and baselines exist; otherwise appendix or future work.

### 11. Uncertainty and human review — **Optional, coherent extension**

1. **Question:** Can model confidence identify posts that merit human review?
2. **Value:** A realistic workflow for ambiguous update discussions, potentially linked to sparse diagnostic information.
3. **Existing support:** LR scores and errors, but class-weighted probabilities and threshold-tuned scores are not automatically calibrated.
4. **Needed:** Development-only calibration protocol and independently reviewed ambiguity judgments on a subset. No claim that score uncertainty equals human ambiguity without testing.
5. **Method:** Fit calibration inside development folds, construct risk-versus-coverage curves, compare low-confidence posts with human disagreement/unclear labels and text completeness. Freeze before new external evaluation.
6. **Measures:** Calibration error/Brier score, selective precision/recall versus coverage, rate of human disagreement by score band, confidence intervals.
7. **Risks:** Calibration drift across source/time, class-prior shift, using the old reserved set to choose abstention thresholds, and sparse true disagreement examples.
8. **Effort:** 20–50 hours, plus any new human ambiguity review.
9. **Placement:** Small subsection if it explains errors; otherwise future work.

### 12. Practitioner evaluation — **High value, separate decision**

1. **Question:** Do people responsible for software maintenance judge the identified reports or structured fields useful for investigation?
2. **Value:** Directly tests the practical benefit that the old paper asserted without evidence and distinguishes observable details from actual use.
3. **Existing support:** Posts and planned diagnostic labels; no practitioner ratings or time-on-task measurements.
4. **Needed:** Qualified participants, recruitment, consent/materials, fixed tasks and rating scales, sampling, and an institutional determination about human-subject requirements. Professor Berhe should help with protocol and access; do not infer that being an author makes a reviewer a representative practitioner.
5. **Method:** Pilot task comprehension, then blinded within-subject or balanced between-subject comparison of raw posts versus structured summaries/ranked lists. Measure investigation decision and missing-information judgments; add time only if the task realistically permits it.
6. **Measures:** Agreement and rating distributions, within-person changes, time/decision accuracy if measured, confidence intervals and qualitative reasons.
7. **Risks:** Tiny convenience sample, expectancy bias, unrealistic task, participant expertise mismatch, privacy/ethics obligations, and claiming deployment benefit from lab ratings.
8. **Effort:** 40–100 hours of design/analysis plus recruitment and review time; calendar time is uncertain.
9. **Placement:** Powerful separate validation section if completed rigorously; otherwise future/separate paper. No developer-utility claim without it.

## Ranking and strongest coherent paper

### Must have

1. Correct task/dataset formulation and honest provenance (direction 1).
2. Feasible generalization stress tests for time and community/source (direction 3).
3. Validated diagnostic-detail taxonomy and measured field distribution (directions 4–5).
4. Error analysis connecting the detector to missing detail (direction 7).

### High value

- One justified semantic model against the fixed classical baselines (direction 2), especially if it improves implicit/mixed cases or transfer. Stop if it adds no interpretable value.
- Ranking only on a meaningful, lower-prevalence queue (direction 10).
- Practitioner evaluation if recruitment and an appropriate study protocol are feasible (direction 12).

### Optional

- A small problem-type codebook on the same diagnostic sample (direction 6).
- Calibration and human-review analysis (direction 11).
- Naive Bayes as a historical bridge, not a new contribution.

### Better as future/separate work

- Recurring-issue clustering (direction 8) unless a feasibility pilot produces enough verified same-issue groups.
- Emerging-issue timing (direction 9) until there is stable longitudinal collection and release linkage.
- Any causal claim about an update causing complaints.

The strongest **four contributions** for one regular paper are: **(1)** a corrected update-discussion task and transparently reviewed corpus; **(2)** a duplicate-safe troubleshooting detector with time/community stress tests and, conditionally, one semantic comparator; **(3)** a validated schema and empirical study of observable diagnostic details; **(4)** an error analysis testing whether missing details accompany missed troubleshooting posts. These form one story: **identify a problem report, represent the information it contains, and explain when automated screening fails**. Ranking/practitioner utility may strengthen it later but should not crowd out the core evidence.

## Decision gates before implementation

1. **Lock the paper question and scope.** S2 remains the primary conditional task. An end-to-end scope detector is a separate question unless it is explicitly added and evaluated.
2. **Taxonomy feasibility pilot first.** Do literature-led codebook drafting and inspect about 40–60 representative troubleshooting posts. Two reviewers independently label a pilot subset; revise confusing fields before any 200–300-post study. Do not label the full corpus immediately.
3. **Generalization feasibility audit before modeling.** Predeclare cutoffs and eligible communities from support counts; identify confounding by source and class. Product transfer waits for a checked product field.
4. **Preserve test integrity.** The old reserved-test result belongs to experiment_v1. Any newly selected model, changed labels, threshold or combined ranking must be confirmed on a genuinely new untouched test set; otherwise its performance remains exploratory/development-only.
5. **Write the paper's framing while experiments proceed.** Related work and methods can be drafted from verified evidence; results/conclusions should follow completed analyses. Do not resurrect unsupported Phase 1 sentiment trajectory claims to fill pages.

This is a research design recommendation for Manu and Professor Berhe to discuss. No large annotation or model run should start until the contribution set and codebook pilot are accepted.

## 2026-10-07 implementation note: sole reviewer and source check

Manu has chosen to proceed as the sole working reviewer for the diagnostic pilot. This supersedes the two-reviewer pilot recommendation above for the current phase. A single reviewer can provide transparent descriptive annotations and later repeat a masked subset as a consistency check, but cannot produce independent inter-annotator agreement. Authorship of the paper is a separate matter from who labels the pilot; existing coauthor contributions must be represented accurately in any publication.

The new API candidate pools contain **30 Stack Overflow records** (`so_...` IDs and `stackoverflow.com` URLs), all in development, none in the old reserved test; 28 of the 30 are S2 troubleshooting. Therefore the combined corpus has **3,332 Reddit records and 30 Stack Overflow records**, not 3,362 Reddit records. These 30 must be excluded from any Reddit-only descriptive or model claim, or explicitly analyzed as a separate source with an updated title/scope. The original experiment is preserved; a future development-only sensitivity analysis should quantify the effect of excluding them before manuscript claims are finalized. The diagnostic pilot excludes them.
