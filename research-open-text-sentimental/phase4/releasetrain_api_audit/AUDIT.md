# ReleaseTrain API audit, 2026-10-08

Live requests were made at about 17:42–17:45 UTC. Compact ID lists, without post text, are `tps_compact.jsonl` and `gds_compact.jsonl`. This file does not change the master dataset.

## What the linked endpoints contain

`/api/reddit/query/tps` and `/api/reddit/query/gds` were paged with `limit=500` until `hasNext` was false.

| Endpoint | Pages | Unique Reddit IDs | `hasNext` on last page | Created range |
|---|---:|---:|---|---|
| TPS | 5 (500+500+500+500+429) | 2,429 | false | 2025-04-24 to 2026-10-08 |
| GDS | 1 | 458 | false | 2025-04-25 to 2026-10-08 |
| Union |  | 2,887 |  |  |

TPS and GDS share no Reddit IDs. There is no `X-Total-Count` header. The page count above is the full retrievable set, not a sample.

`isLabeled=true` on both endpoints returns the same IDs as the unfiltered calls. It does not reveal a separate 500-post labeled collection. Inside the records, `metadata.labeled.isUpdateRelated` is non-null for 40 posts (TPS 27 true and 7 false; GDS 6 true). All 40 are already in the master. Every returned post has `metadata.predicted.isUpdateRelated=true`.

Criteria text and the TPS keyword list match the 2026-10-05 saved responses. Pagination behavior did change: on 2026-10-05, `X-Page` stayed at 1 while a cursor advanced; today `page=2` returns a disjoint next page and `X-Page` is 2.

## Overlap

| Set | Records | In live TPS | In live GDS | In either | In neither |
|---|---:|---:|---:|---:|---:|
| Phase 1 / ICMLA file inside the master | 542 | 8 | 1 | 9 | 533 |
| Current master | 3,362 |  |  | 2,819 | 543 |
| Live TPS ∪ GDS | 2,887 | 2,429 | 458 | 2,887 |  |

The master is 542 Phase 1 records plus 2,820 records from the 2026-10-05 API pull (2,370 stored as TPS, 450 as GDS). The 9 Phase 1 IDs that also appear in today's API are stored once, under Phase 1.

Posts in today's API but not in the master: **68** (61 TPS, 7 GDS). Their created times run from 2026-10-05 16:43 through 2026-10-08 16:00. Thirty of those 68 are already in the 500-post fresh-test file. None are in the reserved test. That leaves **38** posts that are in neither the master nor the fresh test.

Posts in the master but not in today's API: **543**. Of these, 533 are Phase 1 records the current TPS/GDS queries do not return. The other 10 were in the 2026-10-05 TPS download and are no longer returned (`1wr9voc`, `1wrcc8z`, `1wrfhbj`, `1wrg5kv`, `1wrmi5d`, `1wrpotx`, `1wrqch6`, `1wrqmip`, `1wrt20o`, `1wrxo3u`).

Against the 2026-10-05 snapshot: TPS went from 2,378 to 2,429 (61 added, 10 removed). GDS went from 451 to 458 (7 added, none removed).

## Coverage details for the linked endpoints

- Subreddits: TPS 121, GDS 65, union 135. The master has 154 because Phase 1 includes communities these queries do not return.
- Empty titles: 0 on both endpoints.
- Empty bodies (`author_description`): TPS 68/2,429 (2.8%), GDS 121/458 (26.4%). Among the 68 posts absent from the master, 1 has an empty body.

## A larger index exists, but it is not these two URLs

`/api/reddit/query/update-related` with no extra filter reports `total: 21708`, `totalPages: 44` at `limit=500`. Page 44 returns 208 rows and `hasNext: false`. Page 45 returns 0. That total is therefore consistent with pagination. The last page includes older Reddit IDs than the TPS/GDS window, so this index is not the same collection as the two linked endpoints.

The slice previously used for the fresh-test draw, `isLabeled=false&isUpdateRelated=true`, now reports **3,723**. The saved fresh-test crawl reported **3,718**. That pool grew by 5, not by thousands.

`isLabeled=true` on `update-related` reports **53** records, not 500.

The PyPI package `releasetrain-sentiment` fetches `https://releasetrain.io/api/reddit`, not `/query/tps` or `/query/gds`. It is not a hidden copy of several hundred new labels.
