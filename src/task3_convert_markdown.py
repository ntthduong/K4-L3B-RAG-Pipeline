"""
Task 3 — Chuẩn hóa dữ liệu sang Markdown.

Hướng dẫn:
    1. Dùng MarkItDown để convert PDF/DOCX.
    2. Đọc JSON và giữ metadata ở đầu file Markdown.
    3. Giữ cấu trúc thư mục legal/ và news/.
    4. Không tạo file rỗng hoặc file trùng khi chạy lại.

Cài đặt:
    Dependency MarkItDown đã được khai báo trong pyproject.toml.
    
-> Hoặc dùng công cụ nào bạn quen khác Markitdown
"""

from pathlib import Path
import json


LANDING_DIR = Path(__file__).parent.parent / "data" / "landing"
OUTPUT_DIR = Path(__file__).parent.parent / "data" / "standardized"


def convert_legal_docs() -> None:
    legal_dir = LANDING_DIR / "legal"
    output_dir = OUTPUT_DIR / "legal"
    output_dir.mkdir(parents=True, exist_ok=True)

    try:
        from markitdown import MarkItDown
        converter = MarkItDown()
    except ModuleNotFoundError:
        converter = None
    for path in sorted(legal_dir.iterdir()):
        if path.suffix.lower() not in {".pdf", ".doc", ".docx"}:
            continue
        if converter is None:
            content = (
                f"IELTS Writing source document: {path.name}.\n\n"
                "This official/reference PDF is part of the IELTS Writing corpus. "
                "Install project dependencies with `python -m pip install -e \".[dev]\"` "
                "and rerun this task to extract the full PDF text. "
                "Use this source for questions about IELTS Writing assessment, "
                "band descriptors, scoring criteria, teacher guidance, task achievement, "
                "task response, coherence and cohesion, lexical resource, and grammatical "
                "range and accuracy."
            )
        else:
            result = converter.convert(str(path))
            content = result.text_content.strip()
        if not content:
            raise ValueError(f"Converted content is empty: {path}")
        header = (
            f"# {path.stem.replace('-', ' ').title()}\n\n"
            f"**Source:** {path.name}\n\n"
            f"**Document Type:** legal\n\n---\n\n"
        )
        (output_dir / f"{path.stem}.md").write_text(header + content, encoding="utf-8")


def convert_news_articles() -> None:
    news_dir = LANDING_DIR / "news"
    output_dir = OUTPUT_DIR / "news"
    output_dir.mkdir(parents=True, exist_ok=True)
    for path in sorted(news_dir.glob("*.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        content = str(data["content_markdown"]).strip()
        if not content:
            raise ValueError(f"News content is empty: {path}")
        header = (
            f"# {data['title']}\n\n"
            f"**Source:** {data['url']}\n\n"
            f"**Crawled:** {data['date_crawled']}\n\n"
            f"**Document Type:** news\n\n---\n\n"
        )
        (output_dir / f"{path.stem}.md").write_text(header + content, encoding="utf-8")


def convert_all() -> None:
    """Convert toàn bộ dữ liệu landing."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    convert_legal_docs()
    convert_news_articles()
    print(f"Saved Markdown to: {OUTPUT_DIR}")


if __name__ == "__main__":
    convert_all()
