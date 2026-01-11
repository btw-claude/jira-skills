#!/usr/bin/env python3
"""Create a Jira issue from JSON input on stdin.

Reads issue parameters from stdin and creates a new issue via the Jira API.

Example:
    echo '{"project_key": "PROJ", "summary": "Test", "issue_type": "Task"}' | python create_issue.py
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


def build_issue_fields(params: dict[str, Any]) -> dict[str, Any]:
    """Build the Jira API fields structure from input parameters.

    Args:
        params: Input parameters from stdin

    Returns:
        Fields dictionary for Jira API request

    Raises:
        ValueError: If required parameters are missing
    """
    # Validate required fields
    required = ["project_key", "summary", "issue_type"]
    missing = [field for field in required if not params.get(field)]
    if missing:
        raise ValueError(f"Missing required parameters: {', '.join(missing)}")

    # Build base fields
    fields: dict[str, Any] = {
        "project": {"key": params["project_key"]},
        "summary": params["summary"],
        "issuetype": {"name": params["issue_type"]},
    }

    # Add optional description (convert to ADF)
    if params.get("description"):
        fields["description"] = text_to_adf(params["description"])

    # Add optional assignee
    if params.get("assignee_id"):
        fields["assignee"] = {"accountId": params["assignee_id"]}

    # Add optional labels
    if params.get("labels"):
        labels = params["labels"]
        if isinstance(labels, list):
            fields["labels"] = labels
        else:
            # Handle comma-separated string
            fields["labels"] = [label.strip() for label in str(labels).split(",")]

    # Add optional priority
    if params.get("priority"):
        fields["priority"] = {"name": params["priority"]}

    # Add parent for sub-tasks
    if params.get("parent_key"):
        fields["parent"] = {"key": params["parent_key"]}

    return fields


def create_issue(params: dict[str, Any]) -> dict[str, Any]:
    """Create a Jira issue with the given parameters.

    Args:
        params: Issue parameters

    Returns:
        API response with id, key, and self URL
    """
    fields = build_issue_fields(params)
    body = {"fields": fields}

    client = JiraClient()
    return client.post("issue", body)


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

        # Create the issue
        result = create_issue(params)

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
