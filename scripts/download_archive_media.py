#!/usr/bin/env python3
"""Download author-uploaded Seesaa/Fanblogs media and rewrite post URLs."""

from __future__ import annotations

import hashlib
import json
import mimetypes
import re
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path


POSTS_DIR = Path("_posts")
MEDIA_DIR = Path("assets/media/archive")
MANIFEST_PATH = Path("assets/media/archive-manifest.json")
FAILURE_PATH = Path("private-backup/seesaa-media-failures.json")
ATTRIBUTE_URL_RE = re.compile(r"(?P<url>https?://[^\"'<>\s]+)", re.I)


def is_owned_media(url: str) -> bool:
    parsed = urllib.parse.urlparse(url)
    return (
        parsed.netloc == "kaigow.up.seesaa.net" and parsed.path.startswith("/image/")
    ) or (
        parsed.netloc == "fanblogs.jp" and parsed.path.startswith("/864/file/")
    )


def find_urls() -> list[str]:
    urls: set[str] = set()
    for post in POSTS_DIR.glob("*.md"):
        for match in ATTRIBUTE_URL_RE.finditer(post.read_text(encoding="utf-8")):
            url = html_unescape_url(match.group("url"))
            if is_owned_media(url):
                urls.add(url)
    return sorted(urls)


def html_unescape_url(url: str) -> str:
    return url.replace("&amp;", "&")


def safe_filename(url: str, content_type: str = "") -> str:
    parsed = urllib.parse.urlparse(url)
    basename = urllib.parse.unquote(Path(parsed.path).name)
    basename = re.sub(r"[^A-Za-z0-9._-]+", "-", basename).strip("-.")
    if not basename:
        basename = "image"
    if "." not in basename and content_type:
        extension = mimetypes.guess_extension(content_type.split(";", 1)[0].strip()) or ""
        basename += extension
    digest = hashlib.sha256(url.encode("utf-8")).hexdigest()[:12]
    return f"{digest}-{basename}"


def download(url: str) -> tuple[bytes, str]:
    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 (compatible; KaigowArchive/1.0)",
            "Referer": "https://kaigow.seesaa.net/",
        },
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        return response.read(), response.headers.get("Content-Type", "")


def main() -> None:
    MEDIA_DIR.mkdir(parents=True, exist_ok=True)
    manifest: dict[str, str] = {}
    if MANIFEST_PATH.exists():
        manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))

    urls = find_urls()
    failed: dict[str, str] = {}
    for index, url in enumerate(urls, start=1):
        existing = manifest.get(url)
        if existing and Path(existing.lstrip("/")).exists():
            continue
        try:
            data, content_type = download(url)
            if not data:
                raise ValueError("empty response")
            filename = safe_filename(url, content_type)
            destination = MEDIA_DIR / filename
            destination.write_bytes(data)
            manifest[url] = "/" + destination.as_posix()
        except (OSError, ValueError, urllib.error.URLError) as error:
            failed[url] = str(error)
        if index % 20 == 0:
            time.sleep(0.2)

    MANIFEST_PATH.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    FAILURE_PATH.parent.mkdir(parents=True, exist_ok=True)
    FAILURE_PATH.write_text(
        json.dumps(failed, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    rewrites = 0
    for post in POSTS_DIR.glob("*.md"):
        content = post.read_text(encoding="utf-8")
        updated = content
        for url, local_path in manifest.items():
            replacement = "{{ '" + local_path + "' | relative_url }}"
            updated = updated.replace(url, replacement)
            updated = updated.replace(url.replace("&", "&amp;"), replacement)
        for url in failed:
            missing_image = re.compile(
                r"<img\b[^>]*\bsrc=(?P<quote>[\"'])"
                + re.escape(url)
                + r"(?P=quote)[^>]*>",
                re.I,
            )
            updated = missing_image.sub(
                '<span class="missing-media">旧サービス上で画像を取得できません</span>',
                updated,
            )
        updated = re.sub(
            r"<a\b[^>]*>\s*(<span class=\"missing-media\">.*?</span>)\s*</a>",
            r"\1",
            updated,
            flags=re.I | re.S,
        )
        if updated != content:
            post.write_text(updated, encoding="utf-8")
            rewrites += 1

    print(json.dumps({
        "discovered": len(urls),
        "downloaded": len(manifest),
        "failed": len(failed),
        "posts_rewritten": rewrites,
        "failures": failed,
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
