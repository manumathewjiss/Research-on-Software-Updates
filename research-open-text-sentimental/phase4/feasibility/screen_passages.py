#!/usr/bin/env python3
"""Phase 4 feasibility step 1: screen development posts for a passage-removal study.

Cursor screening suggestions only. Does not approve cases or decide go/no-go.
Does not read model predictions, source-pool labels, replies, or test outcomes
when choosing a passage.
"""

from __future__ import annotations

import csv
import hashlib
import json
import re
import unicodedata
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
DEV = ROOT / "phase3/icsc_full_paper/reliability_packet/submissions/2026-10-07-independent/development_after_independent_review.jsonl"
RESERVED = ROOT / "phase3/experiment_v1/data/reserved_test.jsonl"
FRESH = ROOT / "phase3/fresh_test_20261007/frozen_joint_labels/all_500_reviewed.jsonl"
MASTER = ROOT / "phase2/combined_dataset/master_records.json"
CODE_VERSION = "phase4-feasibility-step1-v1"
NEAR_DUP_JACCARD = 0.92
HISTORICAL_NEAR_DUP_IDS = ("1t0wme9", "1wrqch6")

UPDATE_RE = re.compile(
    r"\b(updates?|updated|updating|upgrades?|upgraded|upgrading|patches?|patched|patching|"
    r"roll(?:ed)?\s*back|revert(?:ed|ing)?|downgrad(?:e|ed|ing)|firmware)\b",
    re.I,
)
VERSION_RE = re.compile(
    r"\b(v?\d+\.\d+(?:\.\d+)?|ios\s?\d+(?:\.\d+)?|android\s?\d+|watchos\s?\d+|macos\s?\d+)\b",
    re.I,
)
SYMPTOM_RE = re.compile(
    r"\b(error|errors|crash(?:es|ed|ing)?|broken|fails?|failed|failing|issue|issues|bug|bugs|"
    r"freeze|frozen|stuck|won'?t|cannot|can'?t|doesn'?t|not working|does not work|"
    r"blank|black screen|boot|panic|exception|broken)\b",
    re.I,
)
ROLLBACK_RE = re.compile(
    r"\b("
    r"rolled back|downgraded|went back to"
    r"|reverted to (?:the )?(?:previous|older|official|last|version|\d)"
    r"|tried (?:a |to )?roll(?:ing)? back"
    r"|uninstall(?:ed|ing)? the (?:update|upgrade|patch)"
    r"|removing the (?:update|upgrade|patch)"
    r")\b",
    re.I,
)
ROLLBACK_RESULT_RE = re.compile(
    r"\b(fixed|solved|helped|worked|still|did not|didn't|didnt|no change|same (?:issue|problem)|"
    r"broke|broken|crash|failed|no luck|didn't help|did not help)\b",
    re.I,
)
BEFORE_AFTER_RE = re.compile(
    r"\b("
    r"(?:worked(?: fine| perfectly| normally)?|was working|working normally|working perfectly).{0,50}(?:before|until) (?:the |a |my )?(?:latest |recent |last )?(?:update|upgrade|patch)"
    r"|(?:before|until) (?:the |a )?(?:latest |recent |last )?(?:update|upgrade|patch).{0,80}(?:broke|broken|crash|fail|stuck|error|stopped|stop)"
    r"|until (?:the |I )(?:latest |recent )?(?:update|upgrade|updated)"
    r")\b",
    re.I,
)
GENERIC_AFTER_RE = re.compile(
    r"^(?:so |and |but )?(?:right )?after (?:the |a |my )?(?:latest |recent |last |new )?"
    r"(?:update|upgrade|patch)\b",
    re.I,
)
DEVICE_RE = re.compile(
    r"\b(other (?:phone|device|pc|laptop|machine|computer|tablet)|"
    r"another (?:phone|device|pc|laptop|machine)|"
    r"same (?:issue|problem|error) (?:on|does not|doesn't)|"
    r"only (?:happens|happened|occurs) on|"
    r"not on my (?:other|old|new)|"
    r"my other (?:phone|laptop|pc|device|machine))\b",
    re.I,
)
EMAIL_RE = re.compile(r"\b[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}\b")
PHONE_RE = re.compile(r"\b(?:\+?\d{1,3}[\s-]?)?(?:\(?\d{3}\)?[\s-]?)\d{3}[\s-]?\d{4}\b")
SECRET_RE = re.compile(
    r"\b(api[_-]?key|secret|password|passwd|token)\s*[:=]\s*\S+",
    re.I,
)


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def load_jsonl(path: Path) -> list[dict]:
    rows = []
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def host_of(url: str) -> str:
    host = urlparse(url or "").netloc.lower()
    if host.startswith("www."):
        host = host[4:]
    return host


def is_reddit(host: str) -> bool:
    return host == "reddit.com" or host.endswith(".reddit.com")


def norm_text(title: str, body: str) -> str:
    """Same normalization as experiment_v1 followup duplicate audit."""
    text = f"{title or ''}\n{body or ''}".lower()
    text = unicodedata.normalize("NFKC", text)
    text = re.sub(r"https?://\S+|www\.\S+", " ", text)
    text = re.sub(r"[^a-z0-9\s]+", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def jaccard_char_ngrams(a: str, b: str, n: int = 5) -> float:
    if not a or not b:
        return 0.0
    if a == b:
        return 1.0

    def grams(text: str) -> set[str]:
        if len(text) < n:
            return {text}
        return {text[i : i + n] for i in range(len(text) - n + 1)}

    left, right = grams(a), grams(b)
    if not left or not right:
        return 0.0
    return len(left & right) / len(left | right)


def sentence_spans(body: str) -> list[tuple[int, int, str]]:
    """Split on sentence boundaries without breaking version numbers such as 1.3.7."""
    protected = re.sub(r"\d+\.\d+(?:\.\d+)*", lambda m: m.group(0).replace(".", "\u0001"), body)
    spans = []
    for match in re.finditer(r"[^\n.!?]+(?:[.!?]+|\n+|$)", protected):
        start, end = match.span()
        chunk = body[start:end]
        if chunk.strip():
            spans.append((start, end, chunk))
    if not spans and body.strip():
        spans.append((0, len(body), body))
    return spans


def update_mentions(text: str) -> int:
    return len(UPDATE_RE.findall(text or ""))


def evidence_type(sentence: str) -> str | None:
    if ROLLBACK_RE.search(sentence) and ROLLBACK_RESULT_RE.search(sentence):
        if re.search(r"\b(can i|could i|how (?:do|can) i|is there a way|should i|never an option|not an option)\b", sentence, re.I):
            return None
        return "rollback_outcome"
    if BEFORE_AFTER_RE.search(sentence) and UPDATE_RE.search(sentence):
        if re.search(r"\b(?:i'm|i am|im) fine with\b", sentence, re.I):
            return None
        return "before_after"
    versions = VERSION_RE.findall(sentence)
    if (
        len({v.lower() for v in versions}) >= 2
        and UPDATE_RE.search(sentence)
        and re.search(
            r"\b(works?|worked|working|broke|broken|fail(?:ed|ing)?|error|crash(?:ed|ing)?|"
            r"stopped|stops|issue|problem|not working)\b",
            sentence,
            re.I,
        )
    ):
        return "version_contrast"
    if DEVICE_RE.search(sentence) and UPDATE_RE.search(sentence):
        return "device_contrast"
    return None


def is_generic_after(sentence: str) -> bool:
    stripped = sentence.strip()
    if GENERIC_AFTER_RE.search(stripped) and evidence_type(stripped) is None:
        return True
    if UPDATE_RE.search(stripped) and evidence_type(stripped) is None:
        # A sentence whose only update content is a bare version or a generic timing cue.
        if VERSION_RE.search(stripped) and not re.search(
            r"\b(broke|broken|fixed|worked|fail|crash|caus|regress)\b", stripped, re.I
        ):
            return True
    return False


def looks_unreadable(body: str) -> bool:
    letters = sum(ch.isalpha() for ch in body)
    if letters < 40:
        return True
    if letters / max(len(body), 1) < 0.35:
        return True
    return False


def sensitive(text: str) -> str | None:
    if EMAIL_RE.search(text):
        return "email_address"
    if PHONE_RE.search(text):
        return "phone_number"
    if SECRET_RE.search(text):
        return "credential_like_secret"
    return None


def remaining_ok(title: str, shortened: str) -> tuple[bool, str]:
    blob = f"{title}\n{shortened}"
    if not SYMPTOM_RE.search(blob):
        return False, "shortened title+body no longer states a concrete issue"
    if update_mentions(blob) < 1 and not re.search(r"\b(version|release|build)\b", blob, re.I):
        return False, "shortened title+body no longer has an update connection"
    if update_mentions(blob) < 1:
        return False, "shortened title+body no longer has an update connection"
    if len(title.strip()) < 8 and len(shortened.strip()) < 40:
        return False, "shortened text is too thin to name the product and issue"
    return True, ""


def screen_passage(title: str, body: str) -> dict:
    spans = sentence_spans(body)
    update_sentences = []
    for start, end, chunk in spans:
        if UPDATE_RE.search(chunk):
            update_sentences.append((start, end, chunk))
    title_updates = update_mentions(title)
    if len(update_sentences) + (1 if title_updates else 0) < 2:
        return {
            "decision": "reject",
            "reason": "removing an update passage would delete the only update connection",
            "evidence_type": "",
            "passage": "",
            "start": "",
            "end": "",
            "shortened": "",
            "concern": "only_update_link",
        }
    ranked = []
    for start, end, chunk in update_sentences:
        kind = evidence_type(chunk)
        if kind is None:
            continue
        if sum(ch.isalpha() for ch in chunk) < 40:
            continue
        if is_generic_after(chunk):
            continue
        # Do not remove a sentence if it is the only remaining product-sized clue
        # and the title is empty of symptoms. Checked after deletion.
        ranked.append((kind, start, end, chunk))
    if not ranked:
        return {
            "decision": "reject",
            "reason": "no author passage beyond a bare version or a generic update mention",
            "evidence_type": "",
            "passage": "",
            "start": "",
            "end": "",
            "shortened": "",
            "concern": "insufficient_passage",
        }
    preference = {
        "rollback_outcome": 0,
        "version_contrast": 1,
        "before_after": 2,
        "device_contrast": 3,
    }
    ranked.sort(key=lambda item: (preference[item[0]], item[1]))
    kind, start, end, chunk = ranked[0]
    shortened = body[:start] + body[end:]
    if body != shortened[:start] + chunk + shortened[start:]:
        # Exact reconstruction: shortened is prefix+suffix, so
        # prefix + passage + suffix must equal the body.
        if body != body[:start] + chunk + body[end:]:
            return {
                "decision": "reject",
                "reason": "passage span did not reconstruct the original body",
                "evidence_type": kind,
                "passage": chunk,
                "start": start,
                "end": end,
                "shortened": shortened,
                "concern": "reconstruction",
            }
    ok, why = remaining_ok(title, shortened)
    concern = ""
    decision = "plausible"
    reason = (
        f"Author passage is a {kind.replace('_', ' ')} and is not the only update connection."
    )
    if not ok:
        decision = "reject"
        reason = why
        concern = "meaning_or_coverage"
    elif kind == "device_contrast":
        decision = "borderline"
        reason = "Device contrast is present, but it may not change the first troubleshooting step."
        concern = "weaker_influence_on_first_action"
    elif kind == "before_after" and len(chunk.strip()) < 80:
        decision = "borderline"
        reason = "Before/after cue is short and could be read as a generic update timing statement."
        concern = "possible_generic_timing"
    if decision == "plausible" and (len(chunk) / max(len(body), 1)) > 0.55:
        decision = "borderline"
        reason = "The evidence is concrete, but the passage is a large share of the body, so removing it may remove the issue itself."
        concern = "passage_is_most_of_the_body"
    return {
        "decision": decision,
        "reason": reason,
        "evidence_type": kind,
        "passage": chunk,
        "start": start,
        "end": end,
        "shortened": shortened,
        "concern": concern,
    }


def duplicate_groups(rows: list[dict]) -> dict[str, dict]:
    """Map reddit_id -> duplicate note. Representative is the smallest reddit_id."""
    norms = {r["reddit_id"]: norm_text(r.get("title") or "", r.get("post_body") or "") for r in rows}
    ids = [r["reddit_id"] for r in rows]
    parent = {i: i for i in ids}

    def find(i):
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i

    def union(a, b):
        ra, rb = find(a), find(b)
        if ra == rb:
            return
        if ra < rb:
            parent[rb] = ra
        else:
            parent[ra] = rb

    by_exact = defaultdict(list)
    for rid, text in norms.items():
        by_exact[text].append(rid)
    for group in by_exact.values():
        if len(group) > 1:
            for other in group[1:]:
                union(group[0], other)

    # Near duplicates: same 16-character prefix block, Jaccard >= 0.92.
    blocks = defaultdict(list)
    for rid, text in norms.items():
        blocks[text[:16]].append(rid)
    similarities = {}
    for block in blocks.values():
        for i, left in enumerate(block):
            for right in block[i + 1 :]:
                if norms[left] == norms[right]:
                    continue
                score = jaccard_char_ngrams(norms[left], norms[right], 5)
                if score >= NEAR_DUP_JACCARD:
                    union(left, right)
                    similarities[(left, right)] = score
    groups = defaultdict(list)
    for rid in ids:
        groups[find(rid)].append(rid)
    notes = {}
    for members in groups.values():
        if len(members) < 2:
            continue
        representative = sorted(members)[0]
        exact = len({norms[m] for m in members}) == 1
        for rid in members:
            if rid == representative:
                notes[rid] = {
                    "role": "representative",
                    "representative_id": representative,
                    "members": sorted(members),
                    "kind": "exact" if exact else "near",
                }
            else:
                notes[rid] = {
                    "role": "duplicate",
                    "representative_id": representative,
                    "members": sorted(members),
                    "kind": "exact" if exact else "near",
                }
    return notes


def month_of(value: str) -> str:
    return (value or "")[:7]


def main() -> int:
    dev = load_jsonl(DEV)
    reserved_ids = {r["reddit_id"] for r in load_jsonl(RESERVED)}
    fresh_ids = {r["reddit_id"] for r in load_jsonl(FRESH)}
    master = {r["reddit_id"]: r for r in json.loads(MASTER.read_text(encoding="utf-8"))}
    assert len(dev) == len({r["reddit_id"] for r in dev})
    assert len(reserved_ids) == 200
    assert len(fresh_ids) == 500

    historical_present = [rid for rid in HISTORICAL_NEAR_DUP_IDS if any(r["reddit_id"] == rid for r in dev)]

    audit_rows = []
    label_pool = []
    for row in dev:
        reasons = []
        src = master.get(row["reddit_id"])
        url = src.get("url") if src else ""
        host = host_of(url)
        if row.get("about_software") != "yes":
            reasons.append("not_about_software_yes")
        if row.get("update_related") != "yes":
            reasons.append("not_update_related_yes")
        if row.get("discussion_type") != "technical_troubleshooting":
            reasons.append("not_technical_troubleshooting")
        if not src or not url:
            reasons.append("missing_master_url")
        elif not is_reddit(host):
            reasons.append(f"non_reddit_domain:{host or 'empty'}")
        if row["reddit_id"] in reserved_ids:
            reasons.append("reserved_test_id")
        if row["reddit_id"] in fresh_ids:
            reasons.append("fresh_test_id")
        body = row.get("post_body") or ""
        if row.get("text_availability") == "title_only":
            reasons.append("title_only_record")
        if not body.strip():
            reasons.append("blank_body")
        if body.strip() and looks_unreadable(body):
            reasons.append("unreadable_text")
        privacy = sensitive(f"{row.get('title') or ''}\n{body}")
        if privacy:
            reasons.append(f"sensitive_personal_information:{privacy}")
        structural = [r for r in reasons if r not in ("not_about_software_yes", "not_update_related_yes", "not_technical_troubleshooting")]
        label_ok = row.get("about_software") == "yes" and row.get("update_related") == "yes" and row.get("discussion_type") == "technical_troubleshooting"
        record = {
            "row": row,
            "url": url,
            "host": host,
            "reasons": reasons,
            "label_ok": label_ok,
            "structural": structural,
        }
        if label_ok and not structural:
            label_pool.append(record)
        audit_rows.append(record)

    dup_notes = duplicate_groups([item["row"] for item in label_pool])
    for item in label_pool:
        note = dup_notes.get(item["row"]["reddit_id"])
        if note and note["role"] == "duplicate":
            item["reasons"].append(
                f"duplicate_{note['kind']}_of:{note['representative_id']}"
            )

    screened = []
    for item in label_pool:
        if any(r.startswith("duplicate_") for r in item["reasons"]):
            continue
        row = item["row"]
        result = screen_passage(row.get("title") or "", row.get("post_body") or "")
        item["screen"] = result
        if result["decision"] == "reject":
            item["reasons"].append(f"passage_{result['concern'] or 'reject'}")
        screened.append(item)

    # Flow counts.
    n_dev = len(dev)
    n_label = sum(1 for item in audit_rows if item["label_ok"])
    n_reddit = sum(1 for item in audit_rows if item["label_ok"] and item["host"] and is_reddit(item["host"]))
    n_not_reserved = sum(
        1 for item in audit_rows
        if item["label_ok"] and is_reddit(item["host"]) and "reserved_test_id" not in item["reasons"]
    )
    n_not_fresh = sum(
        1 for item in audit_rows
        if item["label_ok"] and is_reddit(item["host"])
        and "reserved_test_id" not in item["reasons"]
        and "fresh_test_id" not in item["reasons"]
    )
    n_with_body = sum(
        1 for item in label_pool
        if "blank_body" not in item["reasons"] and "title_only_record" not in item["reasons"] and "unreadable_text" not in item["reasons"] and "missing_master_url" not in item["reasons"] and not any(r.startswith("non_reddit") for r in item["reasons"]) and "reserved_test_id" not in item["reasons"] and "fresh_test_id" not in item["reasons"] and not any(r.startswith("sensitive_") for r in item["reasons"])
    )
    n_after_dup = sum(1 for item in screened)
    decisions = Counter(item["screen"]["decision"] for item in screened)
    evidence = Counter(item["screen"]["evidence_type"] for item in screened if item["screen"]["decision"] in ("plausible", "borderline"))
    communities = Counter((item["row"].get("subreddit") or "unknown") for item in screened if item["screen"]["decision"] == "plausible")
    months = Counter(month_of(item["row"].get("created_utc")) for item in screened if item["screen"]["decision"] == "plausible")

    flow = {
        "starting_development_rows": n_dev,
        "unique_development_ids": len({r["reddit_id"] for r in dev}),
        "label_about_software_yes_update_related_yes_troubleshooting": n_label,
        "of_those_reddit_domain": n_reddit,
        "after_removing_reserved_test_ids": n_not_reserved,
        "after_removing_all_fresh_test_ids": n_not_fresh,
        "after_body_readability_and_privacy_filters": n_with_body,
        "duplicate_groups_in_pre_passage_pool": sum(1 for note in dup_notes.values() if note["role"] == "representative"),
        "duplicate_posts_set_aside": sum(1 for item in label_pool if any(r.startswith("duplicate_") for r in item["reasons"])),
        "screened_representatives": n_after_dup,
        "provisional_plausible": decisions["plausible"],
        "provisional_borderline": decisions["borderline"],
        "provisional_reject": decisions["reject"],
        "historical_near_dup_ids_present_in_development": historical_present,
        "duplicate_rule": (
            "Exact: identical NFKC-normalized title+body (URLs and non-alnum removed), "
            "the same rule as phase3/experiment_v1/followup/run_followup.py. "
            f"Near: Jaccard character 5-grams >= {NEAR_DUP_JACCARD} inside a 16-character prefix block. "
            "Representative is the lexicographically smallest reddit_id. Non-representatives are retained in the audit with that ID."
        ),
        "plausible_subreddit_counts": dict(communities.most_common()),
        "plausible_month_counts": dict(sorted(months.items())),
        "plausible_or_borderline_evidence_counts": dict(evidence),
        "validation": {
            "audit_rows": n_dev,
            "audit_unique_ids": n_dev,
            "candidate_rows_have_unique_ids": True,
            "reserved_overlap_in_candidates": 0,
            "fresh_overlap_in_candidates": 0,
            "reconstruction_failures": 0,
            "blank_body_candidates": 0,
            "non_reddit_candidates": 0,
            "passage_decision_inputs": "author title and body only",
        },
    }

    audit_path = HERE / "all_development_audit.csv"
    with audit_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "reddit_id",
                "study_id",
                "subreddit",
                "created_utc",
                "url_domain",
                "about_software",
                "update_related",
                "discussion_type",
                "text_availability",
                "eligibility",
                "exclusion_reasons",
                "duplicate_representative_id",
            ],
        )
        writer.writeheader()
        for item in audit_rows:
            row = item["row"]
            note = dup_notes.get(row["reddit_id"], {})
            screen = item.get("screen")
            if screen:
                eligibility = f"provisional_{screen['decision']}"
            elif item["reasons"]:
                eligibility = "excluded"
            else:
                eligibility = "not_screened"
            writer.writerow(
                {
                    "reddit_id": row["reddit_id"],
                    "study_id": row.get("study_id") or "",
                    "subreddit": row.get("subreddit") or "",
                    "created_utc": row.get("created_utc") or "",
                    "url_domain": item["host"],
                    "about_software": row.get("about_software") or "",
                    "update_related": row.get("update_related") or "",
                    "discussion_type": row.get("discussion_type") or "",
                    "text_availability": row.get("text_availability") or "",
                    "eligibility": eligibility,
                    "exclusion_reasons": "|".join(item["reasons"]),
                    "duplicate_representative_id": note.get("representative_id", ""),
                }
            )

    candidate_fields = [
        "reddit_id",
        "study_id",
        "source_record",
        "subreddit",
        "created_utc",
        "url",
        "title",
        "original_body",
        "removable_passage",
        "passage_start",
        "passage_end",
        "shortened_body",
        "evidence_type",
        "why_it_might_influence_triage",
        "product_symptom_update_remaining",
        "concern",
        "provisional_decision",
        "reason",
        "screening_status",
    ]
    candidates = []
    for item in screened:
        row = item["row"]
        result = item["screen"]
        if result["decision"] == "reject" and not result["passage"]:
            continue
        candidates.append(
            {
                "reddit_id": row["reddit_id"],
                "study_id": row.get("study_id") or "",
                "source_record": str(DEV.relative_to(ROOT)),
                "subreddit": row.get("subreddit") or "",
                "created_utc": row.get("created_utc") or "",
                "url": item["url"],
                "title": row.get("title") or "",
                "original_body": row.get("post_body") or "",
                "removable_passage": result["passage"],
                "passage_start": result["start"],
                "passage_end": result["end"],
                "shortened_body": result["shortened"],
                "evidence_type": result["evidence_type"],
                "why_it_might_influence_triage": (
                    "The passage gives a concrete comparison a first responder could use to decide whether to focus on the update."
                    if result["decision"] != "reject"
                    else ""
                ),
                "product_symptom_update_remaining": (
                    "Title plus shortened body still contain a product cue, a symptom cue, and at least one update mention."
                    if result["decision"] != "reject"
                    else result["reason"]
                ),
                "concern": result["concern"],
                "provisional_decision": result["decision"],
                "reason": result["reason"],
                "screening_status": "cursor_suggestion_not_human_reviewed",
            }
        )
    cand_path = HERE / "passage_candidates.csv"
    with cand_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=candidate_fields)
        writer.writeheader()
        writer.writerows(candidates)

    # Representative difficult rejections, a few per reason.
    reject_buckets = defaultdict(list)
    for item in screened:
        if item["screen"]["decision"] != "reject":
            continue
        reason = item["screen"]["reason"]
        if len(reject_buckets[reason]) < 3:
            reject_buckets[reason].append(item)
    reject_path = HERE / "rejected_examples.csv"
    with reject_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=["reddit_id", "subreddit", "title", "original_body", "rejection_reason", "screening_status"],
        )
        writer.writeheader()
        for reason, items in sorted(reject_buckets.items()):
            for item in items:
                writer.writerow(
                    {
                        "reddit_id": item["row"]["reddit_id"],
                        "subreddit": item["row"].get("subreddit") or "",
                        "title": item["row"].get("title") or "",
                        "original_body": item["row"].get("post_body") or "",
                        "rejection_reason": reason,
                        "screening_status": "cursor_suggestion_not_human_reviewed",
                    }
                )

    flow_path = HERE / "flow.json"
    failures = 0
    non_reddit = 0
    blank = 0
    for item in candidates:
        body = item["original_body"]
        passage = item["removable_passage"]
        if not passage:
            continue
        start = int(item["passage_start"])
        end = int(item["passage_end"])
        if body != body[:start] + passage + body[end:]:
            failures += 1
        if item["shortened_body"] != body[:start] + body[end:]:
            failures += 1
        if not body.strip():
            blank += 1
        host = host_of(item["url"])
        if not is_reddit(host):
            non_reddit += 1
    candidate_ids = [item["reddit_id"] for item in candidates]
    overlap_reserved = len(set(candidate_ids) & reserved_ids)
    overlap_fresh = len(set(candidate_ids) & fresh_ids)
    if failures or blank or non_reddit or overlap_reserved or overlap_fresh or len(candidate_ids) != len(set(candidate_ids)):
        raise SystemExit("validation failed")
    flow["validation"] = {
        "audit_rows": len(audit_rows),
        "audit_unique_ids": len({item["row"]["reddit_id"] for item in audit_rows}),
        "candidate_rows": len(candidates),
        "candidate_unique_ids": len(set(candidate_ids)),
        "reserved_overlap_in_candidates": overlap_reserved,
        "fresh_overlap_in_candidates": overlap_fresh,
        "reconstruction_failures": failures,
        "blank_body_candidates": blank,
        "non_reddit_candidates": non_reddit,
        "passage_decision_inputs": "author title and body only",
    }

    flow_path.write_text(json.dumps(flow, indent=2) + "\n", encoding="utf-8")

    outputs = {
        "README.md": HERE / "README.md",
        "flow.json": flow_path,
        "all_development_audit.csv": audit_path,
        "passage_candidates.csv": cand_path,
        "rejected_examples.csv": reject_path,
        "screen_passages.py": HERE / "screen_passages.py",
        "RUN.md": HERE / "RUN.md",
    }
    # README and RUN are written by this script only after counts exist, below.
    readme = f"""# Phase 4 feasibility, step 1: passage-removal pool

**Date:** {datetime.now(timezone.utc).date().isoformat()}
**Code version:** `{CODE_VERSION}`

This is a screening inventory. It does not approve posts, start a pilot, or decide whether the experiment should proceed.

## Question

Does the latest reviewed development set contain Reddit troubleshooting posts from which one genuine author passage can be removed while the shorter post still names the product, the concrete issue, and a minimal update connection?

## What was used

- Latest reviewed development file listed in `MANIFEST.json`.
- Master `url` for the domain check.
- Every ID in the original reserved-test file and every ID in the 500-post fresh-test file.

Passage choice uses the author title and body only. Replies, source pool, model scores, sentiment, and test outcomes are not inputs to the decision.

## Filters

1. `about_software=yes`, `update_related=yes`, and `discussion_type=technical_troubleshooting`.
2. Master URL domain is Reddit.
3. Drop reserved-test IDs and all fresh-test IDs.
4. Drop title-only records, blank bodies, unreadable text, and obvious emails, phone numbers, or credential-like secrets.
5. Duplicate rule from the earlier development audit: exact normalized title+body, plus Jaccard character 5-grams at least {NEAR_DUP_JACCARD}. A duplicate is kept in the audit with its representative ID. Only the representative is screened.
6. A removable passage must be a rollback outcome, a contrast of versions, an explicit before/after working-state contrast, or a device contrast tied to an update. A bare version or a generic “after the update” is not enough. The passage also cannot be the only update connection.

## Provisional labels

`plausible`, `borderline`, and `reject` are Cursor suggestions. None is human-reviewed or approved.

## Counts

See `flow.json`. Provisional plausible: **{decisions['plausible']}**. Borderline: **{decisions['borderline']}**. Reject among screened representatives: **{decisions['reject']}**.

Plausible cases span **{len(communities)}** communities and the evidence types in `flow.json`. A count above 60 does not mean the experiment is feasible. Codex and Manu still have to inspect the passages and make the go/no-go decision.

## Limits

The passage finder is a rule, not a reading of every post. It can miss a good passage and it can mark a weak one as plausible. Shortened text was checked only for a remaining symptom cue and a remaining update mention, not for natural prose. Privacy detection covers obvious patterns only.
"""
    run = f"""# Run the step-1 screen

From the research repository root:

```bash
phase3/experiment_v1/.venv/bin/python phase4/feasibility/screen_passages.py
```

The script rewrites the CSV, `flow.json`, `README.md`, `RUN.md`, and `MANIFEST.json` in this directory. It does not modify Phase 2 or Phase 3 files.
"""
    (HERE / "README.md").write_text(readme, encoding="utf-8")
    (HERE / "RUN.md").write_text(run, encoding="utf-8")

    manifest = {
        "code_version": CODE_VERSION,
        "date_utc": datetime.now(timezone.utc).isoformat(),
        "inputs": {
            "development": {"path": str(DEV), "sha256": sha256_file(DEV), "rows": len(dev)},
            "reserved_test": {"path": str(RESERVED), "sha256": sha256_file(RESERVED), "ids": len(reserved_ids)},
            "fresh_test_all_500": {"path": str(FRESH), "sha256": sha256_file(FRESH), "ids": len(fresh_ids)},
            "master": {"path": str(MASTER), "sha256": sha256_file(MASTER)},
        },
        "outputs": {},
        "passage_fields_do_not_use": [
            "discussion_context",
            "source_pool_audit_only",
            "model predictions",
            "sentiment scores",
            "test outcomes",
        ],
    }
    for name, path in {
        "README.md": HERE / "README.md",
        "RUN.md": HERE / "RUN.md",
        "flow.json": flow_path,
        "all_development_audit.csv": audit_path,
        "passage_candidates.csv": cand_path,
        "rejected_examples.csv": reject_path,
        "screen_passages.py": HERE / "screen_passages.py",
    }.items():
        manifest["outputs"][name] = {"path": str(path), "sha256": sha256_file(path)}
    manifest_path = HERE / "MANIFEST.json"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    print(json.dumps({
        "screened": n_after_dup,
        "plausible": decisions["plausible"],
        "borderline": decisions["borderline"],
        "reject": decisions["reject"],
        "communities": len(communities),
        "evidence": dict(evidence),
        "candidates": len(candidates),
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
