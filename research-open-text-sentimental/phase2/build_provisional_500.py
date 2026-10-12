#!/usr/bin/env python3
"""Select 500 unreviewed posts and make reproducible, provisional review aids.

These simple text rules are deliberately not research labels. Every row needs
Manu's decision before its fields may enter the confirmed Phase 2 dataset.
"""

from __future__ import annotations

import csv
import hashlib
import json
import random
import re
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline
import sklearn

ROOT = Path(__file__).resolve().parent.parent
MASTER = ROOT / "phase2/combined_dataset/master_records.json"
OUT = ROOT / "phase2/annotation/provisional_500"
SEED = 20261006
QUOTAS = {"phase1_gold_file": 250, "oct5_query_gds": 125, "oct5_query_tps": 125}


def hit(pattern: str, text: str) -> bool:
    return re.search(pattern, text, re.I) is not None


SOFTWARE = (r"\b(?:software|app(?:lication)?s?|operating system|windows|macos|ios|android|"
            r"linux|ubuntu|fedora|browser|chrome|firefox|edge|plugin|extension|firmware|"
            r"driver|code|script|server|api|website|webpage|login|sync(?:ing)?|database|"
            r"github|wordpress|kubernetes|docker|python|javascript|angular|comfyui|"
            r"godot|ui|gui|settings)\b")
STRONG_SOFTWARE = (r"\b(?:software|app(?:lication)?s?|operating system|windows|macos|ios|"
                   r"android|linux|browser|chrome|firefox|plugin|firmware|driver|website|"
                   r"python|javascript|github|wordpress|kubernetes|docker|comfyui)\b")
UPDATE = (r"\b(?:updat(?:e|ed|es|ing)|upgrad(?:e|ed|ing)|patch(?:ed)?|"
          r"releas(?:e|ed|es|ing)|changelog|hotfix|new version|latest version|"
          r"after (?:install(?:ing|ed)?|switch(?:ing|ed)?|migrat(?:ing|ed)?)|"
          r"since (?:install(?:ing|ed)?|switch(?:ing|ed)?|migrat(?:ing|ed)?))\b")
SYMPTOM = (r"\b(?:crash(?:es|ed|ing)?|broken|breaks?|bug(?:gy)?|error|fail(?:s|ed|ing|ure)?|"
           r"not working|won'?t work|can'?t|cannot|unable|stuck|disconnect(?:s|ed|ing)?|"
           r"freeze(?:s|ing)?|frozen|glitch(?:es|y)?|slow|drain(?:ing)?|lag(?:gy)?|"
           r"issue|problem|missing|black screen|bootloop|loop|doesn'?t|wont|lost)\b")
HELP = (r"\b(?:how (?:do|can|to|would|should) i|any (?:fix|solution|ideas?|help)|"
        r"(?:need|looking for|asking for) help|help me|troubleshoot|diagnos(?:e|is)|"
        r"workaround|solution|fix(?:ed|ing)?|resolve|what (?:can|should) i do|"
        r"has anyone (?:faced|seen|had|experienced))\b")
SPECIFIC_FAILURE = (r"\b(?:crash(?:es|ed|ing)?|error|fail(?:s|ed|ing|ure)?|"
                    r"not working|won'?t work|can'?t access|cannot access|unable to|"
                    r"stuck|disconnect(?:s|ed|ing)?|freeze(?:s|ing)?|frozen|"
                    r"glitch(?:es|y)?|won'?t load|not loading|black screen|"
                    r"bootloop|doesn'?t (?:open|load|start|work|connect|send|sync)|"
                    r"lost (?:access|data|connection|all)|not able to|"
                    r"(?:tabs?|data|files?) (?:gone|disappeared|missing))\b")
NEGATIVE = (r"\b(?:sucks?|hate|awful|terrible|worst|annoying|frustrat(?:ed|ing)|"
            r"disappoint(?:ed|ing)|ruined|rant|fed up|garbage|trash|unusable|"
            r"regret|ridiculous)\b")
NEWS = (r"\b(?:announc(?:e|es|ed|ement)|release notes|changelog|what'?s new|"
        r"new features|now available|rolling out|official release|security update|"
        r"weekly roundup|monthly roundup|finally fixed|welcome improvements)\b")
NEWS_TITLE = (r"\b(?:announc(?:e|es|ed)|release notes|new features|is here|"
              r"now available|rolling out|official release|finally fixed|"
              r"welcome improvements|fixing the|first look|new vulnerability|"
              r"getting away with|urges .* to update)\b|^CVE-\d")
NON_SOFTWARE_SUBS = {"bitcoin", "transformers", "anime", "union", "thrive"}
SOFTWARE_SUBS = {"android", "androidquestions", "chrome", "firefox", "microsoftedge",
                 "linux", "linuxquestions", "ubuntu", "fedora", "debian", "macos", "ios",
                 "applehelp", "wordpress", "neovim", "github", "kubernetes", "comfyui",
                 "immich", "vscode", "homeassistant", "windows", "software", "sysadmin",
                 "php", "react", "django", "node", "rustdesk", "tailwindcss", "godot"}
SOFTWARE_SUBS.update({"angular", "docker", "nest", "homeautomation", "visual-studio"})
SOFTWARE_SUBS.update({"cachyos", "grafana", "aws", "powertoys", "rust", "nuxt",
                     "supabase", "openclaw", "opencode"})


def propose(row: dict) -> dict:
    title = row["title"].strip()
    body = row["post_body"].strip()
    op = f"{title}\n{body}".strip()
    sub = row["subreddit"].lower()
    software_word = hit(SOFTWARE, op)
    strong_software_word = hit(STRONG_SOFTWARE, op)
    update_word = hit(UPDATE, op)
    symptom = hit(SYMPTOM, op)
    specific_failure = hit(SPECIFIC_FAILURE, op)
    help_seeking = hit(HELP, op)
    negative = hit(NEGATIVE, title + "\n" + body[:300])
    news = hit(NEWS, op)
    news_title = hit(NEWS_TITLE, title)
    vague = len(op.split()) < 7 and not software_word

    if sub in NON_SOFTWARE_SUBS and not strong_software_word:
        software = "no"
    elif software_word or (sub in SOFTWARE_SUBS and not vague):
        software = "yes"
    elif sub in SOFTWARE_SUBS or vague:
        software = "unclear"
    else:
        software = "unclear"

    if software == "no":
        update = "no"
        discussion = "na"
        reason = "The saved post does not describe software."
    elif software == "unclear":
        update = "yes" if update_word and software_word else "unclear"
        discussion = "na"
        reason = "The saved text does not identify the software topic clearly enough."
    else:
        update = "yes" if update_word else ("unclear" if vague else "no")
        if news_title and not hit(r"\b(?:help|how do i|workaround|issue|problem|broken|crash)\b", title):
            discussion = "other"
            reason = "The title presents news or release information rather than a problem to diagnose."
        elif news and not specific_failure and not hit(r"\b(?:help|how do i|workaround)\b", op):
            discussion = "other"
            reason = "The post presents release or product information rather than a problem to diagnose."
        elif specific_failure or (symptom and help_seeking):
            discussion = "technical_troubleshooting"
            reason = "The post describes a concrete malfunction or asks how to diagnose or fix one."
        elif help_seeking and not negative and not news:
            discussion = "technical_troubleshooting" if symptom else "other"
            reason = ("The post asks for help with a software problem." if symptom else
                      "The post asks a software question without a clear malfunction.")
        elif negative:
            discussion = "general_dissatisfaction"
            reason = "The main message criticizes software without a clear request to diagnose or fix it."
        else:
            discussion = "other"
            reason = "The post discusses software without a clear repair request or chiefly negative opinion."

    if software == "unclear" or update == "unclear" or vague:
        confidence = "low"
    elif discussion == "technical_troubleshooting" and specific_failure and help_seeking and update_word:
        confidence = "high"
    elif discussion == "other" and news:
        confidence = "high"
    elif software == "no" and sub in NON_SOFTWARE_SUBS:
        confidence = "medium"
    else:
        confidence = "medium"
    return {"about_software": software, "update_related": update,
            "discussion_type": discussion, "confidence": confidence, "reason": reason}


def model_text(row: dict) -> str:
    """Only visible post text and subreddit; no source pool or old label."""
    return ("subreddit " + row["subreddit"] + " " * 3 +
            " title " + row["title"] + " " * 3 +
            " body " + row["post_body"][:4000])


def main() -> None:
    records = json.loads(MASTER.read_text(encoding="utf-8"))
    available = [r for r in records if r["phase2_review_status"] == "needs_phase2_review"]
    development = [r for r in records if r["phase2_review_status"] in ("pilot_post_discussion", "joint_review")]
    if len(development) != 400:
        raise ValueError("Expected 400 development-reviewed posts")
    type_model = make_pipeline(
        TfidfVectorizer(analyzer="char", ngram_range=(3, 5), min_df=2, max_features=50000),
        LogisticRegression(max_iter=1000, class_weight="balanced"),
    )
    type_model.fit([model_text(r) for r in development],
                   [r["phase2_discussion_type"] for r in development])
    reserved = {r["reddit_id"] for r in records if r["phase2_review_status"] == "reserved_test_consensus"}
    rng = random.Random(SEED)
    chosen_by_pool = {}
    for pool, quota in QUOTAS.items():
        population = sorted((r for r in available if r["source_pool"] == pool),
                            key=lambda r: r["reddit_id"])
        if len(population) < quota:
            raise ValueError(f"Insufficient unreviewed posts in {pool}")
        chosen_by_pool[pool] = rng.sample(population, quota)
        rng.shuffle(chosen_by_pool[pool])

    selected = []
    for batch in range(1, 6):
        block = (chosen_by_pool["phase1_gold_file"][(batch-1)*50:batch*50] +
                 chosen_by_pool["oct5_query_gds"][(batch-1)*25:batch*25] +
                 chosen_by_pool["oct5_query_tps"][(batch-1)*25:batch*25])
        rng.shuffle(block)
        for pos, record in enumerate(block, 1):
            review_id = f"B{batch}-{pos:03d}"
            selected.append((batch, pos, review_id, record))

    ids = [r["reddit_id"] for _, _, _, r in selected]
    if len(selected) != 500 or len(set(ids)) != 500 or set(ids) & reserved:
        raise ValueError("Duplicate or reserved post in review sample")
    if set(ids) & {r["reddit_id"] for r in development}:
        raise ValueError("Development-reviewed post in review sample")
    predicted_types = type_model.predict([model_text(r) for _, _, _, r in selected])
    type_probs = type_model.predict_proba([model_text(r) for _, _, _, r in selected])
    OUT.mkdir(parents=True, exist_ok=True)
    proposals = []
    review_rows = []
    mapping = []
    for index, (batch, pos, review_id, r) in enumerate(selected):
        p = propose(r)
        model_type = str(predicted_types[index])
        model_strength = float(max(type_probs[index]))
        rule_type = p["discussion_type"]
        if p["about_software"] == "yes":
            if rule_type == "general_dissatisfaction" or p["reason"].startswith("The title presents news"):
                pass
            elif model_type == "na":
                p["discussion_type"] = "other"
                p["reason"] = "The text does not clearly show a troubleshooting request or a mainly negative opinion."
            else:
                p["discussion_type"] = model_type
                if model_type != rule_type:
                    p["reason"] = ("The text may describe a problem to diagnose; check whether its main purpose is troubleshooting."
                                   if model_type == "technical_troubleshooting" else
                                   "The text may be discussion rather than an active repair request; please check its main purpose.")
        if model_type != rule_type or model_strength < 0.40:
            p["confidence"] = "low"
        elif p["confidence"] == "high":
            p["confidence"] = "medium"
        proposals.append({"review_id": review_id, "study_id": r["study_id"],
                          "proposal_method": "development_model_plus_rules_v1", **p})
        review_rows.append({"review_id": review_id, "subreddit": r["subreddit"],
                            "title": r["title"], "post_body": r["post_body"],
                            "discussion_context": r["discussion_context"],
                            "text_availability": r["text_availability"],
                            "proposed_about_software": p["about_software"],
                            "proposed_update_related": p["update_related"],
                            "proposed_discussion_type": p["discussion_type"],
                            "proposed_confidence": p["confidence"],
                            "proposed_reason": p["reason"],
                            "decision": "", "final_about_software": "",
                            "final_update_related": "", "final_discussion_type": "",
                            "reviewer_note": "", "reviewed_at": "",
                            "source_url": r["url"]})
        mapping.append({"review_id": review_id, "study_id": r["study_id"],
                        "reddit_id": r["reddit_id"], "source_pool": r["source_pool"],
                        "source_family": r["source_family"],
                        "phase1_legacy_label": r["phase1_legacy_label"]})

    fields = list(review_rows[0])
    for batch in range(1, 6):
        path = OUT / f"batch_{batch}_review.csv"
        with path.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=fields)
            writer.writeheader()
            writer.writerows(review_rows[(batch-1)*100:batch*100])
    (OUT / "provisional_labels.json").write_text(json.dumps(proposals, indent=2, ensure_ascii=False)+"\n", encoding="utf-8")
    (OUT / "workbook_rows.json").write_text(json.dumps(review_rows, ensure_ascii=False)+"\n", encoding="utf-8")
    (OUT / "ANALYST_ONLY_MAPPING.json").write_text(json.dumps(mapping, indent=2, ensure_ascii=False)+"\n", encoding="utf-8")
    digest = hashlib.sha256(MASTER.read_bytes()).hexdigest()
    manifest = {"created_utc": datetime.now(timezone.utc).isoformat(), "selection_seed": SEED,
                "master_sha256": digest, "proposal_method": "development_model_plus_rules_v1",
                "development_training_posts": len(development), "reserved_test_training_posts": 0,
                "model_library": f"scikit-learn {sklearn.__version__}",
                "type_model": "Character 3-5 gram TF-IDF, balanced logistic regression; title, first 4000 body characters, and subreddit only. Simple text rules constrain scope and update fields and a few obvious news/dissatisfaction cases.",
                "selection": "Random without replacement within each unreviewed source pool; five 100-post batches, each with 50 Phase 1, 25 Oct 5 GDS-pool, 25 Oct 5 TPS-pool posts.",
                "quotas": QUOTAS, "counts": {"selected": len(selected),
                                            "source_pool": dict(Counter(m["source_pool"] for m in mapping)),
                                            "proposed_discussion_type": dict(Counter(p["discussion_type"] for p in proposals)),
                                            "proposed_about_software": dict(Counter(p["about_software"] for p in proposals)),
                                            "proposed_update_related": dict(Counter(p["update_related"] for p in proposals))},
                "reserved_test_overlap": 0,
                "warning": "Proposals are automated review aids, not human-confirmed labels or measured model performance. Source pool, old labels, reserved-test answers, and replies were not used to train or propose labels."}
    (OUT / "sampling_manifest.json").write_text(json.dumps(manifest, indent=2)+"\n", encoding="utf-8")
    print(json.dumps(manifest["counts"], indent=2))


if __name__ == "__main__":
    main()
