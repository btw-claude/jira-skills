#!/usr/bin/env python3
"""Find Jira users from JSON input on stdin.

Supports three actions:
- get: Retrieve a user by account ID
- search: Search users by query string
- assignable: Find users assignable to a project or issue

Example:
    echo '{"action": "search", "query": "john"}' | python find_users.py
"""

from __future__ import annotations

import json
import sys
from typing import Any

from jira_api import JiraClient, JiraAPIError


def get_user(client: JiraClient, params: dict[str, Any]) -> dict[str, Any]:
    """Get a user by account ID.

    Args:
        client: Jira API client
        params: Input parameters containing account_id

    Returns:
        User details from the API

    Raises:
        ValueError: If account_id is missing
    """
    account_id = params.get("account_id")
    if not account_id:
        raise ValueError("Missing required parameter: account_id")

    return client.get("user", params={"accountId": account_id})


def search_users(client: JiraClient, params: dict[str, Any]) -> list[dict[str, Any]]:
    """Search for users by query string.

    Args:
        client: Jira API client
        params: Input parameters containing query and optional pagination

    Returns:
        List of matching users

    Raises:
        ValueError: If query is missing
    """
    query = params.get("query")
    if not query:
        raise ValueError("Missing required parameter: query")

    query_params: dict[str, Any] = {"query": query}

    if params.get("max_results") is not None:
        query_params["maxResults"] = int(params["max_results"])

    if params.get("start_at") is not None:
        query_params["startAt"] = int(params["start_at"])

    return client.get("user/search", params=query_params)


def get_assignable_users(
    client: JiraClient, params: dict[str, Any]
) -> list[dict[str, Any]]:
    """Get users assignable to a project or issue.

    Args:
        client: Jira API client
        params: Input parameters with optional project_key, issue_key, query, max_results

    Returns:
        List of assignable users

    Raises:
        ValueError: If neither project_key nor issue_key is provided
    """
    project_key = params.get("project_key")
    issue_key = params.get("issue_key")

    if not project_key and not issue_key:
        raise ValueError("At least one of project_key or issue_key is required")

    query_params: dict[str, Any] = {}

    if project_key:
        query_params["project"] = project_key

    if issue_key:
        query_params["issueKey"] = issue_key

    if params.get("query"):
        query_params["query"] = params["query"]

    if params.get("max_results") is not None:
        query_params["maxResults"] = int(params["max_results"])

    return client.get("user/assignable/search", params=query_params)


def find_users(params: dict[str, Any]) -> dict[str, Any] | list[dict[str, Any]]:
    """Route to the appropriate user operation based on action.

    Args:
        params: Input parameters with action and action-specific fields

    Returns:
        API response (user object or list of users)

    Raises:
        ValueError: If action is missing or invalid
    """
    action = params.get("action")
    if not action:
        raise ValueError("Missing required parameter: action")

    client = JiraClient()

    if action == "get":
        return get_user(client, params)
    elif action == "search":
        return search_users(client, params)
    elif action == "assignable":
        return get_assignable_users(client, params)
    else:
        raise ValueError(f"Invalid action: {action}. Must be: get, search, assignable")


def main() -> int:
    """Main entry point.

    Returns:
        Exit code (0 for success, 1 for error)
    """
    try:
        input_data = sys.stdin.read().strip()
        if not input_data:
            print("Error: No input provided. Expected JSON on stdin.", file=sys.stderr)
            return 1

        params = json.loads(input_data)
        result = find_users(params)
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
