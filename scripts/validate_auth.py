#!/usr/bin/env python3
"""Validate Jira PAT authentication configuration.

This script checks that the .claude/env file exists with the required
configuration and tests that the PAT token is valid by making a test
API call.

Exit Codes:
    0: Success - configuration valid and authentication works
    1: Configuration error - missing file or required variables
    2: Authentication error - PAT is invalid or expired

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


def validate_configuration() -> tuple[bool, str, dict[str, str] | None]:
    """Validate that configuration file exists and has required variables.

    Returns:
        Tuple of (success, message, config_dict or None)
    """
    try:
        # Find the .claude/env file
        env_path = _find_env_file()
    except JiraConfigError as e:
        return (False, f"Missing .claude/env file\n  {e.message}", None)

    # Load and parse the env file
    config = _load_env_file(env_path)

    # Check required variables
    missing_vars = []
    if not config.get("JIRA_BASE_URL"):
        missing_vars.append("JIRA_BASE_URL")
    if not config.get("JIRA_PAT"):
        missing_vars.append("JIRA_PAT")

    if missing_vars:
        return (
            False,
            f"Missing required variables in .claude/env: {', '.join(missing_vars)}",
            None,
        )

    return (True, str(env_path), config)


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
        if e.status_code == 401:
            return (False, f"Invalid or expired PAT token\n  HTTP 401: {e.response_body}", None)
        elif e.status_code == 403:
            return (False, f"PAT lacks required permissions\n  HTTP 403: {e.response_body}", None)
        else:
            return (False, f"API request failed\n  HTTP {e.status_code}: {e.response_body}", None)


def main() -> int:
    """Main entry point.

    Returns:
        Exit code (0=success, 1=config error, 2=auth error)
    """
    print("Checking configuration...")
    print()

    # Step 1: Validate configuration
    config_ok, config_message, config = validate_configuration()

    if not config_ok:
        print("Configuration ERROR:")
        print(f"  {config_message}")
        return EXIT_CONFIG_ERROR

    # Mask the PAT for display (show first 8 and last 4 chars)
    pat = config["JIRA_PAT"]
    if len(pat) > 16:
        masked_pat = f"{pat[:8]}...{pat[-4:]}"
    else:
        masked_pat = "****"

    print("Configuration OK:")
    print(f"  JIRA_BASE_URL: {config['JIRA_BASE_URL']}")
    print(f"  JIRA_PAT: {masked_pat}")
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
