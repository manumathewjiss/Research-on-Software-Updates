# Phase 3 experiment_v1 data audit

**Generated:** 2026-10-07T16:22:36.410398+00:00
**Input:** `data/development.jsonl`, `data/reserved_test.jsonl`
**Manifest:** `MANIFEST.json`

This audit does not change labels. Questionable rows are flagged for Manu, not auto-corrected.

## 1. File integrity

| File | Manifest SHA-256 match | Rows |
|------|------------------------|------|
| development.jsonl | True | 3155 |
| reserved_test.jsonl | True | 200 |

Manifest expected development rows after exact dedup: 3155.
Observed: 3155. Unique reddit_id: 3155. Duplicate reddit_id: 0.
Reserved observed: 200. Unique reddit_id: 200.

Package already excluded these exact development copies of reserved posts:
- `1u3zzcs` / `C2-5450BF02B19F` — Unable to log in in KDE Fedora 44 after update, getting a black screen
- `1so7xen` / `C2-EF691952AEF7` — Zigbee2MQTT 2.x: Home Assistant Discovery Not Working – Solution

Unresolved Phase 2 IDs are absent from both files (manifest list): `1lp8o76`, `1nwclik`, `1nzj2ic`, `1q03jmr`, `1qozvt5`

## 2. Provenance (reviewed labels of mixed origin)

These are **reviewed decisions**, not all independent blind annotations.

### Development `review_status_audit_only`
- `manu_assisted_review`: 2755
- `joint_review`: 300
- `pilot_post_discussion`: 100

### Reserved `review_status_audit_only`
- `reserved_test_consensus`: 200

`source_pool_audit_only` is a collection route (Phase 1 file / Oct 5 API candidate pools), **not** a class label.

### Development source pools
- `oct5_query_tps`: 2269
- `phase1_gold_file`: 538
- `oct5_query_gds`: 348

The review set was assembled from keyword-driven API candidate pools and Phase 1 posts. Class proportions need not represent Reddit as a whole.

## 3. S2 scope and class balance

S2 = `about_software=yes` and `update_related=yes` (`s2_in_scope=true`). Target `s2_target`: 1 = technical troubleshooting, 0 = other update discussion (includes `other` and `general_dissatisfaction`).

| Split | S2 n | troubleshooting (1) | other update (0) | by discussion_type |
|-------|------|---------------------|------------------|--------------------|
| Development | 2086 | 1690 | 396 | {'technical_troubleshooting': 1690, 'general_dissatisfaction': 67, 'other': 329} |
| Reserved | 159 | 135 | 24 | {'technical_troubleshooting': 135, 'other': 15, 'general_dissatisfaction': 9} |

Scope/target consistency issues: development=0, reserved=0.
Empty titles: dev=0, test=0. Empty bodies: dev=593, test=29.

### S2 development target by source pool

```
{
  "oct5_query_gds": {
    "1": 226,
    "0": 69
  },
  "oct5_query_tps": {
    "1": 1427,
    "0": 162
  },
  "phase1_gold_file": {
    "1": 37,
    "0": 165
  }
}
```

Source and class are strongly related. Models must not receive `source_pool_audit_only` as a feature. Report metrics by source as a stress check.

## 4. Leakage / near-duplicate audit

### Method

- Normalize title+body: NFKC, lower case, strip URLs, keep alphanumeric, collapse whitespace.
- Exact match: identical normalized title+body.
- Near match: Jaccard similarity of character 5-grams on normalized title+body, threshold report 0.85, **exclude development rows at ≥ 0.92** against any reserved S2 post.
- Title-only exact matches with different bodies are reported separately.
- Reserved-test rows are never removed.

Remaining exact full-text development↔reserved overlaps after package dedup: **0**.
Title-only exact overlaps with different bodies: **4** (listed in audit outputs if any).
Near-duplicate candidates (sim ≥ 0.85, S2↔S2): **2**. Saved to `results/near_duplicate_candidates.jsonl`.
Additional development exclusions (sim ≥ 0.92): **2**. Saved to `results/development_exclusions.json`.

### Development IDs to exclude before fitting

- `1t0wme9` (`C2-18544D2C491B`): near_duplicate_of_reserved_1t0wr91 (sim=0.9838)
- `1wrqch6` (`C2-53269BF08151`): near_duplicate_of_reserved_1wrqmip (sim=0.9487)

### Manual examples (highest similarity)

- sim=0.9838: dev `1t0wme9` “AutoRewarder v3.2 is here! Now with Multi-Account Support, Mobile Point Collection, and a Brand New UI.” ↔ test `1t0wr91` “AutoRewarder v3.2 is here! Now with Multi-Account Support, Mobile Point Collection, and a Brand New UI.” (targets 0 vs 0)
- sim=0.9487: dev `1wrqch6` “How to switch between windows in Application windows view on MacOS 27 with only keyboard” ↔ test `1wrqmip` “How to switch between windows in Application windows view on MacOS 27 with only keyboard” (targets 1 vs 1)

### Title-only collisions (different full text)
- `1t0wme9` ↔ `1t0wr91`: “AutoRewarder v3.2 is here! Now with Multi-Account Support, Mobile Point Collection, and a Brand New UI.” (S2 True/True, targets 0/0)
- `1u4fpoj` ↔ `1u4foe4`: “Chrome &amp; Edge sign-in / loading problems on Google, Facebook, Grok, Amazon (and other credentialed sites) after June 2026 Windows Update KB5094127 on Dell Inspiron Inspiron 5502 Windows 10” (S2 True/True, targets 1/1)
- `1wrqch6` ↔ `1wrqmip`: “How to switch between windows in Application windows view on MacOS 27 with only keyboard” (S2 True/True, targets 1/1)
- `1vy4ez6` ↔ `1vyaqsq`: “Submenus stuck open when using the navigation overlay.” (S2 False/True, targets 1/1)

## 5. Label-quality spot check (heuristic flags only)

Flagged development S2 rows (after intended near-dup exclusions): **48**.
Saved to `results/label_quality_flags.jsonl`. These are **not** corrections.

By source: {'oct5_query_gds': 8, 'oct5_query_tps': 37, 'phase1_gold_file': 3}
By review status: {'joint_review': 5, 'manu_assisted_review': 36, 'pilot_post_discussion': 7}

Example flags (up to 12):
- `1rjfro4` [oct5_query_gds/joint_review] target=1 type=technical_troubleshooting: troubleshoot_label_with_rant_language_and_no_tech_cues — “Alarms”
- `1v17vtk` [oct5_query_tps/manu_assisted_review] target=0 type=general_dissatisfaction: non_troubleshoot_label_but_strong_repair_ask — “Fk the new iPhone keyboard update”
- `1wuyax5` [oct5_query_gds/pilot_post_discussion] target=1 type=technical_troubleshooting: troubleshoot_label_with_rant_language_and_no_tech_cues — “How to remove the rounded tabs?”
- `1rm1fsa` [oct5_query_tps/manu_assisted_review] target=1 type=technical_troubleshooting: troubleshoot_label_with_rant_language_and_no_tech_cues — “IOS 26.3 completely ruined my messages app and also extremely buggy”
- `1lsuvac` [oct5_query_gds/manu_assisted_review] target=0 type=other: very_thin_text — “Update PHP Version”
- `1puf7lm` [oct5_query_tps/manu_assisted_review] target=0 type=other: non_troubleshoot_label_but_strong_repair_ask — “My Favorite New Tab Extension Finally Got Updated After So Many Years”
- `1vspeu6` [oct5_query_tps/manu_assisted_review] target=0 type=other: non_troubleshoot_label_but_strong_repair_ask — “My first 5 days on Linux and I honestly can't believe I waited this long”
- `1wuwdcs` [oct5_query_tps/manu_assisted_review] target=1 type=technical_troubleshooting: troubleshoot_label_with_rant_language_and_no_tech_cues — “do they just genuinely hate sidebar + tab group users? (lost all my tab groups)”
- `1tebwdi` [oct5_query_tps/manu_assisted_review] target=1 type=technical_troubleshooting: troubleshoot_label_with_rant_language_and_no_tech_cues — “I f*in hate OMV’s update feature, it just broke everything”
- `1tfj4f4` [oct5_query_tps/manu_assisted_review] target=0 type=general_dissatisfaction: non_troubleshoot_label_but_strong_repair_ask — “WHY CHROME? This update broke chrome. Apparently google doesn't care, aw snap! I'm going to dechrome my life if they don't fix this nonsense soon”
- `1wu62xu` [oct5_query_tps/pilot_post_discussion] target=0 type=other: non_troubleshoot_label_but_strong_repair_ask — “[PROMO] How do you handle quiet site crashes after routine plugin updates? (Built a 100% free tool to help)”
- `1vrquz0` [oct5_query_tps/manu_assisted_review] target=0 type=other: non_troubleshoot_label_but_strong_repair_ask — “I don't think ComfyUI fully supports LTX 2.5 yet.”

If Manu finds systematic errors in a large share of these flags, pause reserved-test scoring and adjudicate first.

## 6. Freeze decision for modeling

- Primary population: `s2_in_scope=true`.
- Target: `s2_target`.
- Text: `title` and `title + post_body` (separate runs). Do not use `discussion_context` in primary models.
- Exclude additional near-duplicate development IDs listed above.
- Do not use audit-only fields as features.
- Reserved test: evaluate once after protocol/model/threshold are frozen on development only.

## 7. Counts after planned exclusions
S2 development before extra exclusions: 2086
S2 development after extra exclusions: 2084
S2 reserved (unchanged): 159
Post-exclusion class counts: {1: 1689, 0: 395}

