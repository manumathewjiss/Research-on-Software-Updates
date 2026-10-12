#!/usr/bin/env python3
"""Reddit-only development sensitivity check for the fixed experiment_v1 model.

Does not score the reserved or fresh tests and does not change historical files.
"""

from __future__ import annotations

import csv
import hashlib
import json
import subprocess
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

import numpy as np
from sklearn.metrics import f1_score
from sklearn.model_selection import StratifiedGroupKFold

ROOT = Path(__file__).resolve().parents[1]  # phase3
REPO = ROOT.parent
EXP = ROOT / "experiment_v1"
sys.path.insert(0, str(EXP))
sys.path.insert(0, str(EXP / "followup"))

from run_experiment import (  # noqa: E402
    build_lr,
    keyword_predict,
    make_text,
    metrics_bundle,
)
from run_followup import audit_within_dev  # noqa: E402

HERE = Path(__file__).resolve().parent
OUT = HERE / "results"
DEV_V2 = ROOT / "revised_development_v2" / "development_v2.jsonl"
MASTER = REPO / "phase2" / "combined_dataset" / "master_records.json"
SAVED_GROUPED = ROOT / "diagnostic_results" / "analysis.json"

THRESHOLD = 0.5877137791150834
C = 4.0
SEED = 42
N_FOLDS = 5
N_BOOT = 1000
NEAR_DUP_EXCLUSIONS = ("1t0wme9", "1wrqch6")
CODE_VERSION = "reddit-only-sensitivity-v1"


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def host_of(url: str) -> str:
    host = urlparse(url or "").netloc.lower()
    if host.startswith("www."):
        host = host[4:]
    return host


def is_reddit(host: str) -> bool:
    return host == "reddit.com" or host.endswith(".reddit.com")


def git_revision() -> str | None:
    try:
        out = subprocess.check_output(
            ["git", "rev-parse", "HEAD"],
            cwd=REPO,
            text=True,
            stderr=subprocess.DEVNULL,
        ).strip()
        return out or None
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None


def bootstrap_ci(y_true, y_pred, n_boot=N_BOOT, seed=SEED) -> dict:
    rng = np.random.default_rng(seed)
    y_true = np.asarray(y_true)
    y_pred = np.asarray(y_pred)
    n = len(y_true)

    def pack(a, b):
        return {
            "macro_f1": float(f1_score(a, b, average="macro", zero_division=0)),
            "other_f1": float(
                f1_score(a, b, pos_label=0, average="binary", zero_division=0)
            ),
            "troubleshooting_f1": float(
                f1_score(a, b, pos_label=1, average="binary", zero_division=0)
            ),
        }

    point = pack(y_true, y_pred)
    draws = {k: [] for k in point}
    for _ in range(n_boot):
        idx = rng.integers(0, n, n)
        sample = pack(y_true[idx], y_pred[idx])
        for k, v in sample.items():
            draws[k].append(v)
    out = {}
    for k, vals in draws.items():
        lo, hi = np.percentile(vals, [2.5, 97.5])
        out[k] = {"point": point[k], "ci95": [float(lo), float(hi)], "n_boot": n_boot}
    return out


def slim(m: dict) -> dict:
    return {
        "n": m["n"],
        "support": m["support"],
        "accuracy": m["accuracy"],
        "balanced_accuracy": m["balanced_accuracy"],
        "macro_f1": m["macro_f1"],
        "class_0_other_update": m["class_0_other_update"],
        "class_1_troubleshooting": m["class_1_troubleshooting"],
        "confusion_matrix_labels_[0,1]": m["confusion_matrix_labels_[0,1]"],
    }


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    master = json.loads(MASTER.read_text(encoding="utf-8"))
    by_id = {r["reddit_id"]: r for r in master}
    v2_rows = [
        json.loads(line)
        for line in DEV_V2.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]

    verified = []
    missing_url = []
    for row in v2_rows:
        src = by_id.get(row["reddit_id"])
        if not src or not src.get("url"):
            missing_url.append(row["reddit_id"])
            continue
        host = host_of(src["url"])
        item = dict(row)
        item["url"] = src["url"]
        item["verified_url_domain"] = host
        verified.append(item)
    if missing_url:
        raise SystemExit(f"Missing master URL for {len(missing_url)} IDs")

    non_reddit = [r for r in verified if not is_reddit(r["verified_url_domain"])]
    reddit_rows = [r for r in verified if is_reddit(r["verified_url_domain"])]
    so_prefix_mismatch = [
        r["reddit_id"]
        for r in verified
        if r["reddit_id"].startswith("so_") and is_reddit(r["verified_url_domain"])
    ]
    stack_without_prefix = [
        r["reddit_id"]
        for r in non_reddit
        if not r["reddit_id"].startswith("so_")
    ]
    if so_prefix_mismatch or stack_without_prefix:
        raise SystemExit(
            "Domain/prefix mismatch: "
            f"so_ but reddit={so_prefix_mismatch}; non-reddit without so_={stack_without_prefix}"
        )
    if len(non_reddit) != 30:
        raise SystemExit(f"Expected 30 non-Reddit rows, found {len(non_reddit)}")

    # Full Reddit snapshot: drop non-Reddit only. Near-dup IDs stay in the file
    # and are excluded from the S2 modeling population, matching v2.
    snapshot_path = HERE / "development_reddit_only.jsonl"
    payload = "".join(json.dumps(r, ensure_ascii=False) + "\n" for r in reddit_rows)
    snapshot_path.write_text(payload, encoding="utf-8")

    audit_rows = []
    for r in non_reddit:
        audit_rows.append(
            {
                "reddit_id": r["reddit_id"],
                "url": r["url"],
                "verified_url_domain": r["verified_url_domain"],
                "source_pool_audit_only": r.get("source_pool_audit_only"),
                "s2_in_scope": r.get("s2_in_scope"),
                "s2_target": r.get("s2_target"),
                "discussion_type": r.get("discussion_type"),
                "id_prefix_so": r["reddit_id"].startswith("so_"),
            }
        )
    with (OUT / "excluded_non_reddit.csv").open("w", encoding="utf-8", newline="") as f:
        fields = list(audit_rows[0].keys())
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(audit_rows)

    def s2_pop(rows: list[dict]) -> list[dict]:
        return [
            r
            for r in rows
            if r.get("s2_in_scope")
            and r.get("s2_target") in (0, 1)
            and r["reddit_id"] not in NEAR_DUP_EXCLUSIONS
        ]

    v2_s2 = s2_pop(verified)
    reddit_s2 = s2_pop(reddit_rows)
    assert len(v2_s2) == 2080
    assert all(r["reddit_id"].startswith("so_") for r in non_reddit)
    assert all(r.get("s2_in_scope") for r in non_reddit)

    texts = [make_text(r, "title_body") for r in reddit_s2]
    y = np.array([int(r["s2_target"]) for r in reddit_s2], dtype=int)
    _, groups = audit_within_dev(reddit_s2)
    # audit_within_dev groups by index order of the list passed in
    splitter = StratifiedGroupKFold(n_splits=N_FOLDS, shuffle=True, random_state=SEED)
    n = len(reddit_s2)
    pred_lr = np.zeros(n, dtype=int)
    scores_lr = np.full(n, np.nan)
    pred_maj = np.zeros(n, dtype=int)
    pred_kw = np.zeros(n, dtype=int)
    fold_ids = np.full(n, -1, dtype=int)

    for fold, (train_idx, test_idx) in enumerate(splitter.split(np.zeros(n), y, groups)):
        y_tr = y[train_idx]
        maj = int(Counter(y_tr.tolist()).most_common(1)[0][0])
        pred_maj[test_idx] = maj
        pred_kw[test_idx] = keyword_predict([texts[i] for i in test_idx])
        pipe = build_lr(C)
        pipe.fit([texts[i] for i in train_idx], y_tr)
        sc = pipe.predict_proba([texts[i] for i in test_idx])[:, 1]
        scores_lr[test_idx] = sc
        pred_lr[test_idx] = (sc >= THRESHOLD).astype(int)
        fold_ids[test_idx] = fold

    assert np.isfinite(scores_lr).all() and (fold_ids >= 0).all()

    metrics_lr = metrics_bundle(y, pred_lr, scores_lr)
    metrics_maj = metrics_bundle(y, pred_maj)
    metrics_kw = metrics_bundle(y, pred_kw)
    ci = bootstrap_ci(y, pred_lr)

    def by_field(field: str) -> dict:
        out = {}
        keys = sorted({r.get(field) or "unknown" for r in reddit_s2})
        for key in keys:
            idx = [i for i, r in enumerate(reddit_s2) if (r.get(field) or "unknown") == key]
            if not idx:
                continue
            out[key] = slim(metrics_bundle(y[idx], pred_lr[idx]))
        return out

    saved = json.loads(SAVED_GROUPED.read_text(encoding="utf-8"))
    saved_metrics = saved["grouped_development_oof"]["metrics"]

    multi = Counter(groups.tolist())
    n_multi_groups = sum(1 for c in multi.values() if c > 1)
    n_multi_posts = sum(c for c in multi.values() if c > 1)

    class_counts = Counter(int(r["s2_target"]) for r in reddit_s2)
    source_counts = Counter(r.get("source_pool_audit_only") for r in reddit_s2)
    domain_counts = Counter(r["verified_url_domain"] for r in verified)

    flow = [
        {
            "stage": "revised_development_v2 all rows",
            "n_rows": len(verified),
            "reddit": sum(1 for r in verified if is_reddit(r["verified_url_domain"])),
            "non_reddit": len(non_reddit),
            "s2_modeling_n": len(v2_s2),
            "s2_troubleshooting_1": sum(int(r["s2_target"]) == 1 for r in v2_s2),
            "s2_other_update_0": sum(int(r["s2_target"]) == 0 for r in v2_s2),
        },
        {
            "stage": "reddit-only snapshot all rows",
            "n_rows": len(reddit_rows),
            "reddit": len(reddit_rows),
            "non_reddit": 0,
            "s2_modeling_n": len(reddit_s2),
            "s2_troubleshooting_1": class_counts[1],
            "s2_other_update_0": class_counts[0],
        },
    ]

    manifest = {
        "code_version": CODE_VERSION,
        "script": str(Path(__file__).resolve()),
        "git_head": git_revision(),
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "inputs": {
            "development_v2": str(DEV_V2),
            "development_v2_sha256": sha256_file(DEV_V2),
            "phase2_master": str(MASTER),
            "phase2_master_sha256": sha256_file(MASTER),
            "saved_grouped_reference": str(SAVED_GROUPED),
            "saved_grouped_reference_sha256": sha256_file(SAVED_GROUPED),
        },
        "outputs": {
            "development_reddit_only": str(snapshot_path),
            "development_reddit_only_sha256": sha256_bytes(payload.encode("utf-8")),
        },
        "domain_verification": {
            "method": "Join revised development reddit_id to phase2 master url; host from URL, not ID prefix",
            "domain_counts_in_v2": dict(domain_counts),
            "non_reddit_n": len(non_reddit),
            "all_non_reddit_ids_start_with_so_": True,
            "non_reddit_without_so_prefix": stack_without_prefix,
            "so_prefix_with_reddit_domain": so_prefix_mismatch,
            "non_reddit_ids": [r["reddit_id"] for r in non_reddit],
            "non_reddit_s2_class_counts": dict(Counter(str(r["s2_target"]) for r in non_reddit)),
            "non_reddit_source_counts": dict(
                Counter(r.get("source_pool_audit_only") for r in non_reddit)
            ),
        },
        "exclusions_applied": {
            "non_reddit_domains": sorted({r["verified_url_domain"] for r in non_reddit}),
            "near_duplicate_ids_excluded_from_s2_modeling_only": list(NEAR_DUP_EXCLUSIONS),
            "note": (
                "Uncertain-review IDs were already absent from revised development v2. "
                "Near-duplicate IDs remain in the Reddit snapshot file and are excluded "
                "only from the S2 modeling population, matching the v2 modeling rule."
            ),
        },
        "population": {
            "snapshot_rows": len(reddit_rows),
            "s2_modeling_n": len(reddit_s2),
            "s2_class_counts": {"troubleshooting_1": class_counts[1], "other_update_0": class_counts[0]},
            "s2_source_counts": dict(source_counts),
            "snapshot_source_counts": dict(
                Counter(r.get("source_pool_audit_only") for r in reddit_rows)
            ),
        },
        "model": {
            "text": "title_body",
            "estimator": "TfidfVectorizer word 1-2 grams + LogisticRegression",
            "C": C,
            "threshold": THRESHOLD,
            "class_weight": "balanced",
            "folds": "StratifiedGroupKFold n_splits=5 shuffle random_state=42",
            "grouping": "exact normalized title+body union Jaccard char-5gram >= 0.92 (run_followup.audit_within_dev)",
            "vectorizer_fit": "inside each training fold only",
            "keyword_baseline": "run_experiment.TROUBLE_RE / keyword_predict",
            "settings_not_retuned": True,
            "reserved_test_used": False,
            "fresh_test_used": False,
        },
        "grouping_on_reddit_s2": {
            "n_multi_post_groups": n_multi_groups,
            "n_posts_in_multi_post_groups": n_multi_posts,
        },
        "dataset_flow": flow,
    }
    (HERE / "MANIFEST.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )

    report = {
        "comparison_note": (
            "The saved grouped development score is on revised development v2 "
            "(mixed Reddit + 30 Stack Overflow; n=2080). This run drops those 30 "
            "and rebuilds duplicate groups, so folds differ. The delta is a "
            "population-and-fold change, not a same-split improvement."
        ),
        "saved_mixed_v2_grouped_oof": slim(saved_metrics),
        "reddit_only_grouped_oof": {
            "tfidf_lr": {**slim(metrics_lr), "bootstrap_ci95": ci},
            "majority": slim(metrics_maj),
            "keyword": slim(metrics_kw),
            "by_source_pool": by_field("source_pool_audit_only"),
            "by_text_availability": by_field("text_availability"),
        },
        "delta_macro_f1_reddit_only_minus_saved_mixed": round(
            metrics_lr["macro_f1"] - saved_metrics["macro_f1"], 6
        ),
    }
    (OUT / "grouped_validation.json").write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8"
    )
    with (OUT / "grouped_oof_predictions.jsonl").open("w", encoding="utf-8") as f:
        for i, r in enumerate(reddit_s2):
            f.write(
                json.dumps(
                    {
                        "reddit_id": r["reddit_id"],
                        "y_true": int(y[i]),
                        "y_pred_tfidf_lr": int(pred_lr[i]),
                        "score_tfidf_lr": float(scores_lr[i]),
                        "y_pred_majority": int(pred_maj[i]),
                        "y_pred_keyword": int(pred_kw[i]),
                        "fold": int(fold_ids[i]),
                        "group_id": int(groups[i]),
                        "source_pool_audit_only": r.get("source_pool_audit_only"),
                        "text_availability": r.get("text_availability"),
                        "verified_url_domain": r["verified_url_domain"],
                    },
                    ensure_ascii=False,
                )
                + "\n"
            )

    write_results_md(manifest, report, audit_rows)
    print(
        json.dumps(
            {
                "snapshot_rows": len(reddit_rows),
                "s2_n": len(reddit_s2),
                "class": dict(class_counts),
                "macro_f1": metrics_lr["macro_f1"],
                "saved_mixed_macro_f1": saved_metrics["macro_f1"],
                "delta": report["delta_macro_f1_reddit_only_minus_saved_mixed"],
            },
            indent=2,
        )
    )
    return 0


def write_results_md(manifest: dict, report: dict, audit_rows: list[dict]) -> None:
    lr = report["reddit_only_grouped_oof"]["tfidf_lr"]
    maj = report["reddit_only_grouped_oof"]["majority"]
    kw = report["reddit_only_grouped_oof"]["keyword"]
    saved = report["saved_mixed_v2_grouped_oof"]
    pop = manifest["population"]
    lines = [
        "# Reddit-only development sensitivity",
        "",
        f"**Created:** {manifest['created_utc']}",
        f"**Code version:** `{manifest['code_version']}`",
        "",
        "Historical datasets, labels, and prior scores were not modified. "
        "The reserved 159-post test and the fresh 344-post test were not scored or used to choose settings.",
        "",
        "## Domain verification",
        "",
        "Every revised-development ID was joined to `phase2/combined_dataset/master_records.json` and the URL host was read directly. "
        "ID prefixes were checked afterward, not used as the inclusion rule.",
        "",
        f"- Revised development v2 rows: **{manifest['dataset_flow'][0]['n_rows']}**",
        f"- `reddit.com`: **{manifest['domain_verification']['domain_counts_in_v2'].get('reddit.com', 0)}**",
        f"- `stackoverflow.com`: **{manifest['domain_verification']['domain_counts_in_v2'].get('stackoverflow.com', 0)}**",
        "- All 30 non-Reddit IDs start with `so_`. No `so_` ID has a Reddit URL, and no Reddit URL lacks a non-`so_` ID among the non-Reddit set.",
        "- All 30 are S2. Class counts: "
        + json.dumps(manifest["domain_verification"]["non_reddit_s2_class_counts"])
        + ". Source pools: "
        + json.dumps(manifest["domain_verification"]["non_reddit_source_counts"])
        + ".",
        "",
        "Row-level list: `results/excluded_non_reddit.csv`.",
        "",
        "## Dataset flow",
        "",
        "| Stage | All rows | Reddit URLs | Non-Reddit URLs | S2 modeling n | Troubleshooting (1) | Other update (0) |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for stage in manifest["dataset_flow"]:
        lines.append(
            f"| {stage['stage']} | {stage['n_rows']} | {stage['reddit']} | {stage['non_reddit']} | "
            f"{stage['s2_modeling_n']} | {stage['s2_troubleshooting_1']} | {stage['s2_other_update_0']} |"
        )
    lines.extend(
        [
            "",
            "S2 modeling drops the already documented near-duplicate development IDs "
            "`1t0wme9` and `1wrqch6` (both Reddit; kept in the snapshot file, excluded from fitting). "
            "The four uncertain-review IDs are already absent from revised development v2.",
            "",
            "## Fixed model (not retuned)",
            "",
            "- Title + body, TF-IDF word unigrams and bigrams, logistic regression `C=4`, class-balanced.",
            f"- Decision threshold `{THRESHOLD}` from the original saved selection.",
            "- Five `StratifiedGroupKFold` folds, `random_state=42`. Exact text and Jaccard ≥ 0.92 near-duplicates stay in one fold. Vectorizer fit only on each fold’s training posts.",
            "- Same folds for majority and the fixed keyword baseline in `run_experiment.py`.",
            "",
            f"Reddit-only duplicate grouping: **{manifest['grouping_on_reddit_s2']['n_multi_post_groups']}** multi-post groups "
            f"({manifest['grouping_on_reddit_s2']['n_posts_in_multi_post_groups']} posts).",
            "",
            "## Scores",
            "",
            "Saved reference is grouped out-of-fold evaluation on **mixed** revised development v2 "
            f"(n={saved['n']}: {saved['support']['troubleshooting_1']} troubleshooting, "
            f"{saved['support']['other_update_0']} other update), from `diagnostic_results/analysis.json`. "
            "That run includes the 30 Stack Overflow posts and built groups on that larger set, so folds are not identical.",
            "",
            "| Evaluation | n | macro-F1 | other P/R/F1 | trouble P/R/F1 | balanced acc. | confusion [[0,1]] |",
            "|---|---:|---:|---|---|---:|---|",
        ]
    )

    def row(name, m):
        c0, c1 = m["class_0_other_update"], m["class_1_troubleshooting"]
        return (
            f"| {name} | {m['n']} | {m['macro_f1']:.4f} | "
            f"{c0['precision']:.3f}/{c0['recall']:.3f}/{c0['f1']:.3f} | "
            f"{c1['precision']:.3f}/{c1['recall']:.3f}/{c1['f1']:.3f} | "
            f"{m['balanced_accuracy']:.4f} | `{m['confusion_matrix_labels_[0,1]']}` |"
        )

    lines.append(row("Saved mixed v2 grouped TF-IDF LR", saved))
    lines.append(row("Reddit-only grouped TF-IDF LR", lr))
    lines.append(row("Reddit-only grouped majority", maj))
    lines.append(row("Reddit-only grouped keyword", kw))
    boot = lr["bootstrap_ci95"]
    lines.extend(
        [
            "",
            f"**Delta macro-F1 (Reddit-only − saved mixed):** {report['delta_macro_f1_reddit_only_minus_saved_mixed']:+.4f}.",
            "",
            "Bootstrap 95% intervals on the Reddit-only TF-IDF predictions "
            f"({N_BOOT} resamples of the out-of-fold pairs, seed {SEED}):",
            "",
            f"- macro-F1 {boot['macro_f1']['point']:.4f} ({boot['macro_f1']['ci95'][0]:.4f}–{boot['macro_f1']['ci95'][1]:.4f})",
            f"- other-update F1 {boot['other_f1']['point']:.4f} ({boot['other_f1']['ci95'][0]:.4f}–{boot['other_f1']['ci95'][1]:.4f})",
            f"- troubleshooting F1 {boot['troubleshooting_f1']['point']:.4f} ({boot['troubleshooting_f1']['ci95'][0]:.4f}–{boot['troubleshooting_f1']['ci95'][1]:.4f})",
            "",
            "These intervals describe resampling of this development check. They are not a new test-set interval.",
            "",
            "## Interpretation",
            "",
            "Removing the 30 Stack Overflow posts changes the development population and the duplicate groups, so this score is not a revision of the saved mixed-corpus number. "
            f"The Reddit-only grouped macro-F1 is {lr['macro_f1']:.3f} versus {saved['macro_f1']:.3f} on the mixed v2 set. "
            "The shift is small relative to the bootstrap interval, and the TF-IDF model still beats the majority and keyword baselines on the same Reddit-only folds. "
            "A claim that post text separates troubleshooting from other update discussion **within this reviewed Reddit S2 development set** remains supported.",
            "",
            "What does not become stronger: the historical reserved-test and fresh-test scores were fit with Stack Overflow posts still in development, so they are mixed-corpus results. "
            "This check does not replace them. The other-update class is still the harder class, and source pool remains entangled with class mix. "
            "Thirty excluded posts are too few, and too class-imbalanced (28 troubleshooting, 2 other), to support a separate Stack Overflow performance claim.",
            "",
            "## Reproduce",
            "",
            "```bash",
            "phase3/experiment_v1/.venv/bin/python phase3/reddit_only_sensitivity/run_reddit_only_sensitivity.py",
            "```",
            "",
            "Run from the research repository root. Inputs and output hashes are in `MANIFEST.json`.",
            "",
        ]
    )
    (HERE / "RESULTS.md").write_text("\n".join(lines), encoding="utf-8")
    (HERE / "RUN.md").write_text(
        "\n".join(
            [
                "# Reproduce the Reddit-only sensitivity check",
                "",
                "From `/Users/manumathewjiss/Documents/Research-on-Software-Updates/research-open-text-sentimental/`:",
                "",
                "```bash",
                "phase3/experiment_v1/.venv/bin/python phase3/reddit_only_sensitivity/run_reddit_only_sensitivity.py",
                "```",
                "",
                "Requires the existing experiment_v1 virtualenv (`scikit-learn`, `numpy`).",
                "Does not read reserved-test or fresh-test predictions and does not edit prior Phase 3 artifacts.",
                "",
                f"Code version recorded in the manifest: `{CODE_VERSION}`.",
                "",
            ]
        ),
        encoding="utf-8",
    )


if __name__ == "__main__":
    raise SystemExit(main())
