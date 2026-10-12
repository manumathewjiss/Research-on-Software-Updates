# experiment_v1 followup (2026-10-07)

Sensitivity check and Manu review pack. **Does not** change the frozen protocol, labels, chosen model/threshold, or reserved-test scores.

## Contents

| File | Purpose |
|------|---------|
| `MANU_LABEL_REVIEW.csv` | 48 heuristic flags + 3 identical-text conflict posts; empty decision columns |
| `DEVELOPMENT_DUPLICATES.md` | Within-development exact/near duplicate audit |
| `GROUPED_VALIDATION.md` | Grouped-fold development validation vs original OOF |
| `run_followup.py` | Reproducible script |
| `results/` | JSON/JSONL machine-readable outputs |

## Reproduce

From the research repo root, with the existing venv:

```bash
phase3/experiment_v1/.venv/bin/python phase3/experiment_v1/followup/run_followup.py
```

## What this does / does not do

- Reviews heuristic flags as **suggestions**, not confirmed mistakes.
- Keeps identical and high-similarity (Jaccard ≥ 0.92) posts in the same CV fold.
- Reuses TF-IDF LR `C=4` and the saved threshold `≈0.5877`.
- Does **not** rescore the reserved test or start a new model-selection round.
