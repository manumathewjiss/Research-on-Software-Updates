# Phase 3 experiment package

This folder contains a fixed copy of reviewed Phase 2 records for the first model evaluation. Source: `../../phase2/combined_dataset/master_records.json`. Run `python3 build_package.py` only when deliberately creating a **new version** of the snapshot; compare `MANIFEST.json` before replacing existing data. Phase 1 and Phase 2 sources are unchanged.

- `data/development.jsonl`: 3,155 resolved development records, after excluding two exact text copies that also appear in the reserved test set.
- `data/reserved_test.jsonl`: 200 reserved records, unchanged. Only 159 meet the recommended S2 update-focused scope.
- `MANIFEST.json`: source and output hashes, counts, and excluded IDs.
- `CURSOR_PROMPT.md`: complete instructions for Cursor.

The five unresolved posts are absent. These records are reviewed labels of different provenance, including assisted review and joint decisions; they are not all independent blind annotations. `source_pool_audit_only` and `review_status_audit_only` are for analysis, never model features. The primary task uses `s2_in_scope=true` and predicts `s2_target` from title or title plus body.

The review set was assembled from keyword-driven API candidate pools and Phase 1 posts. Its class proportions need not represent Reddit as a whole. Report results for this collected corpus, and avoid population-wide claims.
