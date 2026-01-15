---
name: jira-operations
description: Manage Jira issues, projects, and workflows. Use when working with Jira tickets, searching issues, creating/updating issues, or transitioning issue status.
---

# Jira Operations Skill

This skill provides comprehensive Jira integration through the `mcp__jira-agent` MCP server tools. It enables issue management, project administration, user lookup, and workflow automation.

## Configuration

Create a `.claude/env` file with your Jira credentials. This skill supports two authentication methods:

### Option 1: Email + API Token (Recommended for Atlassian Cloud)

```
JIRA_BASE_URL=https://your-domain.atlassian.net
JIRA_USER_EMAIL=your-email@example.com
JIRA_API_TOKEN=your-api-token
```

Generate an API token at: https://id.atlassian.com/manage-profile/security/api-tokens

### Option 2: Personal Access Token (PAT) (Recommended for Jira Data Center/Server)

```
JIRA_BASE_URL=https://your-jira-server.com
JIRA_PAT=your-personal-access-token
```

Generate a PAT using one of these methods:

- **Via UI navigation**: Click your Avatar > Profile > Personal Access Tokens
- **Via direct URL**: Go to `{your-jira-url}/secure/ViewProfile.jspa` and select "Personal Access Tokens" from the left menu

For detailed instructions, see the [Atlassian PAT documentation](https://confluence.atlassian.com/enterprise/using-personal-access-tokens-1026032365.html).

### When to Use Each Method

| Authentication Method | Best For | Notes |
|----------------------|----------|-------|
| Email + API Token | Atlassian Cloud (*.atlassian.net) | Standard method for cloud instances |
| Personal Access Token (PAT) | Jira Data Center / Server | Required for self-hosted instances; also works with Cloud |

### Backward Compatibility

Both authentication methods are fully supported. If both `JIRA_PAT` and `JIRA_USER_EMAIL`/`JIRA_API_TOKEN` are configured, PAT authentication takes precedence. Existing configurations using email + API token will continue to work without modification.

The token/PAT requires appropriate Jira permissions for the operations you intend to perform.

## Available Operations

### Issues

Read the specific skill file for detailed usage and examples.

- `skills/issues/create-issue.md` - Create new issues with type, priority, labels, and parent
- `skills/issues/get-issue.md` - Retrieve issue details by key
- `skills/issues/update-issue.md` - Update, assign, or delete existing issues
- `skills/issues/search-issues.md` - Search issues using JQL queries
- `skills/issues/transition-issue.md` - Change issue status through workflow transitions

### Projects

- `skills/projects/manage-project.md` - List, get, create, update, and delete projects

### Comments

- `skills/comments/manage-comments.md` - Add, update, and delete issue comments

### Users

- `skills/users/find-users.md` - Find users by name/email, get assignable users for projects

### Issue Links

- `skills/links/manage-issue-links.md` - Create and delete links between issues

## Quick Reference

| Operation | Tool |
|-----------|------|
| Create issue | `mcp__jira-agent__create_issue` |
| Get issue | `mcp__jira-agent__get_issue` |
| Update issue | `mcp__jira-agent__update_issue` |
| Delete issue | `mcp__jira-agent__delete_issue` |
| Search issues | `mcp__jira-agent__search_issues` |
| Transition issue | `mcp__jira-agent__transition_issue` |
| Get transitions | `mcp__jira-agent__get_transitions` |
| List projects | `mcp__jira-agent__get_projects` |
| Get project | `mcp__jira-agent__get_project` |
| Add comment | `mcp__jira-agent__add_comment` |
| Find users | `mcp__jira-agent__find_users` |
| Create link | `mcp__jira-agent__create_issue_link` |

## Usage Pattern

1. Identify the operation category (issues, projects, comments, users, links)
2. Read the corresponding skill file for detailed parameters and examples
3. Use the appropriate `mcp__jira-agent__*` tool with required parameters

For JQL query syntax and examples, see `skills/issues/search-issues.md`.
