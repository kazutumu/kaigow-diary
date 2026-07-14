#!/usr/bin/env python3
"""Check Seesaa Draft records against their publicly accessible article URLs."""

from __future__ import annotations

import html
import json
import time
import urllib.error
import urllib.request
from pathlib import Path

from import_seesaa_mt import RECORD_SEPARATOR, parse_record


INPUT_DIR = Path("private-backup/seesaa-mt")
REPORT_PATH = Path("private-backup/public-draft-audit.json")


def visible_from_public_site(article_id: str, title: str) -> tuple[bool, str]:
    url = f"https://kaigow.seesaa.net/article/{article_id}.html"
    request = urllib.request.Request(
        url,
        headers={"User-Agent": "Mozilla/5.0 (compatible; KaigowArchive/1.0)"},
    )
    try:
        with urllib.request.urlopen(request, timeout=25) as response:
            text = html.unescape(response.read().decode("utf-8", errors="replace"))
            visible = response.status == 200 and title.strip() in text
            return visible, f"HTTP {response.status}"
    except urllib.error.HTTPError as error:
        return False, f"HTTP {error.code}"
    except OSError as error:
        return False, str(error)


def main() -> None:
    drafts: list[dict[str, str]] = []
    for source in sorted(INPUT_DIR.glob("*.log")):
        content = source.read_text(encoding="utf-8-sig", errors="replace")
        for raw_record in RECORD_SEPARATOR.split(content):
            record = parse_record(raw_record)
            if not record or record.get("STATUS") != "Draft":
                continue
            article_id = str(record.get("BASENAME", "")).removesuffix(".html")
            drafts.append({"id": article_id, "title": str(record.get("TITLE", ""))})

    visible: list[str] = []
    hidden: list[str] = []
    results: dict[str, dict[str, object]] = {}
    for index, draft in enumerate(drafts, start=1):
        is_visible, detail = visible_from_public_site(draft["id"], draft["title"])
        results[draft["id"]] = {
            "title": draft["title"],
            "visible": is_visible,
            "detail": detail,
        }
        (visible if is_visible else hidden).append(draft["id"])
        if index % 10 == 0:
            time.sleep(0.25)

    REPORT_PATH.write_text(
        json.dumps({
            "visible_ids": visible,
            "hidden_ids": hidden,
            "results": results,
        }, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps({"checked": len(drafts), "visible": len(visible), "hidden": len(hidden)}))


if __name__ == "__main__":
    main()
