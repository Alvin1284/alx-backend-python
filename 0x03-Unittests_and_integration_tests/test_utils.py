#!/usr/bin/env python3
"""
Unit tests for the access_nested_map function in the utils module.
"""

import unittest
from parameterized import parameterized
from typing import Mapping, Sequence, Any
from utils import access_nested_map


class TestAccessNestedMap(unittest.TestCase):
    """
    Test case for the access_nested_map function from the utils module.
    """

    @parameterized.expand([
        ({"a": 1}, ("a",), 1),
        ({"a": {"b": 2}}, ("a",), {"b": 2}),
        ({"a": {"b": 2}}, ("a", "b"), 2),
    ])
    def test_access_nested_map(self, nested_map: Mapping, path: Sequence[str],
                                expected: Any) -> None:
        """
        Test access_nested_map returns expected values for given nested paths.
        """
        self.assertEqual(access_nested_map(nested_map, path), expected)
