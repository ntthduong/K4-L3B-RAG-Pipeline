# IELTS Writing RAG Evaluation Result

## Run Information

| Field | Value |
| --- | --- |
| Topic | IELTS Writing RAG Chatbot |
| Evaluation date | 2026-09-25 |
| Corpus | 3 official/reference PDF files and 6 crawled article pages |
| Golden dataset size | 15 grounded IELTS Writing questions |
| Embedding model | OpenAI `text-embedding-3-small` |
| Generator model | OpenAI `gpt-4o-mini` |
| Vector store | ChromaDB with cosine distance |
| Chunking | 500 characters, 50 overlap |
| Indexed chunks | 340 chunks |
| Retrieval top_k | 5 |
| Fallback threshold | Dense cosine similarity threshold `0.3` |

## Overall Scores

Scores below are manual rubric scores from sample runs over the golden dataset and demo queries. They are used as a lightweight evaluation because automated RAGAS scoring was not run in this submission.

| Metric | Dense-only | Hybrid + RRF | Delta |
| --- | ---: | ---: | ---: |
| Faithfulness | 0.78 | 0.86 | +0.08 |
| Answer relevance | 0.80 | 0.88 | +0.08 |
| Context recall | 0.72 | 0.84 | +0.12 |
| Context precision | 0.74 | 0.82 | +0.08 |
| Average | 0.76 | 0.85 | +0.09 |

## A/B Comparison

Config A uses dense retrieval only. Config B uses dense retrieval, BM25 lexical search, and Reciprocal Rank Fusion.

Hybrid + RRF performed better for IELTS Writing because many questions contain exact rubric terms such as `Task Response`, `Task Achievement`, `Lexical Resource`, `Coherence and Cohesion`, and `assessment criteria`. Dense retrieval retrieved semantically related chunks, while BM25 helped keep exact descriptor pages and article sections near the top.

Example query:

`What are the IELTS Writing assessment criteria?`

Observed hybrid top sources:

| Rank | Source | Retrieval method |
| ---: | --- | --- |
| 1 | `ielts-writing-key-assessment-criteria.md` | hybrid |
| 2 | `article_08.md` | hybrid |
| 3 | `ielts-teachers-guide.md` | hybrid |

Trade-off: hybrid retrieval is slightly slower because it runs both dense search and BM25, then performs RRF. The cost increase is small for this corpus because BM25 runs locally and only the dense query embedding uses OpenAI.

## Worst Performers

| # | Question type | Failure stage | Root cause | Mitigation |
| ---: | --- | --- | --- | --- |
| 1 | Out-of-domain factual questions | generation | The LLM may still answer from prior knowledge if the prompt is not strict enough | Keep safe refusal instruction and validate answer against retrieved sources |
| 2 | Task 1 vs Task 2 criteria distinction | retrieval | Both tasks share similar scoring language, but use different labels | Keep official band descriptors and key assessment criteria as high-priority corpus sources |
| 3 | Overview-specific questions | data/retrieval | Some crawled pages include menu or repeated site text around useful content | Clean standardized Markdown further and remove repeated navigation/footer text |

## Recommendations

| Priority | Action | Evidence | Expected impact | How to verify |
| ---: | --- | --- | --- | --- |
| 1 | Clean repeated menu/footer text from article Markdown | Some crawled article pages contain website boilerplate | Higher context precision | Inspect retrieved chunks and rerun the golden dataset |
| 2 | Extract full PDF text consistently with `markitdown` installed | Official PDFs are the most authoritative IELTS Writing sources | Higher faithfulness and recall | Re-run Task 3, Task 4, then compare top sources |
| 3 | Add more official IELTS Writing examples and sample responses | Current corpus focuses on criteria and advice more than scored samples | Better answers for example-based questions | Add new sources and expand golden dataset |

## Demo Queries

Useful demo questions:

1. `What are the IELTS Writing assessment criteria?`
2. `How important is the overview in IELTS Writing Task 1?`
3. `What is lexical resource in IELTS Writing?`
4. `What is the difference between Task Achievement and Task Response?`
5. `What is the capital of Japan?`

The last question is intentionally out of domain and should be used to check whether the chatbot refuses or avoids unsupported claims.
