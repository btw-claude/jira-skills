#!/usr/bin/env python3
"""Manage comments on Jira issues.

Supports listing, adding, updating, and deleting comments on issues.

Example:
    echo '{"action": "list", "issue_key": "PROJ-123"}' | python manage_comments.py
"""

from __future__ import annotations

import json
import sys
from typing import Any

from jira_api import JiraClient, JiraAPIError


def text_to_adf(text: str) -> dict[str, Any]:
    """Convert plain text to Atlassian Document Format (ADF).

    Jira Cloud API v3 requires comment bodies in ADF format.

    Args:
        text: Plain text string

    Returns:
        ADF document structure
    """
    return {
        "type": "doc",
        "version": 1,
        "content": [
            {
                "type": "paragraph",
                "content": [{"type": "text", "text": text}],
            }
        ],
    }


def list_comments(client: JiraClient, params: dict[str, Any]) -> dict[str, Any]:
    """List comments on an issue.

    Args:
        client: Jira API client
        params: Parameters including issue_key and optional pagination

    Returns:
        API response with comments array
    """
    issue_key = params.get("issue_key")
    if not issue_key:
        raise ValueError("Missing required parameter: issue_key")

    query_params: dict[str, Any] = {}

    if params.get("max_results") is not None:
        query_params["maxResults"] = params["max_results"]

    if params.get("start_at") is not None:
        query_params["startAt"] = params["start_at"]

    if params.get("order_by"):
        query_params["orderBy"] = params["order_by"]

    return client.get(f"issue/{issue_key}/comment", params=query_params or None)


def add_comment(client: JiraClient, params: dict[str, Any]) -> dict[str, Any]:
    """Add a comment to an issue.

    Args:
        client: Jira API client
        params: Parameters including issue_key and body

    Returns:
        API response with created comment details
    """
    issue_key = params.get("issue_key")
    body = params.get("body")

    if not issue_key:
        raise ValueError("Missing required parameter: issue_key")
    if not body:
        raise ValueError("Missing required parameter: body")

    request_body = {"body": text_to_adf(body)}

    return client.post(f"issue/{issue_key}/comment", request_body)


def update_comment(client: JiraClient, params: dict[str, Any]) -> dict[str, Any]:
    """Update an existing comment.

    Args:
        client: Jira API client
        params: Parameters including issue_key, comment_id, and body

    Returns:
        API response with updated comment details
    """
    issue_key = params.get("issue_key")
    comment_id = params.get("comment_id")
    body = params.get("body")

    if not issue_key:
        raise ValueError("Missing required parameter: issue_key")
    if not comment_id:
        raise ValueError("Missing required parameter: comment_id")
    if not body:
        raise ValueError("Missing required parameter: body")

    request_body = {"body": text_to_adf(body)}

    return client.put(f"issue/{issue_key}/comment/{comment_id}", request_body)


def delete_comment(client: JiraClient, params: dict[str, Any]) -> dict[str, Any]:
    """Delete a comment from an issue.

    Args:
        client: Jira API client
        params: Parameters including issue_key and comment_id

    Returns:
        Success message
    """
    issue_key = params.get("issue_key")
    comment_id = params.get("comment_id")

    if not issue_key:
        raise ValueError("Missing required parameter: issue_key")
    if not comment_id:
        raise ValueError("Missing required parameter: comment_id")

    client.delete(f"issue/{issue_key}/comment/{comment_id}")

    return {
        "success": True,
        "message": f"Comment {comment_id} deleted from {issue_key}",
    }


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

        action = params.get("action")
        if not action:
            print("Error: Missing required parameter: action", file=sys.stderr)
            return 1

        client = JiraClient()

        actions = {
            "list": list_comments,
            "add": add_comment,
            "update": update_comment,
            "delete": delete_comment,
        }

        if action not in actions:
            valid = ", ".join(sorted(actions.keys()))
            print(f"Error: Invalid action '{action}'. Valid actions: {valid}", file=sys.stderr)
            return 1

        result = actions[action](client, params)
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
