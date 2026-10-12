# Investigator review of flagged cases

**Date:** 2026-10-08. This file is analyst-only and must not be shown to external reviewers. The original post text and blank workbooks are unchanged.

| Case | Decision | Reason and handling |
|---|---|
| P006 | Keep in pilot | The main request is whether an iCloud restore can revert the Instagram change without changing the current iOS version. The multiple updates make this a useful pilot test of instruction clarity, not a clean example for main analysis. The reviewer guide now gives a general rule to focus on the author's main request and permit `cannot_assess` if that request cannot be identified. |
| P002 | Keep in pilot | The author reports a fix in the saved snapshot. The pilot checks whether reviewers treat the saved state, rather than reconstructing a pre-fix state. |
| P003 | Keep in pilot | The author later reports a fix. This is intentional for the same snapshot-time instruction check. Its certificate warning and domain names are part of the saved error text; no account or credential is present in the supplied packet. |
| Q026 | Keep as boundary case | Historical `other` label does not settle the action. The body reports applications breaking after an update-channel change; a reviewer may reasonably choose investigation. This is precisely a case where purpose classification and triage action may diverge. Do not present it as a clean negative example. |
| Q023 | Keep as boundary case | Strong dissatisfaction coexists with specific UI behaviors. The study examines which aspects reviewers cite; do not assume no action from the label. |
| Q028 | Keep as boundary case | Strong dissatisfaction coexists with changed tab grouping, ignored setting, and a fix question. Do not treat it as pure sentiment. |
| Q014 | Keep pending final privacy gate | The saved text says password values appear empty and mentions `sk.php` and a security-key *file*, but shows no actual password, key value, account name, email, or host address. This is not a technical privacy clearance for distribution; Manu/Professor Berhe must still approve sharing under the project's data-use arrangement. |

The three main boundary cases should be retained whether reviewers agree or disagree. We must report their historical categories as context only after first-pass responses are locked; the categories are not a correctness standard for engineering decisions.
