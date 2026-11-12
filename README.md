\# GDELT Intelligence – Agentic RAG System



\## Overview



An Agentic Retrieval-Augmented Generation (RAG) system designed to answer intelligence-related queries using GDELT news articles.



The system combines semantic search, vector retrieval, cross-encoder reranking, evidence assessment, and claim-level verification through a multi-stage LangGraph-based agentic workflow.



\## Key Features



\- Ingested 30K+ GDELT articles into PostgreSQL.

\- Generated 1,024-dimensional embeddings using BGE-M3.

\- Implemented vector search using PostgreSQL, pgvector, and HNSW indexing.

\- Retrieved Top-20 candidate articles and reranked them to Top-5.

\- Integrated BGE-Reranker-v2-M3 for cross-encoder reranking.

\- Built a six-stage agentic workflow using LangGraph.

\- Integrated Gemini for grounded answer generation.

\- Implemented evidence assessment and a 90-day freshness window.

\- Added claim-level verification against retrieved article contexts.

\- Developed a FastAPI retrieval service and Gradio interface.



\## LangGraph Agentic Workflow



The system uses a six-stage workflow:



1\. \*\*Query Analysis:\*\* Analyzes the user's query and identifies retrieval requirements.

2\. \*\*Vector Retrieval:\*\* Retrieves relevant articles using BGE-M3 embeddings and pgvector.

3\. \*\*Cross-Encoder Reranking:\*\* Reranks the Top-20 retrieved candidates and selects the Top-5 relevant articles.

4\. \*\*Evidence \& Freshness Assessment:\*\* Evaluates supporting evidence, geographic relevance, and article recency.

5\. \*\*Grounded Answer Generation:\*\* Uses Gemini to generate answers based on retrieved article context.

6\. \*\*Claim-Level Verification:\*\* Checks generated claims against the retrieved article evidence.



\## Retrieval Pipeline



\- \*\*Embedding Model:\*\* BGE-M3

\- \*\*Embedding Dimension:\*\* 1,024

\- \*\*Vector Database:\*\* PostgreSQL with pgvector

\- \*\*Indexing:\*\* HNSW

\- \*\*Initial Retrieval:\*\* Top-20

\- \*\*Reranking:\*\* BGE-Reranker-v2-M3

\- \*\*Final Context:\*\* Top-5 articles



\## Evaluation Framework



The evaluation framework covers retrieval quality, ranking performance, and answer generation quality.



| Category | Metric | Purpose |

|---|---|---|

| Retrieval | Precision@K | Measures the relevance of retrieved articles |

| Retrieval | Recall@K | Measures coverage of relevant articles |

| Ranking | MRR | Measures the position of the first relevant result |

| Ranking | nDCG@K | Measures the quality of ranked retrieval results |

| Generation | Faithfulness | Evaluates whether generated answers are supported by retrieved evidence |

| Generation | Answer Relevancy | Evaluates how well answers address the user's query |



Evaluation scores will be reported after benchmark testing.



\## Technology Stack



| Component | Technology |

|---|---|

| Programming Language | Python |

| Agent Orchestration | LangGraph |

| LLM | Gemini |

| Embedding Model | BGE-M3 |

| Reranker | BGE-Reranker-v2-M3 |

| Database | PostgreSQL |

| Vector Search | pgvector, HNSW |

| Backend | FastAPI |

| Interface | Gradio |

| Deployment | Docker |

| Experimentation | Google Colab |



\## Repository Structure



```text

GDELT-Agentic-RAG/

│

├── app/                       # Application and agent workflow

├── database/                  # Database components

├── migration/                 # Database migrations

├── GDELT\_Agentic\_RAG.ipynb    # Google Colab implementation

├── README.md                  # Project documentation

└── .gitignore

```



\## Running the Project



1\. Clone the repository.

2\. Configure the required environment variables.

3\. Set up PostgreSQL with pgvector.

4\. Start the application services using Docker.

5\. Access the FastAPI service and Gradio interface.



Refer to the application configuration and implementation files for detailed setup instructions.



