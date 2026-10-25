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


def group_elements(rows):
    """Keep one searchable element, preserving every inventory occurrence."""
    elements = {}
    for row in rows:
        element_id = row["element_id"].strip()
        if not element_id:
            raise ValueError("Inventory row has an empty element_id")
        spare = row["is_spare"].strip().lower()
        if spare not in {"true", "false"}:
            raise ValueError(f"Invalid is_spare for {element_id}: {spare}")
        quantity = int(row["quantity_in_set"])
        if quantity < 0:
            raise ValueError(f"Negative quantity for {element_id}")
        if element_id not in elements:
            elements[element_id] = {
                key: row[key] for key in (
                    "design_number", "part_name", "colour_id", "colour_name",
                    "part_category",
                )
            }
            elements[element_id].update(
                element_id=element_id, regular_quantity=0, spare_quantity=0,
                inventory_rows=[],
            )
        element = elements[element_id]
        field = "spare_quantity" if spare == "true" else "regular_quantity"
        element[field] += quantity
        element["inventory_rows"].append(dict(row))
    return list(elements.values())


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
            elements = group_elements(rows)
            if not elements:
                raise ValueError("Inventory is empty")
            documents = [
                f"{r['part_name']}; color {r['colour_name']}; "
                f"category {r['part_category']}; design {r['design_number']}; "
                f"element {r['element_id']}"
                for r in elements
            ]
            vectors = list(encoder.embed(documents))
            # Rebuild the managed inventory collection to remove old row-based IDs.
            if client.collection_exists(COLLECTION):
                client.delete_collection(COLLECTION)
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
                        id=str(uuid5(NAMESPACE_URL, "lego-element:" + row["element_id"])),
                        vector=vector.tolist(),
                        payload=row,
                    )
                    for row, vector in zip(elements, vectors, strict=True)
                ],
            )
            count = client.count(COLLECTION, exact=True).count
            if count != len(elements):
                raise RuntimeError(f"Expected {len(elements)} points, found {count}")
            print(f"Indexed {count} distinct element IDs from {len(rows)} rows.")
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
