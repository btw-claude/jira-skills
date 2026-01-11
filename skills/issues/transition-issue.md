# Transition Jira Issue

Get available transitions and change issue status.

## Script

```bash
python scripts/transition_issue.py
```

## Operations

### Get Available Transitions

Retrieve the list of valid transitions for an issue based on its current status.

#### Input

JSON object on stdin:

| Parameter | Required | Description |
|-----------|----------|-------------|
| `action` | Yes | Set to `"get_transitions"` |
| `issue_key` | Yes | Issue key (e.g., "PROJ-123") |

#### Example

```bash
echo '{
  "action": "get_transitions",
  "issue_key": "PROJ-123"
}' | python scripts/transition_issue.py
```

#### Output

```json
{
  "transitions": [
    {"id": "21", "name": "In Progress"},
    {"id": "31", "name": "Done"},
    {"id": "41", "name": "Blocked"}
  ]
}
```

### Transition Issue

Move an issue to a new status.

#### Input

JSON object on stdin:

| Parameter | Required | Description |
|-----------|----------|-------------|
| `action` | Yes | Set to `"transition"` |
| `issue_key` | Yes | Issue key (e.g., "PROJ-123") |
| `transition_id` | Yes | Transition ID from get_transitions |
| `comment` | No | Comment to add with the transition (plain text) |

#### Example

Transition without comment:

```bash
echo '{
  "action": "transition",
  "issue_key": "PROJ-123",
  "transition_id": "31"
}' | python scripts/transition_issue.py
```

Transition with comment:

```bash
echo '{
  "action": "transition",
  "issue_key": "PROJ-123",
  "transition_id": "31",
  "comment": "Completed code review and testing"
}' | python scripts/transition_issue.py
```

#### Output

Success returns empty JSON object:

```json
{}
```

## Errors

The script will output error details to stderr and exit with non-zero status if:
- Required parameters are missing
- Invalid action specified
- Issue key does not exist
- Transition ID is not valid for the issue's current status
- User lacks permission to transition the issue
- API authentication fails
