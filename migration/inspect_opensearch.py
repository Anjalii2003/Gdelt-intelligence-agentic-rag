
import os
from dotenv import load_dotenv
from opensearchpy import OpenSearch

# Load local environment variables
load_dotenv()

# Connect to OpenSearch
client = OpenSearch(
    hosts=[os.getenv("OPENSEARCH_URL")],
    http_auth=(
        os.getenv("OPENSEARCH_USER"),
        os.getenv("OPENSEARCH_PASSWORD")
    ),
    use_ssl=True,
    verify_certs=False,
    ssl_show_warn=False,
    timeout=int(os.getenv("OPENSEARCH_TIMEOUT", 120))
)

index = os.getenv("OPENSEARCH_INDEX")

if not index:
    raise ValueError("OPENSEARCH_INDEX is missing in .env")

# --------------------------------------------------
# 1. Check connection
# --------------------------------------------------

print("\nChecking connection...")

if not client.ping():
    raise RuntimeError("Could not connect to OpenSearch")

print("Connected successfully!")

# --------------------------------------------------
# 2. Get index statistics
# --------------------------------------------------

print("\nIndex statistics:")

stats = client.count(index=index)

print("Requested index:", index)
print("Total documents:", stats["count"])

# --------------------------------------------------
# 3. Read index mapping
# --------------------------------------------------

print("\nReading index mapping...")

mapping = client.indices.get_mapping(index=index)

# Get the actual key returned by OpenSearch.
actual_index_name = next(iter(mapping))

print("Actual mapping key:", actual_index_name)

properties = (
    mapping[actual_index_name]
    .get("mappings", {})
    .get("properties", {})
)

print("\nTop-level fields:")

for field, details in properties.items():

    print(
        field,
        "->",
        details.get("type"),
        "dimensions:",
        details.get("dimension")
    )

    # Display nested object fields
    if "properties" in details:
        for nested_field, nested_details in details["properties"].items():
            print(
                f"    {field}.{nested_field}",
                "->",
                nested_details.get("type"),
                "dimensions:",
                nested_details.get("dimension")
            )

# --------------------------------------------------
# 4. Read one sample document containing embedding
# --------------------------------------------------

print("\nFetching one sample document with embedding...")

response = client.search(
    index=index,
    body={
        "size": 1,
        "_source": True,
        "query": {
            "exists": {
                "field": "embedding"
            }
        }
    }
)

hits = response["hits"]["hits"]

if not hits:

    print("No documents with an embedding field found.")

else:

    doc = hits[0]

    print("\nDocument ID:", doc["_id"])

    print("\nAvailable document fields:")

    for key, value in doc["_source"].items():

        if isinstance(value, list):

            print(key, "-> list, length:", len(value))

        elif isinstance(value, dict):

            print(key, "-> object")

            for nested_key, nested_value in value.items():
                print(
                    f"    {key}.{nested_key}",
                    "->",
                    type(nested_value).__name__
                )

        else:

            print(key, "->", type(value).__name__)

    # Inspect embedding dimensions without printing article content
    embedding = doc["_source"].get("embedding")

    if isinstance(embedding, list):

        print("\nEmbedding dimensions:", len(embedding))
        print("First 5 embedding values:", embedding[:5])

    else:

        print("\nEmbedding is not stored as a list in the returned source.")

# --------------------------------------------------
# 5. Finish
# --------------------------------------------------

print("\nInspection completed successfully.")

# Close the client connection
client.close()
