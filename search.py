"""Dense-only baseline search over the persistent parts_75192 collection."""

import argparse
import json
from functools import lru_cache

from fastembed import TextEmbedding
from qdrant_client import QdrantClient

from ingest import COLLECTION, MODEL, ROOT


@lru_cache(maxsize=1)
def _encoder():
    return TextEmbedding(model_name=MODEL)


def dense_search(query: str, limit: int = 10) -> list[str]:
    """Return element IDs in descending dense similarity order.

    Uses the ingestion model's query embeddings without aliases, colour filters,
    or design-number filters. Run ingest.py before searching.
    """
    if not query.strip():
        raise ValueError("query must not be blank")
    if limit < 1:
        raise ValueError("limit must be positive")
    client = QdrantClient(path=str(ROOT / "qdrant_storage"))
    try:
        if not client.collection_exists(COLLECTION):
            raise RuntimeError("Run python ingest.py before searching")
        vector = next(_encoder().query_embed(query))
        hits = client.query_points(
            collection_name=COLLECTION,
            query=vector.tolist(),
            limit=limit,
            with_payload=True,
        ).points
        return [hit.payload["element_id"] for hit in hits]
    finally:
        client.close()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("query")
    parser.add_argument("--limit", type=int, default=10)
    args = parser.parse_args()
    print(json.dumps(dense_search(args.query, args.limit), indent=2))


if __name__ == "__main__":
    main()
