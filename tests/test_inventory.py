import csv
import unittest
from pathlib import Path

from brick_search import group_elements


class InventoryTests(unittest.TestCase):
    def test_regular_and_spare_rows_share_one_element(self):
        with Path('data/rebrickable_75192_parts_list.csv').open() as source:
            row = next(csv.DictReader(source))
        spare = dict(row, is_spare='true', quantity_in_set='2', bag_number='9')
        elements = group_elements([row, spare])
        self.assertEqual(len(elements), 1)
        self.assertEqual(elements[0]['regular_quantity'], int(row['quantity_in_set']))
        self.assertEqual(elements[0]['spare_quantity'], 2)
        self.assertEqual(elements[0]['inventory_rows'], [row, spare])

    def test_supplied_inventory_counts_distinct_ids(self):
        with Path('data/rebrickable_75192_parts_list.csv').open() as source:
            rows = list(csv.DictReader(source))
        elements = group_elements(rows)
        self.assertEqual(len(elements), len({r['element_id'] for r in rows}))
        self.assertEqual(sum(len(e['inventory_rows']) for e in elements), len(rows))


if __name__ == '__main__':
    unittest.main()
