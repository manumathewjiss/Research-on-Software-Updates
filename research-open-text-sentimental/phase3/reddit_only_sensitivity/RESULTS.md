# Reddit-only development sensitivity

**Created:** 2026-10-08T02:12:23.278973+00:00
**Code version:** `reddit-only-sensitivity-v1`

Historical datasets, labels, and prior scores were not modified. The reserved 159-post test and the fresh 344-post test were not scored or used to choose settings.

## Domain verification

Every revised-development ID was joined to `phase2/combined_dataset/master_records.json` and the URL host was read directly. ID prefixes were checked afterward, not used as the inclusion rule.

- Revised development v2 rows: **3151**
- `reddit.com`: **3121**
- `stackoverflow.com`: **30**
- All 30 non-Reddit IDs start with `so_`. No `so_` ID has a Reddit URL, and no Reddit URL lacks a non-`so_` ID among the non-Reddit set.
- All 30 are S2. Class counts: {"1": 28, "0": 2}. Source pools: {"oct5_query_tps": 25, "oct5_query_gds": 5}.

Row-level list: `results/excluded_non_reddit.csv`.

## Dataset flow

| Stage | All rows | Reddit URLs | Non-Reddit URLs | S2 modeling n | Troubleshooting (1) | Other update (0) |
|---|---:|---:|---:|---:|---:|---:|
| revised_development_v2 all rows | 3151 | 3121 | 30 | 2080 | 1686 | 394 |
| reddit-only snapshot all rows | 3121 | 3121 | 0 | 2050 | 1658 | 392 |

S2 modeling drops the already documented near-duplicate development IDs `1t0wme9` and `1wrqch6` (both Reddit; kept in the snapshot file, excluded from fitting). The four uncertain-review IDs are already absent from revised development v2.

## Fixed model (not retuned)

- Title + body, TF-IDF word unigrams and bigrams, logistic regression `C=4`, class-balanced.
- Decision threshold `0.5877137791150834` from the original saved selection.
- Five `StratifiedGroupKFold` folds, `random_state=42`. Exact text and Jaccard ≥ 0.92 near-duplicates stay in one fold. Vectorizer fit only on each fold’s training posts.
- Same folds for majority and the fixed keyword baseline in `run_experiment.py`.

Reddit-only duplicate grouping: **32** multi-post groups (66 posts).

## Scores

Saved reference is grouped out-of-fold evaluation on **mixed** revised development v2 (n=2080: 1686 troubleshooting, 394 other update), from `diagnostic_results/analysis.json`. That run includes the 30 Stack Overflow posts and built groups on that larger set, so folds are not identical.

| Evaluation | n | macro-F1 | other P/R/F1 | trouble P/R/F1 | balanced acc. | confusion [[0,1]] |
|---|---:|---:|---|---|---:|---|
| Saved mixed v2 grouped TF-IDF LR | 2080 | 0.8347 | 0.709/0.761/0.734 | 0.943/0.927/0.935 | 0.8442 | `[[300, 94], [123, 1563]]` |
| Reddit-only grouped TF-IDF LR | 2050 | 0.8363 | 0.725/0.747/0.736 | 0.940/0.933/0.936 | 0.8403 | `[[293, 99], [111, 1547]]` |
| Reddit-only grouped majority | 2050 | 0.4471 | 0.000/0.000/0.000 | 0.809/1.000/0.894 | 0.5000 | `[[0, 392], [0, 1658]]` |
| Reddit-only grouped keyword | 2050 | 0.6569 | 0.392/0.643/0.487 | 0.900/0.764/0.827 | 0.7035 | `[[252, 140], [391, 1267]]` |

**Delta macro-F1 (Reddit-only − saved mixed):** +0.0016.

Bootstrap 95% intervals on the Reddit-only TF-IDF predictions (1000 resamples of the out-of-fold pairs, seed 42):

- macro-F1 0.8363 (0.8153–0.8567)
- other-update F1 0.7362 (0.7004–0.7705)
- troubleshooting F1 0.9364 (0.9279–0.9453)

These intervals describe resampling of this development check. They are not a new test-set interval.

## Interpretation

Removing the 30 Stack Overflow posts changes the development population and the duplicate groups, so this score is not a revision of the saved mixed-corpus number. The Reddit-only grouped macro-F1 is 0.836 versus 0.835 on the mixed v2 set. The shift is small relative to the bootstrap interval, and the TF-IDF model still beats the majority and keyword baselines on the same Reddit-only folds. A claim that post text separates troubleshooting from other update discussion **within this reviewed Reddit S2 development set** remains supported.

What does not become stronger: the historical reserved-test and fresh-test scores were fit with Stack Overflow posts still in development, so they are mixed-corpus results. This check does not replace them. The other-update class is still the harder class, and source pool remains entangled with class mix. Thirty excluded posts are too few, and too class-imbalanced (28 troubleshooting, 2 other), to support a separate Stack Overflow performance claim.

## Reproduce

```bash
phase3/experiment_v1/.venv/bin/python phase3/reddit_only_sensitivity/run_reddit_only_sensitivity.py
```

Run from the research repository root. Inputs and output hashes are in `MANIFEST.json`.
