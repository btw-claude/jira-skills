#!/usr/bin/env python3
"""Transition a Jira issue to a new status.

Supports two actions:
- get_transitions: Get available transitions for an issue
- transition: Move issue to a new status

Example:
    echo '{"action": "get_transitions", "issue_key": "PROJ-123"}' | python transition_issue.py
    echo '{"action": "transition", "issue_key": "PROJ-123", "transition_id": "31"}' | python transition_issue.py
"""

from __future__ import annotations

import json
import sys
from typing import Any

from jira_api import JiraClient, JiraAPIError


def text_to_adf(text: str) -> dict[str, Any]:
    """Convert plain text to Atlassian Document Format (ADF).

    Jira Cloud API v3 requires text content in ADF format.

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


def get_transitions(client: JiraClient, issue_key: str) -> dict[str, Any]:
    """Get available transitions for an issue.

    Args:
        client: JiraClient instance
        issue_key: Issue key (e.g., "PROJ-123")

    Returns:
        Dictionary with transitions array containing id and name
    """
    endpoint = f"issue/{issue_key}/transitions"
    response = client.get(endpoint)

    # Extract just id and name for cleaner output
    transitions = [
        {"id": t["id"], "name": t["name"]}
        for t in response.get("transitions", [])
    ]

    return {"transitions": transitions}


def transition_issue(
    client: JiraClient,
    issue_key: str,
    transition_id: str,
    comment: str | None = None,
) -> dict[str, Any]:
    """Transition an issue to a new status.

    Args:
        client: JiraClient instance
        issue_key: Issue key (e.g., "PROJ-123")
        transition_id: ID of the transition to perform
        comment: Optional comment to add with the transition

    Returns:
        Empty dict on success (API returns 204 No Content)
    """
    endpoint = f"issue/{issue_key}/transitions"

    body: dict[str, Any] = {
        "transition": {"id": transition_id}
    }

    # Add comment if provided
    if comment:
        body["update"] = {
            "comment": [
                {
                    "add": {
                        "body": text_to_adf(comment)
                    }
                }
            ]
        }

    result = client.post(endpoint, body)

    # POST returns None (204 No Content) on success
    return result if result is not None else {}


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

        if action not in ("get_transitions", "transition"):
            print(
                f"Error: Invalid action '{action}'. Must be 'get_transitions' or 'transition'",
                file=sys.stderr,
            )
            return 1

        # Validate issue_key
        issue_key = params.get("issue_key")
        if not issue_key:
            print("Error: Missing required parameter: issue_key", file=sys.stderr)
            return 1

        client = JiraClient()

        if action == "get_transitions":
            result = get_transitions(client, issue_key)
        else:
            # action == "transition"
            transition_id = params.get("transition_id")
            if not transition_id:
                print(
                    "Error: Missing required parameter: transition_id",
                    file=sys.stderr,
                )
                return 1

            comment = params.get("comment")
            result = transition_issue(client, issue_key, transition_id, comment)

        # Output result as JSON
        print(json.dumps(result, indent=2))
        return 0

    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON input: {e}", file=sys.stderr)
        return 1
    except JiraAPIError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Error: Unexpected error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
