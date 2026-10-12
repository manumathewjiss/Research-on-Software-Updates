# Sentiment-centered development packet

**Created:** 2026-10-09T21:40:24.784064+00:00
**Code version:** `sentiment-paper-dev-v2`

This packet prepares a new paper. It does not edit the current manuscript or Overleaf. The reserved and fresh tests were not scored. S2 class 0 is other update discussion. Historical TPS/GDS and `general_dissatisfaction` are separate populations.

## Stage A: exact title/body replication

The frozen 2,050-row comparison was checked against its saved inputs rather than refit. Input hashes match. The saved TF-IDF scores had already matched the Phase 3 grouped predictions with maximum absolute gap 0.0.

Text macro-F1 0.8319. VADER-only 0.5335. Text plus VADER 0.8331. Majority 0.4471. Hybrid minus text +0.0012 (95% interval -0.0115 to +0.0146; includes zero: True).

This is not a positive incremental finding.

## Stage B: comment roles on the development subset

Any nonempty stored comment: 797 / 2050. Author reply: 474. Community comment: 789. Both roles: 466 (0.227). Title only: 303. Stored comments cover 0.379 of recorded `num_comments`.

Mean compound, troubleshooting minus other update discussion:

- Pre-discussion title/body: -0.0644 vs 0.1941 (n 1658/392; difference -0.2585; Welch p 1.738e-14; bootstrap CI -0.3186 to -0.1961; includes zero: False)
- Title-only posts only: -0.1286 vs 0.0614 (n 126/177; difference -0.1900; Welch p 1.272e-07; bootstrap CI -0.2607 to -0.1264; includes zero: False)
- Posts with a body: -0.0591 vs 0.3033 (n 1532/215; difference -0.3625; Welch p 1.256e-11; bootstrap CI -0.4664 to -0.2584; includes zero: False)
- Author replies, observed only: 0.1317 vs 0.2783 (n 362/112; difference -0.1467; Welch p 0.0002365; bootstrap CI -0.2269 to -0.0655; includes zero: False)
- Community comments, observed only: 0.1681 vs 0.1918 (n 554/235; difference -0.0237; Welch p 0.2627; bootstrap CI -0.0642 to +0.0161; includes zero: True)

No human-confirmed outcome label exists. Reply sentiment is not evidence that a reply solved an issue.

### Restricted discussion type, not a substitute for S2

Technical troubleshooting 1658 versus general dissatisfaction 68.

- Pre-discussion: -0.0644 vs -0.0680 (n 1658/68; difference +0.0036; Welch p 0.9686; bootstrap CI -0.1695 to +0.1736; includes zero: True)
- Author replies observed: 0.1317 vs 0.2596 (n 362/15; difference -0.1280; Welch p 0.21; bootstrap CI -0.3242 to +0.0380; includes zero: True)
- Community observed: 0.1681 vs 0.1057 (n 554/25; difference +0.0624; Welch p 0.1556; bootstrap CI -0.0189 to +0.1418; includes zero: True)

Source-pool comment availability and the largest subreddits are in `results/stage_b_comment_description.json`. Source and subreddit are stratification, not classifier features.

## Stage C: development models

No manuscript recommendation is made here. The pre-discussion task and the full-thread task answer different questions.

### Pre-discussion task

Stage A compares title-and-body TF-IDF with the same title-and-body text plus the title-and-body VADER compound. Comments are not in either arm. That result stands on its own: hybrid minus text +0.0012 (95% interval -0.0115 to +0.0146; includes zero: True).

### Feature timing

On the 797 posts with at least one nonempty stored comment, the full-thread string contains 7388 nonempty comments. 7388 have a timestamp at or after the post, 0 have an earlier timestamp, and 0 lack a comparable timestamp. Those comments are later turns in the saved snapshot when the timestamp is at or after the post. Using them is a retrospective description of the stored thread, not a claim that the model could have classified the post before replies, and not a claim about what caused a later reply.

### Fair full-thread comparison

Chosen snapshot title, body, then nonempty stored comments sorted by created_utc text. Author replies and community comments are included. No role marker is inserted. TF-IDF is fit inside each training fold. The hybrid appends the prespecified sentiment columns to that same vector.

Both author and community text are present for 466 of 2050 posts (0.227), below the predeclared 50% bar.

Same 797 posts, same saved grouped folds, thresholds chosen inside each training split.

| Arm | macro-F1 | other P/R/F1 | positive-class P/R/F1 | confusion [[0,1]] |
|---|---:|---|---|---|
| Full-thread text | 0.8659 | 0.802/0.823/0.812 | 0.924/0.914/0.919 | `[[195, 42], [48, 512]]` |
| Same full-thread text plus sentiment features | 0.8390 | 0.765/0.785/0.775 | 0.908/0.898/0.903 | `[[186, 51], [57, 503]]` |
| VADER title/body only, for reference | 0.5351 | 0.374/0.835/0.517 | 0.854/0.409/0.553 | `[[198, 39], [331, 229]]` |

Full-thread hybrid minus full-thread text: macro-F1 -0.0268 (95% interval -0.0489 to -0.0042; includes zero: False). The interval lies entirely below zero: in this development comparison the sentiment columns have lower macro-F1 than the same thread text. That is not a gain. It is also not a prospective or causal finding, and both-role coverage remains below the predeclared bar for a strong claim.

### Contrast that does not isolate sentiment

Title/body TF-IDF versus title/body TF-IDF plus comment-derived sentiment uses comments only on the hybrid side. That difference was +0.0042 (95% interval -0.0166 to +0.0259). It is not evidence that sentiment adds information beyond comment text, whether or not the interval contains zero.

| Arm | macro-F1 | other P/R/F1 | positive-class P/R/F1 | confusion [[0,1]] |
|---|---:|---|---|---|
| Title/body text | 0.8595 | 0.855/0.747/0.797 | 0.898/0.946/0.922 | `[[177, 60], [30, 530]]` |
| Title/body text plus comment sentiment | 0.8638 | 0.850/0.764/0.804 | 0.904/0.943/0.923 | `[[181, 56], [32, 528]]` |
| Keyword-first rule on title/body, not pure sentiment | 0.7608 | 0.771/0.553/0.644 | 0.831/0.930/0.878 | `[[131, 106], [39, 521]]` |

Full 2,050-row continuity checks use title and body only. They do not add a sentiment feature.

| Text logistic regression, inner threshold | 0.8319 | 0.721/0.737/0.729 | 0.938/0.932/0.935 | `[[289, 103], [112, 1546]]` |
| Naive Bayes, same TF-IDF, inner threshold | 0.5512 | 1.000/0.110/0.198 | 0.826/1.000/0.905 | `[[43, 349], [0, 1658]]` |
| Linear SVM, same TF-IDF, default margin | 0.8203 | 0.867/0.584/0.698 | 0.909/0.979/0.943 | `[[229, 163], [35, 1623]]` |
| Keyword-first rule | 0.6847 | 0.542/0.426/0.477 | 0.871/0.915/0.892 | `[[167, 225], [141, 1517]]` |

Naive Bayes and the linear SVM use the same title/body TF-IDF as logistic regression and no sentiment feature. A difference among them is a model change, not evidence about sentiment. The SVM threshold is the default margin. Naive Bayes uses the same inner-threshold grid as logistic regression.

### Restricted model

n=1726: 1658 technical troubleshooting and 68 general dissatisfaction. 1 = technical_troubleshooting; 0 = general_dissatisfaction. Not S2.

| Text | 0.6580 | 0.301/0.412/0.348 | 0.976/0.961/0.968 | `[[28, 40], [65, 1593]]` |
| VADER title/body only | 0.4900 | 0.000/0.000/0.000 | 0.961/1.000/0.980 | `[[0, 68], [0, 1658]]` |
| Text plus title/body VADER | 0.6684 | 0.316/0.441/0.368 | 0.977/0.961/0.969 | `[[30, 38], [65, 1593]]` |

Hybrid minus text macro-F1 +0.0104 (95% interval -0.0097 to +0.0312; includes zero: True). This contrast drops other update posts whose discussion type is not general dissatisfaction. It does not replace the S2 result.

## Preserved fresh-test score

The existing fresh test remains macro-F1 **0.7915** on 344 posts, with confusion `[[46, 21], [25, 252]]`. This run did not hide or recompute it. It is lower than the earlier reserved-test result and stays visible.

## ReleaseTrain 3% and risk cadence

This remains an unverified separate question. Local snapshots show candidate-pool sizes, not a prevalence, and they do not document the professor's numerator, denominator, time range, or risk definition.

## Proposed paper questions

1. In reviewed software-update posts, does title-and-body sentiment improve troubleshooting-versus-other-update classification beyond TF-IDF text? Current development answer: no reliable gain.
2. On the partial saved thread, do sentiment summaries add information beyond a TF-IDF model that already contains the same title, body, author replies, and community comments? The title/body-plus-comment-sentiment difference does not answer this. The full-thread contrast is the relevant development comparison, and it is retrospective rather than prospective.
3. If the question is specifically technical troubleshooting versus confirmed general dissatisfaction, what is the exact reviewed population, and does the title/body result change? Report that population separately from S2.
4. Historical TPS/GDS divergence remains a limited exploratory finding with title-only fallback and incomplete comments. It is not an S2 result and not evidence of a conversation cadence.
5. Whether about 3% of ReleaseTrain posts are recent update risks is a distinct study and is not answered here.

Do not claim that replies solved an issue. No human-confirmed outcome label exists.

## Files

- `AUDIT.md`
- `results/join_coverage_audit.json`
- `results/stage_a_title_body.json`
- `results/stage_b_comment_description.json`
- `results/stage_c_development_models.json`
- `results/stage_c_comment_subset_predictions.jsonl`
- `results/figures/`
