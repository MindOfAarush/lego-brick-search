"""Show the dense baseline's top five and verdict for Leo's missing piece."""

from search import dense_search

QUERY = "3001 dark grey"
EXPECTED_ELEMENT_ID = "4211388"


def main():
    ranked = dense_search(QUERY, limit=5)
    print(f"Leo's request: {QUERY}")
    print(f"Missing piece element ID: {EXPECTED_ELEMENT_ID}")
    print("\nDense baseline - top 5 element IDs:")
    for rank, element_id in enumerate(ranked, start=1):
        print(f"  {rank}. {element_id}")
    rank = ranked.index(EXPECTED_ELEMENT_ID) + 1 if EXPECTED_ELEMENT_ID in ranked else None
    top1 = "PASS" if rank == 1 else "FAIL"
    top5 = "PASS" if rank is not None else "FAIL"
    print(f"\nVERDICT: Top-1 {top1} | Top-5 {top5} | Expected ID rank: {rank or 'outside top 5'}")


if __name__ == "__main__":
    main()
