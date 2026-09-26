"""
Unit tests for page range parsing.
"""

import unittest
from core.extract import parse_ranges


class TestRangeParsing(unittest.TestCase):
    def test_standard_ranges(self):
        # 1-indexed to 0-indexed
        res = parse_ranges("1-3, 5, 7-8", total_pages=10)
        self.assertEqual(res, [0, 1, 2, 4, 6, 7])

    def test_empty_returns_all_pages(self):
        res = parse_ranges("", total_pages=5)
        self.assertEqual(res, [0, 1, 2, 3, 4])
        res_spaces = parse_ranges("   ", total_pages=3)
        self.assertEqual(res_spaces, [0, 1, 2])

    def test_whitespace_and_commas(self):
        res = parse_ranges(" 1 - 2 , , 4 ", total_pages=5)
        self.assertEqual(res, [0, 1, 3])

    def test_clamping_behavior(self):
        # In clamp mode, 15 clamped to 10
        res = parse_ranges("8-15", total_pages=10, clamp=True)
        self.assertEqual(res, [7, 8, 9])

        # Page completely out of bounds ignored in clamp mode
        res_oob = parse_ranges("20", total_pages=10, clamp=True)
        self.assertEqual(res_oob, [])

    def test_strict_mode_errors(self):
        with self.assertRaises(ValueError):
            parse_ranges("8-15", total_pages=10, clamp=False)

        with self.assertRaises(ValueError):
            parse_ranges("0", total_pages=10, clamp=False)

        with self.assertRaises(ValueError):
            parse_ranges("invalid-text", total_pages=10, clamp=False)

    def test_inverted_range(self):
        # 5-2 normalized to 2-5
        res = parse_ranges("5-2", total_pages=10, clamp=True)
        self.assertEqual(res, [1, 2, 3, 4])

    def test_deduplication(self):
        res = parse_ranges("1, 2, 1-3, 2", total_pages=5)
        self.assertEqual(res, [0, 1, 2])


if __name__ == "__main__":
    unittest.main()
