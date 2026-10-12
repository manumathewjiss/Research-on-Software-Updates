#!/usr/bin/env python3
"""Prepare all untouched posts and six unresolved cases for final review."""

from __future__ import annotations

import csv
import hashlib
import json
import random
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline
import sklearn

from build_provisional_500 import MASTER, ROOT, model_text, propose

OUT = ROOT / "phase2/annotation/final_remaining_768"
SEED = 20261009
QUOTAS = {"oct5_query_tps": 762}
BATCH_ALLOCATIONS = [(100,)] * 7 + [(62,)]
FIELDS = ("about_software", "update_related", "discussion_type")


def fit_model(rows: list[dict], field: str, *, char: bool):
    vectorizer = (TfidfVectorizer(analyzer="char", ngram_range=(3, 5), min_df=2,
                                  max_features=50000) if char else
                  TfidfVectorizer(ngram_range=(1, 2), min_df=2,
                                  max_features=30000, sublinear_tf=True))
    model = make_pipeline(vectorizer, LogisticRegression(max_iter=1000,
                                                         class_weight="balanced"))
    model.fit([model_text(r) for r in rows], [r["phase2_" + field] for r in rows])
    return model


def main() -> None:
    master = json.loads(MASTER.read_text(encoding="utf-8"))
    development = [r for r in master if r["phase2_review_status"] in
                   {"pilot_post_discussion", "joint_review", "manu_assisted_review"}]
    if len(development) != 2394:
        raise ValueError(f"Expected 2394 non-test development labels, found {len(development)}")
    available = [r for r in master if r["phase2_review_status"] == "needs_phase2_review"]
    unresolved = [r for r in master if r["phase2_review_status"] == "manu_assisted_uncertain"]
    reserved = {r["reddit_id"] for r in master if r["phase2_review_status"] == "reserved_test_consensus"}
    if len(available) != 762 or len(unresolved) != 6 or len(reserved) != 200:
        raise ValueError("Unexpected master review-status counts")

    rng = random.Random(SEED)
    chosen = {}
    for pool, quota in QUOTAS.items():
        population = sorted((r for r in available if r["source_pool"] == pool),
                            key=lambda r: r["reddit_id"])
        if len(population) < quota:
            raise ValueError(f"Insufficient posts in {pool}: {len(population)}")
        chosen[pool] = rng.sample(population, quota)
        rng.shuffle(chosen[pool])
    indices = {pool: 0 for pool in QUOTAS}
    selected = []
    pools = list(QUOTAS)
    for offset, allocation in enumerate(BATCH_ALLOCATIONS):
        batch_no = offset + 21
        block = []
        for pool, count in zip(pools, allocation):
            start = indices[pool]
            block += chosen[pool][start:start + count]
            indices[pool] += count
        if len(block) != sum(allocation):
            raise ValueError(f"Bad allocation for batch {batch_no}")
        rng.shuffle(block)
        for position, record in enumerate(block, 1):
            selected.append((batch_no, f"B{batch_no}-{position:03d}", record))
    if any(indices[p] != QUOTAS[p] for p in QUOTAS):
        raise ValueError("Not all selected posts allocated")
    selected_ids = {r["reddit_id"] for _, _, r in selected}
    if (len(selected) != 762 or len(selected_ids) != 762 or
        selected_ids & reserved or
        selected_ids & {r["reddit_id"] for r in development} or
        selected_ids & {r["reddit_id"] for r in unresolved}):
        raise ValueError("Duplicate or previously reviewed post in final batch")

    models = {
        "about_software": fit_model(development, "about_software", char=True),
        "update_related": fit_model(development, "update_related", char=True),
        "discussion_type": fit_model(development, "discussion_type", char=False),
    }
    texts = [model_text(r) for _, _, r in selected]
    predictions = {field: model.predict(texts) for field, model in models.items()}
    strengths = {field: model.predict_proba(texts).max(axis=1)
                 for field, model in models.items()}
    review_rows = []
    proposals = []
    mapping = []
    overflow_bodies = {}
    for index, (batch, review_id, record) in enumerate(selected):
        rule = propose(record)
        fields = {field: str(predictions[field][index]) for field in FIELDS}
        op_words = len((record["title"] + " " + record["post_body"]).split())
        if fields["about_software"] == "yes" and op_words < 7 and rule["about_software"] == "unclear" and strengths["about_software"][index] < 0.60:
            fields["about_software"] = "unclear"
        if fields["about_software"] != "yes":
            fields["discussion_type"] = "na"
            if fields["about_software"] == "no":
                fields["update_related"] = "no"
        elif fields["discussion_type"] == "na":
            fields["discussion_type"] = "other"
        if fields["discussion_type"] == "technical_troubleshooting":
            reason = "The post appears to describe a software problem or seek a diagnosis or fix; check its main purpose."
        elif fields["discussion_type"] == "general_dissatisfaction":
            reason = "The post appears mainly critical without an active repair purpose; check for a concrete problem report."
        elif fields["discussion_type"] == "other":
            reason = "The post appears to discuss software without a clear troubleshooting or chiefly critical purpose."
        else:
            reason = "The saved text appears outside software scope or is too vague to classify reliably."
        conflict = any(fields[field] != rule[field] for field in FIELDS)
        confidence = ("low" if conflict or any(float(strengths[field][index]) < 0.50 for field in FIELDS)
                      else "medium")
        proposal = {"review_id": review_id, "study_id": record["study_id"],
                    "proposal_method": "development_models_v4", **fields,
                    "confidence": confidence, "reason": reason}
        proposals.append(proposal)
        body = record["post_body"]
        text_availability = record["text_availability"]
        if len(body) > 30000:
            overflow_bodies[review_id] = body
            body = body[:15000] + "\n\n[Middle omitted for workbook cell. Full saved body is in " + review_id + ".txt.]\n\n" + body[-14000:]
            text_availability += "; body shortened in workbook"
        review_rows.append({"review_id": review_id, "subreddit": record["subreddit"],
                            "title": record["title"], "post_body": body,
                            "discussion_context": record["discussion_context"],
                            "text_availability": text_availability,
                            "proposed_about_software": fields["about_software"],
                            "proposed_update_related": fields["update_related"],
                            "proposed_discussion_type": fields["discussion_type"],
                            "proposed_confidence": confidence,
                            "proposed_reason": reason,
                            "decision": "", "final_about_software": "",
                            "final_update_related": "", "final_discussion_type": "",
                            "reviewer_note": "", "reviewed_at": "",
                            "source_url": record["url"]})
        mapping.append({"review_id": review_id, "study_id": record["study_id"],
                        "reddit_id": record["reddit_id"],
                        "source_pool": record["source_pool"],
                        "source_family": record["source_family"],
                        "phase1_legacy_label": record["phase1_legacy_label"]})

    OUT.mkdir(parents=True, exist_ok=True)
    for review_id, full_body in overflow_bodies.items():
        (OUT / f"{review_id}.txt").write_text(full_body, encoding="utf-8")
    keys = list(review_rows[0])
    for batch in range(21, 29):
        rows = review_rows[(batch - 21) * 100:(batch - 20) * 100]
        with (OUT / f"batch_{batch}_review.csv").open("w", newline="", encoding="utf-8-sig") as handle:
            writer = csv.DictWriter(handle, fieldnames=keys)
            writer.writeheader()
            writer.writerows(rows)
    (OUT / "workbook_rows.json").write_text(json.dumps(review_rows, ensure_ascii=False) + "\n", encoding="utf-8")
    (OUT / "provisional_labels.json").write_text(json.dumps(proposals, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (OUT / "ANALYST_ONLY_MAPPING.json").write_text(json.dumps(mapping, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    uncertain_rows = []
    for record in sorted(unresolved, key=lambda r: r["phase2_review_ref"]):
        uncertain_rows.append({"review_id": record["phase2_review_ref"],
                               "subreddit": record["subreddit"],
                               "title": record["title"],
                               "post_body": record["post_body"],
                               "discussion_context": record["discussion_context"],
                               "text_availability": record["text_availability"],
                               "previous_uncertainty_note": record["phase2_reason"],
                               "decision": "", "final_about_software": "",
                               "final_update_related": "", "final_discussion_type": "",
                               "reviewer_note": "", "source_url": record["url"]})
    (OUT / "uncertain_rows.json").write_text(json.dumps(uncertain_rows, ensure_ascii=False) + "\n", encoding="utf-8")
    with (OUT / "uncertain_6_review.csv").open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(uncertain_rows[0]))
        writer.writeheader()
        writer.writerows(uncertain_rows)
    manifest = {"created_utc": datetime.now(timezone.utc).isoformat(),
                "master_sha256": hashlib.sha256(MASTER.read_bytes()).hexdigest(),
                "selection_seed": SEED, "proposal_method": "development_models_v4",
                "training_counts": dict(Counter(r["phase2_review_status"] for r in development)),
                "reserved_test_training_posts": 0,
                "model_library": f"scikit-learn {sklearn.__version__}",
                "model_inputs": "Original title, first 4000 body characters, and subreddit; no source pool, legacy label, replies, or reserved-test labels.",
                "selection": "All 762 still-unreviewed posts from the October 5 troubleshooting-query pool, shuffled reproducibly into seven 100-post batches and one 62-post batch. Six previously uncertain cases are on a separate sheet without suggested labels.",
                "selected_source_counts": dict(Counter(r["source_pool"] for _, _, r in selected)),
                "proposal_type_counts": dict(Counter(p["discussion_type"] for p in proposals)),
                "proposal_confidence_counts": dict(Counter(p["confidence"] for p in proposals)),
                "overflow_body_ids": sorted(overflow_bodies),
                "unselected_after_this_batch": len(available) - len(selected),
                "previously_uncertain_unresolved": len(unresolved),
                "work_remaining_if_new_posts_are_resolved": len(available) - len(selected) + len(unresolved),
                "work_remaining_if_every_sheet_is_resolved": len(available) - len(selected),
                "warning": "Automatic proposals are review aids, not confirmed labels. Assisted-review training labels were verified with visible proposals, so this is not an independent blind annotation model evaluation."}
    (OUT / "sampling_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: manifest[k] for k in ("selected_source_counts", "proposal_type_counts",
                                                "unselected_after_this_batch", "previously_uncertain_unresolved",
                                                "work_remaining_if_new_posts_are_resolved",
                                                "work_remaining_if_every_sheet_is_resolved")}, indent=2))


if __name__ == "__main__":
    main()
