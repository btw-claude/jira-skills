#!/usr/bin/env python3
"""Tests for PAT (Personal Access Token) authentication support.

This module tests the dual authentication system that supports both:
1. Personal Access Token (PAT) authentication
2. Basic Auth (email + API token) authentication

Test coverage includes:
- PAT auth succeeds with valid token
- Basic Auth still works (backward compatibility)
- Error when neither auth method is configured
- PAT takes precedence when both auth methods are configured
- Validation script correctly identifies auth method in use

JSKILL-30: Add tests for PAT authentication
JSKILL-34: Improve with pytest best practices
"""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# sys.path manipulation is handled in conftest.py
from jira_api import (
    JiraClient,
    JiraConfigError,
    _find_env_file,
    _load_env_file,
)
from validate_auth import (
    validate_configuration,
    _mask_token,
    EXIT_SUCCESS,
    EXIT_CONFIG_ERROR,
    EXIT_AUTH_ERROR,
)


class TestEnvFileParsing(unittest.TestCase):
    """Test environment file loading and parsing."""

    def setUp(self):
        """Create a temporary directory for test env files."""
        self.temp_dir = tempfile.mkdtemp()
        self.claude_dir = Path(self.temp_dir) / ".claude"
        self.claude_dir.mkdir()
        self.env_file = self.claude_dir / "env"

    def tearDown(self):
        """Clean up temporary files."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_load_env_file_with_pat(self):
        """Test loading env file with PAT configuration."""
        self.env_file.write_text(
            "JIRA_BASE_URL=https://example.atlassian.net\n"
            "JIRA_PAT=test_pat_token_12345\n"
        )
        config = _load_env_file(self.env_file)

        self.assertEqual(config["JIRA_BASE_URL"], "https://example.atlassian.net")
        self.assertEqual(config["JIRA_PAT"], "test_pat_token_12345")

    def test_load_env_file_with_basic_auth(self):
        """Test loading env file with Basic Auth configuration."""
        self.env_file.write_text(
            "JIRA_BASE_URL=https://example.atlassian.net\n"
            "JIRA_USER_EMAIL=user@example.com\n"
            "JIRA_API_TOKEN=api_token_12345\n"
        )
        config = _load_env_file(self.env_file)

        self.assertEqual(config["JIRA_BASE_URL"], "https://example.atlassian.net")
        self.assertEqual(config["JIRA_USER_EMAIL"], "user@example.com")
        self.assertEqual(config["JIRA_API_TOKEN"], "api_token_12345")

    def test_load_env_file_with_both_auth_methods(self):
        """Test loading env file with both PAT and Basic Auth configured."""
        self.env_file.write_text(
            "JIRA_BASE_URL=https://example.atlassian.net\n"
            "JIRA_PAT=test_pat_token\n"
            "JIRA_USER_EMAIL=user@example.com\n"
            "JIRA_API_TOKEN=api_token\n"
        )
        config = _load_env_file(self.env_file)

        # All values should be loaded
        self.assertEqual(config["JIRA_BASE_URL"], "https://example.atlassian.net")
        self.assertEqual(config["JIRA_PAT"], "test_pat_token")
        self.assertEqual(config["JIRA_USER_EMAIL"], "user@example.com")
        self.assertEqual(config["JIRA_API_TOKEN"], "api_token")

    def test_load_env_file_with_comments(self):
        """Test that comments are properly ignored."""
        self.env_file.write_text(
            "# This is a comment\n"
            "JIRA_BASE_URL=https://example.atlassian.net\n"
            "# Another comment\n"
            "JIRA_PAT=token123\n"
        )
        config = _load_env_file(self.env_file)

        self.assertEqual(len(config), 2)
        self.assertNotIn("#", str(config))


class TestJiraClientPATAuth(unittest.TestCase):
    """Test JiraClient PAT authentication."""

    def setUp(self):
        """Create a temporary directory for test env files."""
        self.temp_dir = tempfile.mkdtemp()
        self.claude_dir = Path(self.temp_dir) / ".claude"
        self.claude_dir.mkdir()
        self.env_file = self.claude_dir / "env"

    def tearDown(self):
        """Clean up temporary files."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_pat_auth_creates_bearer_token_header(self):
        """Test that PAT auth creates correct Bearer token header."""
        self.env_file.write_text(
            "JIRA_BASE_URL=https://example.atlassian.net\n"
            "JIRA_PAT=test_pat_token_12345\n"
        )

        client = JiraClient(config_start_path=Path(self.temp_dir))

        self.assertEqual(client.auth_method, "pat")
        self.assertIn("Authorization", client.session.headers)
        self.assertEqual(
            client.session.headers["Authorization"],
            "Bearer test_pat_token_12345"
        )

    def test_basic_auth_creates_basic_header(self):
        """Test that Basic Auth creates correct Authorization header."""
        self.env_file.write_text(
            "JIRA_BASE_URL=https://example.atlassian.net\n"
            "JIRA_USER_EMAIL=user@example.com\n"
            "JIRA_API_TOKEN=api_token_12345\n"
        )

        client = JiraClient(config_start_path=Path(self.temp_dir))

        self.assertEqual(client.auth_method, "basic")
        self.assertIn("Authorization", client.session.headers)
        self.assertTrue(
            client.session.headers["Authorization"].startswith("Basic ")
        )

    def test_pat_takes_precedence_over_basic_auth(self):
        """Test that PAT authentication takes precedence when both are configured."""
        self.env_file.write_text(
            "JIRA_BASE_URL=https://example.atlassian.net\n"
            "JIRA_PAT=my_pat_token\n"
            "JIRA_USER_EMAIL=user@example.com\n"
            "JIRA_API_TOKEN=my_api_token\n"
        )

        client = JiraClient(config_start_path=Path(self.temp_dir))

        # PAT should take precedence
        self.assertEqual(client.auth_method, "pat")
        self.assertEqual(
            client.session.headers["Authorization"],
            "Bearer my_pat_token"
        )

    def test_error_when_neither_auth_method_configured(self):
        """Test that error is raised when no authentication is configured."""
        self.env_file.write_text(
            "JIRA_BASE_URL=https://example.atlassian.net\n"
        )

        with self.assertRaises(JiraConfigError) as context:
            JiraClient(config_start_path=Path(self.temp_dir))

        # Error message should mention both auth options
        error_message = str(context.exception)
        self.assertIn("PAT Auth", error_message)
        self.assertIn("Basic Auth", error_message)
        self.assertIn("JIRA_PAT", error_message)
        self.assertIn("JIRA_USER_EMAIL", error_message)
        self.assertIn("JIRA_API_TOKEN", error_message)

    def test_error_when_missing_base_url(self):
        """Test that error is raised when JIRA_BASE_URL is missing."""
        self.env_file.write_text(
            "JIRA_PAT=my_pat_token\n"
        )

        with self.assertRaises(JiraConfigError) as context:
            JiraClient(config_start_path=Path(self.temp_dir))

        error_message = str(context.exception)
        self.assertIn("JIRA_BASE_URL", error_message)

    def test_error_when_basic_auth_incomplete(self):
        """Test error when only email is provided without API token."""
        self.env_file.write_text(
            "JIRA_BASE_URL=https://example.atlassian.net\n"
            "JIRA_USER_EMAIL=user@example.com\n"
        )

        with self.assertRaises(JiraConfigError) as context:
            JiraClient(config_start_path=Path(self.temp_dir))

        error_message = str(context.exception)
        self.assertIn("JIRA_API_TOKEN", error_message)

    def test_content_type_headers_set_correctly(self):
        """Test that Content-Type and Accept headers are set for both auth methods."""
        # Test PAT auth
        self.env_file.write_text(
            "JIRA_BASE_URL=https://example.atlassian.net\n"
            "JIRA_PAT=pat_token\n"
        )
        client = JiraClient(config_start_path=Path(self.temp_dir))

        self.assertEqual(client.session.headers["Content-Type"], "application/json")
        self.assertEqual(client.session.headers["Accept"], "application/json")


class TestValidateAuthScript(unittest.TestCase):
    """Test the validate_auth.py script functions."""

    def setUp(self):
        """Create a temporary directory for test env files."""
        self.temp_dir = tempfile.mkdtemp()
        self.claude_dir = Path(self.temp_dir) / ".claude"
        self.claude_dir.mkdir()
        self.env_file = self.claude_dir / "env"

    def tearDown(self):
        """Clean up temporary files."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    # Token masking tests have been moved to parametrized tests below

    @patch('validate_auth._find_env_file')
    @patch('validate_auth._load_env_file')
    def test_validate_configuration_with_pat(self, mock_load, mock_find):
        """Test validate_configuration identifies PAT auth correctly."""
        mock_find.return_value = Path("/fake/.claude/env")
        mock_load.return_value = {
            "JIRA_BASE_URL": "https://example.atlassian.net",
            "JIRA_PAT": "pat_token_12345",
        }

        success, message, config, auth_method = validate_configuration()

        self.assertTrue(success)
        self.assertEqual(auth_method, "pat")
        self.assertIn("JIRA_PAT", config)

    @patch('validate_auth._find_env_file')
    @patch('validate_auth._load_env_file')
    def test_validate_configuration_with_basic_auth(self, mock_load, mock_find):
        """Test validate_configuration identifies Basic Auth correctly."""
        mock_find.return_value = Path("/fake/.claude/env")
        mock_load.return_value = {
            "JIRA_BASE_URL": "https://example.atlassian.net",
            "JIRA_USER_EMAIL": "user@example.com",
            "JIRA_API_TOKEN": "api_token",
        }

        success, message, config, auth_method = validate_configuration()

        self.assertTrue(success)
        self.assertEqual(auth_method, "basic")
        self.assertIn("JIRA_USER_EMAIL", config)

    @patch('validate_auth._find_env_file')
    @patch('validate_auth._load_env_file')
    def test_validate_configuration_pat_takes_precedence(self, mock_load, mock_find):
        """Test that PAT takes precedence in validate_configuration."""
        mock_find.return_value = Path("/fake/.claude/env")
        mock_load.return_value = {
            "JIRA_BASE_URL": "https://example.atlassian.net",
            "JIRA_PAT": "pat_token",
            "JIRA_USER_EMAIL": "user@example.com",
            "JIRA_API_TOKEN": "api_token",
        }

        success, message, config, auth_method = validate_configuration()

        self.assertTrue(success)
        self.assertEqual(auth_method, "pat")

    @patch('validate_auth._find_env_file')
    @patch('validate_auth._load_env_file')
    def test_validate_configuration_missing_auth(self, mock_load, mock_find):
        """Test validate_configuration error when no auth configured."""
        mock_find.return_value = Path("/fake/.claude/env")
        mock_load.return_value = {
            "JIRA_BASE_URL": "https://example.atlassian.net",
        }

        success, message, config, auth_method = validate_configuration()

        self.assertFalse(success)
        self.assertIsNone(auth_method)
        self.assertIn("PAT Auth", message)
        self.assertIn("Basic Auth", message)

    @patch('validate_auth._find_env_file')
    @patch('validate_auth._load_env_file')
    def test_validate_configuration_missing_base_url(self, mock_load, mock_find):
        """Test validate_configuration error when JIRA_BASE_URL is missing."""
        mock_find.return_value = Path("/fake/.claude/env")
        mock_load.return_value = {
            "JIRA_PAT": "pat_token",
        }

        success, message, config, auth_method = validate_configuration()

        self.assertFalse(success)
        self.assertIn("JIRA_BASE_URL", message)


class TestJiraClientAPIURL(unittest.TestCase):
    """Test JiraClient URL building."""

    def setUp(self):
        """Create a temporary directory for test env files."""
        self.temp_dir = tempfile.mkdtemp()
        self.claude_dir = Path(self.temp_dir) / ".claude"
        self.claude_dir.mkdir()
        self.env_file = self.claude_dir / "env"

    def tearDown(self):
        """Clean up temporary files."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_base_url_construction(self):
        """Test that base URL is constructed correctly."""
        self.env_file.write_text(
            "JIRA_BASE_URL=https://example.atlassian.net\n"
            "JIRA_PAT=pat_token\n"
        )

        client = JiraClient(config_start_path=Path(self.temp_dir))

        self.assertEqual(
            client.base_url,
            "https://example.atlassian.net/rest/api/3/"
        )

    def test_base_url_with_trailing_slash(self):
        """Test that trailing slash in base URL is handled."""
        self.env_file.write_text(
            "JIRA_BASE_URL=https://example.atlassian.net/\n"
            "JIRA_PAT=pat_token\n"
        )

        client = JiraClient(config_start_path=Path(self.temp_dir))

        # Should not have double slashes
        self.assertEqual(
            client.base_url,
            "https://example.atlassian.net/rest/api/3/"
        )


class TestBackwardCompatibility(unittest.TestCase):
    """Test backward compatibility with existing Basic Auth configurations."""

    def setUp(self):
        """Create a temporary directory for test env files."""
        self.temp_dir = tempfile.mkdtemp()
        self.claude_dir = Path(self.temp_dir) / ".claude"
        self.claude_dir.mkdir()
        self.env_file = self.claude_dir / "env"

    def tearDown(self):
        """Clean up temporary files."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_existing_basic_auth_config_still_works(self):
        """Test that existing Basic Auth configurations continue to work."""
        # This simulates an existing configuration before PAT support was added
        self.env_file.write_text(
            "JIRA_BASE_URL=https://company.atlassian.net\n"
            "JIRA_USER_EMAIL=developer@company.com\n"
            "JIRA_API_TOKEN=existing_api_token_xyz\n"
        )

        # Should not raise any errors
        client = JiraClient(config_start_path=Path(self.temp_dir))

        # Should use basic auth
        self.assertEqual(client.auth_method, "basic")

        # Authorization header should be Basic type
        auth_header = client.session.headers["Authorization"]
        self.assertTrue(auth_header.startswith("Basic "))

    def test_basic_auth_encodes_credentials_correctly(self):
        """Test that Basic Auth credentials are base64 encoded correctly."""
        import base64

        self.env_file.write_text(
            "JIRA_BASE_URL=https://example.atlassian.net\n"
            "JIRA_USER_EMAIL=test@example.com\n"
            "JIRA_API_TOKEN=api_token_123\n"
        )

        client = JiraClient(config_start_path=Path(self.temp_dir))

        # Extract and decode the Basic auth header
        auth_header = client.session.headers["Authorization"]
        encoded_part = auth_header.replace("Basic ", "")
        decoded = base64.b64decode(encoded_part).decode("utf-8")

        # Should be email:token format
        self.assertEqual(decoded, "test@example.com:api_token_123")


class TestAuthMethodIdentification(unittest.TestCase):
    """Test that the auth method is correctly identified and exposed."""

    def setUp(self):
        """Create a temporary directory for test env files."""
        self.temp_dir = tempfile.mkdtemp()
        self.claude_dir = Path(self.temp_dir) / ".claude"
        self.claude_dir.mkdir()
        self.env_file = self.claude_dir / "env"

    def tearDown(self):
        """Clean up temporary files."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_auth_method_attribute_pat(self):
        """Test that auth_method is 'pat' when using PAT."""
        self.env_file.write_text(
            "JIRA_BASE_URL=https://example.atlassian.net\n"
            "JIRA_PAT=pat_token\n"
        )

        client = JiraClient(config_start_path=Path(self.temp_dir))

        self.assertEqual(client.auth_method, "pat")

    def test_auth_method_attribute_basic(self):
        """Test that auth_method is 'basic' when using Basic Auth."""
        self.env_file.write_text(
            "JIRA_BASE_URL=https://example.atlassian.net\n"
            "JIRA_USER_EMAIL=user@example.com\n"
            "JIRA_API_TOKEN=api_token\n"
        )

        client = JiraClient(config_start_path=Path(self.temp_dir))

        self.assertEqual(client.auth_method, "basic")


# JSKILL-34: Parametrized token masking tests
class TestTokenMasking:
    """Test token masking functionality using pytest parametrize."""

    @pytest.mark.parametrize(
        "token,expected",
        [
            # Long tokens (>16 chars) show first 8 and last 4
            ("abcdefghijklmnopqrstuvwxyz", "abcdefgh...wxyz"),
            ("12345678901234567", "12345678...4567"),
            # Short tokens (<=16 chars) are fully masked
            ("short", "****"),
            ("1234567890123456", "****"),
            # Edge cases - JSKILL-36: Add tests for _mask_token() edge cases
            ("", "(empty)"),
            (None, "(empty)"),
            ("a", "****"),
            ("1234567890123456X", "12345678...456X"),
        ],
        ids=[
            "long_token",
            "17_chars",
            "short_token",
            "exactly_16_chars",
            "empty_string",
            "none_input",
            "single_char",
            "17_chars_boundary",
        ],
    )
    def test_mask_token(self, token, expected):
        """Test token masking for various token lengths.

        Tokens longer than 16 characters show first 8 and last 4 characters.
        Shorter tokens are fully masked with ****.
        """
        result = _mask_token(token)
        assert result == expected


# JSKILL-34: Test for empty string PAT token error handling
class TestEmptyPATToken(unittest.TestCase):
    """Test error handling for empty PAT tokens."""

    def setUp(self):
        """Create a temporary directory for test env files."""
        self.temp_dir = tempfile.mkdtemp()
        self.claude_dir = Path(self.temp_dir) / ".claude"
        self.claude_dir.mkdir()
        self.env_file = self.claude_dir / "env"

    def tearDown(self):
        """Clean up temporary files."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_empty_pat_token_raises_error(self):
        """Test that empty string PAT token raises appropriate error."""
        self.env_file.write_text(
            "JIRA_BASE_URL=https://example.atlassian.net\n"
            "JIRA_PAT=\n"
        )

        with self.assertRaises(JiraConfigError) as context:
            JiraClient(config_start_path=Path(self.temp_dir))

        error_message = str(context.exception)
        # Should indicate authentication configuration is missing/invalid
        self.assertIn("PAT Auth", error_message)

    def test_whitespace_only_pat_token_raises_error(self):
        """Test that whitespace-only PAT token raises appropriate error."""
        self.env_file.write_text(
            "JIRA_BASE_URL=https://example.atlassian.net\n"
            "JIRA_PAT=   \n"
        )

        with self.assertRaises(JiraConfigError) as context:
            JiraClient(config_start_path=Path(self.temp_dir))

        error_message = str(context.exception)
        # Should indicate authentication configuration is missing/invalid
        self.assertIn("PAT Auth", error_message)


if __name__ == "__main__":
    unittest.main()
