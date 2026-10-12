#!/usr/bin/env python3
"""Fine-tune RoBERTa on the frozen 2,050 development folds.

Smoke mode trains outer fold 0 only. Full mode is --all-folds.
Does not read the reserved 159 or fresh 344 tests.
"""

from __future__ import annotations

import argparse
import json
import random
import shutil
import sys
import time
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
sys.path.insert(0, str(REPO / "phase5" / "expanded_study"))

import run_expanded as ex  # noqa: E402

OUT = HERE / "results"
SAVED = REPO / "phase5" / "expanded_study" / "results" / "predictions.jsonl"
ROBERTA = Path.home() / ".cache/huggingface/hub/models--roberta-base/snapshots/e2da8e2f811d1448a5b465c236feacd80ffbac7b"
REVISION = "e2da8e2f811d1448a5b465c236feacd80ffbac7b"
SEED = 42
MAX_LENGTH = 256
MAX_EPOCHS = 3
LR = 2e-5
WEIGHT_DECAY = 0.0
BATCH = 8
FOLD_SECONDS = 45 * 60
MIN_FREE_BYTES = 4 * (1024 ** 3)
FORBIDDEN = ("reserved_test", "s2_test_344", "fresh_test")


def refuse_protected(path: Path) -> None:
    text = str(path)
    if any(token in text for token in FORBIDDEN):
        raise SystemExit(f"refusing protected path {path}")


def free_bytes() -> int:
    return int(shutil.disk_usage(HERE).free)


def set_seed(seed: int) -> None:
    random.seed(seed)
    np.random.seed(seed)
    import torch
    torch.manual_seed(seed)


def device_name() -> str:
    import torch
    if torch.backends.mps.is_available():
        return "mps"
    return "cpu"


def token_lengths(tokenizer, texts: list[str]) -> int:
    encoded = tokenizer(texts, add_special_tokens=True, truncation=False, padding=False)
    return int(sum(len(ids) > MAX_LENGTH for ids in encoded["input_ids"]))


def encode(tokenizer, texts: list[str]):
    import torch
    batch = tokenizer(
        texts,
        truncation=True,
        max_length=MAX_LENGTH,
        padding=True,
        return_tensors="pt",
    )
    return batch["input_ids"], batch["attention_mask"]


def predict_proba(model, input_ids, attention, index, device, batch_size: int) -> np.ndarray:
    import torch
    model.eval()
    out = np.empty(len(index), dtype=float)
    with torch.no_grad():
        for start in range(0, len(index), batch_size):
            part = index[start:start + batch_size]
            ids = input_ids[part].to(device)
            mask = attention[part].to(device)
            logits = model(input_ids=ids, attention_mask=mask).logits
            prob = torch.softmax(logits, dim=-1)[:, 1]
            out[start:start + len(part)] = prob.detach().cpu().numpy()
    return out


def train_epoch(model, input_ids, attention, y, index, device, batch_size: int, accum: int, opt) -> None:
    import torch
    model.train()
    order = np.array(index, copy=True)
    rng = np.random.default_rng(SEED)
    rng.shuffle(order)
    opt.zero_grad(set_to_none=True)
    step = 0
    for start in range(0, len(order), batch_size):
        part = order[start:start + batch_size]
        ids = input_ids[part].to(device)
        mask = attention[part].to(device)
        labels = torch.tensor(y[part], dtype=torch.long, device=device)
        loss = model(input_ids=ids, attention_mask=mask, labels=labels).loss
        (loss / accum).backward()
        step += 1
        if step % accum == 0:
            opt.step()
            opt.zero_grad(set_to_none=True)
    if step % accum != 0:
        opt.step()
        opt.zero_grad(set_to_none=True)


def load_model(device: str):
    from transformers import RobertaForSequenceClassification
    model = RobertaForSequenceClassification.from_pretrained(
        ROBERTA, num_labels=2, local_files_only=True
    )
    model.to(device)
    return model


def one_fold(input_ids, attention, y, groups, folds, fold, device, batch_size, accum, deadline):
    import torch
    from torch.optim import AdamW
    from sklearn.metrics import f1_score
    from sklearn.model_selection import StratifiedGroupKFold

    outer_test = np.flatnonzero(folds == fold)
    outer_train = np.flatnonzero(folds != fold)
    y_tr = y[outer_train]
    g_tr = groups[outer_train]
    splitter = StratifiedGroupKFold(n_splits=3, shuffle=True, random_state=SEED)
    fit_rel, val_rel = next(splitter.split(np.zeros(len(outer_train)), y_tr, g_tr))
    fit_idx = outer_train[fit_rel]
    val_idx = outer_train[val_rel]
    set_seed(SEED)
    model = load_model(device)
    opt = AdamW(model.parameters(), lr=LR, weight_decay=WEIGHT_DECAY)
    best_f1 = -1.0
    best_val_proba = None
    epochs_run = 0
    selected_epochs = 0
    stale = 0
    for _epoch in range(MAX_EPOCHS):
        if time.perf_counter() > deadline:
            raise TimeoutError(f"fold {fold} exceeded {FOLD_SECONDS} seconds")
        train_epoch(model, input_ids, attention, y, fit_idx, device, batch_size, accum, opt)
        epochs_run += 1
        val_proba = predict_proba(model, input_ids, attention, val_idx, device, batch_size)
        val_f1 = float(f1_score(y[val_idx], (val_proba >= 0.5).astype(int), average="macro", zero_division=0))
        if val_f1 > best_f1:
            best_f1 = val_f1
            best_val_proba = val_proba.copy()
            selected_epochs = epochs_run
            stale = 0
        else:
            stale += 1
            if stale >= 1:
                break
    threshold = ex.choose_threshold([(y[val_idx], best_val_proba)])
    del model, opt, best_val_proba
    if device == "mps":
        torch.mps.empty_cache()
    set_seed(SEED)
    model = load_model(device)
    opt = AdamW(model.parameters(), lr=LR, weight_decay=WEIGHT_DECAY)
    for _epoch in range(selected_epochs):
        if time.perf_counter() > deadline:
            raise TimeoutError(f"fold {fold} exceeded {FOLD_SECONDS} seconds")
        train_epoch(model, input_ids, attention, y, outer_train, device, batch_size, accum, opt)
    test_proba = predict_proba(model, input_ids, attention, outer_test, device, batch_size)
    pred = (test_proba >= threshold).astype(int)
    del model, opt
    if device == "mps":
        torch.mps.empty_cache()
    return {
        "fold": int(fold),
        "model": "roberta-base",
        "revision": REVISION,
        "source": str(ROBERTA),
        "threshold": float(threshold),
        "inner_macro_f1_at_0.5": best_f1,
        "epochs_selected": selected_epochs,
        "epochs_run_for_selection": epochs_run,
        "n_inner_fit": int(len(fit_idx)),
        "n_outer_train": int(len(outer_train)),
        "n_inner_val": int(len(val_idx)),
        "n_outer_test": int(len(outer_test)),
        "batch_size": batch_size,
        "grad_accum": accum,
        "index": outer_test,
        "pred": pred,
        "proba": test_proba,
    }


def run_fold(input_ids, attention, y, groups, folds, fold, device, deadline):
    """RoBERTa only. One memory retry, then stop. No second architecture."""
    if free_bytes() < MIN_FREE_BYTES:
        raise SystemExit(f"free disk below 4 GB before fold {fold}")
    attempts = ((BATCH, 1), (4, 2))
    last_error = None
    for batch_size, accum in attempts:
        try:
            return one_fold(
                input_ids, attention, y, groups, folds, fold, device,
                batch_size, accum, deadline,
            )
        except RuntimeError as exc:
            if "out of memory" not in str(exc).lower():
                raise
            last_error = str(exc)
            print(f"oom fold {fold} roberta batch {batch_size} accum {accum}", flush=True)
            if device == "mps":
                import torch
                torch.mps.empty_cache()
        except TimeoutError:
            raise
    raise MemoryError(f"fold {fold} stopped after RoBERTa batch-4 retry: {last_error}")


def main() -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--smoke", action="store_true", help="Train outer fold 0 only.")
    mode.add_argument("--all-folds", action="store_true", help="Train all five saved outer folds.")
    parser.add_argument("--resume-smoke", action="store_true", help="For --all-folds, reuse the validated fold-0 smoke outputs.")
    args = parser.parse_args()
    if args.resume_smoke and not args.all_folds:
        parser.error("--resume-smoke requires --all-folds")
    refuse_protected(ex.REDDIT_DEV)
    refuse_protected(ex.REDDIT_OOF)
    refuse_protected(SAVED)
    if not (ROBERTA / "model.safetensors").is_file():
        raise SystemExit(f"missing RoBERTa snapshot {ROBERTA}")
    rows, y, folds, groups, population = ex.load_population()
    saved = {r["reddit_id"]: int(r["pred_title_body"]) for r in ex.read_jsonl(SAVED)}
    texts = [ex.input_text(r, "title_body") for r in rows]
    from transformers import AutoTokenizer
    tokenizer = AutoTokenizer.from_pretrained(ROBERTA, local_files_only=True)
    n_over = token_lengths(tokenizer, texts)
    input_ids, attention = encode(tokenizer, texts)
    dev = device_name()
    set_seed(SEED)
    config = {
        "seed": SEED,
        "learning_rate": LR,
        "weight_decay": WEIGHT_DECAY,
        "batch_size": BATCH,
        "max_length": MAX_LENGTH,
        "max_epochs": MAX_EPOCHS,
        "early_stopping": "inner macro-F1 at probability 0.5, patience 1, selects epoch count only",
        "refit": "fresh RoBERTa trained for the selected epoch count on all outer-training rows",
        "threshold": "grid 0.20-0.80 step 0.05 on inner validation probabilities only",
        "revision": REVISION,
        "memory_retry": "same RoBERTa, batch 4, gradient accumulation 2; stop if that fails",
        "device": dev,
        "n_texts_over_256_tokens": n_over,
        "population": population,
        "mode": "smoke" if args.smoke else "all-folds",
        "protected_tests_opened": False,
    }
    OUT.mkdir(parents=True, exist_ok=True)
    ex.write_json(OUT / "task2_config.json", config)
    fold_ids = [0] if args.smoke else [0, 1, 2, 3, 4]
    records = []
    pred = np.full(len(y), -1, dtype=int)
    proba = np.full(len(y), np.nan)
    if args.resume_smoke:
        smoke = json.loads((OUT / "task2_summary.json").read_text())
        smoke_rows = ex.read_jsonl(OUT / "smoke_fold0_predictions.jsonl")
        if smoke.get("n_predicted") != 410 or len(smoke_rows) != 410 or len(smoke.get("folds", [])) != 1:
            raise SystemExit("fold-0 smoke record incomplete")
        records = smoke["folds"]
        index_by_id = {r["reddit_id"]: i for i, r in enumerate(rows)}
        for rec in smoke_rows:
            i = index_by_id[rec["reddit_id"]]
            if int(folds[i]) != 0 or int(y[i]) != rec["y_true"] or int(groups[i]) != rec["group_id"] or saved[rec["reddit_id"]] != rec["pred_title_body"] or pred[i] != -1:
                raise SystemExit(f"fold-0 smoke mismatch for {rec['reddit_id']}")
            pred[i] = int(rec["pred_roberta"])
            proba[i] = float(rec["score_roberta"])
        if not np.all(pred[folds == 0] >= 0):
            raise SystemExit("fold-0 smoke misses saved fold members")
        fold_ids = [1, 2, 3, 4]
    for fold in fold_ids:
        started = time.perf_counter()
        try:
            rec = run_fold(
                input_ids, attention, y, groups, folds, fold, dev, started + FOLD_SECONDS
            )
        except (TimeoutError, MemoryError) as exc:
            ex.write_json(OUT / "task2_stop.json", {
                "fold": fold,
                "reason": type(exc).__name__,
                "seconds": time.perf_counter() - started,
                "message": str(exc),
                "protected_tests_opened": False,
            })
            print(str(exc), flush=True)
            return 2
        rec["seconds"] = time.perf_counter() - started
        idx = rec.pop("index")
        pred[idx] = rec.pop("pred")
        proba[idx] = rec.pop("proba")
        records.append(rec)
        progress_rows = [{
            "reddit_id": rows[i]["reddit_id"], "fold": int(folds[i]),
            "group_id": int(groups[i]), "y_true": int(y[i]),
            "pred_roberta": int(pred[i]), "score_roberta": float(proba[i]),
            "pred_title_body": saved[rows[i]["reddit_id"]],
        } for i in range(len(y)) if pred[i] >= 0]
        ex.write_jsonl(OUT / "task2_progress_predictions.jsonl", progress_rows)
        ex.write_json(OUT / "task2_progress.json", {
            "folds": records, "n_predicted": len(progress_rows),
            "protected_tests_opened": False,
        })
        print(
            f"fold {fold} epochs {rec['epochs_selected']} "
            f"inner_fit {rec['n_inner_fit']} outer_train {rec['n_outer_train']} "
            f"threshold {rec['threshold']}",
            flush=True,
        )
    done = pred >= 0
    rows_out = []
    for i, row in enumerate(rows):
        if not done[i]:
            continue
        rows_out.append({
            "reddit_id": row["reddit_id"],
            "fold": int(folds[i]),
            "group_id": int(groups[i]),
            "y_true": int(y[i]),
            "pred_roberta": int(pred[i]),
            "score_roberta": float(proba[i]),
            "pred_title_body": saved[row["reddit_id"]],
        })
    name = "smoke_fold0_predictions.jsonl" if args.smoke else "roberta_predictions.jsonl"
    ex.write_jsonl(OUT / name, rows_out)
    summary = {"folds": records, "n_predicted": int(done.sum()), "protected_tests_opened": False}
    if args.all_folds and bool(done.all()):
        from sklearn.metrics import f1_score
        base = np.array([saved[r["reddit_id"]] for r in rows])
        summary["macro_f1"] = float(f1_score(y, pred, average="macro", zero_division=0))
        summary["group_bootstrap_minus_pred_title_body"] = group_interval(y, base, pred, groups)
    ex.write_json(OUT / "task2_summary.json", summary)
    print(json.dumps({"n_predicted": int(done.sum()), "over_256": n_over, "device": dev}), flush=True)
    return 0


def group_interval(y, base, other, groups) -> dict:
    from sklearn.metrics import f1_score
    rng = np.random.default_rng(SEED)
    uniq = np.unique(groups)
    members = {int(g): np.flatnonzero(groups == g) for g in uniq}

    def macro(idx, pred):
        return float(f1_score(y[idx], pred[idx], average="macro", zero_division=0))

    point = macro(np.arange(len(y)), other) - macro(np.arange(len(y)), base)
    draws = np.empty(1000, dtype=float)
    for i in range(1000):
        chosen = rng.choice(uniq, size=len(uniq), replace=True)
        idx = np.concatenate([members[int(g)] for g in chosen])
        draws[i] = macro(idx, other) - macro(idx, base)
    lo, hi = np.percentile(draws, [2.5, 97.5])
    return {
        "point_delta_macro_f1": float(point),
        "ci95": [float(lo), float(hi)],
        "includes_zero": bool(lo <= 0 <= hi),
        "n_boot": 1000,
        "seed": SEED,
    }


if __name__ == "__main__":
    raise SystemExit(main())
