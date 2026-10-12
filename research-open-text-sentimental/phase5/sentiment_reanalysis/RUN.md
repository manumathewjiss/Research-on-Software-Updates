# Reproduce the sentiment reanalysis

From `/Users/manumathewjiss/Documents/Research-on-Software-Updates/research-open-text-sentimental/`:

```bash
PYTHONPATH=phase5/sentiment_reanalysis/vendor \
  phase3/experiment_v1/.venv/bin/python \
  phase5/sentiment_reanalysis/run_sentiment_reanalysis.py
```

The experiment virtualenv supplies scikit-learn, numpy, scipy, and pandas. VADER 3.3.2 is imported from `phase5/sentiment_reanalysis/vendor` so the Phase 3 environment is not modified.

The script reads the saved Reddit-only development rows and folds, the revised 2,080-row development snapshot, the Phase 1 trajectory inputs, and the saved C1′ metrics. It does not read reserved-test or fresh-test labels, scores, predictions, or errors, and it writes only under `phase5/sentiment_reanalysis/`.

Code version: `sentiment-reanalysis-v1`.
