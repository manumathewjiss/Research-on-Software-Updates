# Feasibility and protocol

Inspection date: 9 October 2026. No model was trained, no label was changed, and `phase5/final_synthesis_paper/` was not edited.

This note covers Tasks 1, 2, 4, and 5 from the ten-task request. Tasks 3, 6, 7, 8, 9, and 10 rewrite the manuscript or its figures. They are deferred because this step forbids paper edits. That deferral is not a scientific finding that those tasks are unnecessary.

Population for every proceed decision: the 2,050 Reddit-URL development rows and the saved grouped folds in `phase5/expanded_study/results/predictions.jsonl` (`group_id`, `fold`). Reproduce title-and-body macro-F1 0.8319320360990539 before interpreting a new arm. Do not open the reserved 159 or fresh 344 files.

## Execution environment

Use only `phase3/experiment_v1/.venv/bin/python`. A fresh import there finished in a few seconds: Python from that venv, scikit-learn 1.9.1, torch 2.14.1, transformers 5.19.0. Do not import torch or transformers from `tps_gds_classification/.venv`. That environment has already hung on the import; a later run must not wait on it.

Every new import or shell check gets a 60-second bound. If it exceeds that bound, kill it and record the dependency as unavailable. Do not switch virtualenvs to get around the timeout.

Machine: Apple M3, 8 cores, 16 GB RAM. `df` on 9 October 2026 showed about 11 GB free on the data volume. That free-space figure is a hard gate.

- Task 1 needs an 835,369,209-byte `dsm.bin` plus jars. Start that pull only if at least 6 GB are free, and stop if free space falls below 4 GB.
- Task 2 may keep one RoBERTa checkpoint for the current fold, then delete it after the out-of-fold predictions are written. Do not keep five optimizer states. Stop the fold if free space falls below 4 GB.
- MPS was available in an unsandboxed check of this same venv and unavailable inside the sandbox. The training process has to run unsandboxed. If MPS is still false there, train on CPU inside the same 45-minute fold limit and record the device. Do not hunt for another Python.

Unavailable on this machine until installed, each marked rather than assumed: Java runtime, DVC, R, Git LFS. Homebrew is present. Generic SentiStrength is not an available substitute.

## Task 1 — software-engineering sentiment model

**Decision: conditional proceed with frozen pySenti4SD. Skip generic SentiStrength. Do not score the 2,050 until the gate below passes.**

Official sources checked on 9 October 2026:

- https://github.com/collab-uniba/pySenti4SD — MIT license, copyright 2019 Collaborative Development Group. README requires DVC and Java 8 or newer. Python libraries named in the README are numpy, pandas, scipy, scikit-learn, and joblib.
- `Senti4SD.model` is in that git tree (blob `85e3f7f3aa95fbb14775617cf166e8c4746d51ca`, 550,624 bytes). `Senti4SD_info` says the saved solver is L1-regularized logistic regression, C = 0.5, trained and reported on Stack Overflow polarity (negative, neutral, positive).
- The Java feature-extraction jars and the distributional model are not in git. `java/Senti4SD.jar.dvc`, `java/Senti4SD-fast.jar.dvc`, `java/NgramsExtraction.jar.dvc`, and `java/dsm.bin.dvc` are DVC pointers. `.dvc/config` sets remote `origin` to `https://dagshub.com/collab-uniba/pySenti4SD.dvc`. `dsm.bin` is 835,369,209 bytes, md5 `395cb470cacd6e584508d108945b67d3`.
- https://github.com/collab-uniba/Senti4SD — also MIT. That tree is the R/Java tool and needs Git LFS, Java 8, and R, plus caret, LiblineaR, and e1071.

This machine, checked without installing anything: Java, DVC, R, and Git LFS are unavailable. Homebrew is present. About 11 GB of disk is free, so the 835 MB semantic model fits only if the 6 GB start gate above still holds at pull time. The repository also ships `python/core/liblinear_multicore/so/liblinear.so.3`, a Linux shared library. The classification path in the README is `classification.sh`, which calls Java. The Linux library is not the planned inference path and is not a macOS binary.

Senti4SD is a polarity classifier for developer communication, trained on more than 4,000 Stack Overflow posts (Calefato, Lanubile, Maiorano, and Novielli, Empirical Software Engineering, 2018, DOI 10.1007/s10664-017-9546-9). It is not a troubleshooting-purpose model. A fair use on this study is the same use as VADER: a frozen score, then a development-only logistic head. Generic SentiStrength is not SE-specific and is not a substitute if this gate fails. SentiStrength-SE was not selected; the primary-source lead for this task is Senti4SD, and the generic SentiStrength jar is a different license and a different tool.

**Gate, in order. Stop at the first failure and write the blocker. Do not score the 2,050 if the gate fails.**

1. Install a JDK that reports version 8 or newer, and install DVC.
2. Clone `pySenti4SD` outside the manuscript directory. Run `dvc pull -r origin`.
3. Confirm `dsm.bin` size 835,369,209 and md5 `395cb470cacd6e584508d108945b67d3`, and confirm a jar named by the DVC pointers is present.
4. Run `classification.sh` on the repository `Sample.csv` only. Record the command, Java version, and whether polarities are emitted.

**If the gate passes, the only analysis is:**

- Input: raw title, newline, raw body, including empty bodies. Do not retrain Senti4SD.
- Map the tool's labels before seeing any purpose score: positive = +1, neutral = 0, negative = −1. Do not change that map after the macro-F1 is known.
- Two arms on the saved folds, with the existing inner-threshold rule (grid 0.20–0.80 step 0.05; training folds only): Senti4SD score alone, and title-and-body TF–IDF plus that score. Scaler fit on the training fold only.
- Compare each arm with saved `pred_title_body` by the existing group bootstrap (1,000 draws, seed 42). An interval that includes zero stays a null increment.
- Record any truncation, crash, or row the tool skips. There is no sentiment gold label, so polarity accuracy is not claimed.
- Cite Calefato et al. 2018 only if this run is actually used. Do not add the citation to the paper in this step.

**Skip rule:** if Java, DVC, the jar, or `dsm.bin` cannot be obtained, or `Sample.csv` does not classify, Task 1 is skipped. The R/Java repository is a second setup only when Git LFS, Java 8, and R are all available and the Python gate has failed. It is not a reason to run generic SentiStrength.

## Task 2 — one fine-tuned transformer purpose classifier

**Decision: proceed with cached `roberta-base`, fine-tuned. Do not start training in this step.**

Interpreter, versions, RAM, disk, and MPS rules are in the execution-environment section. CUDA is absent. Do not use the classification virtualenv.

Cached encoder with weights: `roberta-base` snapshot `e2da8e2f811d1448a5b465c236feacd80ffbac7b` (`model.safetensors`, tokenizer, and config are present). `distilbert-base-uncased` snapshot `12040accade4e8a0f71eabdb258fecc2e7e948be` is also cached. ModernBERT and DeBERTa are not cached.

RoBERTa-base is the selected model because it is a full transformer encoder, it is already on disk, and the question is purpose classification rather than another frozen sentiment score. DistilBERT is the only predeclared compute fallback, and only after the memory fallback below fails. DeBERTa and ModernBERT would add an uncached download and a heavier or less local run. Neither is required to answer whether a fine-tuned transformer beats the saved TF–IDF model on these folds.

**Fixed protocol, chosen before any score:**

- Data and folds: the same 2,050 rows and saved `fold` / `group_id`. Text is cleaned title, newline, cleaned body, as in `run_expanded.py`. Empty bodies stay empty.
- Architecture: `RobertaForSequenceClassification`, 2 labels, dropout left at the checkpoint default. The encoder is fine-tuned. This is not a frozen embedding plus a linear head.
- Optimization: AdamW, learning rate 2e-5, batch size 8, maximum length 256, seed 42, at most 3 epochs. Maximum length 256 is fixed because 188 of 2,050 contextual inputs already exceeded 512 tokens; 256 keeps the M3 run bounded. Record how many texts exceed 256 tokens. Do not raise the length after seeing scores.
- Inner control: on each outer training split, one `StratifiedGroupKFold` (3 splits, shuffle, seed 42). Inner fold 0 is the validation slice. Early stopping uses inner macro-F1 with patience 1. The outer labels are not used to pick the epoch.
- Threshold: the same 0.20–0.80 grid, chosen on inner validation probabilities only, with the existing tie breaks.
- Memory fallback, predeclared: if that fold runs out of memory, retry batch size 4 and gradient accumulation 2. If that also fails, stop and switch to cached DistilBERT with the same schedule. Do not try a third architecture.
- Time box: if one outer fold exceeds 45 minutes of training, stop, write the elapsed time, and do not continue to a protected test. Expected wall time for five folds on this M3 is on the order of one to three hours if MPS is used. That estimate was not measured by a training run.
- Comparison: out-of-fold macro-F1 minus 0.8319320360990539, group bootstrap against saved `pred_title_body`, 1,000 draws, seed 42. A lower score is reported. No post-hoc epoch, learning-rate, or threshold search on the outer predictions.

## Task 4 — expanded ablation

**Decision: proceed for three VADER arms. Do not rerun the whole sentiment suite.**

Already saved on these folds: title only 0.750534, body only 0.781424, title and body 0.831932, title and body plus VADER 0.833130. The augmented group interval includes zero.

The missing comparisons that change the scientific question are title plus VADER, and body plus VADER. They ask whether the compound stands in for the field that was removed. Title and body plus VADER is already answered; recompute it only as a reproduction check against 0.8331300906317138 and stop if the absolute gap exceeds 1e-9.

VADER for the title arm is the compound of the raw title only. VADER for the body arm is the compound of the raw body only. An empty body remains a compound of 0.0, which collides with neutral text; 303 bodies are empty (177 other-update, 126 troubleshooting). Do not feed title-and-body sentiment into a title-only or body-only arm. Same classifier, same inner thresholds, same group bootstrap versus title-and-body text. No held-out test.

Adding TextBlob or the contextual score to every input slice is not part of this step. Those tools already have a title-and-body result, and repeating them on slices would not separate a new claim.

## Task 5 — explainability

**Decision: proceed with training-fold TF–IDF coefficients. Do not use SHAP or LIME as the primary method. Do not treat the current coefficient file as fold-safe.**

`phase5/expanded_study/results/tfidf_coefficients.json` is one fit on all 2,050 rows. Its own note says the weights are associative and not a held-out result. Using it as the explanation would let every development post influence the displayed terms.

The model is class-balanced linear TF–IDF. The matching explanation is the logistic coefficient on features fit inside each outer training fold only, with the same vectorizer and `C=4`. For each of the five training folds, keep the 25 largest positive and 25 largest negative coefficients. A term is reported only when it appears in that list for at least four of the five training folds. The held-out fold is not used to rank or select terms. No new labels are created.

SHAP and LIME are a poor fit here: the feature space is up to 20,000 sparse n-grams, LIME is unstable on short posts, and either method can be pointed at the full development set by mistake. They are not a planned run.

The saved all-rows file may be quoted only as a sensitivity list, labeled as fit on all 2,050 rows, and kept separate from the four-fold agreement list.

## Runnable next step

Do not train and do not edit the manuscript until this protocol is accepted.

1. Task 1 gate only: install JDK 8+ and DVC, clone `pySenti4SD` outside the paper directory, `dvc pull -r origin`, verify `dsm.bin`, and classify `Sample.csv`. Write the pass or the blocker under `phase5/final_improvement/`. Score the 2,050 only after that pass, with the map and folds fixed above.
2. After that gate, or immediately if Task 1 is skipped, add one script under `phase5/final_improvement/` that reads only the 2,050 development files and runs, in order: VADER title and body reproduction check, title-plus-VADER, body-plus-VADER, fold-wise TF–IDF coefficients, then the RoBERTa fine-tune. Refuse to open reserved or fresh test paths.

## Checklist for this step

| Task | This step | Rationale |
| --- | --- | --- |
| 1 | Conditional proceed | pySenti4SD is MIT and SE-trained, but Java, DVC, and the 835 MB `dsm.bin` are not on this machine. Generic SentiStrength will not be used. |
| 2 | Proceed, not started | Cached RoBERTa-base can be fine-tuned on the saved folds with inner early stopping. MPS and 16 GB make it plausible. No training has been run. |
| 3 | Deferred | Manuscript story. Paper edits are forbidden in this step. |
| 4 | Proceed, not started | Title-plus-VADER and body-plus-VADER are the useful missing slices. Title-and-body plus VADER is already saved. |
| 5 | Proceed, not started | Fold-wise coefficients are leakage-safe. The all-rows coefficient file is not. |
| 6–10 | Deferred | Figure, future-work, and conclusion edits. Paper edits are forbidden in this step. |
