#!/usr/bin/env python3
"""Unit tests for GithubOrgClient"""

import unittest
from unittest.mock import patch
from parameterized import parameterized
from client import GithubOrgClient


class TestGithubOrgClient(unittest.TestCase):
    """Test the GithubOrgClient.org method"""

    @parameterized.expand([("google", {"login": "google"}), ("abc", {"login": "abc"})])
    @patch("client.get_json")
    def test_org(self, org_name, expected_payload, mock_get_json):
        """Test that GithubOrgClient.org returns the expected result"""
        mock_get_json.return_value = expected_payload

        client = GithubOrgClient(org_name)
        result = client.org  # should call get_json once

        mock_get_json.assert_called_once_with(f"https://api.github.com/orgs/{org_name}")
        self.assertEqual(result, expected_payload)

        def test_public_repos_url(self):
            """Test that _public_repos_url returns correct URL from org"""
            test_url = "https://api.github.com/orgs/test/repos"
            payload = {"repos_url": test_url}

            with patch.object(
                GithubOrgClient, "org", new_callable=PropertyMock
            ) as mock_org:
                mock_org.return_value = payload

            client = GithubOrgClient("test")
            result = client._public_repos_url

            mock_org.assert_called_once()
            self.assertEqual(result, test_url)


if __name__ == "__main__":
    unittest.main()
