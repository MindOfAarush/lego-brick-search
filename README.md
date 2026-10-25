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
This folder is excluded from Git. Repeating indexing upserts the same records.
If you replace the inventory or change the embedding model, delete
`qdrant_storage/` and index again to remove stale records.

Search returns candidate inventory rows with their element IDs, design numbers,
colors, and similarity scores. Scores are not confidence probabilities; review
candidates before correcting part numbers. The supplied inventory has not been
validated against the complete official set inventory. Element IDs and design
numbers remain separate strings, preserving alphanumeric identifiers.

## References

- [Qdrant Python client](https://github.com/qdrant/qdrant-client)
- [FastEmbed](https://github.com/qdrant/fastembed)

This project is not affiliated with LEGO or Rebrickable. The supplied CSV is
included as provided; no additional redistribution license is asserted.
