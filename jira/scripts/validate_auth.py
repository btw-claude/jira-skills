#!/usr/bin/env python3
"""Validate Jira API authentication configuration.

This script checks that the .claude/env file exists with the required
configuration and tests that authentication credentials are valid by
making a test API call.

Supports two authentication methods:
1. PAT Auth: Requires JIRA_BASE_URL and JIRA_PAT
2. Basic Auth: Requires JIRA_BASE_URL, JIRA_USER_EMAIL, and JIRA_API_TOKEN

PAT authentication takes precedence if JIRA_PAT is configured.

Exit Codes:
    0: Success - configuration valid and authentication works
    1: Configuration error - missing file or required variables
    2: Authentication error - credentials are invalid or expired

Usage:
    python scripts/validate_auth.py
"""

from __future__ import annotations

import sys
from pathlib import Path

from jira_api import (
    JiraClient,
    JiraAPIError,
    JiraConfigError,
    _find_env_file,
    _load_env_file,
)


# Exit codes
EXIT_SUCCESS = 0
EXIT_CONFIG_ERROR = 1
EXIT_AUTH_ERROR = 2


def validate_configuration() -> tuple[bool, str, dict[str, str] | None, str | None]:
    """Validate that configuration file exists and has required variables.

    Supports two authentication methods:
    1. PAT Auth: Requires JIRA_BASE_URL and JIRA_PAT
    2. Basic Auth: Requires JIRA_BASE_URL, JIRA_USER_EMAIL, and JIRA_API_TOKEN

    Returns:
        Tuple of (success, message, config_dict or None, auth_method or None)
        auth_method is "pat" or "basic" when successful
    """
    try:
        # Find the .claude/env file
        env_path = _find_env_file()
    except JiraConfigError as e:
        return (False, f"Missing .claude/env file\n  {e.message}", None, None)

    # Load and parse the env file
    config = _load_env_file(env_path)

    # Check base required variable
    if not config.get("JIRA_BASE_URL"):
        return (
            False,
            "Missing required variable in .claude/env: JIRA_BASE_URL",
            None,
            None,
        )

    # Check for authentication credentials
    # PAT auth takes precedence if configured
    has_pat = bool(config.get("JIRA_PAT"))
    has_basic_auth = bool(config.get("JIRA_USER_EMAIL")) and bool(config.get("JIRA_API_TOKEN"))

    if has_pat:
        return (True, str(env_path), config, "pat")
    elif has_basic_auth:
        return (True, str(env_path), config, "basic")
    else:
        # Neither auth method is fully configured
        missing_info = []
        if not config.get("JIRA_PAT"):
            missing_info.append("JIRA_PAT (for PAT authentication)")
        if not config.get("JIRA_USER_EMAIL") or not config.get("JIRA_API_TOKEN"):
            basic_missing = []
            if not config.get("JIRA_USER_EMAIL"):
                basic_missing.append("JIRA_USER_EMAIL")
            if not config.get("JIRA_API_TOKEN"):
                basic_missing.append("JIRA_API_TOKEN")
            missing_info.append(f"{', '.join(basic_missing)} (for Basic authentication)")

        return (
            False,
            f"Missing authentication configuration in .claude/env.\n"
            f"  Please configure one of the following:\n"
            f"  - PAT Auth: Set JIRA_PAT\n"
            f"  - Basic Auth: Set JIRA_USER_EMAIL and JIRA_API_TOKEN",
            None,
            None,
        )


def test_authentication(client: JiraClient) -> tuple[bool, str, dict | None]:
    """Test authentication by calling the /myself endpoint.

    Args:
        client: Configured JiraClient instance

    Returns:
        Tuple of (success, message, user_info or None)
    """
    try:
        # Call /myself to get current user info
        user_info = client.get("myself")
        return (True, "Authentication successful", user_info)

    except JiraAPIError as e:
        auth_method = client.auth_method
        if auth_method == "pat":
            credential_type = "Personal Access Token (PAT)"
        else:
            credential_type = "API token"

        if e.status_code == 401:
            return (
                False,
                f"Invalid or expired {credential_type}\n"
                f"  HTTP 401: {e.response_body}\n"
                f"  Verify your credentials in .claude/env are correct.\n"
                f"  For PAT auth: Check JIRA_PAT is valid\n"
                f"  For Basic auth: Check JIRA_USER_EMAIL and JIRA_API_TOKEN",
                None,
            )
        elif e.status_code == 403:
            return (
                False,
                f"{credential_type} lacks required permissions\n"
                f"  HTTP 403: {e.response_body}",
                None,
            )
        else:
            return (False, f"API request failed\n  HTTP {e.status_code}: {e.response_body}", None)


def _mask_token(token: str) -> str:
    """Mask a token for display, showing first 8 and last 4 chars.

    Args:
        token: The token to mask

    Returns:
        Masked token string
    """
    if len(token) > 16:
        return f"{token[:8]}...{token[-4:]}"
    return "****"


def main() -> int:
    """Main entry point.

    Returns:
        Exit code (0=success, 1=config error, 2=auth error)
    """
    print("Checking configuration...")
    print()

    # Step 1: Validate configuration
    config_ok, config_message, config, auth_method = validate_configuration()

    if not config_ok:
        print("Configuration ERROR:")
        print(f"  {config_message}")
        return EXIT_CONFIG_ERROR

    # Display configuration based on auth method
    print("Configuration OK:")
    print(f"  JIRA_BASE_URL: {config['JIRA_BASE_URL']}")

    if auth_method == "pat":
        print(f"  Authentication: Personal Access Token (PAT)")
        print(f"  JIRA_PAT: {_mask_token(config['JIRA_PAT'])}")
    else:  # basic auth
        print(f"  Authentication: Basic Auth (Email + API Token)")
        print(f"  JIRA_USER_EMAIL: {config['JIRA_USER_EMAIL']}")
        print(f"  JIRA_API_TOKEN: {_mask_token(config['JIRA_API_TOKEN'])}")

    print(f"  Config file: {config_message}")
    print()

    # Step 2: Test authentication
    print("Testing authentication...")
    print()

    try:
        client = JiraClient()
    except JiraConfigError as e:
        print("Configuration ERROR:")
        print(f"  Failed to initialize client: {e.message}")
        return EXIT_CONFIG_ERROR

    auth_ok, auth_message, user_info = test_authentication(client)

    if not auth_ok:
        print("Authentication ERROR:")
        print(f"  {auth_message}")
        return EXIT_AUTH_ERROR

    # Extract user details
    display_name = user_info.get("displayName", "Unknown")
    email = user_info.get("emailAddress", "Unknown")
    account_id = user_info.get("accountId", "Unknown")
    active = user_info.get("active", False)

    print("Authentication OK:")
    print(f"  User: {display_name} ({email})")
    print(f"  Account ID: {account_id}")
    print(f"  Active: {active}")
    print()
    print("All checks passed.")

    return EXIT_SUCCESS


if __name__ == "__main__":
    sys.exit(main())
