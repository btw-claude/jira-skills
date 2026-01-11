#!/usr/bin/env python3
"""Search for Jira issues using JQL from JSON input on stdin.

Reads search parameters from stdin and returns matching issues via the Jira API.

Example:
    echo '{"jql": "project = PROJ AND status = Open"}' | python search_issues.py
"""

from __future__ import annotations

import json
import sys
from typing import Any

from jira_api import JiraClient, JiraAPIError


def search_issues(params: dict[str, Any]) -> dict[str, Any]:
    """Search for Jira issues with the given parameters.

    Args:
        params: Input parameters containing jql and optional fields/pagination

    Returns:
        Search results JSON from the API with issues and pagination info

    Raises:
        ValueError: If jql is missing
    """
    jql = params.get("jql")
    if not jql:
        raise ValueError("Missing required parameter: jql")

    # Build request body
    body: dict[str, Any] = {
        "jql": jql,
    }

    # Add optional fields
    if params.get("fields"):
        fields = params["fields"]
        if isinstance(fields, list):
            body["fields"] = fields
        else:
            # Handle comma-separated string
            body["fields"] = [f.strip() for f in str(fields).split(",")]

    # Add pagination parameters
    if params.get("max_results") is not None:
        body["maxResults"] = int(params["max_results"])
    else:
        body["maxResults"] = 50  # Default

    if params.get("start_at") is not None:
        body["startAt"] = int(params["start_at"])
    else:
        body["startAt"] = 0  # Default

    # Add expand parameter
    if params.get("expand"):
        expand = params["expand"]
        if isinstance(expand, list):
            body["expand"] = expand
        else:
            # Handle comma-separated string
            body["expand"] = [e.strip() for e in str(expand).split(",")]

    client = JiraClient()
    return client.post("search", body)


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

        # Search for issues
        result = search_issues(params)

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
