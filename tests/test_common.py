"""Tests for shared helpers."""
import asyncio
import unittest
from unittest import mock

import pandas as pd

from straditize.common import (
    ensure_asyncio_event_loop,
    nearest_index_position,
    nearest_index_value,
)


class CommonHelpersTest(unittest.TestCase):

    def test_nearest_index_position(self):
        index = pd.Index([0.0, 4.0, 9.0, 15.0])

        self.assertEqual(nearest_index_position(index, 10.1), 2)

    def test_nearest_index_value(self):
        index = pd.Index([0.0, 4.0, 9.0, 15.0])

        self.assertEqual(nearest_index_value(index, 13.0), 15.0)

    def test_ensure_asyncio_event_loop_sets_missing_loop(self):
        sentinel = object()

        with mock.patch.object(
                asyncio, 'get_event_loop',
                side_effect=RuntimeError('missing loop')) as get_loop, \
                mock.patch.object(
                    asyncio, 'new_event_loop',
                    return_value=sentinel) as new_event_loop, \
                mock.patch.object(asyncio, 'set_event_loop') as set_event_loop:
            self.assertIs(ensure_asyncio_event_loop(), sentinel)

        get_loop.assert_called_once_with()
        new_event_loop.assert_called_once_with()
        set_event_loop.assert_called_once_with(sentinel)


if __name__ == '__main__':
    unittest.main()
