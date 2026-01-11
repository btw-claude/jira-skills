#!/usr/bin/env python3
"""Manage Jira projects from JSON input on stdin.

Supports five actions:
- list: List all projects
- get: Get a single project by key
- create: Create a new project
- update: Update an existing project
- delete: Delete a project

Example:
    echo '{"action": "list"}' | python manage_project.py
"""

from __future__ import annotations

import json
import sys
from typing import Any

from jira_api import JiraClient, JiraAPIError


def list_projects(client: JiraClient, params: dict[str, Any]) -> dict[str, Any]:
    """List all projects.

    Args:
        client: Jira API client
        params: Parameters including max_results, start_at, expand

    Returns:
        List of projects with pagination info
    """
    query_params: dict[str, Any] = {}

    if "max_results" in params:
        query_params["maxResults"] = params["max_results"]

    if "start_at" in params:
        query_params["startAt"] = params["start_at"]

    if "expand" in params:
        query_params["expand"] = params["expand"]

    result = client.get("project/search", params=query_params if query_params else None)
    return result


def get_project(client: JiraClient, params: dict[str, Any]) -> dict[str, Any]:
    """Get a single project by key.

    Args:
        client: Jira API client
        params: Parameters including project_key and optional expand

    Returns:
        Project details

    Raises:
        ValueError: If project_key is missing
    """
    project_key = params.get("project_key")
    if not project_key:
        raise ValueError("Missing required parameter: project_key")

    query_params: dict[str, Any] = {}
    if "expand" in params:
        query_params["expand"] = params["expand"]

    result = client.get(
        f"project/{project_key}",
        params=query_params if query_params else None
    )
    return result


def create_project(client: JiraClient, params: dict[str, Any]) -> dict[str, Any]:
    """Create a new project.

    Args:
        client: Jira API client
        params: Parameters for project creation

    Returns:
        Success response with project info

    Raises:
        ValueError: If required parameters are missing
    """
    required = ["key", "name", "project_type_key", "project_template_key", "lead_account_id"]
    missing = [p for p in required if not params.get(p)]
    if missing:
        raise ValueError(f"Missing required parameters: {', '.join(missing)}")

    body: dict[str, Any] = {
        "key": params["key"],
        "name": params["name"],
        "projectTypeKey": params["project_type_key"],
        "projectTemplateKey": params["project_template_key"],
        "leadAccountId": params["lead_account_id"],
    }

    if "description" in params:
        body["description"] = params["description"]

    result = client.post("project", body)
    return {
        "success": True,
        "message": f"Project {params['key']} created successfully",
        "project": result,
    }


def update_project(client: JiraClient, params: dict[str, Any]) -> dict[str, Any]:
    """Update an existing project.

    Args:
        client: Jira API client
        params: Parameters including project_key and fields to update

    Returns:
        Success response

    Raises:
        ValueError: If project_key is missing or no fields to update
    """
    project_key = params.get("project_key")
    if not project_key:
        raise ValueError("Missing required parameter: project_key")

    body: dict[str, Any] = {}

    if "name" in params:
        body["name"] = params["name"]

    if "description" in params:
        body["description"] = params["description"]

    if "lead_account_id" in params:
        body["leadAccountId"] = params["lead_account_id"]

    if not body:
        raise ValueError("No fields to update provided")

    client.put(f"project/{project_key}", body)
    return {"success": True, "message": f"Project {project_key} updated successfully"}


def delete_project(client: JiraClient, params: dict[str, Any]) -> dict[str, Any]:
    """Delete a project.

    Args:
        client: Jira API client
        params: Parameters including project_key and optional enable_undo

    Returns:
        Success response

    Raises:
        ValueError: If project_key is missing
    """
    project_key = params.get("project_key")
    if not project_key:
        raise ValueError("Missing required parameter: project_key")

    query_params: dict[str, Any] = {}

    # enable_undo defaults to True; only set if explicitly False
    if params.get("enable_undo") is False:
        query_params["enableUndo"] = "false"

    client.delete(
        f"project/{project_key}",
        params=query_params if query_params else None
    )
    return {"success": True, "message": f"Project {project_key} deleted successfully"}


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
        if action == "list":
            result = list_projects(client, params)
        elif action == "get":
            result = get_project(client, params)
        elif action == "create":
            result = create_project(client, params)
        elif action == "update":
            result = update_project(client, params)
        elif action == "delete":
            result = delete_project(client, params)
        else:
            valid_actions = "'list', 'get', 'create', 'update', or 'delete'"
            print(f"Error: Invalid action: {action}. Must be {valid_actions}.", file=sys.stderr)
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
