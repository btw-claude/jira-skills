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
cat << 'EOF' | python scripts/transition_issue.py
{
  "action": "get_transitions",
  "issue_key": "PROJ-123"
}
EOF
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
cat << 'EOF' | python scripts/transition_issue.py
{
  "action": "transition",
  "issue_key": "PROJ-123",
  "transition_id": "31"
}
EOF
```

Transition with comment:

```bash
cat << 'EOF' | python scripts/transition_issue.py
{
  "action": "transition",
  "issue_key": "PROJ-123",
  "transition_id": "31",
  "comment": "Completed code review and testing"
}
EOF
```

Transition with multi-line comment:

```bash
cat << 'EOF' | python scripts/transition_issue.py
{
  "action": "transition",
  "issue_key": "PROJ-123",
  "transition_id": "31",
  "comment": "Closing this issue:\n\n- All tests passing\n- Code reviewed\n- Documentation updated"
}
EOF
```

**Note:** Always use heredoc syntax (`cat << 'EOF'`) instead of `echo` to avoid JSON parsing errors with special characters or newlines in comments.

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
