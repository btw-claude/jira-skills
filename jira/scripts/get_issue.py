#!/usr/bin/env python3
"""Retrieve a Jira issue from JSON input on stdin.

Reads issue key and optional parameters from stdin and returns issue details.

Example:
    echo '{"issue_key": "PROJ-123"}' | python get_issue.py
"""

from __future__ import annotations

import json
import sys
from typing import Any

from jira_api import JiraClient, JiraAPIError


def get_issue(params: dict[str, Any]) -> dict[str, Any]:
    """Retrieve a Jira issue with the given parameters.

    Args:
        params: Input parameters containing issue_key and optional fields/expand

    Returns:
        Full issue JSON from the API

    Raises:
        ValueError: If issue_key is missing
    """
    issue_key = params.get("issue_key")
    if not issue_key:
        raise ValueError("Missing required parameter: issue_key")

    # Build query parameters
    query_params: dict[str, str] = {}

    if params.get("fields"):
        query_params["fields"] = params["fields"]

    if params.get("expand"):
        query_params["expand"] = params["expand"]

    # Build endpoint
    endpoint = f"issue/{issue_key}"

    client = JiraClient()
    return client.get(endpoint, params=query_params if query_params else None)


def main() -> int:
    """Main entry point.

    Returns:
        Exit code (0 for success, 1 for error)
    """
    try:
        # Read JSON from stdin
        input_data = sys.stdin.read().strip()
        if not input_data:
            print("Error: No input provided. Expected JSON on stdin.", file=sys.stderr)
            return 1

        params = json.loads(input_data)

        # Get the issue
        result = get_issue(params)

        # Output result as JSON
        print(json.dumps(result, indent=2))
        return 0

    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON input: {e}", file=sys.stderr)
        return 1
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except JiraAPIError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Error: Unexpected error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
