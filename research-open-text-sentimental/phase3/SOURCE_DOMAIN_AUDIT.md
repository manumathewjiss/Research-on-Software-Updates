# Source-domain finding, 2026-10-07

The Phase 2 combined master has 3,362 unique records but **not 3,362 Reddit records**. Its `url` domains are:

| URL domain | Records |
|---|---:|
| `reddit.com` | 3,332 |
| `stackoverflow.com` | 30 |

All 30 Stack Overflow records entered through Professor Berhe's Oct-5 API candidate pools. Their IDs begin `so_`. All 30 are in the experiment_v1 development file and all meet S2; 28 have `s2_target=1` and two have `s2_target=0`. None is in the 200-record reserved-test file. They were **not** removed from the saved v1 experiment or the revised v2 development snapshot, so those original results must be described as a mixed-source candidate corpus until a separate Reddit-only sensitivity analysis is conducted. The 50-post diagnostic pilot deliberately excludes them.

Immediate methods repair: specify domain counts in the dataset flow. For a paper about Reddit alone, predefine Reddit-only inclusion, rerun development-only grouped validation without these 30 (including baselines and source breakdowns), and evaluate any new finalist on a fresh untouched test. Do not silently delete the 30 from historical files or call the resulting score directly comparable to v1 without stating the changed population. Alternatively, explicitly broaden the paper to cross-platform software-update discussions and evaluate Stack Overflow as a separate, very small source; 30 records are too few to make strong cross-platform claims.
