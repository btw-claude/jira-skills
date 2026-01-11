# Manage Jira Comments

List, add, update, or delete comments on Jira issues.

## Script

```bash
python scripts/manage_comments.py
```

## Input

JSON object on stdin with an `action` field to specify the operation.

### Action: list

List comments on an issue.

| Parameter | Required | Description |
|-----------|----------|-------------|
| `action` | Yes | Set to `"list"` |
| `issue_key` | Yes | Issue key (e.g., "PROJ-123") |
| `max_results` | No | Maximum comments to return |
| `start_at` | No | Index of first result (for pagination) |
| `order_by` | No | Sort order: "created", "-created", "+created" |

### Action: add

Add a comment to an issue.

| Parameter | Required | Description |
|-----------|----------|-------------|
| `action` | Yes | Set to `"add"` |
| `issue_key` | Yes | Issue key (e.g., "PROJ-123") |
| `body` | Yes | Comment text (plain text, converted to ADF) |

### Action: update

Update an existing comment.

| Parameter | Required | Description |
|-----------|----------|-------------|
| `action` | Yes | Set to `"update"` |
| `issue_key` | Yes | Issue key (e.g., "PROJ-123") |
| `comment_id` | Yes | Comment ID to update |
| `body` | Yes | New comment text (plain text, converted to ADF) |

### Action: delete

Delete a comment.

| Parameter | Required | Description |
|-----------|----------|-------------|
| `action` | Yes | Set to `"delete"` |
| `issue_key` | Yes | Issue key (e.g., "PROJ-123") |
| `comment_id` | Yes | Comment ID to delete |

## Examples

List comments on an issue:

```bash
echo '{
  "action": "list",
  "issue_key": "PROJ-123",
  "max_results": 10
}' | python scripts/manage_comments.py
```

Add a comment:

```bash
echo '{
  "action": "add",
  "issue_key": "PROJ-123",
  "body": "This issue is now in code review."
}' | python scripts/manage_comments.py
```

Update a comment:

```bash
echo '{
  "action": "update",
  "issue_key": "PROJ-123",
  "comment_id": "10001",
  "body": "Updated: Code review complete."
}' | python scripts/manage_comments.py
```

Delete a comment:

```bash
echo '{
  "action": "delete",
  "issue_key": "PROJ-123",
  "comment_id": "10001"
}' | python scripts/manage_comments.py
```

## Output

### List Response

```json
{
  "startAt": 0,
  "maxResults": 10,
  "total": 2,
  "comments": [
    {
      "id": "10001",
      "author": {
        "accountId": "5b10a2844c20165700ede21g",
        "displayName": "John Doe"
      },
      "body": { ... },
      "created": "2024-01-15T10:30:00.000+0000",
      "updated": "2024-01-15T10:30:00.000+0000"
    }
  ]
}
```

### Add/Update Response

```json
{
  "id": "10001",
  "author": {
    "accountId": "5b10a2844c20165700ede21g",
    "displayName": "John Doe"
  },
  "body": { ... },
  "created": "2024-01-15T10:30:00.000+0000",
  "updated": "2024-01-15T10:30:00.000+0000"
}
```

### Delete Response

```json
{
  "success": true,
  "message": "Comment 10001 deleted from PROJ-123"
}
```

## Errors

The script will output error details to stderr and exit with non-zero status if:
- Required parameters are missing
- Invalid action specified
- Issue key does not exist
- Comment ID does not exist
- User lacks permission to manage comments
- API authentication fails
