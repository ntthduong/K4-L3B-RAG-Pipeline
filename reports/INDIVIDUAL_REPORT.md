# Individual contribution report

## Thông tin

- Họ và tên: Nguyễn Thị Thùy Dương
- Mã học viên: 2A202602905
- Nhóm: MotMinhTui
- Repository/branch: ntthduong/K4-L3B-RAG-Pipeline
- Chủ đề: IELTS Writing RAG Chatbot

## Phần việc đã thực hiện

| Module/deliverable | Việc tôi trực tiếp làm | File/commit/PR | Trạng thái |
|---|---|---|---|
| Data collection | Chuẩn bị 3 PDF IELTS Writing và danh sách URL article theo nhóm `legal`/`news` | `data/crawl/url.txt`, `data/landing/legal/*.pdf` | Done |
| Task 1 | Implement script đọc URL legal và tải PDF vào landing folder | `src/task1_collect_legal_docs.py` | Done |
| Task 2 | Implement crawler đọc phần `news:` trong `url.txt` và lưu JSON đúng schema | `src/task2_crawl_news.py`, `data/landing/news/*.json` | Done |
| Task 3 | Convert PDF/JSON sang Markdown chuẩn hóa, có fallback khi thiếu dependency | `src/task3_convert_markdown.py`, `data/standardized/**/*.md` | Done |
| Task 4 | Load documents, chunk, embed bằng OpenAI, index vào ChromaDB | `src/task4_chunking_indexing.py` | Done |
| Task 5-7 | Implement dense search, BM25 search và RRF hybrid reranking | `src/task5_semantic_search.py`, `src/task6_lexical_search.py`, `src/task7_reranking.py` | Done |
| Task 8-9 | Implement fallback search an toàn và retrieval pipeline hybrid | `src/task8_pageindex_vectorless.py`, `src/task9_retrieval_pipeline.py` | Done |
| Task 10 | Implement OpenAI generation có citation và safe refusal | `src/task10_generation.py` | Done |
| Streamlit UI | Tích hợp chatbot UI, hiển thị answer, sources, score và method | `app.py` | Done |
| Evaluation | Tạo golden dataset 15 câu và báo cáo evaluation | `group_project/evaluation/golden_dataset.json`, `group_project/evaluation/RESULT.md` | Done |

## Quyết định kỹ thuật quan trọng

1. **Quyết định:** Dùng OpenAI `text-embedding-3-small` cho embedding và ChromaDB cosine distance cho vector store.  
   **Lý do/evidence:** Corpus IELTS Writing nhỏ, cần embedding ổn định và dễ tái tạo với Task 5 semantic search. Query `What are the IELTS Writing assessment criteria?` trả top source đúng là `ielts-writing-key-assessment-criteria.md`.  
   **Trade-off:** Có chi phí API và cần `.env` có `OPENAI_API_KEY`, nhưng chất lượng retrieval tốt hơn so với tự cấu hình local model trong thời gian ngắn.

2. **Quyết định:** Dùng hybrid retrieval gồm dense search, BM25 và RRF.  
   **Lý do/evidence:** IELTS Writing có nhiều thuật ngữ chính xác như `Task Response`, `Task Achievement`, `Lexical Resource`, `Coherence and Cohesion`; BM25 giúp bắt exact keyword, dense giúp bắt ngữ nghĩa.  
   **Trade-off:** Pipeline chậm hơn dense-only một chút, nhưng BM25 và RRF chạy local nên chi phí tăng không đáng kể.

## Kiểm thử và kết quả

- Test đã dùng:
  - `pytest tests/test_contracts.py -q`
  - `pytest tests/test_acceptance.py -q`
  - `pytest -q`
- Kết quả cuối:
  - `20 passed`
- Query dense search đã kiểm tra:
  - `What are the IELTS Writing assessment criteria?`
  - Top 3 dense sources: `ielts-writing-key-assessment-criteria.md`, `article_08.md`, `ielts-teachers-guide.md`
- Query hybrid retrieval đã kiểm tra:
  - `What are the IELTS Writing assessment criteria?`
  - Top hybrid sources: `ielts-writing-key-assessment-criteria.md`, `article_08.md`, `ielts-teachers-guide.md`, `article_06.md`, `article_03.md`
- Lỗi đã phát hiện và cách xử lý:
  - Một số URL British Council bị timeout khi crawl, nên crawler vẫn lưu các article crawl được; 6 article thành công, đủ yêu cầu tối thiểu 5 article.
  - Môi trường có thể thiếu `markitdown` hoặc `langchain_text_splitters`, nên Task 3 và Task 4 có fallback để pipeline không bị chặn.
  - PageIndex thật chưa được tích hợp, nên Task 8 dùng fallback local an toàn và không làm UI crash.

## Điều còn hạn chế

- Một hạn chế cụ thể của phần tôi làm: Một số Markdown crawl từ website có thể còn menu, footer hoặc boilerplate, làm giảm context precision trong vài query.
- Nếu có thêm thời gian, thay đổi đầu tiên tôi sẽ thực hiện: Viết bước cleaning mạnh hơn trong Task 3 để loại bỏ navigation/footer lặp lại, sau đó rerun Task 4 để index lại corpus sạch hơn.

## Xác nhận đóng góp

Tôi xác nhận nội dung trên phản ánh đúng phần việc của mình và có thể giải thích hoặc chạy lại trong buổi demo.

- Ngày: 2026-09-25
- Tên thành viên: Nguyễn Thị Thùy Dương
