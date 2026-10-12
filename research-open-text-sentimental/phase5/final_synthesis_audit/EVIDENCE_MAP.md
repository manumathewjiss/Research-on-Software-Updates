# Evidence map

Status words: **verified** means a saved file states the number and a later check reproduced it or the manuscript quotes that file; **uncertain** means the files disagree, the sample is selected, or provenance of the label is incomplete; **unsupported** means the claim is not in a saved result.

## Verified

| Finding | Saved fields | Limit |
|---|---|---|
| Historical labels are 86 TPS and 456 GDS | `DATA_CARD.md`; `historical_542_audit.json` | Corrected/assigned labels. Who assigned each row is not in the 542-row notes column (`phase2/RESEARCH_AUDIT.md`) |
| Divergence 0.371 vs 0.287, p = 0.009221 | `historical_542_audit.json` `published_reference.full_divergence_means`; ICMLA PDF | Full file, including 205 title-only author tracks |
| Author means differ; community means do not | Same audit: author Welch p = 4.72e-05; community Welch p = 0.332 | Not a change over the thread. Author slope Welch p = 0.274 |
| After dropping title-only tracks, author means still differ (0.077 vs 0.261, Welch p = 0.0008) but divergence does not (p = 0.060) | `historical_542_audit.json` `saved_divergence_excluding_title_only_author_tracks` | n = 62 and 275 |
| Current primary set is 2,050 Reddit-URL posts, 1,658 / 392 | `phase5/sentiment_paper/AUDIT.md`; `stage_a_title_body.json` `population.support` | 30 non-Reddit URL rows are outside this set |
| Title/body text macro-F1 0.8319; text+VADER 0.8331; difference +0.0012, interval includes zero | `stage_a_title_body.json` `paired_hybrid_minus_text_macro_f1` | Development grouped out-of-fold, not a test |
| Group bootstrap of that difference also includes zero | `manuscript/analysis/group_bootstrap.json` `pre_discussion_2050_group_bootstrap` | |
| Reserved text-only macro-F1 0.8627; fresh text-only 0.7915 | `RESULT_VERSION_RECONCILIATION.json` | Same specification, different train and test populations. Not sentiment scores |
| On 797 posts with a stored comment, full-thread text 0.866 vs same text plus sentiment 0.839 | `RESULTS.md`; group interval in `group_bootstrap.json` excludes zero | Selected subset. Only 14 posts share a duplicate group. Retrospective |
| Mean compound gap vs other update discussion disappears for 68 general-dissatisfaction posts (−0.064 vs −0.068) | `RESULTS.md` restricted section | n = 68, not the S2 negative class |
| Comment coverage differs by class: 1,098/1,658 troubleshooting posts lack a stored comment vs 155/392 other-update posts | `AUDIT.md` and the polarity manuscript Table III | Snapshot coverage, not Reddit's true comment count |
| No human-confirmed resolution field | `AUDIT.md` "Outcome labels" | Absence is unknown outcome |
| Diagnostic sample: 237 reconfirmed troubleshooting posts; reproduction context 108; error evidence 40 | `phase4/manuscript_icsc2027/DRAFT_V2.md` Table III, repeated in the 8-page PDF | Development sample. Symptom rate is 237/237 because the sample was reconfirmed as troubleshooting |
| BERT undersampled test macro-F1 0.635 on 40 rows | `tps_gds_classification/outputs/bert/metrics.json` | Old labels, GDS undersampled to 175. Not an ICSC result |

## Uncertain

| Item | Why it is not settled |
|---|---|
| Historical `corrected_label` provenance | `RESEARCH_AUDIT.md` records empty notes on all 542 rows and no per-decision annotator name. The polarity paper therefore says "corrected/assigned," not "gold" |
| Whether technical words cause the valence gap | `technical_word_description.json` shows incident terms are more common in troubleshooting (1,258/1,658 vs 154/392) but incident-only means still differ (−0.060 vs +0.355). Descriptive co-occurrence, not a masking effect |
| 30-case reviewer disagreements | Reported in the troubleshooting PDF as exploratory. Two reviewers, purposefully selected cases. Not a population rate and not linked to VADER |
| Community slope on the 542 | Welch p = 0.083 and Mann–Whitney p = 0.026. The tests disagree. The polarity paper does not claim a community change |
| API `positiveScore` and `/query/tps` `/query/gds` | `pagination_manifest.json` and `DATA_CARD.md` define them as candidate pools. 24% of the 542 disagree with `corrected_label` (`DATA_CARD.md` §3.2). Not labels |
| `releasetrain-sentiment` 0.2.1 | Inspected under `phase2/new_sources/package/`. `score.py` `trajectory_summary` averages author comments and returns 0 if none exist. The study trajectory can use the title. Scores were not mixed |

## Unsupported

| Claim | Why it is unsupported |
|---|---|
| Sentiment improves troubleshooting detection | Stage A interval includes zero. The fair thread comparison is lower, not higher |
| Comments show that an issue was fixed | No resolution label (`AUDIT.md`) |
| A risk cadence or a 3% risk-post rate | `phase5/SCIENTIFIC_INTEGRATION_DECISION.md` and `AUDIT.md` "Unverified ReleaseTrain question." No numerator, denominator, or definition in the saved files |
| All 3,362 URLs are Reddit | 30 development rows are non-Reddit URL records |
| Reviewers' actions are caused by diagnostic fields or by the classifier | The troubleshooting PDF states the case study does not establish causal effects |
| The fresh-test drop is a measured transfer effect | `RESULT_VERSION_RECONCILIATION.json` `interpretation`: different training populations and different tests; descriptive, not a controlled transfer estimate |
| BERT, the 324-post cohort, or sibling prototypes improve a combined paper | Different samples and tasks. No saved comparison against the fresh test |

## What can sit in one paper without new experiments

The verified pieces already share one negative structure:

1. Historical valence (542, TPS vs GDS) is a different question from current purpose (2,050, troubleshooting vs other update discussion).
2. On the current task, VADER does not add a reliable gain to the same text.
3. A text-only classifier reaches macro-F1 0.792 on a fresh test and leaves the other-update class harder.
4. In 237 troubleshooting posts, reproduction context and error evidence are often absent from the saved title and body.
5. In 30 cases, two engineers sometimes chose different first actions.

None of these steps predicts the next one. That separation is the coherent finding. It is not a pipeline.
