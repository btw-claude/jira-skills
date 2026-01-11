# Update Jira Issue

Update, assign, or delete a Jira issue.

## Script

```bash
python scripts/update_issue.py
```

## Input

JSON object on stdin with an `action` field to specify the operation.

### Action: update

Update issue fields.

| Parameter | Required | Description |
|-----------|----------|-------------|
| `action` | Yes | Set to `"update"` |
| `issue_key` | Yes | Issue key (e.g., "PROJ-123") |
| `summary` | No | New issue title |
| `description` | No | New description (plain text) |
| `priority` | No | "Highest", "High", "Medium", "Low", "Lowest" |
| `labels` | No | Array of labels (replaces existing) |
| `assignee_id` | No | Jira account ID for assignee |

### Action: assign

Assign or unassign an issue.

| Parameter | Required | Description |
|-----------|----------|-------------|
| `action` | Yes | Set to `"assign"` |
| `issue_key` | Yes | Issue key (e.g., "PROJ-123") |
| `account_id` | No | Account ID to assign, or omit/null to unassign |

### Action: delete

Delete an issue.

| Parameter | Required | Description |
|-----------|----------|-------------|
| `action` | Yes | Set to `"delete"` |
| `issue_key` | Yes | Issue key (e.g., "PROJ-123") |
| `delete_subtasks` | No | Boolean, delete subtasks (default: false) |

## Examples

Update issue fields:

```bash
echo '{
  "action": "update",
  "issue_key": "PROJ-123",
  "summary": "Updated title",
  "priority": "High",
  "labels": ["urgent", "backend"]
}' | python scripts/update_issue.py
```

Assign an issue:

```bash
echo '{
  "action": "assign",
  "issue_key": "PROJ-123",
  "account_id": "5b10a2844c20165700ede21g"
}' | python scripts/update_issue.py
```

Unassign an issue:

```bash
echo '{
  "action": "assign",
  "issue_key": "PROJ-123",
  "account_id": null
}' | python scripts/update_issue.py
```

Delete an issue with subtasks:

```bash
echo '{
  "action": "delete",
  "issue_key": "PROJ-123",
  "delete_subtasks": true
}' | python scripts/update_issue.py
```

## Output

Update and assign return success message:

```json
{
  "success": true,
  "message": "Issue PROJ-123 updated successfully"
}
```

Delete returns:

```json
{
  "success": true,
  "message": "Issue PROJ-123 deleted successfully"
}
```

## Errors

The script will output error details to stderr and exit with non-zero status if:
- Required parameters are missing
- Invalid action specified
- Issue key does not exist
- User lacks permission to modify the issue
- API authentication fails
