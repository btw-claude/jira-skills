# Create Jira Issue

Create a new issue in a Jira project with specified fields.

## Script

```bash
python scripts/create_issue.py
```

## Input

JSON object on stdin with the following parameters:

| Parameter | Required | Description |
|-----------|----------|-------------|
| `project_key` | Yes | Project key (e.g., "PROJ") |
| `summary` | Yes | Issue title/summary |
| `issue_type` | Yes | Type: "Task", "Bug", "Story", "Epic", "Sub-task" |
| `description` | No | Issue description (plain text) |
| `assignee_id` | No | Jira account ID for assignee |
| `labels` | No | Array of label strings |
| `priority` | No | "Highest", "High", "Medium", "Low", "Lowest" |
| `parent_key` | No | Parent issue key (required for Sub-tasks) |

## Example

Create a basic task:

```bash
cat << 'EOF' | python scripts/create_issue.py
{
  "project_key": "PROJ",
  "summary": "Implement user authentication",
  "issue_type": "Task",
  "description": "Add OAuth2 authentication flow",
  "priority": "High",
  "labels": ["backend", "security"]
}
EOF
```

Create an issue with multi-line description:

```bash
cat << 'EOF' | python scripts/create_issue.py
{
  "project_key": "PROJ",
  "summary": "Update API endpoints",
  "issue_type": "Task",
  "description": "Update the following endpoints:\n\n- GET /users\n- POST /users\n- DELETE /users/:id\n\nEnsure proper error handling."
}
EOF
```

Create a sub-task:

```bash
cat << 'EOF' | python scripts/create_issue.py
{
  "project_key": "PROJ",
  "summary": "Write unit tests for auth module",
  "issue_type": "Sub-task",
  "parent_key": "PROJ-123"
}
EOF
```

**Note:** Always use heredoc syntax (`cat << 'EOF'`) instead of `echo` to avoid JSON parsing errors with special characters or newlines in descriptions.

## Output

JSON response with created issue details:

```json
{
  "id": "10001",
  "key": "PROJ-124",
  "self": "https://your-domain.atlassian.net/rest/api/3/issue/10001"
}
```

## Errors

The script will output error details to stderr and exit with non-zero status if:
- Required parameters are missing
- Project key is invalid
- Issue type is not available in the project
- API authentication fails
