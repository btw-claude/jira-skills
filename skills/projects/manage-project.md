# Manage Jira Projects

List, get, create, update, or delete Jira projects.

## Script

```bash
python scripts/manage_project.py
```

## Input

JSON object on stdin with an `action` field to specify the operation.

### Action: list

List all projects.

| Parameter | Required | Description |
|-----------|----------|-------------|
| `action` | Yes | Set to `"list"` |
| `max_results` | No | Maximum number of results (default: 50) |
| `start_at` | No | Index of first result (default: 0) |
| `expand` | No | Comma-separated fields to expand |

### Action: get

Get a single project by key.

| Parameter | Required | Description |
|-----------|----------|-------------|
| `action` | Yes | Set to `"get"` |
| `project_key` | Yes | Project key (e.g., "PROJ") |
| `expand` | No | Comma-separated fields to expand |

### Action: create

Create a new project.

| Parameter | Required | Description |
|-----------|----------|-------------|
| `action` | Yes | Set to `"create"` |
| `key` | Yes | Unique project key (e.g., "PROJ") |
| `name` | Yes | Project display name |
| `project_type_key` | Yes | Type: "software", "business", or "service_desk" |
| `project_template_key` | Yes | Template key (see below) |
| `lead_account_id` | Yes | Account ID for project lead |
| `description` | No | Project description |

Common template keys:
- Software Kanban: `com.pyxis.greenhopper.jira:gh-simplified-kanban-classic`
- Software Scrum: `com.pyxis.greenhopper.jira:gh-simplified-scrum-classic`
- Software Basic: `com.pyxis.greenhopper.jira:gh-simplified-basic`
- Business Task Tracking: `com.atlassian.jira-core-project-templates:jira-core-simplified-task-tracking`

### Action: update

Update an existing project.

| Parameter | Required | Description |
|-----------|----------|-------------|
| `action` | Yes | Set to `"update"` |
| `project_key` | Yes | Project key to update |
| `name` | No | New project name |
| `description` | No | New description |
| `lead_account_id` | No | New lead account ID |

### Action: delete

Delete a project.

| Parameter | Required | Description |
|-----------|----------|-------------|
| `action` | Yes | Set to `"delete"` |
| `project_key` | Yes | Project key to delete |
| `enable_undo` | No | Allow restore from recycle bin (default: true) |

## Examples

List all projects:

```bash
echo '{
  "action": "list",
  "max_results": 10
}' | python scripts/manage_project.py
```

Get a project:

```bash
echo '{
  "action": "get",
  "project_key": "PROJ"
}' | python scripts/manage_project.py
```

Create a Kanban project:

```bash
echo '{
  "action": "create",
  "key": "NEWPROJ",
  "name": "New Project",
  "project_type_key": "software",
  "project_template_key": "com.pyxis.greenhopper.jira:gh-simplified-kanban-classic",
  "lead_account_id": "5b10a2844c20165700ede21g",
  "description": "A new software project"
}' | python scripts/manage_project.py
```

Update a project:

```bash
echo '{
  "action": "update",
  "project_key": "PROJ",
  "name": "Updated Project Name",
  "description": "Updated description"
}' | python scripts/manage_project.py
```

Delete a project (with undo):

```bash
echo '{
  "action": "delete",
  "project_key": "PROJ"
}' | python scripts/manage_project.py
```

Permanently delete a project:

```bash
echo '{
  "action": "delete",
  "project_key": "PROJ",
  "enable_undo": false
}' | python scripts/manage_project.py
```

## Output

List returns array of projects:

```json
{
  "values": [
    {
      "key": "PROJ",
      "name": "My Project",
      "projectTypeKey": "software"
    }
  ],
  "total": 1
}
```

Get returns project details:

```json
{
  "key": "PROJ",
  "name": "My Project",
  "description": "Project description",
  "lead": {
    "accountId": "5b10a2844c20165700ede21g",
    "displayName": "John Doe"
  }
}
```

Create returns new project:

```json
{
  "success": true,
  "message": "Project NEWPROJ created successfully",
  "project": {
    "id": "10001",
    "key": "NEWPROJ"
  }
}
```

Update returns:

```json
{
  "success": true,
  "message": "Project PROJ updated successfully"
}
```

Delete returns:

```json
{
  "success": true,
  "message": "Project PROJ deleted successfully"
}
```

## Errors

The script outputs error details to stderr and exits with non-zero status if:
- Required parameters are missing
- Invalid action specified
- Project key does not exist
- User lacks permission to manage projects
- API authentication fails
