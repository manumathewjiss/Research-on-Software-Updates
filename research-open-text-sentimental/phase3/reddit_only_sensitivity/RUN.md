# Reproduce the Reddit-only sensitivity check

From `/Users/manumathewjiss/Documents/Research-on-Software-Updates/research-open-text-sentimental/`:

```bash
phase3/experiment_v1/.venv/bin/python phase3/reddit_only_sensitivity/run_reddit_only_sensitivity.py
```

Requires the existing experiment_v1 virtualenv (`scikit-learn`, `numpy`).
Does not read reserved-test or fresh-test predictions and does not edit prior Phase 3 artifacts.

Code version recorded in the manifest: `reddit-only-sensitivity-v1`.
