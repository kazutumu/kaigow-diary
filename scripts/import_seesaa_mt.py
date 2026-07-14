#!/usr/bin/env python3
"""Convert Seesaa MT exports into privacy-safe Jekyll posts."""

from __future__ import annotations

import argparse
import html
import json
import re
from collections import Counter
from datetime import datetime
from pathlib import Path


RECORD_SEPARATOR = re.compile(r"^--------\s*$", re.MULTILINE)
SECTION_SEPARATOR = re.compile(r"^-----\s*$", re.MULTILINE)
TAG_RE = re.compile(r"<[^>]+>")
LIQUID_OPEN_RE = re.compile(r"({{|{%)")

# Preserve the category order shown in the original Seesaa sidebar.
SEESAA_CATEGORY_ORDER = [
    "うつ病",
    "介護現場で思った事ｗ",
    "介護現場で思ったことｗ②",
    "2017",
    "2018",
    "2019",
    "2020",
    "2021",
    "2022",
    "2023",
    "2024",
    "2025",
    "2026",
    "2026手術",
    "40代の男性介護職員の年収",
    "腰椎椎間板ヘル二アとは",
    "twitter",
    "介護職に就いた理由ｗ",
    "（カテゴリなし）",
    "介護職員処遇改善交付金",
    "ホームヘルパー二級",
    "ｗ強い思いｗ＠まとめ",
    "なぜ離職率が高いのか",
    "厚生労働省　発表資料",
    "プリセプター",
    "利用者様＝お客様",
    "利用者様にとって一番の介護士（職員）にならない",
    "介護福祉士試験！！！",
    "精神的な負担ｗ",
    "介護福祉士に男性が少ない理由",
    "介護職の良いところ",
    "職場環境",
    "認知症",
    "看護師、ＰＴ、ＯＴと介護士の確執",
    "信頼関係",
    "介護職員による痰の吸引等の取扱いについて",
    "介助方法",
    "愛用している小物達♪",
    "介護保険",
    "【介護労働者の雇用管理改善等】関連助成金申請関係書類等",
    "総合的介護予防システムについてのマニュアル（改訂版）",
    "介護予防マニュアル概要版",
    "介護予防のための生活機能評価に関するマニュアル（改訂版）",
    "認知症予防・支援マニュアル",
    "介護保険と福祉用具（パンフレット）",
    "ケアマネジャー試験 合格",
    "介護予防",
    "ヒヤリ・ハットの報告書等の書式",
    "東日本大震災",
    "通所リハビリテーション",
    "利用者様との人間関係",
    "介護職員による、暴行・虐待",
    "転職活動",
    "死臭",
    "介護職員の結婚について、書きたいと思います。",
    "ボランティア活動",
    "離婚",
    "カルピスでうつ病を治す！！",
    "グリーフケア",
    "介護職をしていて死に直面したとき。",
    "サービス付き高齢者向け住宅(サ高住・サ付き）が大",
    "心療内科・精神科",
    "幸せの見つけ方。",
    "私のブログでよく読まれている記事です",
    "御衣黄（ぎょいこう）桜",
    "離職介護福祉士等届出制度ｗｗ",
    "予知夢・予言",
    "引き寄せの法則",
    "認知療法",
    "厄年",
    "禁煙",
    "移住生活",
    "詩",
    "コロナ陽性",
    "こころ観測室",
    "月結び占い",
]


def category_sort_key(item: tuple[str, int]) -> tuple[int, str]:
    name, _ = item
    try:
        return SEESAA_CATEGORY_ORDER.index(name), name
    except ValueError:
        return len(SEESAA_CATEGORY_ORDER), name


def parse_fields(text: str) -> dict[str, object]:
    fields: dict[str, object] = {"CATEGORY": []}
    for line in text.splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        value = value.strip()
        if key == "CATEGORY":
            fields["CATEGORY"].append(value)
        else:
            fields[key] = value
    return fields


def parse_comment(segment: str) -> dict[str, str] | None:
    lines = segment.removeprefix("COMMENT:\n").splitlines()
    metadata: dict[str, str] = {}
    body_start = 0
    for index, line in enumerate(lines):
        match = re.match(r"^(AUTHOR|EMAIL|IP|URL|DATE):\s?(.*)$", line)
        if not match:
            body_start = index
            break
        metadata[match.group(1)] = match.group(2).strip()
    body = "\n".join(lines[body_start:]).strip()
    if not body:
        return None
    return {
        "author": metadata.get("AUTHOR", "匿名"),
        "date": metadata.get("DATE", ""),
        "body": body,
    }


def parse_record(text: str) -> dict[str, object] | None:
    segments = SECTION_SEPARATOR.split(text.strip())
    if not segments or "TITLE:" not in segments[0]:
        return None
    fields = parse_fields(segments[0])
    sections: dict[str, str] = {}
    comments: list[dict[str, str]] = []
    for segment in segments[1:]:
        segment = segment.strip("\n")
        if segment.startswith("COMMENT:\n"):
            comment = parse_comment(segment)
            if comment:
                comments.append(comment)
            continue
        match = re.match(r"^([A-Z ]+):\n?(.*)$", segment, re.DOTALL)
        if match:
            sections[match.group(1)] = match.group(2).strip()
    fields["sections"] = sections
    fields["comments"] = comments
    return fields


def clean_excerpt(value: str, limit: int = 150) -> str:
    value = re.sub(r"<(script|style).*?</\1>", " ", value, flags=re.I | re.S)
    value = TAG_RE.sub(" ", value)
    value = html.unescape(value)
    value = re.sub(r"\s+", " ", value).strip()
    return value[:limit]


def protect_liquid(value: str) -> str:
    return LIQUID_OPEN_RE.sub(lambda match: "&#123;" + match.group(1)[1:], value)


def sanitize_body(value: str) -> str:
    # The exports contain obsolete Amazon affiliate iframes, not article content.
    value = re.sub(r"<iframe\b.*?</iframe>", "", value, flags=re.I | re.S)
    return value.strip()


def yaml_json(value: object) -> str:
    return json.dumps(value, ensure_ascii=False)


def write_post(record: dict[str, object], output_dir: Path) -> tuple[str, list[dict[str, str]]]:
    date = datetime.strptime(str(record["DATE"]), "%m/%d/%Y %H:%M:%S")
    basename = str(record.get("BASENAME", "")).strip() or date.strftime("%H%M%S") + ".html"
    article_id = re.sub(r"\.html$", "", basename, flags=re.I)
    safe_id = re.sub(r"[^A-Za-z0-9_-]+", "-", article_id).strip("-") or date.strftime("%H%M%S")
    filename = f"{date:%Y-%m-%d}-{safe_id}.md"
    categories = [item for item in record.get("CATEGORY", []) if item]
    sections = record.get("sections", {})
    body = str(sections.get("BODY", "")).strip()
    extended = str(sections.get("EXTENDED BODY", "")).strip()
    if extended:
        body = body + "\n\n" + extended
    body = protect_liquid(sanitize_body(body))
    excerpt = clean_excerpt(str(sections.get("EXCERPT", "")) or body)
    comments = record.get("comments", [])

    front_matter = [
        "---",
        f"title: {yaml_json(str(record['TITLE']))}",
        f"date: {date:%Y-%m-%d %H:%M:%S} +0900",
        f"categories: {yaml_json(categories)}",
        f"excerpt: {yaml_json(excerpt)}",
        f"seesaa_id: {yaml_json(article_id)}",
        f"permalink: /article/{basename}",
        f"legacy_comments: {str(bool(comments)).lower()}",
        "---",
        "",
    ]
    output_dir.joinpath(filename).write_text("\n".join(front_matter) + body + "\n", encoding="utf-8")
    return article_id, comments


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, default=Path("private-backup/seesaa-mt"))
    parser.add_argument("--posts", type=Path, default=Path("_posts"))
    parser.add_argument("--data", type=Path, default=Path("_data"))
    args = parser.parse_args()

    args.posts.mkdir(parents=True, exist_ok=True)
    args.data.mkdir(parents=True, exist_ok=True)
    for existing in args.posts.glob("*.md"):
        existing.unlink()

    audit_path = Path("private-backup/public-draft-audit.json")
    public_draft_ids: set[str] = set()
    if audit_path.exists():
        audit = json.loads(audit_path.read_text(encoding="utf-8"))
        public_draft_ids = set(audit.get("visible_ids", []))

    published = 0
    public_drafts = 0
    private_drafts = 0
    comments_by_post: dict[str, list[dict[str, str]]] = {}
    category_counts: Counter[str] = Counter()

    for source in sorted(args.input.glob("*.log")):
        content = source.read_text(encoding="utf-8-sig", errors="replace")
        for raw_record in RECORD_SEPARATOR.split(content):
            record = parse_record(raw_record)
            if not record:
                continue
            if record.get("STATUS") != "Publish":
                record_id = str(record.get("BASENAME", "")).removesuffix(".html")
                if record_id not in public_draft_ids:
                    private_drafts += 1
                    continue
                public_drafts += 1
            article_id, comments = write_post(record, args.posts)
            published += 1
            category_counts.update(item for item in record.get("CATEGORY", []) if item)
            if comments:
                comments_by_post[article_id] = comments

    args.data.joinpath("comments.json").write_text(
        json.dumps(comments_by_post, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    category_data = [
        {"name": name, "count": count}
        for name, count in sorted(category_counts.items(), key=category_sort_key)
    ]
    args.data.joinpath("category_counts.json").write_text(
        json.dumps(category_data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps({
        "published": published,
        "public_drafts_included": public_drafts,
        "private_drafts_skipped": private_drafts,
        "posts_with_comments": len(comments_by_post),
        "comments": sum(len(items) for items in comments_by_post.values()),
        "categories": len(category_counts),
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
