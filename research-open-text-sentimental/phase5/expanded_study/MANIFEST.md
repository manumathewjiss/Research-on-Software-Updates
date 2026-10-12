# Manifest

Recorded from the finished result files and from package metadata. Models were not rerun.

| item | value | source |
| --- | --- | --- |
| started | 2026-10-10T00:48:38.299720+00:00 | `results/run_manifest.json` |
| finished | 2026-10-10T01:01:45.433731+00:00 | `results/run_manifest.json` |
| reproduction | passed, macro-F1 0.8319320360990539 | `results/reproduction_title_body.json` |
| Python | 3.14.7 | run manifest |
| scikit-learn | 1.9.1 | run manifest |
| VADER | 3.3.2 | `vaderSentiment-3.3.2.dist-info/METADATA` |
| TextBlob | 0.20.1 | `vendor/textblob-0.20.1.dist-info/METADATA` |
| NLTK | 3.10.3 | `vendor/nltk-3.10.3.dist-info/METADATA` |
| torch | 2.14.1 | `results/sentiment_comparison.json` |
| transformers | 5.19.0 | same |
| contextual model | cardiffnlp/twitter-roberta-base-sentiment-latest | same |
| contextual cache main | 3216a57f2a0d9c45a2e6c20157c20c49fb4bf9c7 | Hugging Face cache `refs/main` at inspection; not pinned in the run |
| contextual truncation | 188/2050 over 512 tokens; median 134 including special tokens | sentiment JSON |
| sentence-transformers | 6.1.0 | `results/minilm.json` |
| MiniLM snapshot | 1110a243fdf4706b3f48f1d95db1a4f5529b4d41 | minilm JSON `local_snapshot_dirs` |
| held-out tests read | false | run manifest |
| sentiment gold labels | none | study protocol |
| group bootstrap | 1000 draws, seed 42, 2016 groups | `results/group_bootstrap.json` |

A second Cardiff snapshot directory, `d616e2bdfcdb0ca89d9b6efc4909e1db063af290`, contains `model.safetensors` only. `refs/main` points at `3216a57f`, which contains `pytorch_model.bin`. The run called the model id without a revision argument.
