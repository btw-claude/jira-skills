"""
Jira API Client Module

A Python wrapper for the Jira REST API that handles authentication,
configuration loading, and HTTP request management.

Configuration is loaded exclusively from .claude/env file - no fallback
to environment variables is provided.

Example usage:
    from jira_api import JiraClient

    client = JiraClient()
    issue = client.get("issue/PROJ-123")
    client.post("issue", {"fields": {...}})
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import requests


class JiraAPIError(Exception):
    """Custom exception for Jira API errors.

    Attributes:
        message: Human-readable error description
        status_code: HTTP status code (if applicable)
        response_body: Raw response body from Jira (if applicable)
    """

    def __init__(
        self,
        message: str,
        status_code: int | None = None,
        response_body: str | None = None,
    ) -> None:
        self.message = message
        self.status_code = status_code
        self.response_body = response_body
        super().__init__(self._format_message())

    def _format_message(self) -> str:
        """Format the full error message including status and response details."""
        parts = [self.message]
        if self.status_code is not None:
            parts.append(f"Status Code: {self.status_code}")
        if self.response_body:
            parts.append(f"Response: {self.response_body}")
        return " | ".join(parts)


class JiraConfigError(JiraAPIError):
    """Exception raised for configuration-related errors.

    This includes missing .claude/env file or missing required variables.
    """

    pass


def _find_env_file(start_path: Path | None = None) -> Path:
    """Find the .claude/env file by searching parent directories.

    Starts from the script's directory and walks up to find .claude/env.

    Args:
        start_path: Starting directory for the search. Defaults to the
                   directory containing this script.

    Returns:
        Path to the .claude/env file

    Raises:
        JiraConfigError: If .claude/env file is not found
    """
    if start_path is None:
        start_path = Path(__file__).resolve().parent

    current = start_path
    # Walk up the directory tree looking for .claude/env
    while current != current.parent:  # Stop at filesystem root
        env_path = current / ".claude" / "env"
        if env_path.is_file():
            return env_path
        current = current.parent

    # Check root as well
    env_path = current / ".claude" / "env"
    if env_path.is_file():
        return env_path

    raise JiraConfigError(
        f"Configuration file .claude/env not found. "
        f"Searched from {start_path} to filesystem root. "
        f"Please create .claude/env with JIRA_BASE_URL and JIRA_PAT."
    )


def _load_env_file(env_path: Path) -> dict[str, str]:
    """Parse a .claude/env file into a dictionary.

    The file format is simple KEY=VALUE pairs, one per line.
    - Lines starting with # are ignored (comments)
    - Empty lines are ignored
    - No export prefix needed
    - Quotes around values are not stripped (use raw values)

    Args:
        env_path: Path to the .claude/env file

    Returns:
        Dictionary of environment variable names to values
    """
    config: dict[str, str] = {}

    with open(env_path, "r", encoding="utf-8") as f:
        for line_num, line in enumerate(f, start=1):
            line = line.strip()

            # Skip empty lines and comments
            if not line or line.startswith("#"):
                continue

            # Parse KEY=VALUE
            if "=" not in line:
                continue  # Skip malformed lines silently

            key, _, value = line.partition("=")
            key = key.strip()
            value = value.strip()

            if key:
                config[key] = value

    return config


class JiraClient:
    """A client for interacting with the Jira REST API.

    This client handles authentication and provides convenient methods
    for making API requests. Configuration is loaded from .claude/env.

    Attributes:
        base_url: The base URL for Jira API requests
        session: The requests Session used for all HTTP calls

    Example:
        client = JiraClient()

        # Get an issue
        issue = client.get("issue/PROJ-123")

        # Create an issue
        new_issue = client.post("issue", {
            "fields": {
                "project": {"key": "PROJ"},
                "summary": "New issue",
                "issuetype": {"name": "Task"}
            }
        })

        # Update an issue
        client.put("issue/PROJ-123", {
            "fields": {"summary": "Updated summary"}
        })

        # Delete an issue
        client.delete("issue/PROJ-123")
    """

    API_VERSION = "3"
    REQUIRED_VARS = ("JIRA_BASE_URL", "JIRA_PAT")

    def __init__(self, config_start_path: Path | None = None) -> None:
        """Initialize the Jira client.

        Loads configuration from .claude/env and sets up the HTTP session
        with proper authentication headers.

        Args:
            config_start_path: Optional starting path for .claude/env search.
                             Defaults to the directory containing this script.

        Raises:
            JiraConfigError: If .claude/env is missing or required variables
                           are not set.
        """
        # Find and load configuration
        env_path = _find_env_file(config_start_path)
        config = _load_env_file(env_path)

        # Validate required variables
        missing_vars = [var for var in self.REQUIRED_VARS if not config.get(var)]
        if missing_vars:
            raise JiraConfigError(
                f"Missing required configuration in {env_path}: {', '.join(missing_vars)}. "
                f"Please add these variables to your .claude/env file."
            )

        # Store configuration
        self._jira_base_url = config["JIRA_BASE_URL"].rstrip("/")
        self._jira_pat = config["JIRA_PAT"]

        # Construct the API base URL
        self.base_url = f"{self._jira_base_url}/rest/api/{self.API_VERSION}/"

        # Set up the session with authentication
        self.session = requests.Session()
        self.session.headers.update(
            {
                "Authorization": f"Bearer {self._jira_pat}",
                "Content-Type": "application/json",
                "Accept": "application/json",
            }
        )

    def _build_url(self, endpoint: str) -> str:
        """Build the full URL for an API endpoint.

        Args:
            endpoint: The API endpoint path (relative to base URL).
                     Leading slashes are handled automatically.

        Returns:
            The full URL for the endpoint
        """
        # Remove leading slash from endpoint if present
        endpoint = endpoint.lstrip("/")
        return f"{self.base_url}{endpoint}"

    def _handle_response(self, response: requests.Response) -> Any:
        """Process an API response and handle errors.

        Args:
            response: The HTTP response object

        Returns:
            Parsed JSON response body, or None for 204 No Content

        Raises:
            JiraAPIError: If the response indicates an error (4xx or 5xx)
        """
        # Check for HTTP errors
        if not response.ok:
            try:
                error_body = response.text
            except Exception:
                error_body = "<unable to read response body>"

            raise JiraAPIError(
                message=f"Jira API request failed: {response.reason}",
                status_code=response.status_code,
                response_body=error_body,
            )

        # Handle 204 No Content (common for DELETE)
        if response.status_code == 204:
            return None

        # Parse JSON response
        try:
            return response.json()
        except ValueError:
            # Some endpoints may return empty responses
            if not response.text:
                return None
            raise JiraAPIError(
                message="Failed to parse JSON response from Jira API",
                status_code=response.status_code,
                response_body=response.text,
            )

    def get(self, endpoint: str, params: dict[str, Any] | None = None) -> Any:
        """Make a GET request to the Jira API.

        Args:
            endpoint: API endpoint path (e.g., "issue/PROJ-123")
            params: Optional query parameters

        Returns:
            Parsed JSON response

        Raises:
            JiraAPIError: If the request fails
        """
        url = self._build_url(endpoint)
        response = self.session.get(url, params=params)
        return self._handle_response(response)

    def post(
        self, endpoint: str, json_body: dict[str, Any] | None = None
    ) -> Any:
        """Make a POST request to the Jira API.

        Args:
            endpoint: API endpoint path (e.g., "issue")
            json_body: Optional JSON request body

        Returns:
            Parsed JSON response

        Raises:
            JiraAPIError: If the request fails
        """
        url = self._build_url(endpoint)
        response = self.session.post(url, json=json_body)
        return self._handle_response(response)

    def put(
        self, endpoint: str, json_body: dict[str, Any] | None = None
    ) -> Any:
        """Make a PUT request to the Jira API.

        Args:
            endpoint: API endpoint path (e.g., "issue/PROJ-123")
            json_body: Optional JSON request body

        Returns:
            Parsed JSON response

        Raises:
            JiraAPIError: If the request fails
        """
        url = self._build_url(endpoint)
        response = self.session.put(url, json=json_body)
        return self._handle_response(response)

    def delete(self, endpoint: str, params: dict[str, Any] | None = None) -> Any:
        """Make a DELETE request to the Jira API.

        Args:
            endpoint: API endpoint path (e.g., "issue/PROJ-123")
            params: Optional query parameters

        Returns:
            Parsed JSON response (usually None for successful deletes)

        Raises:
            JiraAPIError: If the request fails
        """
        url = self._build_url(endpoint)
        response = self.session.delete(url, params=params)
        return self._handle_response(response)


# Convenience function for quick access
def get_client(config_start_path: Path | None = None) -> JiraClient:
    """Create and return a JiraClient instance.

    This is a convenience function for scripts that just need a client.

    Args:
        config_start_path: Optional starting path for .claude/env search

    Returns:
        Configured JiraClient instance
    """
    return JiraClient(config_start_path)
