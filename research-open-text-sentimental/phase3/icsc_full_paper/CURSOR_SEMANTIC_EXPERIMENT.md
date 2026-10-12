# Cursor task: one semantic-representation comparison

**Research question:** On the audited Reddit-only software-update development set, does a frozen sentence-level semantic representation distinguish troubleshooting from other update discussion more reliably than the existing word-based TF-IDF model, especially outside the dominant source pool?

## Inputs and guards

- Audited development snapshot: `phase3/update_connection_audit/targeted_submission/development_after_update_audit.jsonl`.
- Join URLs to `phase2/combined_dataset/master_records.json`; retain Reddit domains only; exclude the two near-duplicate IDs `1t0wme9` and `1wrqch6`. Expected S2 n=2,136 (1,733 troubleshooting, 403 other update).
- Use the **same outer fold IDs** as `phase3/update_connection_audit/targeted_submission/post_audit_reddit_only_oof.jsonl`.
- Read **no reserved-test or fresh-test labels/predictions** for model choice or scoring. Do not modify historical files.
- Use title+body only, no comments, source, subreddit, IDs, label reason, or diagnostic fields as predictors.

## Exactly one semantic model

- Frozen encoder: `sentence-transformers/all-MiniLM-L6-v2`, record exact model revision, package versions and text construction. Record the proportion of posts truncated at its 256-word-piece default; report by class.
- One `LogisticRegression` head on the frozen embeddings, with `class_weight=balanced` and a fixed `C=1.0`. Do not fine-tune the encoder or search many backbones.
- For a fair classification-threshold comparison, determine any threshold from each outer fold's **training records only**, using three inner grouped folds and a preregistered grid. Apply the same inner-threshold procedure to the TF-IDF LR comparator (`C=4`). If this nested procedure is impractical, predeclare one fixed threshold per arm without looking at outer-fold labels and explain the limitation; do not tune on outer results.

## Measures and interpretation

- Primary: macro-F1 and other-update F1 from paired out-of-fold predictions on identical outer folds. Also report both-class precision/recall, confusion matrices, and paired bootstrap interval for the macro-F1 difference.
- Secondary: results by source pool and text availability, with counts. A source-held-out or date-ordered development analysis is allowed only if defined before scoring and its smaller comparison class is reported.
- Include computational cost and truncation. A worse semantic result is still a valid finding.
- Save a manifest, runnable code, fold-level and per-post outputs, and a plain-language results note under a new `phase3/semantic_comparator/` directory.
- Do **not** claim the semantic model is a novel architecture, and do not claim independent generalization from development folds.
