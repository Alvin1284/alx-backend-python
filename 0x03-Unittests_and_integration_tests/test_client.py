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

            @patch("client.get_json")
            def test_public_repos(self, mock_get_json):
                """Test that public_repos returns expected list of repo names"""
                # Payload returned by get_json
                mocked_repos_payload = [
                    {"name": "repo1", "license": {"key": "mit"}},
                    {"name": "repo2", "license": {"key": "apache-2.0"}},
                    {"name": "repo3", "license": {"key": "mit"}},
                ]

                mock_get_json.return_value = mocked_repos_payload

            # Patch the _public_repos_url property
            with patch.object(
                GithubOrgClient, "_public_repos_url", new_callable=PropertyMock
            ) as mock_url:
                mock_url.return_value = "https://api.github.com/orgs/test-org/repos"

                client = GithubOrgClient("test-org")
                result = client.public_repos()

                # We expect only the names of the repos
                expected = ["repo1", "repo2", "repo3"]

                self.assertEqual(result, expected)
                mock_url.assert_called_once()
                mock_get_json.assert_called_once_with(
                    "https://api.github.com/orgs/test-org/repos"
                )


if __name__ == "__main__":
    unittest.main()
