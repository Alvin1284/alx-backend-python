#!/usr/bin/env python3
"""
Unit tests for the access_nested_map function in the utils module.
"""

import unittest
from parameterized import parameterized
from typing import Mapping, Sequence, Any
from utils import access_nested_map, memoize
from unittest.mock import patch, Mock
from typing import Dict
from utils import get_json


class TestAccessNestedMap(unittest.TestCase):
    """
    Test case for the access_nested_map function from the utils module.
    """

    @parameterized.expand(
        [
            ({"a": 1}, ("a",), 1),
            ({"a": {"b": 2}}, ("a",), {"b": 2}),
            ({"a": {"b": 2}}, ("a", "b"), 2),
        ]
    )
    def test_access_nested_map(
        self, nested_map: Mapping, path: Sequence[str], expected: Any
    ) -> None:
        """
        Test access_nested_map returns expected values for given nested paths.
        """
        self.assertEqual(access_nested_map(nested_map, path), expected)

    @parameterized.expand(
        [
            ({}, ("a",), "a"),
            ({"a": 1}, ("a", "b"), "b"),
        ]
    )
    def test_access_nested_map_exception(
        self, nested_map: Mapping, path: Sequence[str], missing_key: str
    ) -> None:
        """
        Test that access_nested_map raises KeyError with the correct message.
        """
        with self.assertRaises(KeyError) as context:
            access_nested_map(nested_map, path)
        self.assertEqual(str(context.exception), f"'{missing_key}'")


class TestGetJson(unittest.TestCase):
    """
    Test case for the get_json function from the utils module.
    """

    @parameterized.expand(
        [
            ("http://example.com", {"payload": True}),
            ("http://holberton.io", {"payload": False}),
        ]
    )
    def test_get_json(self, test_url: str, test_payload: Dict) -> None:
        """
        Test get_json returns the expected payload from a mocked HTTP request.
        """
        mock_response = Mock()
        mock_response.json.return_value = test_payload

        with patch("utils.requests.get", return_value=mock_response) as mock_get:
            result = get_json(test_url)
            mock_get.assert_called_once_with(test_url)
            self.assertEqual(result, test_payload)


class TestMemoize(unittest.TestCase):
    """
    Test case for the memoize decorator from the utils module.
    """

    def test_memoize(self) -> None:
        """
        Test that memoize caches the result and avoids repeated method calls.
        """

        class TestClass:
            """
            Simple class to test memoization of a method result.
            """

            def a_method(self) -> int:
                """
                Sample method that returns an integer.
                """
                return 42

            @memoize
            def a_property(self) -> int:
                """
                Memoized property that calls a_method once and caches result.
                """
                return self.a_method()

        with patch.object(TestClass, "a_method", return_value=42) as mock_method:
            obj = TestClass()
            self.assertEqual(obj.a_property, 42)
            self.assertEqual(obj.a_property, 42)
            mock_method.assert_called_once()
