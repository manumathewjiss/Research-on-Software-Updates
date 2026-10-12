#!/usr/bin/env python3
"""AI-proposed labels for the expansion feasibility sample.

These proposals are not ground truth. Confidence is explicit.
Subreddit, source pool, and model scores are not used as labels.
The API predicted-update flag is recorded only as the sampling stratum.
"""

from __future__ import annotations

import json
import math
import re
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
POSTS = HERE / "wave1_posts.jsonl"

SOFTWARE_RE = re.compile(
    r"\b(app|application|software|os|windows|linux|ubuntu|fedora|macos|ios|android|"
    r"chrome|firefox|browser|kernel|driver|firmware|docker|kubernetes|python|java|"
    r"install|bug|crash|api|server|client|plugin|extension)\b",
    re.I,
)
UPDATE_STRONG_RE = re.compile(
    r"\b(updates?|updated|updating|upgrades?|upgraded|upgrading|patches?|patched|"
    r"firmware|rollback|downgrad)\b",
    re.I,
)
UPDATE_WEAK_RE = re.compile(r"\b(releases?|released|version)\b", re.I)
TROUBLE_RE = re.compile(
    r"\b(crash(?:es|ed|ing)?|error|bug|broken|fails?|failed|failing|not working|"
    r"doesn'?t work|won'?t|cannot|can'?t|stuck|freeze|frozen|issue|problem|"
    r"help|fix|broke|breaks|boot|panic|exception)\b",
    re.I,
)
SYMPTOM_RE = re.compile(
    r"\b(crash(?:es|ed|ing)?|error|blank|black screen|won'?t (?:boot|start|open|connect)|"
    r"doesn'?t (?:work|start|open|boot)|not working|fails? to|failed to|stuck|"
    r"freeze|frozen|exception|kernel panic|boot loop)\b",
    re.I,
)
RELEASE_RE = re.compile(
    r"\b(v?\d+\.\d+(?:\.\d+)?|ios\s?\d+|android\s?\d+|windows\s?1[01]|ubuntu\s?\d+|fedora\s?\d+)\b",
    re.I,
)
ENV_RE = re.compile(
    r"\b(iphone|ipad|pixel|laptop|desktop|server|vm|docker|raspberry|router|switch|"
    r"gpu|nvidia|intel|amd|macbook|thinkpad|windows 1[01]|linux)\b",
    re.I,
)
ERROR_RE = re.compile(
    r"\b(error\s*(?:code)?\s*[:#]?\s*\w?\d{2,}|0x[0-9a-f]{3,}|exception|traceback|"
    r"stack trace|kernel panic|bsod|segfault)\b",
    re.I,
)
REPRO_RE = re.compile(
    r"\b(when I|after I|if I|on (?:boot|startup|launch)|reproduc|steps|every time I)\b",
    re.I,
)
REMEDY_RE = re.compile(
    r"\b(i (?:tried|attempted|reinstalled|downgraded|rolled back|cleared|reset|updated)|"
    r"tried (?:to )?(?:reinstall|update|downgrade|rollback)|safe mode)\b",
    re.I,
)
HELP_RE = re.compile(r"\b(how (?:do|can) i|anyone|help|suggestions|workaround|what should)\b", re.I)

THEMES = {
    "os_or_driver": re.compile(r"\b(windows|linux|ubuntu|fedora|kernel|driver|bios|gpu|nvidia)\b", re.I),
    "mobile": re.compile(r"\b(ios|iphone|android|pixel|samsung)\b", re.I),
    "browser": re.compile(r"\b(chrome|firefox|edge|safari|browser)\b", re.I),
    "homelab_or_network": re.compile(r"\b(docker|kubernetes|proxmox|unifi|ubiquiti|pfsense|opnsense|home assistant|zigbee)\b", re.I),
    "cloud_or_enterprise": re.compile(r"\b(aws|azure|intune|active directory|kubernetes|terraform)\b", re.I),
    "ai_tooling": re.compile(r"\b(llm|gpt|openai|claude|comfyui|ollama|langchain|agent)\b", re.I),
    "security_advisory": re.compile(r"\b(cve-\d{4}|vulnerability|exploit|malware|ransomware)\b", re.I),
}


def wilson(k: int, n: int) -> tuple[float, float]:
    if n == 0:
        return (0.0, 1.0)
    z = 1.959963984540054
    p = k / n
    center = (p + z * z / (2 * n)) / (1 + z * z / n)
    margin = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / (1 + z * z / n)
    return (max(0.0, center - margin), min(1.0, center + margin))


def propose(post: dict) -> dict:
    title = post.get("title") or ""
    body = post.get("body") or ""
    text = f"{title}\n{body}"
    software_hits = len(SOFTWARE_RE.findall(text))
    update_hits = len(UPDATE_STRONG_RE.findall(text))
    weak_update = bool(UPDATE_WEAK_RE.search(text))
    trouble_hits = len(TROUBLE_RE.findall(text))
    if software_hits >= 2:
        software, software_conf = "yes", "high"
    elif software_hits == 1:
        software, software_conf = "yes", "medium"
    else:
        software, software_conf = "no", "medium"
    if update_hits >= 2:
        update, update_conf = "yes", "high"
    elif update_hits == 1:
        update, update_conf = "yes", "medium"
    elif weak_update:
        update, update_conf = "uncertain", "low"
    else:
        update, update_conf = "no", "medium"
    symptom = bool(SYMPTOM_RE.search(text))
    if trouble_hits >= 2 and symptom:
        trouble, trouble_conf = "yes", "high"
    elif trouble_hits >= 1:
        trouble, trouble_conf = "yes", "medium"
    else:
        trouble, trouble_conf = "no", "medium"
    fields = {
        "software_product": "present" if software == "yes" else "not_observed",
        "identifiable_release": "present" if RELEASE_RE.search(text) else "not_observed",
        "environment": "present" if ENV_RE.search(text) else "not_observed",
        "specific_symptom": "present" if symptom else "not_observed",
        "reproduction_context": "present" if REPRO_RE.search(text) else "not_observed",
        "error_evidence": "present" if ERROR_RE.search(text) else "not_observed",
        "attempted_remedy": "present" if REMEDY_RE.search(text) else "not_observed",
        "help_request": "present" if HELP_RE.search(text) else "not_observed",
    }
    present_diag = sum(fields[k] == "present" for k in (
        "identifiable_release", "environment", "specific_symptom",
        "reproduction_context", "error_evidence", "attempted_remedy",
    ))
    themes = [name for name, pattern in THEMES.items() if pattern.search(text)]
    uncertain = []
    if update_conf == "low":
        uncertain.append("only_weak_version_or_release_word")
    if update_hits == 1:
        uncertain.append("single_strong_update_cue")
    if trouble == "yes" and not symptom:
        uncertain.append("trouble_language_without_concrete_symptom")
    if software_conf != "high" and trouble == "yes":
        uncertain.append("weak_software_cue")
    if len(body.strip()) < 80:
        uncertain.append("thin_body")
    expansion = (
        software == "yes" and update == "yes" and trouble == "yes"
        and fields["specific_symptom"] == "present"
        and present_diag >= 2
        and "thin_body" not in uncertain
    )
    high_confidence_expansion = expansion and not uncertain
    if high_confidence_expansion:
        confidence = "high"
    elif expansion:
        confidence = "medium"
    else:
        confidence = "low"
    # Qualitative candidate: explicit before/after, version contrast, or completed rollback.
    qualitative = False
    if expansion and (
        re.search(r"\b(worked|working).{0,40}(?:before|until).{0,20}(?:update|upgrade)", text, re.I)
        or (len(set(v.lower() for v in RELEASE_RE.findall(text))) >= 2 and UPDATE_STRONG_RE.search(text))
        or re.search(r"\b(rolled back|downgraded|reverted to)\b", text, re.I)
    ):
        qualitative = True
    reason_bits = []
    if software == "no":
        reason_bits.append("no software cue in title or body")
    if update == "no":
        reason_bits.append("no update, version, patch, or firmware cue")
    elif update_conf == "low":
        reason_bits.append("only one update-related word")
    if trouble == "no":
        reason_bits.append("no troubleshooting language")
    elif not symptom:
        reason_bits.append("troubleshooting words without a concrete symptom")
    if expansion:
        reason_bits.append(f"{present_diag} diagnostic fields present")
    return {
        "reddit_id": post["reddit_id"],
        "subreddit": post.get("subreddit"),
        "created_utc": post.get("created_utc"),
        "sampling_stratum_predicted_update": post.get("predicted_update"),
        "api_labeled_update_not_used_as_truth": post.get("labeled_update"),
        "about_software": software,
        "about_software_confidence": software_conf,
        "update_related": update,
        "update_related_confidence": update_conf,
        "troubleshooting": trouble,
        "troubleshooting_confidence": trouble_conf,
        "diagnostic_fields": fields,
        "diagnostic_fields_present": present_diag,
        "themes": themes,
        "proposal_confidence": confidence,
        "uncertain_flags": uncertain,
        "expansion_worthy_proposal": high_confidence_expansion,
        "expansion_candidate_needs_review": expansion and not high_confidence_expansion,
        "qualitative_candidate_proposal": qualitative,
        "reason": "; ".join(reason_bits) or "matches software, update, and a concrete symptom",
        "label_status": "ai_proposal_not_ground_truth",
        "title": title,
    }


def main() -> None:
    posts = [json.loads(line) for line in POSTS.read_text().splitlines() if line.strip()]
    proposals = [propose(p) for p in posts]
    (HERE / "wave1_proposals.jsonl").write_text(
        "".join(json.dumps(p, ensure_ascii=False) + "\n" for p in proposals)
    )
    def rate(subset, pred):
        k = sum(1 for p in subset if pred(p))
        lo, hi = wilson(k, len(subset))
        return {"n": len(subset), "k": k, "rate": k / len(subset) if subset else None, "wilson95": [lo, hi]}
    by_stratum = {}
    for key in (True, False, None):
        subset = [p for p in proposals if p["sampling_stratum_predicted_update"] is key]
        by_stratum[str(key)] = {
            "expansion_worthy": rate(subset, lambda p: p["expansion_worthy_proposal"]),
            "needs_review": rate(subset, lambda p: p["expansion_candidate_needs_review"]),
            "qualitative_candidate": rate(subset, lambda p: p["qualitative_candidate_proposal"]),
            "update_yes": rate(subset, lambda p: p["update_related"] == "yes"),
            "troubleshooting_yes": rate(subset, lambda p: p["troubleshooting"] == "yes"),
        }
    summary = {
        "n": len(proposals),
        "about_software": dict(Counter(p["about_software"] for p in proposals)),
        "update_related": dict(Counter(p["update_related"] for p in proposals)),
        "troubleshooting": dict(Counter(p["troubleshooting"] for p in proposals)),
        "proposal_confidence": dict(Counter(p["proposal_confidence"] for p in proposals)),
        "expansion_worthy": rate(proposals, lambda p: p["expansion_worthy_proposal"]),
        "qualitative_candidate": rate(proposals, lambda p: p["qualitative_candidate_proposal"]),
        "by_predicted_stratum": by_stratum,
        "themes_among_expansion": dict(Counter(t for p in proposals if p["expansion_worthy_proposal"] for t in p["themes"])),
        "uncertain_n": sum(1 for p in proposals if p["uncertain_flags"]),
    }
    (HERE / "wave1_summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
