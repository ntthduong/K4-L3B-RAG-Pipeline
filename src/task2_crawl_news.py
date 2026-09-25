"""
Task 2 — Crawl bài viết/thông báo.

Hướng dẫn:
    1. Điền tối thiểu 5 URL công khai vào ARTICLE_URLS.
    2. Crawl từng URL bằng Crawl4AI.
    3. Lưu mỗi bài thành một JSON trong data/landing/news/.
    4. Giữ đủ url, title, date_crawled và content_markdown.

Cài browser trước khi chạy:
    python -m playwright install chromium
    
-> Dùng Firecrawl or bất cứ công cụ nào bạn quen    
"""

import asyncio
import json
import re
from datetime import datetime
from html.parser import HTMLParser
from pathlib import Path
from urllib.request import Request, urlopen


DATA_DIR = Path(__file__).parent.parent / "data" / "landing" / "news"
URL_FILE = Path(__file__).parent.parent / "data" / "crawl" / "url.txt"

ARTICLE_URLS: list[str] = []


class ArticleHTMLParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.title = ""
        self._in_title = False
        self._skip_depth = 0
        self._current_tag = ""
        self.parts: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self._current_tag = tag
        if tag == "title":
            self._in_title = True
        if tag in {"script", "style", "noscript", "svg"}:
            self._skip_depth += 1
        if tag in {"p", "h1", "h2", "h3", "li"}:
            self.parts.append("\n")

    def handle_endtag(self, tag: str) -> None:
        if tag == "title":
            self._in_title = False
        if tag in {"script", "style", "noscript", "svg"} and self._skip_depth:
            self._skip_depth -= 1
        if tag in {"p", "h1", "h2", "h3", "li"}:
            self.parts.append("\n")
        self._current_tag = ""

    def handle_data(self, data: str) -> None:
        text = " ".join(data.split())
        if not text:
            return
        if self._in_title:
            self.title += f" {text}"
        elif not self._skip_depth and self._current_tag in {"p", "h1", "h2", "h3", "li"}:
            self.parts.append(text)

    def markdown(self) -> str:
        text = " ".join(self.parts)
        lines = [line.strip() for line in re.split(r"\s*\n\s*", text) if line.strip()]
        return "\n\n".join(lines)


def load_article_urls() -> list[str]:
    """Read URLs under the news section in data/crawl/url.txt."""
    if not URL_FILE.exists():
        return ARTICLE_URLS

    urls: list[str] = []
    section = ""
    for raw_line in URL_FILE.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line:
            continue
        lowered = line.lower().rstrip(":")
        if lowered in {"legal", "news"}:
            section = lowered
            continue
        if section == "news" and line.startswith(("http://", "https://")):
            urls.append(line)
    return urls or ARTICLE_URLS


async def crawl_article(url: str) -> dict:
    request = Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urlopen(request, timeout=30) as response:
        html = response.read().decode("utf-8", errors="replace")

    parser = ArticleHTMLParser()
    parser.feed(html)
    title = " ".join(parser.title.split()) or url.rstrip("/").rsplit("/", 1)[-1]
    content_markdown = parser.markdown()
    if len(content_markdown) < 200:
        raise ValueError("article content is too short")

    return {
        "url": url,
        "title": title,
        "date_crawled": datetime.now().isoformat(),
        "content_markdown": content_markdown,
    }


async def crawl_all() -> None:
    """Crawl và lưu từng bài thành một file JSON."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    for index, url in enumerate(load_article_urls(), 1):
        try:
            article = await crawl_article(url)
            output = DATA_DIR / f"article_{index:02d}.json"
            output.write_text(
                json.dumps(article, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
            print(f"Saved: {output}")
        except Exception as error:
            print(f"Failed: {url} — {error}")


if __name__ == "__main__":
    asyncio.run(crawl_all())
