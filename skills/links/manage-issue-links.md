# Manage Issue Links

Create, retrieve, and delete links between Jira issues.

## Script

```bash
python scripts/manage_issue_links.py
```

## Operations

### Get Link Types

Retrieve all available issue link types in the Jira instance.

#### Input

| Parameter | Required | Description |
|-----------|----------|-------------|
| `action` | Yes | Set to `"get_types"` |

#### Example

```bash
echo '{
  "action": "get_types"
}' | python scripts/manage_issue_links.py
```

#### Output

```json
{
  "issueLinkTypes": [
    {"id": "10000", "name": "Blocks", "inward": "is blocked by", "outward": "blocks"},
    {"id": "10001", "name": "Cloners", "inward": "is cloned by", "outward": "clones"},
    {"id": "10002", "name": "Relates", "inward": "relates to", "outward": "relates to"}
  ]
}
```

### Create Link

Create a link between two issues.

#### Input

| Parameter | Required | Description |
|-----------|----------|-------------|
| `action` | Yes | Set to `"create"` |
| `link_type` | Yes | Link type name (e.g., "Blocks", "Cloners", "Relates") |
| `inward_issue_key` | Yes | Key of the inward issue (e.g., "PROJ-1") |
| `outward_issue_key` | Yes | Key of the outward issue (e.g., "PROJ-2") |

Link direction: The outward issue performs the action on the inward issue. For example, with "Blocks" link type: outward_issue "blocks" inward_issue.

#### Example

```bash
echo '{
  "action": "create",
  "link_type": "Blocks",
  "inward_issue_key": "PROJ-1",
  "outward_issue_key": "PROJ-2"
}' | python scripts/manage_issue_links.py
```

This creates a link where PROJ-2 blocks PROJ-1.

#### Output

```json
{
  "success": true
}
```

### Get Link

Retrieve details of a specific issue link by its ID.

#### Input

| Parameter | Required | Description |
|-----------|----------|-------------|
| `action` | Yes | Set to `"get"` |
| `link_id` | Yes | The issue link ID |

#### Example

```bash
echo '{
  "action": "get",
  "link_id": "10001"
}' | python scripts/manage_issue_links.py
```

#### Output

```json
{
  "id": "10001",
  "type": {
    "id": "10000",
    "name": "Blocks",
    "inward": "is blocked by",
    "outward": "blocks"
  },
  "inwardIssue": {
    "key": "PROJ-1",
    "fields": {"summary": "First issue"}
  },
  "outwardIssue": {
    "key": "PROJ-2",
    "fields": {"summary": "Second issue"}
  }
}
```

### Delete Link

Delete an issue link.

#### Input

| Parameter | Required | Description |
|-----------|----------|-------------|
| `action` | Yes | Set to `"delete"` |
| `link_id` | Yes | The issue link ID to delete |

#### Example

```bash
echo '{
  "action": "delete",
  "link_id": "10001"
}' | python scripts/manage_issue_links.py
```

#### Output

```json
{
  "success": true,
  "message": "Link 10001 deleted successfully"
}
```

## Errors

The script outputs error details to stderr and exits with non-zero status if:
- Required parameters are missing
- Invalid action specified
- Link type does not exist
- Issue keys do not exist
- Link ID does not exist
- User lacks permission to create/delete links
- API authentication fails
