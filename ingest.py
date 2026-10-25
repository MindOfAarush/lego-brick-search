"""Embed one description per distinct LEGO element into persistent local Qdrant."""

import csv
from pathlib import Path
from uuid import NAMESPACE_URL, uuid5

from fastembed import TextEmbedding
from qdrant_client import QdrantClient, models

ROOT = Path(__file__).resolve().parent
COLLECTION = "parts_75192"
MODEL = "BAAI/bge-small-en-v1.5"


def read_elements(path):
    """Prefer a regular row when a spare shares its element ID."""
    elements = {}
    with path.open(encoding="utf-8-sig", newline="") as source:
        for row in csv.DictReader(source):
            element_id = row["element_id"].strip()
            if not element_id:
                raise ValueError("Inventory row has an empty element_id")
            row["element_id"] = element_id
            existing = elements.get(element_id)
            if existing is None or (
                existing["is_spare"].strip().lower() == "true"
                and row["is_spare"].strip().lower() != "true"
            ):
                elements[element_id] = row
    return list(elements.values())


def main():
    elements = read_elements(ROOT / "data/rebrickable_75192_parts_list.csv")
    if not elements:
        raise ValueError("Inventory is empty")
    descriptions = [
        f"{row['design_number']} {row['colour_name']} {row['part_name']}"
        for row in elements
    ]
    encoder = TextEmbedding(model_name=MODEL)
    vectors = list(encoder.embed(descriptions))
    client = QdrantClient(path=str(ROOT / "qdrant_storage"))
    try:
        # Rebuild this managed collection so removed IDs cannot leave stale points.
        if client.collection_exists(COLLECTION):
            client.delete_collection(COLLECTION)
        client.create_collection(
            collection_name=COLLECTION,
            vectors_config=models.VectorParams(
                size=len(vectors[0]), distance=models.Distance.COSINE
            ),
        )
        client.upsert(
            collection_name=COLLECTION,
            points=[
                models.PointStruct(
                    id=str(uuid5(NAMESPACE_URL, row["element_id"])),
                    vector=vector.tolist(),
                    payload={key: row[key] for key in (
                        "element_id", "design_number", "colour_name"
                    )},
                )
                for row, vector in zip(elements, vectors, strict=True)
            ],
            wait=True,
        )
        count = client.count(collection_name=COLLECTION, exact=True).count
        print(f"Qdrant point count: {count} | Distinct element IDs: {len(elements)}")
        if count != len(elements):
            raise RuntimeError("Qdrant point count does not match distinct element IDs")
    finally:
        client.close()


if __name__ == "__main__":
    main()
