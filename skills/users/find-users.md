# Find Jira Users

Find and retrieve Jira user information.

## Script

```bash
python scripts/find_users.py
```

## Input

JSON object on stdin with `action` and action-specific parameters.

### Actions

| Action | Description |
|--------|-------------|
| `get` | Get a user by account ID |
| `search` | Search users by name or email |
| `assignable` | Find users assignable to a project or issue |

## Action: get

Retrieve a single user by their account ID.

| Parameter | Required | Description |
|-----------|----------|-------------|
| `action` | Yes | Must be `get` |
| `account_id` | Yes | The user's Jira account ID |

```bash
echo '{
  "action": "get",
  "account_id": "5b10ac8d82e05b22cc7d4ef5"
}' | python scripts/find_users.py
```

## Action: search

Search for users by name or email.

| Parameter | Required | Description |
|-----------|----------|-------------|
| `action` | Yes | Must be `search` |
| `query` | Yes | Search string (name or email) |
| `max_results` | No | Maximum results to return |
| `start_at` | No | Pagination offset |

```bash
echo '{
  "action": "search",
  "query": "john"
}' | python scripts/find_users.py
```

With pagination:

```bash
echo '{
  "action": "search",
  "query": "dev",
  "max_results": 10,
  "start_at": 0
}' | python scripts/find_users.py
```

## Action: assignable

Find users who can be assigned to issues in a project or specific issue.

| Parameter | Required | Description |
|-----------|----------|-------------|
| `action` | Yes | Must be `assignable` |
| `project_key` | No* | Project key to check assignability |
| `issue_key` | No* | Issue key to check assignability |
| `query` | No | Filter results by name/email |
| `max_results` | No | Maximum results to return |

*At least one of `project_key` or `issue_key` is required.

By project:

```bash
echo '{
  "action": "assignable",
  "project_key": "PROJ"
}' | python scripts/find_users.py
```

By issue:

```bash
echo '{
  "action": "assignable",
  "issue_key": "PROJ-123"
}' | python scripts/find_users.py
```

With filter:

```bash
echo '{
  "action": "assignable",
  "project_key": "PROJ",
  "query": "john",
  "max_results": 5
}' | python scripts/find_users.py
```

## Output

### Single User (get action)

```json
{
  "accountId": "5b10ac8d82e05b22cc7d4ef5",
  "accountType": "atlassian",
  "displayName": "John Doe",
  "emailAddress": "john.doe@example.com",
  "active": true,
  "avatarUrls": {
    "48x48": "https://...",
    "24x24": "https://...",
    "16x16": "https://...",
    "32x32": "https://..."
  },
  "timeZone": "America/New_York"
}
```

### User List (search/assignable actions)

```json
[
  {
    "accountId": "5b10ac8d82e05b22cc7d4ef5",
    "displayName": "John Doe",
    "emailAddress": "john.doe@example.com",
    "active": true
  },
  {
    "accountId": "5b10a2844c20165700ede21g",
    "displayName": "Jane Smith",
    "emailAddress": "jane.smith@example.com",
    "active": true
  }
]
```

## User Fields

| Field | Description |
|-------|-------------|
| `accountId` | Unique identifier for the user |
| `displayName` | User's display name |
| `emailAddress` | User's email (may be hidden by privacy settings) |
| `active` | Whether the account is active |
| `accountType` | Type: `atlassian`, `app`, `customer` |
| `avatarUrls` | URLs for user avatar in various sizes |
| `timeZone` | User's configured timezone |

## Errors

The script outputs error details to stderr and exits with non-zero status if:
- Required parameters are missing
- User not found (404)
- Permission denied to view user
- API authentication fails
