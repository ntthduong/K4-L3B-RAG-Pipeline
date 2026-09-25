"""
Task 1 — Thu thập tài liệu chính sách/quy định.

Hướng dẫn:
    1. Chọn chủ đề của nhóm.
    2. Tìm tối thiểu 3 tài liệu PDF/DOCX từ nguồn công khai.
    3. Lưu file gốc vào data/landing/legal/.
    4. Đặt tên không dấu và thể hiện đúng nội dung.

Ví dụ tài liệu: học phí, học bổng, ký túc xá, quy trình đăng ký.
Nếu website chặn crawler, hãy chọn nguồn công khai khác; không vượt WAF.
"""

from pathlib import Path
from urllib.parse import unquote, urlparse
from urllib.request import Request, urlopen


DATA_DIR = Path(__file__).parent.parent / "data" / "landing" / "legal"
URL_FILE = Path(__file__).parent.parent / "data" / "crawl" / "url.txt"


def setup_directory() -> None:
    """Tạo thư mục lưu tài liệu gốc."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    print(f"Ready: {DATA_DIR}")


def load_legal_urls() -> list[str]:
    """Read URLs under the legal section in data/crawl/url.txt."""
    if not URL_FILE.exists():
        raise FileNotFoundError(f"Missing URL file: {URL_FILE}")

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
        if section == "legal" and line.startswith(("http://", "https://")):
            urls.append(line)

    if not urls:
        raise ValueError(f"No legal URLs found in {URL_FILE}")
    return urls


def filename_from_url(url: str) -> str:
    """Create a stable local filename from a source URL."""
    path = unquote(urlparse(url).path)
    name = Path(path).name.strip()
    if not name:
        raise ValueError(f"Cannot infer filename from URL: {url}")
    return name.lower().replace(" ", "-")


def download_documents() -> None:
    """Tải ít nhất 3 PDF/DOCX từ nguồn công khai."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    for url in load_legal_urls():
        filename = filename_from_url(url)
        output = DATA_DIR / filename
        if output.exists() and output.stat().st_size > 1024:
            print(f"Exists: {output}")
            continue

        request = Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urlopen(request, timeout=60) as response:
            content = response.read()
        if len(content) <= 1024:
            raise ValueError(f"Downloaded file is too small: {url}")
        output.write_bytes(content)
        print(f"Saved: {output}")


if __name__ == "__main__":
    setup_directory()
    download_documents()
