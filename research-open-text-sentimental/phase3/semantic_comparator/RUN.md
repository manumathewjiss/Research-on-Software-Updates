# Reproduce the semantic comparison

From the research repository root:

```bash
phase3/experiment_v1/.venv/bin/python phase3/semantic_comparator/run_semantic_comparator.py
```

The script downloads `sentence-transformers/all-MiniLM-L6-v2` on first run. It does not read the reserved or fresh tests.
