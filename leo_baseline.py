"""Show dense retrieval and distinguish a colour miss from an element-ID miss."""

from ingest import ROOT, read_elements
from search import dense_search_results

QUERY = "I need a dark grey 3001 Brick 2 x 4 for set 75192."
EXPECTED_ELEMENT_ID = "4211388"


def format_results(ranked, target):
    lines = [
        f"Leo's request: {QUERY}",
        f"Missing piece: {target['element_id']} | {target['colour_name']} | "
        f"design {target['design_number']}",
        "\nDense baseline - top 5:",
    ]
    for rank, hit in enumerate(ranked, start=1):
        lines.append(
            f"  {rank}. {hit['element_id']} | {hit['colour_name']} | "
            f"design {hit['design_number']} | score {hit['score']:.6f}"
        )
    ids = [hit['element_id'] for hit in ranked]
    rank = ids.index(target['element_id']) + 1 if target['element_id'] in ids else None
    top1 = "PASS" if rank == 1 else "FAIL"
    top5 = "PASS" if rank is not None else "FAIL"
    lines.append(
        f"\nID CHECK: Top-1 {top1} | Top-5 {top5} | "
        f"Expected ID rank: {rank or 'outside top 5'}"
    )
    if ranked:
        colour_match = ranked[0]['colour_name'] == target['colour_name']
        lines.append(
            f"COLOUR VERDICT: Top-1 {'PASS' if colour_match else 'FAIL'} | "
            f"Returned: {ranked[0]['colour_name']} | Expected: {target['colour_name']}"
        )
        if colour_match and rank != 1:
            lines.append("The top result has the right colour but the wrong element ID.")
        elif not colour_match:
            lines.append("The top result has the wrong colour.")
        else:
            lines.append("The top result matches both the element ID and colour.")
    else:
        lines.append("COLOUR VERDICT: No results; colour cannot be assessed.")
    return "\n".join(lines)


def main():
    elements = read_elements(ROOT / 'data/rebrickable_75192_parts_list.csv')
    target = next(row for row in elements if row['element_id'] == EXPECTED_ELEMENT_ID)
    print(format_results(dense_search_results(QUERY, limit=5), target))


if __name__ == "__main__":
    main()
