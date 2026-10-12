# Evidence behind the October 8 broad API counts

The live endpoint is `https://releasetrain.io/api/reddit/query/update-related`.

On 2026-10-08 from 19:30:40 to 19:32:01 UTC, `collect_broad_inventory.py` fetched 44 pages using `limit=500` with no `isLabeled` or `isUpdateRelated` filter. `BROAD_INVENTORY.json` stores the first server-reported total, each page's row count, HTTP Date, and response SHA-256. It records:

- First server-reported total: **21,813**.
- Downloaded rows: **21,814**.
- Unique `redditId` values across downloaded rows: **21,813**.
- Duplicate ID rows: **one**, consistent with an offset-paginated collection changing during download.
- Returned-row values of `metadata.predicted.isUpdateRelated`: **3,727 true**, **8,495 false**, **9,592 missing/null**. These sum to 21,814 rows.

The exact **3,727** figure is a count of returned rows with a server prediction of `true`; it is **not** a count of good posts, human-confirmed update posts, or necessarily 3,727 unique IDs. It may include the duplicated row. A separate filtered request with `isLabeled=false&isUpdateRelated=true` reported 3,727 at the time of the first check, but the API is live and later returned a different total.

The inventory contains page hashes but does **not** retain all 44 raw API response bodies. Therefore an independent reader cannot reconstruct the exact October 8 unique-ID calculation solely from the saved snapshot files. The collection script documents the calculation, and the manifest documents what it observed; the live endpoint can corroborate the mechanism but will not reproduce a past total after the database changes. Do not call this an immutable archived dataset or use the 21,813/3,727 figures as manuscript findings without a frozen raw export.

Safe presentation wording: **“In our October 8 live API inventory, 44 pages returned 21,814 rows with 21,813 distinct IDs. The API marked 3,727 returned rows update-related. These were automated flags, not human-reviewed labels, and the live totals later changed.”**
