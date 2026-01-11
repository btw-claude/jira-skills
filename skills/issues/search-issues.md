# Search Jira Issues

Search for Jira issues using JQL (Jira Query Language).

## Script

```bash
python scripts/search_issues.py
```

## Input

JSON object on stdin with the following parameters:

| Parameter | Required | Description |
|-----------|----------|-------------|
| `jql` | Yes | JQL query string |
| `fields` | No | Comma-separated list of fields to return |
| `max_results` | No | Maximum results to return (default: 50) |
| `start_at` | No | Pagination offset (default: 0) |
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

## JQL Reference

### Fields

| Field | Description | Example |
|-------|-------------|---------|
| `project` | Project key | `project = PROJ` |
| `issuetype` | Issue type | `issuetype = Bug` |
| `status` | Issue status | `status = "In Progress"` |
| `assignee` | Assigned user | `assignee = currentUser()` |
| `reporter` | Issue reporter | `reporter = "john.doe"` |
| `priority` | Priority level | `priority = High` |
| `labels` | Issue labels | `labels = urgent` |
| `created` | Creation date | `created >= -7d` |
| `updated` | Last updated date | `updated >= -1d` |
| `resolved` | Resolution date | `resolved >= startOfMonth()` |
| `summary` | Issue summary | `summary ~ "login"` |
| `description` | Issue description | `description ~ "error"` |
| `fixVersion` | Fix version | `fixVersion = "1.0"` |
| `component` | Component | `component = "Backend"` |
| `sprint` | Sprint name/ID | `sprint = "Sprint 1"` |

### Operators

| Operator | Description | Example |
|----------|-------------|---------|
| `=`, `!=` | Exact match | `status = Open` |
| `~`, `!~` | Contains text | `summary ~ "login"` |
| `IN`, `NOT IN` | Multiple values | `status IN (Open, "In Progress")` |
| `>`, `>=`, `<`, `<=` | Comparisons | `created >= -7d` |
| `IS`, `IS NOT` | Null checks | `assignee IS EMPTY` |
| `WAS`, `WAS IN`, `WAS NOT` | Historical values | `status WAS Open` |

### Functions

| Function | Description | Example |
|----------|-------------|---------|
| `currentUser()` | Logged in user | `assignee = currentUser()` |
| `startOfDay()` | Start of today | `created >= startOfDay()` |
| `endOfDay()` | End of today | `created <= endOfDay()` |
| `startOfWeek()` | Start of current week | `created >= startOfWeek()` |
| `startOfMonth()` | Start of current month | `created >= startOfMonth()` |
| `membersOf()` | Group members | `assignee IN membersOf("developers")` |

### Relative Dates

Use relative date syntax for dynamic queries:
- `-1d` - 1 day ago
- `-7d` - 7 days ago
- `-30d` - 30 days ago
- `-4w` - 4 weeks ago

### Sorting

Add `ORDER BY` clause for sorting:
- `ORDER BY created DESC`
- `ORDER BY priority ASC, created DESC`

## Example Queries

Search open issues in a project:

```bash
echo '{
  "jql": "project = PROJ AND status = Open"
}' | python scripts/search_issues.py
```

Find issues assigned to current user:

```bash
echo '{
  "jql": "assignee = currentUser() AND status != Done",
  "fields": "summary,status,priority"
}' | python scripts/search_issues.py
```

Find recently created issues:

```bash
echo '{
  "jql": "created >= -7d ORDER BY created DESC",
  "max_results": 20
}' | python scripts/search_issues.py
```

Find urgent issues:

```bash
echo '{
  "jql": "labels IN (urgent, critical) AND status != Done"
}' | python scripts/search_issues.py
```

Text search across summary and description:

```bash
echo '{
  "jql": "summary ~ \"login\" OR description ~ \"login\""
}' | python scripts/search_issues.py
```

Paginated results:

```bash
echo '{
  "jql": "project = PROJ",
  "max_results": 25,
  "start_at": 25
}' | python scripts/search_issues.py
```

Get issues with changelog:

```bash
echo '{
  "jql": "project = PROJ AND updated >= -1d",
  "expand": "changelog"
}' | python scripts/search_issues.py
```

## Output

JSON response with issues and pagination info:

```json
{
  "expand": "names,schema",
  "startAt": 0,
  "maxResults": 50,
  "total": 125,
  "issues": [
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
  ]
}
```

### Pagination

Use `startAt` and `maxResults` to paginate through large result sets:
- `total` - Total number of matching issues
- `startAt` - Current offset
- `maxResults` - Number of results returned

To get the next page, set `start_at` to `startAt + maxResults`.

## Errors

The script will output error details to stderr and exit with non-zero status if:
- Required `jql` parameter is missing
- JQL syntax is invalid
- User lacks permission to view issues
- API authentication fails
