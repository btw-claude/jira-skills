#!/usr/bin/env python3
"""Manage Jira issue links.

Supports four actions:
- get_types: Get available link types
- create: Create a link between two issues
- get: Get details of a specific link
- delete: Delete a link

Example:
    echo '{"action": "get_types"}' | python manage_issue_links.py
    echo '{"action": "create", "link_type": "Blocks", "inward_issue_key": "PROJ-1", "outward_issue_key": "PROJ-2"}' | python manage_issue_links.py
    echo '{"action": "get", "link_id": "10001"}' | python manage_issue_links.py
    echo '{"action": "delete", "link_id": "10001"}' | python manage_issue_links.py
"""

from __future__ import annotations

import json
import sys
from typing import Any

from jira_api import JiraClient, JiraAPIError


def get_link_types(client: JiraClient) -> dict[str, Any]:
    """Get all available issue link types.

    Args:
        client: JiraClient instance

    Returns:
        Dictionary with issueLinkTypes array
    """
    response = client.get("issueLinkType")
    return response


def create_link(
    client: JiraClient,
    link_type: str,
    inward_issue_key: str,
    outward_issue_key: str,
) -> dict[str, Any]:
    """Create a link between two issues.

    Args:
        client: JiraClient instance
        link_type: Link type name (e.g., "Blocks", "Clones", "Relates")
        inward_issue_key: Key of the inward issue (e.g., "PROJ-1")
        outward_issue_key: Key of the outward issue (e.g., "PROJ-2")

    Returns:
        Empty dict on success (API returns 201 with no content)
    """
    body = {
        "type": {"name": link_type},
        "inwardIssue": {"key": inward_issue_key},
        "outwardIssue": {"key": outward_issue_key},
    }

    result = client.post("issueLink", body)
    return result if result is not None else {"success": True}


def get_link(client: JiraClient, link_id: str) -> dict[str, Any]:
    """Get details of a specific issue link.

    Args:
        client: JiraClient instance
        link_id: The ID of the issue link

    Returns:
        Link details including type, inward and outward issues
    """
    return client.get(f"issueLink/{link_id}")


def delete_link(client: JiraClient, link_id: str) -> dict[str, Any]:
    """Delete an issue link.

    Args:
        client: JiraClient instance
        link_id: The ID of the issue link to delete

    Returns:
        Success message dict
    """
    client.delete(f"issueLink/{link_id}")
    return {"success": True, "message": f"Link {link_id} deleted successfully"}


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

        valid_actions = ("get_types", "create", "get", "delete")
        if action not in valid_actions:
            print(
                f"Error: Invalid action '{action}'. Must be one of: {', '.join(valid_actions)}",
                file=sys.stderr,
            )
            return 1

        client = JiraClient()

        if action == "get_types":
            result = get_link_types(client)

        elif action == "create":
            # Validate required params
            link_type = params.get("link_type")
            inward_issue_key = params.get("inward_issue_key")
            outward_issue_key = params.get("outward_issue_key")

            missing = []
            if not link_type:
                missing.append("link_type")
            if not inward_issue_key:
                missing.append("inward_issue_key")
            if not outward_issue_key:
                missing.append("outward_issue_key")

            if missing:
                print(
                    f"Error: Missing required parameters: {', '.join(missing)}",
                    file=sys.stderr,
                )
                return 1

            result = create_link(client, link_type, inward_issue_key, outward_issue_key)

        elif action == "get":
            link_id = params.get("link_id")
            if not link_id:
                print("Error: Missing required parameter: link_id", file=sys.stderr)
                return 1
            result = get_link(client, link_id)

        elif action == "delete":
            link_id = params.get("link_id")
            if not link_id:
                print("Error: Missing required parameter: link_id", file=sys.stderr)
                return 1
            result = delete_link(client, link_id)

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
