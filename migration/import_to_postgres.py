
import json
import time
from pathlib import Path

import psycopg2
from psycopg2.extras import execute_values, Json
from pgvector.psycopg2 import register_vector

# -----------------------------------------
# Configuration
# -----------------------------------------

INPUT_FILE = Path("exports/gdelt_latest_30000.jsonl")
BATCH_SIZE = 500

DB_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "database": "gdelt_rag",
    "user": "gdelt_user",
    "password": "change_this_local_password"
}

# -----------------------------------------
# Connect to PostgreSQL
# -----------------------------------------

print("Connecting to PostgreSQL...")

conn = psycopg2.connect(**DB_CONFIG)
register_vector(conn)

print("Connected successfully.")

# -----------------------------------------
# Check existing records
# -----------------------------------------

with conn.cursor() as cur:
    cur.execute("SELECT COUNT(*) FROM gdelt_articles")
    existing_count = cur.fetchone()[0]

print("Existing records:", existing_count)

if existing_count > 0:
    conn.close()
    raise RuntimeError(
        "Target table is not empty. Stopping to avoid "
        "mixing datasets. Inspect the existing records first."
    )

# -----------------------------------------
# Insert query
# -----------------------------------------

insert_query = """
INSERT INTO gdelt_articles (
    article_id,
    title,
    content,
    source_url,
    source_domain,
    published_at,
    country,
    entities,
    embedding,
    embedding_model,
    summary,
    language,
    author,
    category,
    tags,
    gdelt,
    gkg,
    mentions,
    metadata,
    published_at_confidence,
    published_at_precision,
    published_at_source,
    published_at_raw,
    updated_at,
    ingested_at,
    opensearch_id,
    source_table,
    embedding_truncated
)
VALUES %s
ON CONFLICT (article_id) DO NOTHING
"""

# -----------------------------------------
# Convert JSONL records into SQL values
# -----------------------------------------

def convert_record(record):

    gkg = record.get("gkg") or {}

    entities = {
        "persons": gkg.get("persons", []),
        "organizations": gkg.get("organizations", []),
        "all_names": gkg.get("all_names", [])
    }

    embedding = record.get("embedding")

    if not isinstance(embedding, list) or len(embedding) != 1024:
        raise ValueError(
            f"Invalid embedding for article {record.get('article_id')}"
        )

    article_id = record.get("article_id")

    if article_id is None:
        raise ValueError("Article is missing article_id")

    return (
        str(article_id),
        record.get("title"),
        record.get("content"),
        record.get("url"),
        record.get("source_domain"),
        record.get("published_at"),
        record.get("country"),
        Json(entities),
        embedding,
        record.get("embedding_model"),
        record.get("summary"),
        record.get("language"),
        record.get("author"),
        record.get("category"),
        Json(record.get("tags")) if record.get("tags") is not None else None,
        Json(record.get("gdelt")) if record.get("gdelt") is not None else None,
        Json(gkg) if record.get("gkg") is not None else None,
        Json(record.get("mentions")) if record.get("mentions") is not None else None,
        Json(record.get("metadata")) if record.get("metadata") is not None else None,
        record.get("published_at_confidence"),
        record.get("published_at_precision"),
        record.get("published_at_source"),
        record.get("published_at_raw"),
        record.get("updated_at"),
        record.get("ingested_at"),
        record.get("_opensearch_id"),
        record.get("source_table"),
        record.get("embedding_truncated")
    )

# -----------------------------------------
# Batch import
# -----------------------------------------

total_processed = 0
total_inserted = 0
start_time = time.time()

batch = []

try:

    with open(INPUT_FILE, "r", encoding="utf-8") as file:

        for line_number, line in enumerate(file, start=1):

            record = json.loads(line)
            batch.append(convert_record(record))

            if len(batch) >= BATCH_SIZE:

                with conn.cursor() as cur:

                    execute_values(
                        cur,
                        insert_query,
                        batch,
                        page_size=BATCH_SIZE
                    )

                    total_inserted += cur.rowcount

                conn.commit()

                total_processed += len(batch)
                batch.clear()

                print(
                    f"Processed: {total_processed:,}/30,000 "
                    f"| Inserted: {total_inserted:,}"
                )

        # Insert remaining records
        if batch:

            with conn.cursor() as cur:

                execute_values(
                    cur,
                    insert_query,
                    batch,
                    page_size=BATCH_SIZE
                )

                total_inserted += cur.rowcount

            conn.commit()

            total_processed += len(batch)

    # -------------------------------------
    # Final verification
    # -------------------------------------

    with conn.cursor() as cur:

        cur.execute("SELECT COUNT(*) FROM gdelt_articles")
        final_count = cur.fetchone()[0]

        cur.execute("""
            SELECT COUNT(*)
            FROM gdelt_articles
            WHERE embedding IS NOT NULL
        """)

        embedding_count = cur.fetchone()[0]

    elapsed = time.time() - start_time

    print("\nIMPORT COMPLETED")
    print("=" * 45)
    print("Processed:", total_processed)
    print("Inserted:", total_inserted)
    print("Database total:", final_count)
    print("Records with embeddings:", embedding_count)
    print(f"Time taken: {elapsed:.2f} seconds")

except Exception:

    conn.rollback()
    print("\nImport failed. Last uncommitted batch rolled back.")
    raise

finally:

    conn.close()
    print("\nPostgreSQL connection closed.")
