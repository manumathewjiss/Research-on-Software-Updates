# Manu's completed label review: intake and next step

The submitted 51-row CSV was checked against the original blank review file and archived here unchanged. All IDs and original post fields match, all decisions have explanations, and no answer field is missing. The SHA-256 of the archived submission is recorded in `DEVELOPMENT_SENSITIVITY.json`.

## Decisions

- Keep: 45.
- Change: 2. `1tebwdi` changed from troubleshooting to general dissatisfaction. `1wxl35m` changed from troubleshooting to other update discussion; its label now agrees with the two identical Kubernetes posts.
- Uncertain: 4 (`1lsuvac`, `1lrpn7u`, `1s3krfu`, `1qzew1k`). Their saved text is too thin for a confident type judgment. Exclude them from revised supervised development analysis rather than guessing.

The original Phase 2 master and experiment_v1 input files remain unchanged. This submission is a versioned correction record, not a retroactive alteration of the saved experiment.

## Development-only sensitivity check

Using the same title+body TF-IDF logistic regression, `C=4`, exact saved threshold, and grouped five-fold validation, the revised development set has 2,080 posts (1,686 troubleshooting; 394 other update). No identical-text group now has a conflicting binary target.

| Development setting | Macro-F1 | Other F1 | Troubleshooting F1 |
|---|---:|---:|---:|
| Grouped validation before Manu's decisions | 0.8348 | 0.7336 | 0.9360 |
| Grouped validation after Manu's decisions | 0.8347 | 0.7344 | 0.9351 |
| Keyword baseline after decisions | 0.6880 | 0.5175 | 0.8586 |
| Majority baseline after decisions | 0.4477 | 0.0000 | 0.8954 |

The development result is essentially unchanged. This is a sensitivity check, not a new model-selection round. The reserved test was not read or rescored by this intake script.

## Next step

Finalize a revised training-label snapshot from Manu's two corrections and four exclusions, with provenance and a new version ID. Then design a **new untouched external or later-collected test set** for a final confirmatory evaluation of a model trained on revised labels. The old 159-post reserved result remains the original v1 result and should be described as such; it cannot serve as a fresh one-shot test for a model retrained after these decisions. The new test should contain enough other-update posts to measure the minority class, and its selection and labels should be locked before model scoring. No new large development-labeling batch is needed.
