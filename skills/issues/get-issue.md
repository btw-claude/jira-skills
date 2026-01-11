# Get Jira Issue

Retrieve details of a Jira issue by its key.

## Script

```bash
python scripts/get_issue.py
```

## Input

JSON object on stdin with the following parameters:

| Parameter | Required | Description |
|-----------|----------|-------------|
| `issue_key` | Yes | Issue key (e.g., "PROJ-123") |
| `fields` | No | Comma-separated list of fields to return |
| `expand` | No | Comma-separated list of expansions |

### Fields Parameter

Specify which fields to include in the response. Common fields:
- `summary`, `description`, `status`, `priority`
- `assignee`, `reporter`, `creator`
- `created`, `updated`, `resolutiondate`
- `labels`, `components`, `fixVersions`
- `issuetype`, `project`

Use `*all` for all fields, or `*navigable` for default navigable fields.

### Expand Parameter

Request additional data in the response:
- `changelog` - Issue change history
- `renderedFields` - HTML-rendered field values
- `names` - Field display names
- `schema` - Field schema information
- `operations` - Available operations
- `editmeta` - Edit metadata

## Example

Get basic issue details:

```bash
echo '{"issue_key": "PROJ-123"}' | python scripts/get_issue.py
```

Get specific fields only:

```bash
echo '{
  "issue_key": "PROJ-123",
  "fields": "summary,status,assignee,priority"
}' | python scripts/get_issue.py
```

Get issue with changelog:

```bash
echo '{
  "issue_key": "PROJ-123",
  "expand": "changelog,renderedFields"
}' | python scripts/get_issue.py
```

## Output

JSON response with full issue details:

```json
{
  "id": "10001",
  "key": "PROJ-123",
  "self": "https://your-domain.atlassian.net/rest/api/3/issue/10001",
  "fields": {
    "summary": "Issue title",
    "status": {
      "name": "In Progress"
    },
    "priority": {
      "name": "High"
    },
    "assignee": {
      "displayName": "John Doe",
      "accountId": "abc123"
    }
  }
}
```

## Errors

The script will output error details to stderr and exit with non-zero status if:
- Required `issue_key` parameter is missing
- Issue key does not exist
- User lacks permission to view the issue
- API authentication fails
