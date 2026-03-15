"""Tests for shared helpers."""
import unittest

import pandas as pd

from straditize.common import nearest_index_position, nearest_index_value


class CommonHelpersTest(unittest.TestCase):

    def test_nearest_index_position(self):
        index = pd.Index([0.0, 4.0, 9.0, 15.0])

        self.assertEqual(nearest_index_position(index, 10.1), 2)

    def test_nearest_index_value(self):
        index = pd.Index([0.0, 4.0, 9.0, 15.0])

        self.assertEqual(nearest_index_value(index, 13.0), 15.0)


if __name__ == '__main__':
    unittest.main()
