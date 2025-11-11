"""Utilities to fetch and format daily AI news from AI Hot."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import textwrap
from collections import Counter
from dataclasses import dataclass
from typing import Any, Dict, Iterable, List, Optional, Sequence
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

BASE_URL = "https://aihot.today"
NEWS_PATH = "/ai-news"
DEFAULT_URL = f"{BASE_URL}{NEWS_PATH}"
FALLBACK_URLS = (
    "https://r.jina.ai/https://aihot.today/ai-news",
    "https://r.jina.ai/http://aihot.today/ai-news",
)
DEFAULT_TIMEZONE = dt.timezone(dt.timedelta(hours=8), name="Asia/Shanghai")


@dataclass(slots=True)
class AINewsItem:
    """Normalized representation of an AI news article."""

    title: str
    url: str
    source: Optional[str] = None
    published_at: Optional[dt.datetime] = None
    summary: Optional[str] = None

    def display_time(self, timezone: Optional[dt.tzinfo] = None) -> Optional[str]:
        """Return a formatted timestamp suitable for display."""

        if self.published_at is None:
            return None
        tz = timezone or (self.published_at.tzinfo or DEFAULT_TIMEZONE)
        aware = self.published_at
        if aware.tzinfo is None:
            aware = aware.replace(tzinfo=DEFAULT_TIMEZONE)
        display_time = aware.astimezone(tz)
        fmt = "%Y-%m-%d %H:%M"
        return display_time.strftime(fmt)


def fetch_aihot_daily_html(timeout: float = 30.0, session: Optional[requests.Session] = None) -> str:
    """Fetch the AI Hot news landing page and return the raw HTML."""

    http = session or requests.Session()
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/120.0 Safari/537.36"
        ),
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
    }
    errors: List[str] = []
    for url in (DEFAULT_URL, *FALLBACK_URLS):
        try:
            response = http.get(url, headers=headers, timeout=timeout)
        except requests.RequestException as exc:  # pragma: no cover - network errors
            errors.append(f"{url}: {exc}")
            continue
        if response.ok and response.text.strip():
            return response.text
        errors.append(f"{url}: HTTP {response.status_code}")
    raise RuntimeError(
        "Unable to download AI Hot news page. Attempts: " + "; ".join(errors)
    )


def parse_aihot_daily(html: str) -> List[AINewsItem]:
    """Parse the AI Hot AI news landing page into structured entries."""

    if not html.strip():
        return []
    soup = BeautifulSoup(html, "html.parser")
    items: List[AINewsItem] = []
    seen: set[tuple[str, str]] = set()

    def maybe_add(item: AINewsItem) -> None:
        key = (item.title.strip(), item.url.strip())
        if not item.title.strip() or not item.url.strip():
            return
        if key in seen:
            return
        seen.add(key)
        items.append(item)

    for article in _extract_from_next_data(soup):
        maybe_add(article)
    for article in _extract_from_ld_json(soup):
        maybe_add(article)
    for article in _extract_from_dom_cards(soup):
        maybe_add(article)

    items.sort(
        key=lambda item: (
            item.published_at is not None,
            item.published_at or dt.datetime.min,
        ),
        reverse=True,
    )
    return items


def format_daily_digest(
    items: Sequence[AINewsItem],
    *,
    limit: int = 12,
    report_date: Optional[dt.date] = None,
    timezone: Optional[dt.tzinfo] = DEFAULT_TIMEZONE,
) -> str:
    """Format a collection of news items into a Markdown digest."""

    if not items:
        return "# 🧠 AI Hot 今日 AI 日报\n\n> 今日暂未抓取到新的资讯，请稍后再试。\n"
    if report_date is None:
        now = dt.datetime.now(timezone or DEFAULT_TIMEZONE)
        report_date = now.date()
    header_date = report_date.strftime("%Y-%m-%d (%A)")
    tz = timezone or DEFAULT_TIMEZONE
    lines: List[str] = [f"# 🧠 AI Hot 今日 AI 日报｜{header_date}", ""]
    lines.append("## 🔍 今日速览")
    lines.append("")

    for idx, item in enumerate(items[:limit], start=1):
        lines.append(f"{idx}. **{item.title.strip()}**")
        meta: List[str] = []
        if item.source:
            meta.append(f"来源：{item.source}")
        display_time = item.display_time(tz)
        if display_time:
            meta.append(f"时间：{display_time}")
        if meta:
            lines.append("   " + " | ".join(meta))
        if item.summary:
            wrapped = textwrap.fill(
                item.summary.strip(),
                width=90,
                initial_indent="   ",
                subsequent_indent="   ",
            )
            lines.append(wrapped)
        lines.append(f"   [阅读全文]({item.url})")
        lines.append("")

    sources = [item.source for item in items if item.source]
    if sources:
        lines.append("## 🗞️ 来源统计")
        for source, count in Counter(sources).most_common():
            lines.append(f"- {source}：{count}篇")
        lines.append("")

    remaining = items[limit:]
    if remaining:
        lines.append("## 📚 更多资讯")
        for item in remaining:
            more_meta = []
            display_time = item.display_time(tz)
            if item.source:
                more_meta.append(item.source)
            if display_time:
                more_meta.append(display_time)
            suffix = f"（{'｜'.join(more_meta)}）" if more_meta else ""
            lines.append(f"- [{item.title.strip()}]({item.url}){suffix}")
    lines.append("")
    return "\n".join(lines)


def _extract_from_next_data(soup: BeautifulSoup) -> Iterable[AINewsItem]:
    script = soup.find("script", id="__NEXT_DATA__")
    if not script or not script.string:
        return []
    try:
        data = json.loads(script.string)
    except json.JSONDecodeError:
        return []
    articles: List[Optional[AINewsItem]] = []
    for node in _walk_article_dicts(data):
        articles.append(_build_item_from_dict(node))
    return [item for item in articles if item is not None]


def _walk_article_dicts(obj: Any) -> Iterable[Dict[str, Any]]:
    if isinstance(obj, dict):
        if _looks_like_article(obj):
            yield obj
        for value in obj.values():
            yield from _walk_article_dicts(value)
    elif isinstance(obj, (list, tuple)):
        for value in obj:
            yield from _walk_article_dicts(value)


def _looks_like_article(node: Dict[str, Any]) -> bool:
    if not node:
        return False
    lower = {key.lower(): key for key in node.keys()}
    has_title = any(key in lower for key in ("title", "name"))
    has_url = any(key in lower for key in ("url", "link", "href", "path"))
    return has_title and has_url


def _build_item_from_dict(node: Dict[str, Any]) -> Optional[AINewsItem]:
    lower = {key.lower(): key for key in node.keys()}
    title_key = next((lower[key] for key in ("title", "name") if key in lower), None)
    url_key = next((lower[key] for key in ("url", "link", "href", "path") if key in lower), None)
    if not title_key or not url_key:
        return None
    title = _stringify(node.get(title_key, ""))
    url_raw = _stringify(node.get(url_key, ""))
    if not title or not url_raw:
        return None
    url = urljoin(BASE_URL, url_raw)
    summary = None
    for key in ("summary", "abstract", "description", "excerpt", "digest"):
        if key in lower:
            summary = _stringify(node.get(lower[key]))
            if summary:
                break
    source = None
    for key in ("source", "site", "publisher", "origin"):
        if key in lower:
            raw_source = node.get(lower[key])
            if isinstance(raw_source, dict):
                source = _stringify(
                    raw_source.get("name")
                    or raw_source.get("title")
                    or raw_source.get("brand")
                )
            else:
                source = _stringify(raw_source)
            if source:
                break
    published = None
    for key in ("publishedat", "publishat", "date", "datetime", "published", "time"):
        if key in lower:
            published = _parse_datetime(node.get(lower[key]))
            if published:
                break
    return AINewsItem(
        title=title,
        url=url,
        source=source,
        published_at=published,
        summary=summary,
    )


def _extract_from_ld_json(soup: BeautifulSoup) -> Iterable[AINewsItem]:
    articles: List[AINewsItem] = []
    for script in soup.find_all("script", type="application/ld+json"):
        if not script.string:
            continue
        try:
            data = json.loads(script.string)
        except json.JSONDecodeError:
            continue
        nodes = data if isinstance(data, list) else [data]
        for node in nodes:
            if not isinstance(node, dict):
                continue
            node_type = _stringify(node.get("@type", "")).lower()
            if node_type not in {"newsarticle", "article", "blogposting"}:
                continue
            item = _build_item_from_dict(node)
            if item:
                articles.append(item)
    return articles


def _extract_from_dom_cards(soup: BeautifulSoup) -> Iterable[AINewsItem]:
    articles: List[AINewsItem] = []
    candidates = soup.find_all(["article", "li", "div"], class_=True)
    for candidate in candidates:
        classes = " ".join(candidate.get("class", [])).lower()
        if not any(keyword in classes for keyword in ("news", "card", "item", "post")):
            continue
        link = candidate.find("a", href=True)
        if not link:
            continue
        title = _stringify(link.get_text()) or _stringify(candidate.get("title"))
        if not title:
            continue
        url = urljoin(BASE_URL, link["href"])
        summary = None
        summary_tag = candidate.find(["p", "div"], class_=lambda c: c and "summary" in c.lower())
        if summary_tag:
            summary = _stringify(summary_tag.get_text())
        source = None
        source_tag = candidate.find(["span", "div"], class_=lambda c: c and "source" in c.lower())
        if source_tag:
            source = _stringify(source_tag.get_text())
        time_tag = candidate.find(["time", "span"], attrs={"datetime": True})
        published = None
        if time_tag and time_tag.has_attr("datetime"):
            published = _parse_datetime(time_tag["datetime"])
        elif time_tag:
            published = _parse_datetime(time_tag.get_text())
        articles.append(
            AINewsItem(
                title=title,
                url=url,
                source=source,
                summary=summary,
                published_at=published,
            )
        )
    return articles


def _stringify(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return value.strip()
    if isinstance(value, (list, tuple)):
        return ", ".join(filter(None, (_stringify(v) for v in value)))
    return str(value).strip()


def _parse_datetime(value: Any) -> Optional[dt.datetime]:
    if value is None:
        return None
    if isinstance(value, (int, float)):
        if value > 1e12:
            value /= 1000.0
        try:
            return dt.datetime.fromtimestamp(value, tz=dt.timezone.utc)
        except (OSError, OverflowError, ValueError):
            return None
    text = _stringify(value)
    if not text:
        return None
    text = text.replace("T", " ").replace("Z", "+00:00")
    for fmt in (
        "%Y-%m-%d %H:%M:%S%z",
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d %H:%M%z",
        "%Y-%m-%d %H:%M",
        "%Y/%m/%d %H:%M:%S",
        "%Y/%m/%d %H:%M",
        "%Y-%m-%d",
        "%Y/%m/%d",
    ):
        try:
            parsed = dt.datetime.strptime(text, fmt)
            if parsed.tzinfo is None:
                return parsed.replace(tzinfo=DEFAULT_TIMEZONE)
            return parsed
        except ValueError:
            continue
    try:
        return dt.datetime.fromisoformat(text)
    except ValueError:
        return None


def _parse_timezone(value: str) -> dt.tzinfo:
    if not value:
        return DEFAULT_TIMEZONE
    value = value.strip()
    if not value:
        return DEFAULT_TIMEZONE
    if value.upper() in {"UTC", "Z"}:
        return dt.timezone.utc
    try:
        sign = 1 if value[0] != "-" else -1
        hours, minutes = value.strip("+-").split(":")
        offset = dt.timedelta(hours=int(hours), minutes=int(minutes)) * sign
        return dt.timezone(offset)
    except Exception:  # pragma: no cover - defensive fallback
        return DEFAULT_TIMEZONE


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Generate a daily AI news digest from AI Hot.")
    parser.add_argument("--limit", type=int, default=12, help="Maximum number of highlighted stories.")
    parser.add_argument("--output", type=str, help="Optional path to write the digest Markdown.")
    parser.add_argument("--timezone", type=str, default="+08:00", help="Timezone offset, e.g. +08:00.")
    parser.add_argument("--date", type=str, help="Override the report date (YYYY-MM-DD).")
    parser.add_argument(
        "--html",
        type=str,
        help="Inline HTML content to parse instead of downloading.",
    )
    parser.add_argument(
        "--html-file",
        type=str,
        help="Path to an HTML file to parse without performing a network request.",
    )
    args = parser.parse_args(argv)

    try:
        tzinfo = _parse_timezone(args.timezone)
    except ValueError as exc:
        parser.error(str(exc))

    if args.html_file:
        with open(args.html_file, "r", encoding="utf-8") as file:
            html = file.read()
    elif args.html:
        html = args.html
    else:
        try:
            html = fetch_aihot_daily_html()
        except Exception as exc:  # pragma: no cover - network errors
            parser.error(str(exc))
            return 2
    items = parse_aihot_daily(html)
    report_date = None
    if args.date:
        try:
            report_date = dt.datetime.strptime(args.date, "%Y-%m-%d").date()
        except ValueError:
            parser.error("--date must follow YYYY-MM-DD format")
    digest = format_daily_digest(items, limit=args.limit, report_date=report_date, timezone=tzinfo)
    if args.output:
        with open(args.output, "w", encoding="utf-8") as file:
            file.write(digest)
    else:
        print(digest)
    return 0


if __name__ == "__main__":  # pragma: no cover - CLI entry point
    raise SystemExit(main())
