#!/usr/bin/env python3
"""抓取并结构化《唐類函》识典古籍页面。"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any


DEFAULT_URL = "https://www.shidianguji.com/book/HY7244/chapter/1l1u7tac5qr0f?page_from=searching_page&version=14"
ROUTER_DATA_RE = re.compile(r"window\._ROUTER_DATA\s*=\s*(\{.*?\})</script>", re.S)
LINE_TYPE_LABELS = {1: "正文", 2: "注文", 3: "分页"}
LAYER_ORDER = ["敘事", "事對", "詩文", "未分"]
STYLE_MARKERS = (
    "詩曰",
    "诗曰",
    "賦曰",
    "赋曰",
    "頌曰",
    "颂曰",
    "贊曰",
    "赞曰",
    "銘曰",
    "铭曰",
    "箴曰",
    "謌曰",
    "歌曰",
)
SOURCE_HINTS = (
    "類聚",
    "类聚",
    "初學記",
    "初学记",
    "北堂",
    "書鈔",
    "书钞",
    "御覽",
    "御览",
    "文選",
    "文选",
    "藝文",
    "艺文",
    "群書",
    "群书",
)
PUNCT_STRIP = " ，。,.、；;：:「」『』（）()[]【】"
CN_NUM = "一二三四五六七八九十百千〇零壹貳參肆伍陸柒捌玖拾佰仟"


def now_iso() -> str:
    return dt.datetime.now(dt.timezone.utc).astimezone().isoformat(timespec="seconds")


def fetch_text(url: str, timeout: int, retries: int, user_agent: str) -> str:
    headers = {
        "User-Agent": user_agent,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    }
    last_error: Exception | None = None
    for attempt in range(retries + 1):
        request = urllib.request.Request(url, headers=headers)
        try:
            with urllib.request.urlopen(request, timeout=timeout) as response:
                return response.read().decode("utf-8", "replace")
        except (urllib.error.URLError, TimeoutError) as exc:
            last_error = exc
            if attempt < retries:
                time.sleep(1.5 * (attempt + 1))
    raise RuntimeError(f"抓取失败：{url}；原因：{last_error}") from last_error


def extract_router_data(html: str) -> dict[str, Any]:
    match = ROUTER_DATA_RE.search(html)
    if not match:
        raise ValueError("页面中未找到 window._ROUTER_DATA。")
    return json.loads(match.group(1))


def book_payload(router_data: dict[str, Any]) -> dict[str, Any]:
    loader = router_data.get("loaderData", {})
    key = "__session/(lang$)/book/$"
    if key not in loader:
        raise KeyError(f"ROUTER_DATA 缺少 {key}")
    return loader[key]


def text_from_name(parts: list[dict[str, Any]] | None) -> str:
    return "".join(str(part.get("content", "")) for part in parts or []).strip()


def clean_text(text: str) -> str:
    return re.sub(r"\s+", "", text or "")


def strip_punct(text: str) -> str:
    return clean_text(text).strip(PUNCT_STRIP)


def safe_filename(order: int, name: str, suffix: str) -> str:
    cleaned = re.sub(r'[<>:"/\\|?*\x00-\x1f]', "_", strip_punct(name) or "未命名")
    cleaned = cleaned[:80].rstrip(" .")
    return f"{order:03d}_{cleaned}{suffix}"


def chapter_url(book_id: str, chapter_id: str, version: int) -> str:
    return f"https://www.shidianguji.com/book/{book_id}/chapter/{chapter_id}?version={version}"


def summarize_book_info(book_info: dict[str, Any]) -> dict[str, Any]:
    return {
        "book_id": book_info.get("bookId"),
        "book_name": book_info.get("bookName"),
        "version": book_info.get("version"),
        "authors": book_info.get("authors", []),
        "dynasty": book_info.get("dynastyCategoryName"),
        "image_source": book_info.get("imageSource"),
        "total_page": book_info.get("totalPage"),
    }


def catalog_from_book_info(book_info: dict[str, Any]) -> list[dict[str, Any]]:
    chapters = []
    for order, chapter in enumerate(book_info.get("catalog", {}).get("chapters", []), start=1):
        chapters.append(
            {
                "order": order,
                "chapter_id": chapter.get("chapterId"),
                "chapter_name": text_from_name(chapter.get("chapterName")),
                "chapter_level": chapter.get("chapterLevel"),
                "chapter_type": chapter.get("chapterType"),
                "paragraph_count": chapter.get("paragraphCount"),
                "start_page_num": chapter.get("startPageNum"),
                "end_page_num_without_subchapter": chapter.get("endPageNumWithoutSubchapter"),
                "volume_id": chapter.get("volumeId"),
                "volume_version": chapter.get("volumeVersion"),
            }
        )
    return chapters


def parse_paragraphs(payload: dict[str, Any]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    paragraphs: list[dict[str, Any]] = []
    raw_lines: list[dict[str, Any]] = []
    for paragraph in payload.get("paragraphList", []):
        try:
            content = json.loads(paragraph.get("content") or "{}")
        except json.JSONDecodeError:
            content = {"lines": [], "parse_error": True, "raw_content": paragraph.get("content")}
        parsed_lines = []
        for line in content.get("lines", []):
            line_type = line.get("lineType")
            page_id = None
            page_pass = line.get("pagePass")
            if isinstance(page_pass, dict):
                page_id = page_pass.get("PageId")
            record = {
                "paragraph_id": paragraph.get("paragraphId"),
                "paragraph_order": paragraph.get("inChapterOrder"),
                "line_id": line.get("lineId"),
                "line_num": line.get("lineNum"),
                "line_type": line_type,
                "line_type_label": LINE_TYPE_LABELS.get(line_type, "未知"),
                "content": line.get("content") or "",
                "page_id": page_id,
                "start_page_id": paragraph.get("startPageId"),
                "end_page_id": paragraph.get("endPageId"),
            }
            parsed_lines.append(record)
            raw_lines.append(record)
        paragraphs.append(
            {
                "paragraph_id": paragraph.get("paragraphId"),
                "paragraph_order": paragraph.get("inChapterOrder"),
                "paragraph_type": paragraph.get("paragraphType"),
                "start_page_id": paragraph.get("startPageId"),
                "end_page_id": paragraph.get("endPageId"),
                "chapter_order": paragraph.get("chapterOrder"),
                "volume_id": paragraph.get("volumeId"),
                "volume_version": paragraph.get("volumeVersion"),
                "lines": parsed_lines,
                "content_parse_error": bool(content.get("parse_error")),
            }
        )
    return paragraphs, raw_lines


def is_volume_title(text: str) -> bool:
    compact = strip_punct(text)
    return "卷" in compact and ("唐類函" in compact or "唐类函" in compact or len(compact) <= 12)


def extract_category_heading(text: str) -> str:
    compact = strip_punct(text)
    if not compact or compact == "部":
        return ""
    if any(mark in compact for mark in ("曰", "謂", "谓")):
        return ""
    parts = [part for part in re.split(r"[。！？!?，,；;：:]", compact) if part]
    for part in parts or [compact]:
        normalized = part.replace("叩", "部")
        numbered = re.search(rf"([\u3400-\u9fff\U00020000-\U0002ebe0]{{1,8}}部[{CN_NUM}0-9]+)", normalized)
        if numbered:
            return numbered.group(1)
        plain = re.fullmatch(r"([\u3400-\u9fff\U00020000-\U0002ebe0]{1,8}部)", normalized)
        if plain:
            return plain.group(1)
    return ""


def is_category_heading(text: str) -> bool:
    return bool(extract_category_heading(text))


def looks_like_source_note(text: str) -> bool:
    compact = strip_punct(text)
    if not compact or len(compact) > 30:
        return False
    return any(hint in compact for hint in SOURCE_HINTS)


def is_topic_heading(text: str, current_layer: str) -> bool:
    compact = strip_punct(text)
    if not compact or current_layer == "事對":
        return False
    if len(compact) > 14:
        return False
    if any(mark in compact for mark in ("曰", "云", "雲", "謂", "谓", "：", ":")):
        return False
    compact = compact.lstrip("〇○")
    return bool(re.search(rf"[{CN_NUM}0-9]+$", compact))


def split_layer_marker(text: str) -> list[tuple[str, str]]:
    if "事對" in text:
        before, after = text.split("事對", 1)
        parts = []
        if before:
            parts.append(("text", before))
        if after:
            parts.append(("事對", after))
        else:
            parts.append(("事對", ""))
        return parts
    if "事对" in text:
        before, after = text.split("事对", 1)
        parts = []
        if before:
            parts.append(("text", before))
        parts.append(("事對", after))
        return parts
    if text.startswith("詩文") or text.startswith("诗文"):
        return [("詩文", text[2:])]
    return [("text", text)]


def looks_poetry_or_prose(text: str) -> bool:
    compact = clean_text(text)
    return any(marker in compact for marker in STYLE_MARKERS)


def extract_title(text: str, layer: str) -> str:
    compact = strip_punct(text)
    if layer == "事對":
        return compact
    for marker in ("曰", "云", "雲", "謂", "谓", "：", ":"):
        if marker in compact:
            candidate = compact.split(marker, 1)[0]
            if 1 <= len(candidate) <= 18:
                return candidate
    if looks_poetry_or_prose(compact):
        for marker in STYLE_MARKERS:
            if marker in compact:
                candidate = compact.split(marker, 1)[0] + marker[:-1]
                if 1 <= len(candidate) <= 30:
                    return candidate
    return ""


def new_topic(title: str, category: str | None) -> dict[str, Any]:
    return {
        "title": strip_punct(title) or "未分門",
        "category": category,
        "source_notes": [],
        "items": [],
        "layers": [],
    }


def new_item(order: int, layer: str, line: dict[str, Any], title: str = "", text: str = "") -> dict[str, Any]:
    return {
        "order": order,
        "layer": layer,
        "layer_confidence": "explicit" if layer in ("敘事", "事對") else "heuristic",
        "title": title,
        "text": text,
        "notes": [],
        "paragraph_ids": [line.get("paragraph_id")] if line.get("paragraph_id") else [],
        "line_ids": [line.get("line_id")] if line.get("line_id") else [],
        "page_ids": [line.get("page_id") or line.get("start_page_id")] if (line.get("page_id") or line.get("start_page_id")) else [],
        "raw_lines": [line],
    }


def append_unique(values: list[Any], value: Any) -> None:
    if value and value not in values:
        values.append(value)


def append_line_to_item(item: dict[str, Any], line: dict[str, Any], text: str, as_note: bool = False) -> None:
    if as_note:
        item["notes"].append(text)
    else:
        item["text"] = (item.get("text") or "") + text
    append_unique(item["paragraph_ids"], line.get("paragraph_id"))
    append_unique(item["line_ids"], line.get("line_id"))
    append_unique(item["page_ids"], line.get("page_id") or line.get("start_page_id"))
    item["raw_lines"].append(line)


def attach_item(topic: dict[str, Any], item: dict[str, Any] | None) -> None:
    if not item:
        return
    if not (item.get("title") or item.get("text") or item.get("notes")):
        return
    topic["items"].append(item)


def group_layers(topic: dict[str, Any]) -> None:
    groups: dict[str, list[dict[str, Any]]] = {layer: [] for layer in LAYER_ORDER}
    for item in topic["items"]:
        groups.setdefault(item.get("layer") or "未分", []).append(item)
    topic["layers"] = [
        {"name": layer, "items": groups[layer]}
        for layer in LAYER_ORDER
        if groups.get(layer)
    ]


def structure_chapter(chapter: dict[str, Any], payload: dict[str, Any], source_url: str, retrieved_at: str) -> dict[str, Any]:
    paragraphs, raw_lines = parse_paragraphs(payload)
    topics: list[dict[str, Any]] = []
    preamble: list[str] = []
    category_notes: list[str] = []
    category: str | None = None
    category_candidates: list[str] = []
    current_topic: dict[str, Any] | None = None
    current_item: dict[str, Any] | None = None
    current_layer = "敘事"
    item_order = 0
    expect_topic_source = False

    def ensure_topic() -> dict[str, Any]:
        nonlocal current_topic
        if current_topic is None:
            current_topic = new_topic("未分門", category)
            topics.append(current_topic)
        return current_topic

    def finish_item() -> None:
        nonlocal current_item
        if current_item is not None:
            attach_item(ensure_topic(), current_item)
            current_item = None

    def start_main_item(line: dict[str, Any], text: str, layer: str) -> None:
        nonlocal current_item, item_order
        topic = ensure_topic()
        item_order += 1
        title = extract_title(text, layer)
        item_text = "" if layer == "事對" else text
        item = new_item(item_order, layer, line, title=title, text=item_text)
        if layer == "事對":
            item["title"] = strip_punct(text)
        current_item = item
        if topic is None:
            raise RuntimeError("未能创建条目所属门目。")

    def process_main_line(line: dict[str, Any], text: str) -> None:
        nonlocal current_item, current_layer
        if not strip_punct(text):
            return
        layer = "詩文" if (current_layer == "敘事" and looks_poetry_or_prose(text)) else current_layer
        if current_item is None:
            start_main_item(line, text, layer)
            return
        same_para = current_item["paragraph_ids"] and current_item["paragraph_ids"][-1] == line.get("paragraph_id")
        if layer == "事對":
            if current_item.get("layer") == "事對" and not current_item.get("notes"):
                current_item["title"] = strip_punct((current_item.get("title") or "") + text)
                append_line_to_item(current_item, line, "", as_note=False)
            else:
                finish_item()
                start_main_item(line, text, layer)
            return
        starts_new_poem = layer == "詩文" and looks_poetry_or_prose(text) and current_item.get("text")
        if current_item.get("layer") == layer and same_para and not starts_new_poem:
            append_line_to_item(current_item, line, text, as_note=False)
            if not current_item.get("title"):
                current_item["title"] = extract_title(current_item.get("text", ""), layer)
        else:
            finish_item()
            start_main_item(line, text, layer)

    for paragraph in paragraphs:
        for line in paragraph["lines"]:
            text = line.get("content") or ""
            line_type = line.get("line_type")
            if line_type == 3 or not strip_punct(text):
                continue
            if line_type == 1 and is_volume_title(text) and category is None:
                finish_item()
                preamble.append(text)
                continue
            category_heading = extract_category_heading(text) if line_type in (1, 2) and (category is None or current_topic is None) else ""
            if category_heading:
                finish_item()
                category = category_heading
                category_candidates.append(category)
                current_topic = None
                current_layer = "敘事"
                expect_topic_source = False
                if line_type == 2 and strip_punct(text) != category_heading:
                    category_notes.append(text)
                continue
            if line_type == 2 and category and current_topic is None:
                category_notes.append(text)
                continue
            if line_type == 1 and is_topic_heading(text, current_layer):
                finish_item()
                current_topic = new_topic(text, category)
                topics.append(current_topic)
                current_layer = "敘事"
                expect_topic_source = True
                continue
            if line_type == 2 and expect_topic_source and looks_like_source_note(text):
                ensure_topic()["source_notes"].append(text)
                expect_topic_source = False
                continue
            expect_topic_source = False
            if line_type == 2:
                if current_item is None:
                    ensure_topic()["source_notes"].append(text)
                else:
                    append_line_to_item(current_item, line, text, as_note=True)
                continue
            for marker, part in split_layer_marker(text):
                if marker == "text":
                    process_main_line(line, part)
                elif marker == "事對":
                    if part:
                        finish_item()
                    current_layer = "事對"
                    if part:
                        process_main_line(line, part)
                elif marker == "詩文":
                    if part:
                        finish_item()
                    current_layer = "詩文"
                    if part:
                        process_main_line(line, part)
    finish_item()
    for topic in topics:
        group_layers(topic)
    return {
        "source": {
            "url": source_url,
            "retrieved_at": retrieved_at,
            "parser": "scripts/scrape_tang_leihan.py",
        },
        "chapter": chapter,
        "volume": chapter.get("chapter_name"),
        "category": category,
        "category_candidates": category_candidates,
        "category_notes": category_notes,
        "preamble": preamble,
        "topics": topics,
        "raw_paragraph_count": len(paragraphs),
        "raw_line_count": len(raw_lines),
        "raw_lines": raw_lines,
    }


def render_markdown(chapter_doc: dict[str, Any], book: dict[str, Any]) -> str:
    lines: list[str] = []
    chapter = chapter_doc["chapter"]
    lines.append(f"# {chapter.get('chapter_name')}")
    lines.append("")
    lines.append(f"- 書名：{book.get('book_name')}")
    lines.append(f"- 來源：{chapter_doc['source']['url']}")
    lines.append(f"- 抓取時間：{chapter_doc['source']['retrieved_at']}")
    if chapter_doc.get("category"):
        lines.append(f"- 部類：{chapter_doc['category']}")
    if chapter_doc.get("category_notes"):
        lines.append(f"- 部類注文：{' '.join(chapter_doc['category_notes'])}")
    lines.append("")
    if chapter_doc.get("preamble"):
        lines.append("## 卷首信息")
        lines.append("")
        for text in chapter_doc["preamble"]:
            lines.append(text)
        lines.append("")
    for topic in chapter_doc["topics"]:
        category = topic.get("category") or chapter_doc.get("category") or "未分部類"
        lines.append(f"## {category}｜{topic.get('title')}")
        lines.append("")
        if topic.get("source_notes"):
            lines.append(f"來源注文：{' '.join(topic['source_notes'])}")
            lines.append("")
        for layer in topic.get("layers", []):
            lines.append(f"### {layer['name']}")
            lines.append("")
            for item in layer.get("items", []):
                title = item.get("title") or f"條目{item.get('order')}"
                lines.append(f"#### {item.get('order'):04d} {title}")
                lines.append("")
                if item.get("text"):
                    lines.append(item["text"])
                    lines.append("")
                if item.get("notes"):
                    lines.append("注文：")
                    for note in item["notes"]:
                        lines.append(f"> {note}")
                    lines.append("")
                if item.get("line_ids"):
                    lines.append(f"行號：{', '.join(str(x) for x in item['line_ids'] if x)}")
                    lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="抓取并结构化《唐類函》识典古籍页面。")
    parser.add_argument("--source-url", default=DEFAULT_URL, help="任一《唐類函》章节页 URL。")
    parser.add_argument("--output-dir", default="data", help="输出目录。")
    parser.add_argument("--limit", type=int, default=0, help="只抓取前 N 个章节；0 表示全量。")
    parser.add_argument("--start", type=int, default=1, help="从目录序号开始抓取，序号从 1 开始。")
    parser.add_argument("--delay", type=float, default=1.0, help="章节请求间隔秒数。")
    parser.add_argument("--timeout", type=int, default=30, help="单次请求超时秒数。")
    parser.add_argument("--retries", type=int, default=2, help="失败重试次数。")
    parser.add_argument("--user-agent", default="TangLeihanResearchBot/0.1", help="HTTP User-Agent。")
    parser.add_argument("--skip-front-matter", action="store_true", help="跳过卷首和目录章节。")
    parser.add_argument("--no-combined", action="store_true", help="不写出总 JSON。")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    output_dir = Path(args.output_dir)
    retrieved_at = now_iso()
    first_html = fetch_text(args.source_url, args.timeout, args.retries, args.user_agent)
    first_payload = book_payload(extract_router_data(first_html))
    book_info = first_payload["bookInfo"]
    book = summarize_book_info(book_info)
    catalog = catalog_from_book_info(book_info)
    if args.skip_front_matter:
        selected = [
            chapter
            for chapter in catalog
            if "卷" in chapter["chapter_name"]
            and chapter["chapter_name"] != "卷首"
            and "目錄" not in chapter["chapter_name"]
            and "目录" not in chapter["chapter_name"]
        ]
    else:
        selected = catalog
    selected = [chapter for chapter in selected if chapter["order"] >= args.start]
    if args.limit:
        selected = selected[: args.limit]
    write_json(output_dir / "catalog.json", {"source_url": args.source_url, "retrieved_at": retrieved_at, "book": book, "chapters": catalog})

    chapter_docs: list[dict[str, Any]] = []
    book_id = book_info["bookId"]
    version = book_info["version"]
    for index, chapter in enumerate(selected, start=1):
        url = chapter_url(book_id, chapter["chapter_id"], version)
        print(f"[{index}/{len(selected)}] {chapter['chapter_name']} {url}", flush=True)
        if chapter["chapter_id"] == first_payload.get("ssrChapterId"):
            payload = first_payload
        else:
            html = fetch_text(url, args.timeout, args.retries, args.user_agent)
            payload = book_payload(extract_router_data(html))
            if args.delay > 0:
                time.sleep(args.delay)
        chapter_doc = structure_chapter(chapter, payload, url, retrieved_at)
        chapter_docs.append(chapter_doc)
        json_name = safe_filename(chapter["order"], chapter["chapter_name"], ".json")
        md_name = safe_filename(chapter["order"], chapter["chapter_name"], ".md")
        write_json(output_dir / "json" / json_name, chapter_doc)
        write_text(output_dir / "md" / md_name, render_markdown(chapter_doc, book))

    summary = {
        "retrieved_at": retrieved_at,
        "chapter_count": len(chapter_docs),
        "item_count": sum(len(topic.get("items", [])) for doc in chapter_docs for topic in doc.get("topics", [])),
        "raw_line_count": sum(doc.get("raw_line_count", 0) for doc in chapter_docs),
        "outputs": {
            "catalog": str(output_dir / "catalog.json"),
            "json_dir": str(output_dir / "json"),
            "md_dir": str(output_dir / "md"),
            "combined_json": str(output_dir / "tang_leihan.json") if not args.no_combined else None,
        },
    }
    write_json(output_dir / "summary.json", summary)
    if not args.no_combined:
        write_json(output_dir / "tang_leihan.json", {"source_url": args.source_url, "retrieved_at": retrieved_at, "book": book, "chapters": chapter_docs})
    print(json.dumps(summary, ensure_ascii=False, indent=2), flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
