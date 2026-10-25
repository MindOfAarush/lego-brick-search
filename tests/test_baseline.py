import unittest

from leo_baseline import format_results


class VerdictTests(unittest.TestCase):
    target = {'element_id': '4211388', 'colour_name': 'Dark Bluish Gray', 'design_number': '3001'}

    def hit(self, element_id, colour):
        return {'element_id': element_id, 'colour_name': colour,
                'design_number': '3001', 'score': 0.8}

    def test_right_colour_wrong_id_is_not_colour_failure(self):
        output = format_results([self.hit('other', 'Dark Bluish Gray')], self.target)
        self.assertIn('ID CHECK: Top-1 FAIL', output)
        self.assertIn('COLOUR VERDICT: Top-1 PASS', output)
        self.assertIn('right colour but the wrong element ID', output)
        self.assertIn('set 75192', output)

    def test_wrong_colour_is_explicit(self):
        output = format_results([self.hit('other', 'Light Bluish Gray')], self.target)
        self.assertIn('other | Light Bluish Gray', output)
        self.assertIn('COLOUR VERDICT: Top-1 FAIL', output)

    def test_exact_match_passes_both_checks(self):
        output = format_results([self.hit('4211388', 'Dark Bluish Gray')], self.target)
        self.assertIn('ID CHECK: Top-1 PASS', output)
        self.assertIn('COLOUR VERDICT: Top-1 PASS', output)

    def test_no_results_does_not_claim_colour_match(self):
        self.assertIn('colour cannot be assessed', format_results([], self.target))
