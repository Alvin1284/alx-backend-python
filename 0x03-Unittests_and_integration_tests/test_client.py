#!/usr/bin/env python3
"""
Integration tests for the GithubOrgClient.public_repos method.
"""

import unittest
from unittest.mock import patch
from parameterized import parameterized_class
import requests
from client import GithubOrgClient
import fixtures  


@parameterized_class([
    {
        "org_payload": fixtures.org_payload,
        "repos_payload": fixtures.repos_payload,
        "expected_repos": fixtures.expected_repos,
        "apache2_repos": fixtures.apache2_repos,
    }
])
class TestIntegrationGithubOrgClient(unittest.TestCase):
    """
    Integration test for GithubOrgClient.public_repos.
    """

    @classmethod
    def setUpClass(cls) -> None:
        """
        Setup mocked requests.get to return specific payloads for URLs.
        """
        cls.get_patcher = patch('requests.get')
        cls.mock_get = cls.get_patcher.start()

        def side_effect(url, *args, **kwargs):
            """
            Side effect for requests.get mock that returns different
            responses based on the requested URL.
            """
            mock_resp = unittest.mock.Mock()
            if url == "https://api.github.com/orgs/google":
                mock_resp.json.return_value = cls.org_payload
            elif url == "https://api.github.com/orgs/google/repos":
                mock_resp.json.return_value = cls.repos_payload
            else:
                mock_resp.json.return_value = {}
            return mock_resp

        cls.mock_get.side_effect = side_effect

    @classmethod
    def tearDownClass(cls) -> None:
        """
        Stop patching requests.get.
        """
        cls.get_patcher.stop()

    def test_public_repos(self) -> None:
        """
        Test that public_repos returns the list of repo names from repos_payload.
        """
        client = GithubOrgClient("google")
        repos = client.public_repos
        self.assertEqual(repos, self.expected_repos)

    def test_public_repos_with_license(self) -> None:
        """
        Test that public_repos filters repos by license key correctly.
        """
        client = GithubOrgClient("google")
        repos = client.public_repos(license="apache-2.0")
        self.assertEqual(repos, self.apache2_repos)


if __name__ == "__main__":
    unittest.main()