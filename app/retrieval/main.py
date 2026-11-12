import os
import secrets
from typing import List

import psycopg
from fastapi import FastAPI, HTTPException, Header, Depends
from pydantic import BaseModel, Field
from pgvector.psycopg import register_vector


# API key authentication
def verify_api_key(x_api_key: str = Header(...)):
    expected_key = os.environ.get("GDELT_API_KEY")

    if not expected_key or not secrets.compare_digest(
        x_api_key, expected_key
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid or missing API key"
        )


app = FastAPI(
    title="GDELT Article Retrieval API",
    dependencies=[Depends(verify_api_key)]
)


# Request format
class SearchRequest(BaseModel):
    embedding: List[float]
    top_k: int = Field(default=5, ge=1, le=20)


# PostgreSQL connection
def get_connection():
    conn = psycopg.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=os.getenv("DB_PORT", "5432"),
        dbname=os.getenv("DB_NAME", "gdelt_rag"),
        user=os.getenv("DB_USER", "gdelt_user"),
        password=os.environ["DB_PASSWORD"]
    )

    register_vector(conn)
    return conn


# Health check
@app.get("/health")
def health():
    try:
        with get_connection() as conn:
            count = conn.execute(
                "SELECT COUNT(*) FROM gdelt_articles"
            ).fetchone()[0]

        return {
            "status": "ok",
            "database": "connected",
            "total_articles": count
        }

    except Exception:
        raise HTTPException(
            status_code=503,
            detail="Database connection failed"
        )


# Vector similarity search
@app.post("/search")
def search_articles(request: SearchRequest):

    if len(request.embedding) != 1024:
        raise HTTPException(
            status_code=400,
            detail="Expected a 1024-dimensional embedding"
        )

    try:
        query_vector = "[" + ",".join(
            map(str, request.embedding)
        ) + "]"

        with get_connection() as conn:
            rows = conn.execute(
                """
                SELECT
                    article_id,
                    title,
                    content,
                    source_url,
                    source_domain,
                    published_at,
                    country,
                    1 - (embedding <=> %s::vector) AS similarity
                FROM gdelt_articles
                WHERE embedding IS NOT NULL
                ORDER BY embedding <=> %s::vector
                LIMIT %s
                """,
                (
                    query_vector,
                    query_vector,
                    request.top_k
                )
            ).fetchall()

        return {
            "results": [
                {
                    "article_id": row[0],
                    "title": row[1],
                    "content": row[2],
                    "source_url": row[3],
                    "source_domain": row[4],
                    "published_at": str(row[5]) if row[5] else None,
                    "country": row[6],
                    "similarity": float(row[7])
                }
                for row in rows
            ],
            "count": len(rows)
        }

    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Vector search failed"
        )