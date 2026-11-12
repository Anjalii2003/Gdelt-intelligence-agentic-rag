
import os
from dotenv import load_dotenv
from opensearchpy import OpenSearch

load_dotenv()

client = OpenSearch(
    hosts=[os.getenv("OPENSEARCH_URL")],
    http_auth=(
        os.getenv("OPENSEARCH_USER"),
        os.getenv("OPENSEARCH_PASSWORD")
    ),
    use_ssl=True,
    verify_certs=False,
    ssl_show_warn=False,
    timeout=120
)

index = os.getenv("OPENSEARCH_INDEX")

fields = [
    "published_at",
    "updated_at",
    "ingested_at",
    "embedding",
    "content",
    "title"
]

print("\nDATA QUALITY CHECK")
print("=" * 55)

total = client.count(index=index)["count"]

print(f"\nTotal documents: {total:,}")

for field in fields:

    result = client.count(
        index=index,
        body={
            "query": {
                "exists": {
                    "field": field
                }
            }
        }
    )

    count = result["count"]
    missing = total - count
    percentage = (count / total) * 100 if total else 0

    print(f"\nField: {field}")
    print(f"Available: {count:,}")
    print(f"Missing: {missing:,}")
    print(f"Coverage: {percentage:.2f}%")

# Check timestamp ranges
print("\nTIMESTAMP RANGES")
print("=" * 55)

for field in ["published_at", "updated_at", "ingested_at"]:

    result = client.search(
        index=index,
        body={
            "size": 0,
            "aggs": {
                "date_range": {
                    "stats": {
                        "field": field
                    }
                }
            }
        }
    )

    stats = result["aggregations"]["date_range"]

    print(f"\n{field}")
    print("Documents with date:", stats["count"])
    print("Earliest:", stats.get("min_as_string"))
    print("Latest:", stats.get("max_as_string"))

print("\nQuality check completed.")

client.close()
