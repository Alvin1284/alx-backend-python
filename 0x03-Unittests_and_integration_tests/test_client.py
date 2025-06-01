#!/usr/bin/env python3
"""Unit tests for the GithubOrgClient class in client module.
This module ensures that the GithubOrgClient behaves as expected
when fetching organization data from the GitHub API.
"""

import unittest
from unittest.mock import patch
from parameterized import parameterized
from client import GithubOrgClient


class TestGithubOrgClient(unittest.TestCase):
    """Test case class for testing GithubOrgClient methods."""

    @parameterized.expand(
        [
            ("google", {"login": "google"}),
            ("abc", {"login": "abc"}),
        ]
    )
    @patch("client.get_json")
    def test_org(
        self, org_name: str, expected_payload: dict, mock_get_json: unittest.mock.Mock
    ) -> None:
        """Test that GithubOrgClient.org returns the correct payload
        and that get_json is called exactly once with the correct URL.
        """
        mock_get_json.return_value = expected_payload

        client = GithubOrgClient(org_name)
        result = client.org

        expected_url = f"https://api.github.com/orgs/{org_name}"
        mock_get_json.assert_called_once_with(expected_url)
        self.assertEqual(result, expected_payload)


if __name__ == "__main__":
    unittest.main()
