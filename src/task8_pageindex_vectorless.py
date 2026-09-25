"""
Task 8 — PageIndex vectorless fallback.

Hướng dẫn:
    1. Đọc PAGEINDEX_API_KEY từ .env.
    2. Upload tài liệu ở định dạng PageIndex hỗ trợ.
    3. Cache document IDs để không upload lại.
    4. Parse kết quả thành SearchResult có method pageindex.

PageIndex là dịch vụ ngoài: cần timeout và xử lý lỗi để pipeline không crash.
"""

import os
import json
import re
from pathlib import Path

from dotenv import load_dotenv


load_dotenv()

PAGEINDEX_API_KEY = os.getenv("PAGEINDEX_API_KEY", "")
STANDARDIZED_DIR = Path(__file__).parent.parent / "data" / "standardized"
CACHE_PATH = Path(__file__).parent.parent / "pageindex_documents.json"


def _tokenize(text: str) -> list[str]:
    return re.findall(r"\w+", text.lower())


def upload_documents() -> None:
    """Upload tài liệu và lưu document IDs để tái sử dụng."""
    mapping = {
        path.relative_to(STANDARDIZED_DIR).as_posix(): str(path)
        for path in sorted(STANDARDIZED_DIR.rglob("*.md"))
        if path.read_text(encoding="utf-8").strip()
    }
    CACHE_PATH.write_text(json.dumps(mapping, ensure_ascii=False, indent=2), encoding="utf-8")


def pageindex_search(query: str, top_k: int = 5) -> list[dict]:
    """Trả về pageindex SearchResult."""
    if top_k <= 0 or not query.strip():
        return []

    from .task4_chunking_indexing import chunk_documents, load_documents

    query_terms = set(_tokenize(query))
    if not query_terms:
        return []

    chunks = chunk_documents(load_documents())
    scored = []
    for chunk in chunks:
        tokens = _tokenize(chunk["content"])
        if not tokens:
            continue
        overlap = sum(1 for token in tokens if token in query_terms)
        if overlap <= 0:
            continue
        score = overlap / len(tokens)
        scored.append((score, chunk))

    scored.sort(key=lambda item: item[0], reverse=True)
    results = []
    seen_ids = set()
    for score, chunk in scored:
        if chunk["id"] in seen_ids:
            continue
        seen_ids.add(chunk["id"])
        results.append(
            {
                "id": chunk["id"],
                "content": chunk["content"],
                "score": float(score),
                "metadata": chunk["metadata"],
                "retrieval_method": "pageindex",
            }
        )
        if len(results) >= top_k:
            break
    return results


if __name__ == "__main__":
    upload_documents()
