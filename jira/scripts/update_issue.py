#!/usr/bin/env python3
"""Update, assign, or delete a Jira issue from JSON input on stdin.

Supports three actions:
- update: Update issue fields (summary, description, priority, labels, assignee)
- assign: Assign or unassign an issue
- delete: Delete an issue

Example:
    echo '{"action": "update", "issue_key": "PROJ-123", "summary": "New title"}' | python update_issue.py
"""

from __future__ import annotations

import json
import sys
from typing import Any

from jira_api import JiraClient, JiraAPIError


def text_to_adf(text: str) -> dict[str, Any]:
    """Convert plain text to Atlassian Document Format (ADF).

    Jira Cloud API v3 requires descriptions in ADF format.

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


def update_issue(client: JiraClient, params: dict[str, Any]) -> dict[str, Any]:
    """Update issue fields.

    Args:
        client: Jira API client
        params: Parameters including issue_key and fields to update

    Returns:
        Success response

    Raises:
        ValueError: If issue_key is missing
    """
    issue_key = params.get("issue_key")
    if not issue_key:
        raise ValueError("Missing required parameter: issue_key")

    fields: dict[str, Any] = {}

    # Build fields to update
    if "summary" in params:
        fields["summary"] = params["summary"]

    if "description" in params:
        desc = params["description"]
        fields["description"] = text_to_adf(desc) if desc else None

    if "priority" in params:
        fields["priority"] = {"name": params["priority"]}

    if "labels" in params:
        labels = params["labels"]
        if isinstance(labels, list):
            fields["labels"] = labels
        elif labels:
            fields["labels"] = [label.strip() for label in str(labels).split(",")]
        else:
            fields["labels"] = []

    if "assignee_id" in params:
        assignee_id = params["assignee_id"]
        fields["assignee"] = {"accountId": assignee_id} if assignee_id else None

    if not fields:
        raise ValueError("No fields to update provided")

    client.put(f"issue/{issue_key}", {"fields": fields})
    return {"success": True, "message": f"Issue {issue_key} updated successfully"}


def assign_issue(client: JiraClient, params: dict[str, Any]) -> dict[str, Any]:
    """Assign or unassign an issue.

    Args:
        client: Jira API client
        params: Parameters including issue_key and optional account_id

    Returns:
        Success response

    Raises:
        ValueError: If issue_key is missing
    """
    issue_key = params.get("issue_key")
    if not issue_key:
        raise ValueError("Missing required parameter: issue_key")

    account_id = params.get("account_id")
    body = {"accountId": account_id}

    client.put(f"issue/{issue_key}/assignee", body)

    if account_id:
        return {"success": True, "message": f"Issue {issue_key} assigned successfully"}
    return {"success": True, "message": f"Issue {issue_key} unassigned successfully"}


def delete_issue(client: JiraClient, params: dict[str, Any]) -> dict[str, Any]:
    """Delete an issue.

    Args:
        client: Jira API client
        params: Parameters including issue_key and optional delete_subtasks

    Returns:
        Success response

    Raises:
        ValueError: If issue_key is missing
    """
    issue_key = params.get("issue_key")
    if not issue_key:
        raise ValueError("Missing required parameter: issue_key")

    query_params = {}
    if params.get("delete_subtasks"):
        query_params["deleteSubtasks"] = "true"

    client.delete(f"issue/{issue_key}", params=query_params if query_params else None)
    return {"success": True, "message": f"Issue {issue_key} deleted successfully"}


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

        # Validate action
        action = params.get("action")
        if not action:
            print("Error: Missing required parameter: action", file=sys.stderr)
            return 1

        client = JiraClient()

        # Dispatch to appropriate handler
        if action == "update":
            result = update_issue(client, params)
        elif action == "assign":
            result = assign_issue(client, params)
        elif action == "delete":
            result = delete_issue(client, params)
        else:
            print(f"Error: Invalid action: {action}. Must be 'update', 'assign', or 'delete'.", file=sys.stderr)
            return 1

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
