"""Index the supplied LEGO inventory and search it with local embeddings."""

import argparse
import csv
import json
from pathlib import Path
from uuid import NAMESPACE_URL, uuid5

from fastembed import TextEmbedding
from qdrant_client import QdrantClient, models

ROOT = Path(__file__).resolve().parent
COLLECTION = "lego_parts"
MODEL = "BAAI/bge-small-en-v1.5"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=["index", "search"])
    parser.add_argument("query", nargs="?")
    args = parser.parse_args()
    if args.command == "search" and not args.query:
        parser.error("search requires a query")

    client = QdrantClient(path=str(ROOT / "qdrant_storage"))
    try:
        if args.command == "search" and not client.collection_exists(COLLECTION):
            parser.error("run 'python brick_search.py index' first")
        encoder = TextEmbedding(model_name=MODEL)
        if args.command == "index":
            with (ROOT / "data/rebrickable_75192_parts_list.csv").open(
                encoding="utf-8-sig", newline=""
            ) as source:
                rows = list(csv.DictReader(source))
            documents = [
                f"{r['part_name']}; color {r['colour_name']}; "
                f"category {r['part_category']}; design {r['design_number']}; "
                f"element {r['element_id']}"
                for r in rows
            ]
            vectors = list(encoder.embed(documents))
            if not client.collection_exists(COLLECTION):
                client.create_collection(
                    COLLECTION,
                    vectors_config=models.VectorParams(
                        size=len(vectors[0]), distance=models.Distance.COSINE
                    ),
                )
            client.upsert(
                COLLECTION,
                points=[
                    models.PointStruct(
                        id=str(uuid5(NAMESPACE_URL, json.dumps(row, sort_keys=True))),
                        vector=vector.tolist(),
                        payload=row,
                    )
                    for row, vector in zip(rows, vectors, strict=True)
                ],
            )
            print(f"Indexed {len(rows)} inventory rows.")
        else:
            vector = next(encoder.query_embed(args.query))
            hits = client.query_points(
                COLLECTION, query=vector.tolist(), limit=5
            ).points
            print(json.dumps([
                {"score":hit.score, "part":hit.payload} for hit in hits
            ], indent=2))

    finally:
        client.close()


if __name__ == "__main__":
    main()
