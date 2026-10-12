# Grouped development validation (followup)

**Generated:** 2026-10-07T16:32:09.068799+00:00

This is a **sensitivity check** of the already-chosen experiment_v1 model. Model, `C`, and decision threshold are unchanged. **Reserved test was not rerun.**

## Config (locked from v1)

- Text: `title_body`
- Model: TF-IDF + logistic regression, `C=4.0`
- Threshold: `0.5877137791150834` (exact saved value from `results/model_selection.json`)
- Folds: 5, `random_state=42`
- Grouping: exact identical text ∪ near-dup pairs with Jaccard ≥ 0.92
- Multi-post groups: 32 (66 posts)

## Headline comparison

| Setting | macro-F1 | other F1 | troubleshooting F1 | confusion [[TN,FP],[FN,TP]] |
|---------|----------|----------|--------------------|-----------------------------|
| Original saved OOF (ungrouped, after threshold) | 0.8409 | 0.7438 | 0.9380 | `[[302, 93], [115, 1574]]` |
| Ungrouped replay (this script) | 0.8409 | 0.7438 | 0.9380 | `[[302, 93], [115, 1574]]` |
| **Grouped StratifiedGroupKFold** | **0.8348** | **0.7336** | **0.9360** | `[[296, 99], [116, 1573]]` |
| Grouped majority baseline | 0.4477 | 0.0000 | 0.8953 | `[[0, 395], [0, 1689]]` |
| Grouped keyword baseline | 0.6891 | 0.5195 | 0.8587 | `[[246, 149], [306, 1383]]` |

**Delta (grouped − original saved macro-F1):** -0.0061

## Grouped TF-IDF LR by source pool

| Source | n | macro-F1 | other F1 | trouble F1 |
|--------|---|----------|----------|------------|
| oct5_query_gds | 295 | 0.7218 | 0.5775 | 0.8661 |
| oct5_query_tps | 1587 | 0.7747 | 0.5970 | 0.9524 |
| phase1_gold_file | 202 | 0.8346 | 0.9394 | 0.7297 |

## Grouped TF-IDF LR by text availability

| Availability | n | macro-F1 | other F1 | trouble F1 |
|--------------|---|----------|----------|------------|
| title_and_body | 1147 | 0.7890 | 0.6245 | 0.9535 |
| title_body_comments | 630 | 0.7778 | 0.6163 | 0.9393 |
| title_only | 138 | 0.6515 | 0.5176 | 0.7853 |
| title_plus_comments | 169 | 0.8196 | 0.9562 | 0.6829 |

## Simple-language conclusion

Keeping identical/near-duplicate posts in the same fold changes development macro-F1 by only -0.006 (0.841 → 0.835). That is a small shift. The chosen TF-IDF model still clearly beats the majority and keyword baselines under the same grouped folds, so the **qualitative conclusion stands**: post text carries usable signal for troubleshooting vs other update discussion on this reviewed development set. This check does not change the model or re-open the reserved test.

## Files

- Review sheet: `MANU_LABEL_REVIEW.csv`
- `DEVELOPMENT_DUPLICATES.md` / `results/development_duplicates.json`
- `results/grouped_validation.json`
- `results/grouped_oof_predictions.jsonl`
- `run_followup.py`

