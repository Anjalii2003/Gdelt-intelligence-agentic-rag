
import json
from pathlib import Path

FILE_PATH = Path("exports/gdelt_latest_30000.jsonl")

EXPECTED_COUNT = 30000
EXPECTED_DIMENSIONS = 1024

print("\nValidating exported dataset...")
print("=" * 50)

total = 0
invalid_json = 0
invalid_embeddings = 0
missing_content = 0
article_ids = set()
duplicate_ids = 0

with open(FILE_PATH, "r", encoding="utf-8") as file:

    for line_number, line in enumerate(file, start=1):

        try:
            record = json.loads(line)
        except json.JSONDecodeError:
            invalid_json += 1
            continue

        total += 1

        article_id = record.get("article_id")

        if article_id is not None:
            if article_id in article_ids:
                duplicate_ids += 1
            article_ids.add(article_id)

        embedding = record.get("embedding")

        if (
            not isinstance(embedding, list)
            or len(embedding) != EXPECTED_DIMENSIONS
        ):
            invalid_embeddings += 1

        if not record.get("content"):
            missing_content += 1

print("\nVALIDATION RESULTS")
print("=" * 50)

print("Total records:", total)
print("Expected records:", EXPECTED_COUNT)
print("Invalid JSON:", invalid_json)
print("Invalid embeddings:", invalid_embeddings)
print("Missing content:", missing_content)
print("Unique article IDs:", len(article_ids))
print("Duplicate article IDs:", duplicate_ids)

print("\nFile size:",
      round(FILE_PATH.stat().st_size / (1024**2), 2), "MB")

if (
    total == EXPECTED_COUNT
    and invalid_json == 0
    and invalid_embeddings == 0
    and missing_content == 0
):
    print("\nSUCCESS: Dataset validation passed!")

else:
    print("\nWARNING: Dataset validation needs attention.")
