# Phase 3 experiment_v1 results

**Run date:** 2026-10-07  
**Protocol:** `PROTOCOL.md` (frozen before reserved-test scoring)  
**Audit:** `DATA_AUDIT.md`  
**Code:** `audit_data.py`, `run_experiment.py`  
**Artifacts:** `results/`

---

## Plain-English verdict

Within already-scoped software-update posts, a simple **TF-IDF + logistic regression** model on **title + body** clearly beats majority and keyword baselines at separating **technical troubleshooting** from **other update discussion**. On the held-out reserved test (159 S2 posts), macro-F1 was about **0.86** and troubleshooting F1 about **0.96**. That supports a limited claim: post text carries usable signal for this binary distinction under the current reviewed labels.

It does **not** yet support strong claims about Reddit overall, independent annotator agreement, or Phase 1 “sentiment” reframing. Failures concentrate on the minority “other update” class, title-only posts, and source pools where keywords already push class mix. Forty-eight heuristic label flags need human review before manuscript wording hardens.

---

## Data used

| Split | S2 n after protocol exclusions | troubleshooting (1) | other update (0) |
|-------|--------------------------------|---------------------|------------------|
| Development | 2084 | 1689 | 395 |
| Reserved test | 159 | 135 | 24 |

Excluded from development (near-dup of reserved): `1t0wme9`, `1wrqch6`. Reserved set untouched.

---

## Model selection (development OOF only)

Selection metric: macro-F1, then troubleshooting F1, then troubleshooting recall. Stratified 5-fold CV, seed 42. Vectorizers fit inside each fold.

| Rank | Setting | Model | C | OOF macro-F1 | Trouble F1 | Other F1 |
|------|---------|-------|---|--------------|------------|----------|
| 1 | title_body | tfidf_lr | 4.0 | 0.838 | 0.943 | 0.733 |
| 2 | title_body | tfidf_linear_svm | 0.25 | 0.837 | 0.942 | 0.731 |
| 3 | title_body | tfidf_linear_svm | 1.0 | 0.836 | 0.945 | 0.726 |
| — | title_body | keyword | — | 0.659 | 0.829 | 0.489 |
| — | either | majority | — | 0.448 | 0.895 | 0.000 |

Title-only TF-IDF models topped out near macro-F1 **0.76** — useful but weaker than title+body.

**Chosen:** `title_body` + `tfidf_lr` + `C=4.0`. OOF threshold swept to maximize macro-F1 → **threshold ≈ 0.588** (default would be 0.5). After threshold: OOF macro-F1 **0.841** (95% bootstrap CI ≈ 0.820–0.861), troubleshooting F1 **0.938**.

### Baselines

- **Majority** always predicts troubleshooting: high trouble F1, **zero** other-class F1, macro-F1 ≈ 0.45.
- **Keyword** (fixed troubleshooting cues on title+body): macro-F1 ≈ 0.66 — real signal, but TF-IDF LR gains ~0.18 macro-F1 on OOF.

### Source stress (chosen model OOF)

| Source | n | macro-F1 | notes |
|--------|---|----------|-------|
| oct5_query_tps | 1587 | 0.774 | heavy troubleshooting prior |
| oct5_query_gds | 295 | 0.750 | weaker other-class precision |
| phase1_gold_file | 202 | 0.858 | more balanced / other-heavy |

Source was **not** a model feature. Performance still varies by pool; do not over-claim pool-independent accuracy.

---

## Reserved-test evaluation (once)

Config locked from development. Refit on all 2084 eligible development rows. Scored once on 159 S2 reserved posts.

| Metric | Value | Bootstrap 95% CI |
|--------|-------|------------------|
| Accuracy | 0.931 | — |
| Balanced accuracy | 0.856 | — |
| Macro-F1 | **0.863** | 0.778–0.931 |
| Troubleshooting F1 | **0.959** | 0.933–0.981 |
| Other-update F1 | 0.766 | — |
| Trouble precision / recall | 0.956 / 0.963 | — |
| Other precision / recall | 0.783 / 0.750 | — |
| Average precision (trouble) | 0.988 | — |
| Precision@10 / @20 | 1.0 / 1.0 | — |

Confusion matrix `[actual rows × pred cols]` for labels [0, 1]:

```
[[18,  6],
 [ 5, 130]]
```

Reserved set is troubleshooting-heavy (135 vs 24). Accuracy and top-k alone would look strong even for weaker models; macro-F1 and other-class metrics are the fairer read. Test CI for macro-F1 is wide because the minority class is small (n=24).

Machine-readable: `results/reserved_test_metrics.json`, `results/reserved_test_predictions.jsonl`.

---

## What this can and cannot support

**Can support (cautiously):**

- Among reviewed S2 posts in this package, title+body text separates troubleshooting from other update discussion better than majority or a fixed keyword rule.
- Errors are mostly minority-class confusions, not total failure of the positive class.

**Cannot support yet:**

- Population estimates for all of Reddit or all software talk.
- Claims that labels are independent double-blind gold (they are reviewed decisions of mixed origin).
- Scope detection (`about_software` / `update_related`) — assumed given.
- Using `discussion_context` / comments as primary features.
- Tiny differences among top TF-IDF configs as “significant.”

---

## Failures and review needs

1. **Other-update class** remains the hard class (OOF other F1 ≈ 0.74; test ≈ 0.77).
2. **Title-only** availability hurts OOF macro-F1 (~0.67 for that slice).
3. **Label flags:** 48 heuristic rows in `results/label_quality_flags.jsonl` (rant vs fix-ask boundary, thin text). Not auto-corrected.
4. If Manu overturns many flags, treat this reserved-test number as **exploratory** for confirmatory writing and plan a fresh untouched test set.

---

## Files

| Path | Role |
|------|------|
| `DATA_AUDIT.md` | Integrity, leakage, provenance |
| `PROTOCOL.md` | Frozen experiment rules |
| `RUN.md` | Exact commands |
| `QUESTIONS_FOR_MANU.md` | Human decisions |
| `results/model_selection.json` | OOF ranking + chosen config |
| `results/development_oof_predictions.jsonl` | OOF preds |
| `results/reserved_test_*.json*` | One-shot test |
| `results/environment.txt` | `pip freeze` |
| `results/development_exclusions.json` | Near-dup exclusions |
| `results/label_quality_flags.jsonl` | Heuristic flags |
