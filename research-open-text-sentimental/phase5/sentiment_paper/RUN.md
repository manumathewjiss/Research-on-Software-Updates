# Reproduce the sentiment-paper development packet

From the research repository root:

```bash
phase3/experiment_v1/.venv/bin/python phase5/sentiment_paper/audit_join_coverage.py
PYTHONPATH=phase5/sentiment_reanalysis/vendor \
  phase3/experiment_v1/.venv/bin/python phase5/sentiment_paper/run_staged_analysis.py
```

Run the audit first. The staged script reads the audit's preserved fresh-test quote and does not score either protected test. VADER is imported from `phase5/sentiment_reanalysis/vendor`. Outputs stay under `phase5/sentiment_paper/`.

Code version: `sentiment-paper-dev-v2`.

## Manuscript checks

The review draft is `manuscript/main.tex`. It is for coauthor review, not submission. Local checks, which are not printed in the paper:

```bash
phase3/experiment_v1/.venv/bin/python \
  phase5/sentiment_paper/manuscript/analysis/group_bootstrap.py
phase3/experiment_v1/.venv/bin/python \
  phase5/sentiment_paper/manuscript/analysis/technical_word_description.py
```

The group bootstrap reads saved development predictions only. The word-count script writes aggregate cells only: no identifiers and no verbatim post text. Compile the manuscript with `tectonic -X compile main.tex` from `phase5/sentiment_paper/manuscript/`.
