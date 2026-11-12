
import os
import json
import time
from pathlib import Path

from dotenv import load_dotenv
from opensearchpy import OpenSearch

# --------------------------------------------------
# 1. Configuration
# --------------------------------------------------

load_dotenv()

OPENSEARCH_URL = os.getenv("OPENSEARCH_URL")
OPENSEARCH_INDEX = os.getenv("OPENSEARCH_INDEX")
OPENSEARCH_USER = os.getenv("OPENSEARCH_USER")
OPENSEARCH_PASSWORD = os.getenv("OPENSEARCH_PASSWORD")

EXPORT_LIMIT = int(os.getenv("EXPORT_LIMIT", 30000))
BATCH_SIZE = int(os.getenv("EXPORT_BATCH_SIZE", 500))
OUTPUT_FILE = Path(
    os.getenv(
        "EXPORT_OUTPUT",
        "exports/gdelt_latest_30000.jsonl"
    )
)

SCROLL_TIMEOUT = "2m"
EXPECTED_EMBEDDING_DIMENSIONS = 1024

if not all([
    OPENSEARCH_URL,
    OPENSEARCH_INDEX,
    OPENSEARCH_USER,
    OPENSEARCH_PASSWORD
]):
    raise ValueError("Missing OpenSearch configuration in .env")

# --------------------------------------------------
# 2. Connect to OpenSearch
# --------------------------------------------------

client = OpenSearch(
    hosts=[OPENSEARCH_URL],
    http_auth=(OPENSEARCH_USER, OPENSEARCH_PASSWORD),
    use_ssl=True,
    verify_certs=False,
    ssl_show_warn=False,
    timeout=120,
    max_retries=3,
    retry_on_timeout=True
)

print("\nConnecting to OpenSearch...")

if not client.ping():
    raise RuntimeError("OpenSearch connection failed.")

print("Connected successfully.")
print("Index:", OPENSEARCH_INDEX)

# --------------------------------------------------
# 3. Prepare local output
# --------------------------------------------------

OUTPUT_FILE.parent.mkdir(
    parents=True,
    exist_ok=True
)

# Write to a temporary file first.
# Rename only after successful completion.
TEMP_FILE = OUTPUT_FILE.with_suffix(
    OUTPUT_FILE.suffix + ".partial"
)

if TEMP_FILE.exists():
    TEMP_FILE.unlink()

print("\nExport configuration")
print("-----------------------------")
print("Target documents:", EXPORT_LIMIT)
print("Batch size:", BATCH_SIZE)
print("Sort field: ingested_at DESC")
print("Output:", OUTPUT_FILE)

# --------------------------------------------------
# 4. Read-only search query
# --------------------------------------------------

query = {
    "size": BATCH_SIZE,

   

    "_source": True,

    "query": {
        "bool": {
            "filter": [
                {"exists": {"field": "embedding"}},
                {"exists": {"field": "content"}},
                {"exists": {"field": "title"}},
                {"exists": {"field": "ingested_at"}}
            ]
        }
    },

    "sort": [
        {
            "ingested_at": {
                "order": "desc"
            }
        }
    ]
}

# --------------------------------------------------
# 5. Start export
# --------------------------------------------------

scroll_id = None
exported_count = 0
invalid_embeddings = 0
start_time = time.time()

try:

    print("\nStarting export...")

    response = client.search(
        index=OPENSEARCH_INDEX,
        body=query,
        params={
            "scroll": SCROLL_TIMEOUT
        }
    )

    scroll_id = response.get("_scroll_id")

    with open(
        TEMP_FILE,
        "w",
        encoding="utf-8"
    ) as output:

        while exported_count < EXPORT_LIMIT:

            hits = response["hits"]["hits"]

            if not hits:
                break

            for hit in hits:

                if exported_count >= EXPORT_LIMIT:
                    break

                source = hit.get("_source", {})

                embedding = source.get("embedding")

                # Validate embedding dimensions.
                if (
                    not isinstance(embedding, list)
                    or len(embedding) != EXPECTED_EMBEDDING_DIMENSIONS
                ):
                    invalid_embeddings += 1
                    continue

                # Preserve OpenSearch document ID.
                record = {
                    "_opensearch_id": hit["_id"],
                    **source
                }

                output.write(
                    json.dumps(
                        record,
                        ensure_ascii=False,
                        allow_nan=False
                    ) + "\n"
                )

                exported_count += 1

            output.flush()

            elapsed = time.time() - start_time

            print(
                f"Exported: {exported_count:,}/{EXPORT_LIMIT:,} "
                f"| Invalid embeddings: {invalid_embeddings:,} "
                f"| Time: {elapsed:.1f}s"
            )

            if exported_count >= EXPORT_LIMIT:
                break

            # Retrieve the next batch.
            response = client.scroll(
                body={
                    "scroll": SCROLL_TIMEOUT,
                    "scroll_id": scroll_id
                }
            )

            # Always use the latest returned scroll ID.
            scroll_id = response.get(
                "_scroll_id",
                scroll_id
            )

    # --------------------------------------------------
    # 6. Validate export
    # --------------------------------------------------

    if exported_count != EXPORT_LIMIT:
        raise RuntimeError(
            f"Expected {EXPORT_LIMIT} records, "
            f"but exported {exported_count}."
        )

    # Rename partial file after successful completion.
    os.replace(TEMP_FILE, OUTPUT_FILE)

    elapsed = time.time() - start_time

    print("\nEXPORT COMPLETED")
    print("=============================")
    print("Exported records:", exported_count)
    print("Invalid embeddings:", invalid_embeddings)
    print(f"Time taken: {elapsed:.2f} seconds")
    print(
        "File size:",
        f"{OUTPUT_FILE.stat().st_size / (1024**2):.2f} MB"
    )
    print("Saved to:", OUTPUT_FILE.resolve())

except Exception:

    print("\nExport failed.")
    print("A partial file may remain:", TEMP_FILE.resolve())
    raise

finally:

    # Release the scroll search context.
    if scroll_id:

        try:
            client.clear_scroll(
                scroll_id=scroll_id
            )

            print("\nScroll context closed.")

        except Exception as error:
            print("Could not close scroll context:", error)

    client.close()

print("\nOpenSearch connection closed.")
