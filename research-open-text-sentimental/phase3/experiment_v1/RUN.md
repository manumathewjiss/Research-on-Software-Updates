# How to reproduce experiment_v1

Work from the repo root:

`/Users/manumathewjiss/Documents/Research-on-Software-Updates/research-open-text-sentimental/`

Do not rebuild `data/*.jsonl` or edit labels for this run.

## One-time setup

```bash
python3 -m venv phase3/experiment_v1/.venv
phase3/experiment_v1/.venv/bin/pip install -U pip
phase3/experiment_v1/.venv/bin/pip install scikit-learn numpy
```

## Audit (before / with protocol)

```bash
phase3/experiment_v1/.venv/bin/python phase3/experiment_v1/audit_data.py
```

Writes `DATA_AUDIT.md` and under `results/`:

- `near_duplicate_candidates.jsonl`
- `development_exclusions.json`
- `label_quality_flags.jsonl`
- `title_only_collisions.jsonl`

Then confirm `PROTOCOL.md` matches the exclusions (already frozen for the reported run).

## Train, select, one reserved-test eval

```bash
phase3/experiment_v1/.venv/bin/python phase3/experiment_v1/run_experiment.py
```

Writes:

- `results/environment.txt`
- `results/model_selection.json`
- `results/development_oof_predictions.jsonl`
- `results/reserved_test_predictions.jsonl`
- `results/reserved_test_metrics.json`

Expected wall time on a laptop: on the order of one minute.

## Notes

- Seed: 42. Protocol: `PROTOCOL.md`.
- Re-running `run_experiment.py` will overwrite result files with the same procedure; it does not authorize protocol changes after peeking at test metrics.
- Package versions for the reported run are in `results/environment.txt`.
