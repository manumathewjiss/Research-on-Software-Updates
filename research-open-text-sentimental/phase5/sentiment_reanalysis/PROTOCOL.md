# Sentiment reanalysis protocol

Status: planned on 2026-10-09, before Phase 5 results are inspected.

## Research question

Does VADER sentiment measured from the saved post title and body add useful information for distinguishing troubleshooting from other software-update discussion beyond the existing TF-IDF text classifier?

This is a comparison on the current reviewed task. The original ICMLA sentiment and trajectory results are historical findings, not outcomes for the revised labels.

## Frozen inputs and boundaries

- Primary development population: `phase3/reddit_only_sensitivity/development_reddit_only.jsonl`, restricted to the existing S2 modeling rows and the same two documented near-duplicate exclusions. Expected n=2,050 (1,658 troubleshooting; 392 other update). Preserve the exact/near-duplicate groups and fold assignments in `phase3/reddit_only_sensitivity/results/grouped_oof_predictions.jsonl`.
- Secondary sensitivity: the existing 2,080-row revised S2 development snapshot, with the same exclusions and grouped-fold rule. This includes 30 records with conflicting source metadata; report it separately.
- Do not read labels, scores, predictions, or errors from the 159-row reserved test or 344-row fresh test for model design, selection, or tuning. Do not score either test in this task.
- Do not alter Phase 1 files, existing labels, Phase 3 outputs, the current manuscript, Overleaf, or its figures.

## Primary comparison

Use the same saved title and body text for each arm. VADER features must be computed from these fields only; no comments, source route, community, IDs, timestamps, review metadata, or target-derived fields may enter the classifier.

Compare on identical grouped outer folds:

1. Reproduced frozen TF-IDF + balanced logistic regression (`C=4`) with its recorded threshold, as a continuity check against saved grouped out-of-fold predictions.
2. Sentiment-only model: VADER compound score of title plus body, with a training-fold-only logistic regression and class balancing. Report a constant/majority baseline for context.
3. Hybrid model: the same TF-IDF logistic regression augmented by the one prespecified VADER compound score. Fit all feature transformations only within each outer training fold.

Because model scores need not share the same probability scale, also make a *fair* paired text-only versus hybrid comparison with thresholds selected from inner grouped training folds only. Apply each selected threshold once to the untouched outer fold. Do not use outer-fold outcomes to choose cutoffs. Do not tune extra sentiment features after seeing results; any exploratory additions must be clearly separated and cannot replace the primary comparison.

Report pooled out-of-fold macro-F1, F1/precision/recall for both classes, balanced accuracy, confusion counts, and the paired macro-F1 difference (hybrid minus text-only) with a post-level paired bootstrap interval. Include the exact fold count, class supports, and feature and missing-text behavior. Examine errors that change between text-only and hybrid without treating post hoc explanations as validated labels. Do not call a small positive difference an improvement when its interval spans zero.

## Historical author/community sentiment check

Inspect the Phase 1 `trajectory/` code, `data/c1_prime/` records, and the Phase 2 audit. Reproduce the historical 542-post author/community summary if possible. State the saved-comment coverage, title-only author fallback count, and whether author and community means differ separately. Report the divergence comparison with and without title-only author tracks, and the saved slope/early-late tests. Do not describe a cumulative sentiment plot as evidence of change over time unless an actual temporal test supports it. Keep this historical check separate from the current 2,050-row classifier population.

## Outputs

Create code and outputs only under `phase5/sentiment_reanalysis/`: `RUN.md`, `MANIFEST.json` (input hashes, software versions, folds, settings), `RESULTS.md`, and machine-readable per-fold predictions/metrics. Explicitly mark verified results, missing inputs, and limitations. End `RESULTS.md` with a recommendation: add a bounded sentiment result to the current paper, pivot to a sentiment-centered revision, or retain the current paper without new sentiment claims. Do not edit the paper in this run.
