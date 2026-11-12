\# GDELT Intelligence – Agentic RAG System



An Agentic Retrieval-Augmented Generation (RAG) system designed for intelligence analysis using GDELT news articles. The system combines semantic retrieval, cross-encoder reranking, evidence assessment, and claim-level verification through a multi-stage LangGraph workflow.



\## Project Overview



The system processes GDELT news articles and answers intelligence-related queries using retrieved evidence.



It integrates:

\- Semantic search and vector retrieval.

\- Cross-encoder reranking.

\- Evidence and geographic relevance assessment.

\- Article freshness evaluation.

\- Grounded answer generation.

\- Claim-level verification.



\*\*Dataset:\*\* 30K+ GDELT articles.



\## Key Features



\- BGE-M3 embedding generation with 1,024 dimensions.

\- PostgreSQL with pgvector for vector storage.

\- HNSW indexing for efficient similarity search.

\- Top-20 candidate retrieval followed by Top-5 reranking.

\- BGE-Reranker-v2-M3 cross-encoder integration.

\- Six-stage LangGraph-based agentic workflow.

\- Gemini-powered answer generation.

\- Evidence assessment and a 90-day freshness window.

\- Claim-level verification against retrieved article contexts.

\- FastAPI retrieval service.

\- Gradio interface.



\## Agentic Workflow – LangGraph



The system uses a six-stage workflow orchestrated through LangGraph.



\### 1. Query Analysis

Analyzes the user's question and identifies retrieval requirements.



\### 2. Vector Retrieval

Retrieves relevant GDELT articles using BGE-M3 embeddings and PostgreSQL pgvector.



\### 3. Cross-Encoder Reranking

Reranks the Top-20 retrieved candidates using BGE-Reranker-v2-M3 and selects the Top-5 articles.



\### 4. Evidence and Freshness Assessment

Evaluates retrieved evidence, geographic relevance, and article recency.



\### 5. Grounded Answer Generation

Uses Gemini to generate answers based on retrieved article contexts.



\### 6. Claim-Level Verification

Checks generated claims against retrieved article evidence to identify unsupported statements.



\## Retrieval Architecture



\- \*\*Article Collection:\*\* 30K+ GDELT articles

\- \*\*Embedding Model:\*\* BGE-M3

\- \*\*Embedding Dimensions:\*\* 1,024

\- \*\*Vector Database:\*\* PostgreSQL with pgvector

\- \*\*Indexing:\*\* HNSW

\- \*\*Initial Retrieval:\*\* Top-20

\- \*\*Reranking Model:\*\* BGE-Reranker-v2-M3

\- \*\*Final Context:\*\* Top-5

\- \*\*Freshness Window:\*\* 90 days



\## Evaluation Framework



The evaluation framework covers retrieval performance, ranking quality, and answer generation quality.



\### Retrieval Metrics

\- \*\*Precision@K:\*\* Measures the relevance of retrieved articles.

\- \*\*Recall@K:\*\* Measures the coverage of relevant articles.



\### Ranking Metrics

\- \*\*Mean Reciprocal Rank (MRR):\*\* Measures the position of the first relevant result.

\- \*\*Normalized Discounted Cumulative Gain (nDCG):\*\* Evaluates the quality of ranked retrieval results.



\### Generation Metrics

\- \*\*Faithfulness:\*\* Evaluates whether generated answers are supported by retrieved evidence.

\- \*\*Answer Relevancy:\*\* Measures how well generated answers address user queries.



Evaluation scores will be reported after benchmark testing.



\## Google Colab Implementation



The repository includes a Google Colab notebook containing the implementation and experiments.



\*\*Notebook:\*\* `GDELT\_Agentic\_RAG.ipynb`



The notebook documents the implementation of the Agentic RAG pipeline, including:



\- Article processing and preparation.

\- BGE-M3 embedding generation.

\- PostgreSQL and pgvector integration.

\- Semantic vector retrieval.

\- Cross-encoder reranking.

\- LangGraph agent orchestration.

\- Gemini integration.

\- Evidence assessment.

\- Claim-level verification.

\- Retrieval and generation evaluation methodology.



\## Technology Stack



\- \*\*Programming Language:\*\* Python

\- \*\*Agent Orchestration:\*\* LangGraph

\- \*\*LLM:\*\* Gemini

\- \*\*Embedding Model:\*\* BGE-M3

\- \*\*Reranker:\*\* BGE-Reranker-v2-M3

\- \*\*Database:\*\* PostgreSQL

\- \*\*Vector Search:\*\* pgvector and HNSW

\- \*\*Backend:\*\* FastAPI

\- \*\*Interface:\*\* Gradio

\- \*\*Deployment:\*\* Docker

\- \*\*Experimentation:\*\* Google Colab



\## Repository Structure



```text

GDELT-Agentic-RAG/

│

├── app/

│   └── Application logic and agent workflow

│

├── database/

│   └── Database components

│

├── migration/

│   └── Database migration scripts

│

├── GDELT\_Agentic\_RAG.ipynb

│   └── Google Colab implementation

│

├── README.md

│

├── requirements.txt

│

└── .gitignore

```



\## Setup and Execution



1\. Clone the repository.

2\. Create a Python virtual environment.

3\. Install the required dependencies from `requirements.txt`.

4\. Configure environment variables.

5\. Set up PostgreSQL with pgvector.

6\. Start the application services using Docker.

7\. Access the FastAPI backend and Gradio interface.



Refer to the application configuration and implementation files for detailed execution instructions.





