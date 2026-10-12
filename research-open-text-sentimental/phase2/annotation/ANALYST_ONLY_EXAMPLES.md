# Analyst-only examples (not for reviewers)

**Audience:** Manu, Professor Berhe, analysts  
**Do not give this file to Reviewer A or Reviewer B before or during labeling.**

These posts appear in Phase 1 files or Phase 2 API snapshots. Tentative categories below are for internal discussion of the rule wording. They are **not** gold labels and **not** human validation.

Five of these ids are also inside the current 100-post pilot (`1o0nzld`, `1nuwiid`, `1nze9rs`, `1pf32mo`, `1r7chxn`). That is why they were removed from every reviewer-facing document.

---

## Real-post examples (review carefully; do not treat as answer keys)

| Reddit id | Title (short) | Why useful internally | Tentative fields under the repaired definition |
|-----------|---------------|----------------------|------------------------------------------------|
| `1o0nzld` | After update doesn't work FaceDetailer | Clear post-update failure | `about_software=yes`, `update_related=yes`, `discussion_type=technical_troubleshooting` |
| `1nwebdk` | Latest Chrome version introduces Auto Dark Mode bug | Version-specific defect | `about_software=yes`, `update_related=yes`, `discussion_type=technical_troubleshooting` |
| `1nuwiid` | YouTube grey/blank screen, audio plays | Looks like browser troubleshooting; Phase 1 gold was GDS | Likely `about_software=yes`; `update_related` depends on body; type likely `technical_troubleshooting` |
| `1onnoh7` | Android November security update is out… | Security update news | `about_software=yes`, `update_related=yes`, `discussion_type=other` |
| `1pf32mo` | Microsoft wants to fix app updates on Windows 11… | Product news / opinion | `about_software=yes`, `update_related=yes`, type `other` or `general_dissatisfaction` if mainly rant |
| `1nze9rs` | Plugin store upgrade announcement | Product/news | `about_software=yes`, `update_related=yes`, `discussion_type=other` |
| `1r7chxn` | Transformers display cabinet shelves | Toy showcase | `about_software=no`, `update_related=no`, `discussion_type=na` |
| `1qz4z4c` | Don't trust, verify (Bitcoin) | Crypto talk | Usually `about_software=no` unless a wallet/app bug dominates |
| Oct 5 GDS title: “Firefox 157.0 has some serious memory leaks” | API “no keyword” pool, but technical-looking | `about_software=yes`; `update_related` unclear from title alone; type depends on body | API pool ≠ label |
| Oct 5 TPS title: “Successful Upgrade to 26.04.1 (with glitches)” | Keyword pool hit; may be success + side issues | `about_software=yes`, `update_related=yes`; type `other` or troubleshooting | API pool ≠ label |

---

## How analysts may use this file after the pilot

1. Compare human–human disagreements to these edge cases.  
2. Decide whether firmware / news / “is X dead?” rules need a sharper sentence.  
3. Optionally, after agreement is reported, compare humans to Phase 1 `corrected_label` **as a secondary table**, never as the pilot’s primary truth.
