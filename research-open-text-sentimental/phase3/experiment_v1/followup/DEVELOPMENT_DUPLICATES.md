# Within-development duplicate audit (followup)

**Generated:** 2026-10-07T16:32:05.397858+00:00
**Population:** eligible S2 development rows after protocol exclusions (n=2084)

Similarity findings are **not** confirmed labeling errors. Confirmed label conflicts on identical text are listed separately below.

## Method

- Exact: identical normalized title+body (NFKC, lower, URLs stripped, non-alnum collapsed)
- Near: Jaccard similarity of character 5-grams on the same normalized text; report pairs ≥ 0.85; group for validation at ≥ 0.92
- Blocking for near search: prefix-16 of normalized text, plus same raw-title groups for near search

## Exact duplicates (identical normalized title+body)

- Groups with ≥2 posts: **25**
- Posts involved: **52**
- Groups with conflicting `s2_target`: **1**

### Confirmed label conflicts on identical text

- IDs `1wxl2u9, 1wxl3ma, 1wxl35m` — targets [0, 0, 1] (['other', 'other', 'technical_troubleshooting']) — title: 'Need advice: Kubernetes 1.34 → 1.35 upgrade with Elasticsearch running in the cluster'

### All exact groups (summary)

| n | reddit_ids | targets | conflict | title |
|---|------------|---------|----------|-------|
| 3 | 1wxl2u9, 1wxl3ma, 1wxl35m | [0, 0, 1] | yes | Need advice: Kubernetes 1.34 → 1.35 upgrade with Elasticsear |
| 3 | 1u5a41p, 1u5a4oi, 1u5a4as | [0, 0, 0] | no | from fedora back to Ubuntu |
| 2 | 1mmn51c, 1mncd11 | [1, 1] | no | Weird popup after updating Chrome |
| 2 | 1oualta, 1oualms | [0, 0] | no | Firefox 145.0, See All New Features, Updates and Fixes |
| 2 | 1r1wt4l, 1r1wspr | [1, 1] | no | Newest iOS Update broke my iPhone 15 plus |
| 2 | 1r6i5er, 1r6i45v | [1, 1] | no | Strange GAP over the top |
| 2 | 1ry5y9x, 1ry5wjh | [0, 0] | no | Our 'harmless' backend migration silently broke the app for  |
| 2 | 1rzlgiu, 1rzlhe1 | [1, 1] | no | Unstable performance after recent update to kernel 6.17.0-19 |
| 2 | 1s295zo, 1s295e4 | [1, 1] | no | Fedora 43 - Impossible to boot Windows from Grub (black scre |
| 2 | 1s4bcur, 1s4bdc2 | [1, 1] | no | Codex CLI v0.116+ breaks on Ubuntu LTS / Debian with "bwrap: |
| 2 | 1s5rp8r, 1s5rpge | [1, 1] | no | Home network setting problem seek for help |
| 2 | 1so5j4j, 1so5g68 | [1, 1] | no | Health and fitness app not in sync |
| 2 | 1t1c6um, 1t1c79o | [1, 1] | no | Why is it every time I try to update my drivers, it breaks m |
| 2 | 1t2m2cy, 1t2lkk9 | [1, 1] | no | Krita Pen Tablet issue with Ubuntu 26.04 Resolute Raccoon, G |
| 2 | 1thowwi, 1thoyny | [1, 1] | no | Enlisted broken on Linux after Scorching Rays update — Intel |
| 2 | 1thsn3n, 1tho6vf | [1, 1] | no | Fedora splash screen then black monitor |
| 2 | 1tk5l5t, 1tk5lnq | [1, 1] | no | Updated to the latest frame ware and my wired express 7 set  |
| 2 | 1tmj0wk, 1tmj19o | [1, 1] | no | Zorin update made me unable to connect to the internet. |
| 2 | 1u71ioe, 1u71hyg | [0, 0] | no | Latest Honeywell T10+ Pro Thermostat Firmware |
| 2 | 1ug08ts, 1ug09do | [1, 1] | no | 6.8.0-2019-raspi-realtime kernel: installation on cm5 not wo |
| 2 | 1uyg6ln, 1uyg5kl | [1, 1] | no | Weird Bluetooth issue after recent update |
| 2 | 1v17vtk, 1v17wwt | [0, 0] | no | Fk the new iPhone keyboard update |
| 2 | 1v1owf5, 1v1ompn | [1, 1] | no | Facing sleep issues due to NVIDIA drivers |
| 2 | 1v37lko, 1v37l9m | [1, 1] | no | Network shares won't mount after scheduled reboot |
| 2 | 1vqp5mh, 1vqp6c5 | [0, 0] | no | UPDATE: EchoMuse Gains a Home Assistant App! |

## Near duplicates (similarity only)

- Pairs with sim ≥ 0.85: **8**
- Pairs with sim ≥ 0.92 (used for fold grouping): **7**
- Pairs ≥ 0.85 with disagreeing targets: **0** (disagreement on *similar* text is not automatic proof of error)

| sim | id_a | id_b | targets | titles |
|-----|------|------|---------|--------|
| 0.9961 | `1s8zswp` | `1s8zrvp` | 1/1 | Logitech MX mouse volume buttons delayed / Logitech MX mouse volume buttons delayed |
| 0.9931 | `1wv9y2s` | `1wv9i7x` | 1/1 | ASUS TUF Gaming A15 FA507NV – Fedora 44  / ASUS TUF Gaming A15 FA507NV – Fedora 44  |
| 0.9892 | `1su4lrk` | `1su4kqy` | 1/1 | Long boot times after upgrading from Ubu / Long boot times after upgrading from 24. |
| 0.9816 | `1ovh310` | `1ovh3qq` | 1/1 | iPhone 14 Pro Max DFU Problem? / iPhone 14 Pro Max DFU and model problem. |
| 0.9689 | `1sk8zv4` | `1skatru` | 0/0 | Firmware Updates Breaks and Conflicts Wi / Firmware Updates Breaks and Conflicts Wi |
| 0.9609 | `1s3r9jj` | `1sqbmz5` | 0/0 | OS upgrade / OS upgrade |
| 0.9433 | `1u4wd1t` | `1u4wa8c` | 0/0 | Fedora has been my main OS for years, bu / Fedora has been my main OS for years, bu |
| 0.8968 | `1scg8al` | `1sch5ru` | 0/0 | My week with Tahoe 26.4 (Spoiler: I like / My week with Tahoe. |

## Groups used for followup validation folds

- Rule: union of exact-text identity and near-dup pairs with sim ≥ 0.92
- Multi-post groups: **32** (66 posts)
- Singletons: **2018**

Machine-readable: `results/development_duplicates.json`.

