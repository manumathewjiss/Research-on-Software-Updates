"""Save a dated, read-only snapshot of broad update-related Reddit candidates."""
from __future__ import annotations

import hashlib
import json
import time
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "fresh_test_20261007" / "raw"
BASE = "https://releasetrain.io/api/reddit/query/update-related?isLabeled=false&isUpdateRelated=true&limit=500&page={}"


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    records = []
    total_pages = None
    page = 1
    while total_pages is None or page <= total_pages:
        url = BASE.format(page)
        response = urllib.request.urlopen(
            urllib.request.Request(url, headers={"User-Agent": "SoftwareUpdateResearchAudit/1.0"}), timeout=45
        )
        content = response.read()
        payload = json.loads(content)
        pagination = payload["pagination"]
        assert pagination["page"] == page
        if total_pages is None:
            total_pages = pagination["totalPages"]
        elif pagination["totalPages"] != total_pages:
            raise RuntimeError("Page count changed during collection; do not use mixed snapshot")
        path = OUT / f"update_related_page_{page:02d}.json"
        path.write_bytes(content)
        records.append({
            "page": page, "url": url, "file": path.name,
            "server_date": response.headers.get("Date"),
            "sha256": hashlib.sha256(content).hexdigest(),
            "n": len(payload["data"]), "reported_total": pagination["total"],
        })
        print(f"page {page}/{total_pages}: {len(payload['data'])}", flush=True)
        page += 1
        time.sleep(0.3)
    manifest = {
        "collected_at_utc": datetime.now(timezone.utc).isoformat(),
        "description": "Broad predicted-update-related candidate pool; predictions are not human labels",
        "pages": records,
    }
    (OUT / "collection_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")


if __name__ == "__main__":
    main()
