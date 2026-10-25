# LEGO Brick Search

Python starter for finding LEGO part numbers using Qdrant and FastEmbed.
Includes the supplied `rebrickable_75192_parts_list.csv` inventory, preserved
without changing its contents, in `data/`.

## Setup

Use Python 3.11 or 3.12:

```bash
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python brick_search.py index
python brick_search.py search "light gray brick 2 x 4"
```

FastEmbed downloads its embedding model on first use. Qdrant runs locally,
without Docker or a server, and persists vectors in `qdrant_storage/`.
This folder is excluded from Git. Indexing rebuilds the managed `lego_parts` collection from the CSV, removing
stale points from earlier indexing runs. Each distinct `element_id` creates
exactly one point, including when regular and spare rows share that ID.
Payloads retain all original `inventory_rows` and separate `regular_quantity`
and `spare_quantity` totals. Point IDs depend only on the element ID.

Search returns candidate elements with their element IDs, design numbers,
colors, and similarity scores. Scores are not confidence probabilities; review
candidates before correcting part numbers. The supplied inventory has not been
validated against the complete official set inventory. Element IDs and design
numbers remain separate strings, preserving alphanumeric identifiers.

## Set 75192 ingestion

```bash
mkdir -p outputs
python ingest.py | tee outputs/ingest_output.txt
```

This builds `parts_75192` in persistent `qdrant_storage/`, with one UUID point
per distinct element ID and payload fields `element_id`, `design_number`, and
`colour_name`. Descriptions use `design_number colour_name part_name` with
`BAAI/bge-small-en-v1.5` embeddings and cosine distance. Regular rows take
precedence over duplicate spare rows. Each run rebuilds this collection and
prints the exact point count beside the distinct-ID count.

## Dense baseline search

```python
from search import dense_search

ranked_ids = dense_search("3001 dark grey", limit=5)
```

Or run `python search.py "3001 dark grey" --limit 5`.
Returns element IDs in descending cosine similarity order from `parts_75192`.
This baseline uses the same FastEmbed model as ingestion, with no colour aliases,
metadata filters, or reranking. Run `python ingest.py` first.

## References

- [Qdrant Python client](https://github.com/qdrant/qdrant-client)
- [FastEmbed](https://github.com/qdrant/fastembed)

This project is not affiliated with LEGO or Rebrickable. The supplied CSV is
included as provided; no additional redistribution license is asserted.
