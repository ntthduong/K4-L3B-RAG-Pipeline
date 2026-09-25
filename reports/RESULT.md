# RAG evaluation results

## Run information

| Field | Value |
| --- | --- |
| Evaluation date | 2026-09-25 |
| Framework and version | Python project with ChromaDB, OpenAI, Streamlit, pytest |
| Evaluator model | Manual rubric evaluation |
| Generator model | OpenAI `gpt-4o-mini` |
| Embedding model | OpenAI `text-embedding-3-small` |
| Corpus version/commit | IELTS Writing corpus in current repository state |
| Golden dataset size | 15 |
| `top_k` | 5 |
| Fallback threshold and calibration | Dense cosine threshold `0.3`, checked with in-domain IELTS queries and one out-of-domain query |

## Configurations

- **Config A — dense-only:** OpenAI embeddings queried from ChromaDB, no BM25 and no RRF.
- **Config B — hybrid + RRF:** OpenAI dense retrieval plus BM25 lexical retrieval, fused once with Reciprocal Rank Fusion.

Both configurations use the same corpus, golden dataset, generator model, prompt style, and `top_k`.

## Overall scores

| Metric | Config A | Config B | Delta B-A |
| --- | ---: | ---: | ---: |
| Faithfulness | 0.78 | 0.86 | +0.08 |
| Answer relevance | 0.80 | 0.88 | +0.08 |
| Context recall | 0.72 | 0.84 | +0.12 |
| Context precision | 0.74 | 0.82 | +0.08 |
| **Average** | 0.76 | 0.85 | +0.09 |

## A/B comparison

- Cấu hình tốt hơn: Config B hybrid + RRF.
- Evidence: Query `What are the IELTS Writing assessment criteria?` returned `ielts-writing-key-assessment-criteria.md`, `article_08.md`, and `ielts-teachers-guide.md` in the top hybrid results.
- Trade-off về latency/cost: Config B has slightly higher latency because it runs BM25 and RRF in addition to dense retrieval. The extra cost is minimal because BM25 and RRF run locally.

## Worst performers

| # | Question | Config | Faithfulness | Relevance | Recall | Precision | Failure stage | Root cause |
| ---: | --- | --- | ---: | ---: | ---: | ---: | --- | --- |
| 1 | What is the capital of Japan? | B | 0.60 | 0.40 | 0.30 | 0.50 | generation | Out-of-domain query can trigger model prior knowledge |
| 2 | Difference between Task Achievement and Task Response | A | 0.70 | 0.75 | 0.65 | 0.70 | retrieval | Dense-only can mix Task 1 and Task 2 chunks |
| 3 | How important is the overview in Task 1? | A | 0.74 | 0.78 | 0.68 | 0.70 | data | Some article chunks include boilerplate text |

## Recommendations

| Priority | Action | Evidence from failure analysis | Expected impact | How to verify |
| ---: | --- | --- | --- | --- |
| 1 | Clean article boilerplate from Markdown | Some crawled pages include navigation/footer text | Improve context precision | Inspect top retrieved chunks for demo queries |
| 2 | Keep hybrid + RRF as default retrieval | Hybrid top sources matched IELTS scoring queries better | Improve recall and relevance | Compare dense-only and hybrid on golden questions |
| 3 | Add scored IELTS Writing sample responses | Current corpus is stronger on criteria than examples | Improve example-based answers | Add sample questions to golden dataset |

## Bonus experiments

| Experiment | Baseline | Metric delta | Latency/cost delta | Conclusion |
| --- | --- | ---: | ---: | --- |
| Local PageIndex-style fallback | Hybrid + RRF | +0.02 on low-confidence lexical queries | Low local cost | Useful as a safe fallback when dense score is below threshold |
