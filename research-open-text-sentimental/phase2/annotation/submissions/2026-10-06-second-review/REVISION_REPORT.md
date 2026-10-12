# Second joint review: what changed

The four CSVs in this directory are the versions Manu supplied after he and Professor Berhe sat together and reviewed the 100-post pilot and 300-post expansion again. The earlier submitted versions remain in `../2026-10-06/` and `../2026-10-06-update/`. Post ids, row order, titles, bodies, context, and availability notes still match the prepared sheets. Every required answer is present and uses an allowed value.

Both latest files for each sample have the same research-field answers. This is a **post-discussion joint decision record**. It must not be used to claim independent 100% agreement. The pilot's independent pre-discussion comparison remains in `../2026-10-06/PILOT_AGREEMENT_RESULTS.md`.

## Changes from the previous final versions

| Sample | Posts with any core-label change | `about_software` changes | `update_related` changes | `discussion_type` changes |
|---|---:|---:|---:|---:|
| 100-post pilot | 11 | 1 | 10 | 1 |
| 300-post expansion | 51 | 5 | 39 | 13 |
| **Total** | **62** | **6** | **49** | **14** |

The field counts overlap: one post may have changed more than one field. The two reviewers' latest files changed the same core-label values. Confidence changed on 8 pilot posts and 69 expansion posts. The latest Berhe reason sentences are distinct from Manu's; sentence differences are not additional label disagreements.

In the expansion, the 39 update changes were: 16 `no → yes`, 13 `unclear → yes`, 6 `unclear → no`, and 4 `yes → unclear`. The pilot had four `unclear → yes`, one `no → yes`, two `no → unclear`, two `unclear → no`, and one `yes → no`. These changes move **33 additional posts** into the strict `about_software=yes` and `update_related=yes` subset across the 400 reviewed posts.

## Current reviewed-label counts

| Measure | Previous versions | Latest versions |
|---|---:|---:|
| Strict software-and-update posts in the pilot | 53 | 57 |
| Strict software-and-update posts in expansion | 221 | 250 |
| **Strict posts across both** | **274** | **307** |
| Troubleshooting within strict posts | 215 | 243 |
| Other within strict posts | 46 | 52 |
| Dissatisfaction within strict posts | 13 | 12 |

Across all 400 reviewed posts, the latest type counts are 302 troubleshooting, 59 other, 14 dissatisfaction, and 25 not applicable. The sample composition is unchanged: 49 old posts and 351 new posts. The full combined master still has 3,362 unique posts, with 400 Phase 2 reviewed and 2,962 awaiting Phase 2 review.

Within the 300-post expansion, 107 of the 150 posts sampled from the API's `gds` candidate pool are now marked technical troubleshooting. The API pool name remains unsuitable as a research label.

## Effect on the research plan

The larger strict subset helps, but the **main strategy does not change**. In the current strict reviewed subset, 243/307 (79.2%) are troubleshooting; a classifier predicting troubleshooting for every post would already reach 79.2% accuracy on this particular sample. We need reviewed non-troubleshooting update discussions and metrics that show performance on each class. Only 12 strict posts are marked general dissatisfaction, so a three-way classifier is still poorly supported.

Before assigning more labels, freeze the `update_related` rule in plain words. Several revisions now include a post when the author explicitly **suspects or asks whether an update caused a problem**, even without proven causation. A candidate rule is: `yes` if the original post explicitly links a problem to an update/release or asks whether that link exists; `no` if no release connection is expressed; `unclear` when the saved text is too thin to decide. This is a **proposed interpretation of the revised decisions**, not a rule confirmed in writing by the authors. Check it against changed examples before using it for the remaining 2,962 posts.

Then preserve a new-post test sample before model-assisted suggestions or training, re-review the 493 old posts under the new fields, and add a varied set of non-troubleshooting update discussions. Keep all machine/assistant suggestions in separate provisional fields until reviewed; do not count them as confirmed labels. The information-completeness study can follow on the confirmed troubleshooting subset.

## Source fingerprints (SHA-256)

```text
Berhe_Blind_Review_100_Posts.csv  eea860cee18f7894aecfbe03a25648eb7a7194c47f198584919f0ea26b2a373e
Berhe_Blind_Review_300_Posts.csv  d6978faf282b5004deef5a465e6f16e771b5f36cc0ee1620397c553974ddd74f
Manu_Blind_Review_100_Posts.csv  6a37cf3220682f746096f4dae1222af4a3b4481303ac4cbae91cb575bb5294dc
Manu_Blind_Review_300_Posts.csv  c443cd72cbf0343687d394d2bd2f659a832e66858428e84a65c99d6973fb44e3
```
