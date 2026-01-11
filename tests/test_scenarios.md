# Jira Skills Test Scenarios

This document contains comprehensive test scenarios for all Jira MCP server skills.
Each scenario includes input, expected behavior, and verification steps.

---

## 1. Configuration Tests

### 1.1 Missing .claude/env File

**Test Name:** `config_missing_env_file`

**Setup:** Remove or rename `.claude/env` file

**Input:** Any MCP tool call, e.g.:
```json
{
  "tool": "mcp__jira-agent__get_projects",
  "parameters": {}
}
```

**Expected Behavior:** Failure with clear error message

**Verification:**
- Error message indicates missing configuration file
- Error suggests creating `.claude/env` with required variables
- No partial operations executed

---

### 1.2 Missing JIRA_BASE_URL

**Test Name:** `config_missing_base_url`

**Setup:** `.claude/env` contains only `JIRA_PAT=xxx`

**Input:**
```json
{
  "tool": "mcp__jira-agent__get_projects",
  "parameters": {}
}
```

**Expected Behavior:** Failure with clear error message

**Verification:**
- Error message specifically mentions missing `JIRA_BASE_URL`
- Error provides example format: `https://your-domain.atlassian.net`

---

### 1.3 Missing JIRA_PAT

**Test Name:** `config_missing_pat`

**Setup:** `.claude/env` contains only `JIRA_BASE_URL=https://example.atlassian.net`

**Input:**
```json
{
  "tool": "mcp__jira-agent__get_projects",
  "parameters": {}
}
```

**Expected Behavior:** Failure with clear error message

**Verification:**
- Error message specifically mentions missing `JIRA_PAT`
- Error explains how to generate a Personal Access Token

---

### 1.4 Invalid JIRA_PAT (Authentication Failure)

**Test Name:** `config_invalid_pat`

**Setup:** `.claude/env` contains valid URL but invalid PAT

**Input:**
```json
{
  "tool": "mcp__jira-agent__get_projects",
  "parameters": {}
}
```

**Expected Behavior:** Failure with 401 Unauthorized

**Verification:**
- Error message indicates authentication failure
- Suggests verifying PAT is valid and not expired

---

### 1.5 Valid Configuration

**Test Name:** `config_valid`

**Setup:** `.claude/env` contains valid `JIRA_BASE_URL` and `JIRA_PAT`

**Input:**
```json
{
  "tool": "mcp__jira-agent__get_projects",
  "parameters": {}
}
```

**Expected Behavior:** Success - returns list of projects

**Verification:**
- Response contains project data
- No authentication errors
- Connection established successfully

---

## 2. Issue Operations Tests

### 2.1 Create Issue - Required Fields Only

**Test Name:** `issue_create_minimal`

**Input:**
```json
{
  "tool": "mcp__jira-agent__create_issue",
  "parameters": {
    "project_key": "TEST",
    "summary": "Test issue with required fields only",
    "issue_type": "Task"
  }
}
```

**Expected Behavior:** Success - issue created

**Verification:**
- Response contains new issue key (e.g., `TEST-123`)
- Issue visible in Jira with correct summary
- Issue type is "Task"
- Default values applied for optional fields

---

### 2.2 Create Issue - All Optional Fields

**Test Name:** `issue_create_full`

**Input:**
```json
{
  "tool": "mcp__jira-agent__create_issue",
  "parameters": {
    "project_key": "TEST",
    "summary": "Test issue with all fields",
    "issue_type": "Bug",
    "description": "Detailed description of the issue.\n\nWith multiple paragraphs.",
    "priority": "High",
    "labels": "test,automated,verification",
    "assignee_id": "557058:f3a1b2c3-d4e5-6789-abcd-ef0123456789",
    "parent_key": "TEST-100",
    "links": "blocks:TEST-50,relates to:TEST-51"
  }
}
```

**Expected Behavior:** Success - issue created with all fields populated

**Verification:**
- Issue has correct summary and description
- Priority is "High"
- Labels array contains: test, automated, verification
- Assignee matches provided account ID
- Parent relationship established (for subtasks)
- Issue links created as specified

---

### 2.3 Create Issue - Invalid Project Key

**Test Name:** `issue_create_invalid_project`

**Input:**
```json
{
  "tool": "mcp__jira-agent__create_issue",
  "parameters": {
    "project_key": "NONEXISTENT",
    "summary": "This should fail",
    "issue_type": "Task"
  }
}
```

**Expected Behavior:** Failure with project not found error

**Verification:**
- Error message indicates project does not exist
- No issue created

---

### 2.4 Create Issue - Invalid Issue Type

**Test Name:** `issue_create_invalid_type`

**Input:**
```json
{
  "tool": "mcp__jira-agent__create_issue",
  "parameters": {
    "project_key": "TEST",
    "summary": "This should fail",
    "issue_type": "InvalidType"
  }
}
```

**Expected Behavior:** Failure with invalid issue type error

**Verification:**
- Error message indicates issue type not valid for project
- Suggests valid issue types if possible

---

### 2.5 Get Issue by Key

**Test Name:** `issue_get_by_key`

**Input:**
```json
{
  "tool": "mcp__jira-agent__get_issue",
  "parameters": {
    "issue_key": "TEST-123"
  }
}
```

**Expected Behavior:** Success - returns issue details

**Verification:**
- Response contains issue key, summary, description
- Status, priority, assignee included
- Created/updated timestamps present

---

### 2.6 Get Issue - With Field Selection

**Test Name:** `issue_get_with_fields`

**Input:**
```json
{
  "tool": "mcp__jira-agent__get_issue",
  "parameters": {
    "issue_key": "TEST-123",
    "fields": "summary,status,assignee"
  }
}
```

**Expected Behavior:** Success - returns only specified fields

**Verification:**
- Response contains only summary, status, assignee
- Other fields not included (reduced payload)

---

### 2.7 Get Issue - With Expand

**Test Name:** `issue_get_with_expand`

**Input:**
```json
{
  "tool": "mcp__jira-agent__get_issue",
  "parameters": {
    "issue_key": "TEST-123",
    "expand": "changelog,transitions"
  }
}
```

**Expected Behavior:** Success - returns issue with expanded data

**Verification:**
- Changelog history included
- Available transitions included

---

### 2.8 Get Issue - Non-existent Key

**Test Name:** `issue_get_not_found`

**Input:**
```json
{
  "tool": "mcp__jira-agent__get_issue",
  "parameters": {
    "issue_key": "TEST-999999"
  }
}
```

**Expected Behavior:** Failure with issue not found error

**Verification:**
- Error message indicates issue does not exist
- 404 status code returned

---

### 2.9 Update Issue - Single Field

**Test Name:** `issue_update_single_field`

**Input:**
```json
{
  "tool": "mcp__jira-agent__update_issue",
  "parameters": {
    "issue_key": "TEST-123",
    "summary": "Updated summary text"
  }
}
```

**Expected Behavior:** Success - field updated

**Verification:**
- Issue summary changed to new value
- Other fields unchanged
- Updated timestamp modified

---

### 2.10 Update Issue - Multiple Fields

**Test Name:** `issue_update_multiple_fields`

**Input:**
```json
{
  "tool": "mcp__jira-agent__update_issue",
  "parameters": {
    "issue_key": "TEST-123",
    "summary": "New summary",
    "description": "New description",
    "priority": "Low",
    "labels": "updated,modified"
  }
}
```

**Expected Behavior:** Success - all fields updated

**Verification:**
- All specified fields changed
- Labels replaced with new set

---

### 2.11 Update Issue - Add Links

**Test Name:** `issue_update_add_links`

**Input:**
```json
{
  "tool": "mcp__jira-agent__update_issue",
  "parameters": {
    "issue_key": "TEST-123",
    "add_links": "blocks:TEST-200,relates to:TEST-201"
  }
}
```

**Expected Behavior:** Success - links added

**Verification:**
- New links visible on issue
- Existing links preserved
- Link types correct

---

### 2.12 Update Issue - Remove Links

**Test Name:** `issue_update_remove_links`

**Input:**
```json
{
  "tool": "mcp__jira-agent__update_issue",
  "parameters": {
    "issue_key": "TEST-123",
    "remove_link_ids": "12345,12346"
  }
}
```

**Expected Behavior:** Success - links removed

**Verification:**
- Specified links no longer exist
- Other links preserved

---

### 2.13 Assign Issue

**Test Name:** `issue_assign`

**Input:**
```json
{
  "tool": "mcp__jira-agent__assign_issue",
  "parameters": {
    "issue_key": "TEST-123",
    "account_id": "557058:f3a1b2c3-d4e5-6789-abcd-ef0123456789"
  }
}
```

**Expected Behavior:** Success - issue assigned

**Verification:**
- Assignee field shows correct user
- Assignment notification triggered (if configured)

---

### 2.14 Unassign Issue

**Test Name:** `issue_unassign`

**Input:**
```json
{
  "tool": "mcp__jira-agent__assign_issue",
  "parameters": {
    "issue_key": "TEST-123"
  }
}
```

**Expected Behavior:** Success - issue unassigned

**Verification:**
- Assignee field is empty/null
- Issue shows as unassigned

---

### 2.15 Delete Issue

**Test Name:** `issue_delete`

**Input:**
```json
{
  "tool": "mcp__jira-agent__delete_issue",
  "parameters": {
    "issue_key": "TEST-123"
  }
}
```

**Expected Behavior:** Success - issue deleted

**Verification:**
- Issue no longer accessible
- Get issue returns 404
- Search does not include deleted issue

---

### 2.16 Delete Issue - With Subtasks

**Test Name:** `issue_delete_with_subtasks`

**Input:**
```json
{
  "tool": "mcp__jira-agent__delete_issue",
  "parameters": {
    "issue_key": "TEST-123",
    "delete_subtasks": true
  }
}
```

**Expected Behavior:** Success - issue and subtasks deleted

**Verification:**
- Parent issue deleted
- All subtasks also deleted
- No orphaned subtasks remain

---

### 2.17 Delete Issue - With Subtasks (delete_subtasks=false)

**Test Name:** `issue_delete_subtasks_blocked`

**Input:**
```json
{
  "tool": "mcp__jira-agent__delete_issue",
  "parameters": {
    "issue_key": "TEST-123",
    "delete_subtasks": false
  }
}
```

**Expected Behavior:** Failure if issue has subtasks

**Verification:**
- Error indicates issue has subtasks
- Suggests using delete_subtasks=true
- Issue not deleted

---

### 2.18 Search Issues - Simple JQL

**Test Name:** `issue_search_simple`

**Input:**
```json
{
  "tool": "mcp__jira-agent__search_issues",
  "parameters": {
    "jql": "project = TEST AND status = Open"
  }
}
```

**Expected Behavior:** Success - returns matching issues

**Verification:**
- All returned issues are in TEST project
- All returned issues have Open status
- Total count provided

---

### 2.19 Search Issues - Complex JQL

**Test Name:** `issue_search_complex`

**Input:**
```json
{
  "tool": "mcp__jira-agent__search_issues",
  "parameters": {
    "jql": "project = TEST AND assignee = currentUser() AND status NOT IN (Done, Closed) AND created >= -30d ORDER BY priority DESC",
    "max_results": 50,
    "fields": "summary,status,priority,created"
  }
}
```

**Expected Behavior:** Success - returns filtered, sorted results

**Verification:**
- Only current user's issues returned
- Status excludes Done and Closed
- Created within last 30 days
- Sorted by priority descending
- Max 50 results

---

### 2.20 Search Issues - Text Search

**Test Name:** `issue_search_text`

**Input:**
```json
{
  "tool": "mcp__jira-agent__search_issues",
  "parameters": {
    "jql": "project = TEST AND (summary ~ \"login\" OR description ~ \"authentication\")"
  }
}
```

**Expected Behavior:** Success - returns text-matching issues

**Verification:**
- Issues contain "login" in summary OR "authentication" in description

---

### 2.21 Search Issues - Invalid JQL

**Test Name:** `issue_search_invalid_jql`

**Input:**
```json
{
  "tool": "mcp__jira-agent__search_issues",
  "parameters": {
    "jql": "project = TEST AND invalid_field = 'value'"
  }
}
```

**Expected Behavior:** Failure with JQL parse error

**Verification:**
- Error message indicates JQL syntax error
- Identifies problematic field or clause

---

### 2.22 Search Issues - Pagination

**Test Name:** `issue_search_pagination`

**Input:**
```json
{
  "tool": "mcp__jira-agent__search_issues",
  "parameters": {
    "jql": "project = TEST",
    "start_at": 50,
    "max_results": 25
  }
}
```

**Expected Behavior:** Success - returns paginated results

**Verification:**
- Results start from offset 50
- Maximum 25 results returned
- Total count reflects all matching issues

---

### 2.23 Get Transitions

**Test Name:** `issue_get_transitions`

**Input:**
```json
{
  "tool": "mcp__jira-agent__get_transitions",
  "parameters": {
    "issue_key": "TEST-123"
  }
}
```

**Expected Behavior:** Success - returns available transitions

**Verification:**
- List of valid transitions for current status
- Each transition has ID and name
- Only permitted transitions included

---

### 2.24 Transition Issue

**Test Name:** `issue_transition`

**Input:**
```json
{
  "tool": "mcp__jira-agent__transition_issue",
  "parameters": {
    "issue_key": "TEST-123",
    "transition_id": "21"
  }
}
```

**Expected Behavior:** Success - issue transitioned

**Verification:**
- Issue status changed
- Transition logged in history
- Workflow rules executed

---

### 2.25 Transition Issue - With Comment

**Test Name:** `issue_transition_with_comment`

**Input:**
```json
{
  "tool": "mcp__jira-agent__transition_issue",
  "parameters": {
    "issue_key": "TEST-123",
    "transition_id": "31",
    "comment": "Closing this issue as completed. All acceptance criteria met."
  }
}
```

**Expected Behavior:** Success - issue transitioned with comment

**Verification:**
- Issue status changed
- Comment added to issue
- Comment visible in activity stream

---

### 2.26 Transition Issue - Invalid Transition

**Test Name:** `issue_transition_invalid`

**Input:**
```json
{
  "tool": "mcp__jira-agent__transition_issue",
  "parameters": {
    "issue_key": "TEST-123",
    "transition_id": "9999"
  }
}
```

**Expected Behavior:** Failure with invalid transition error

**Verification:**
- Error indicates transition not available
- Issue status unchanged

---

## 3. Project Operations Tests

### 3.1 List Projects

**Test Name:** `project_list`

**Input:**
```json
{
  "tool": "mcp__jira-agent__get_projects",
  "parameters": {}
}
```

**Expected Behavior:** Success - returns project list

**Verification:**
- List of projects user has access to
- Each project has key and name
- Pagination info included

---

### 3.2 List Projects - With Pagination

**Test Name:** `project_list_paginated`

**Input:**
```json
{
  "tool": "mcp__jira-agent__get_projects",
  "parameters": {
    "start_at": 10,
    "max_results": 5
  }
}
```

**Expected Behavior:** Success - returns paginated results

**Verification:**
- Results start from offset 10
- Maximum 5 projects returned

---

### 3.3 List Projects - With Expand

**Test Name:** `project_list_expanded`

**Input:**
```json
{
  "tool": "mcp__jira-agent__get_projects",
  "parameters": {
    "expand": "description,lead"
  }
}
```

**Expected Behavior:** Success - returns expanded project data

**Verification:**
- Description included for each project
- Lead user information included

---

### 3.4 Get Project by Key

**Test Name:** `project_get`

**Input:**
```json
{
  "tool": "mcp__jira-agent__get_project",
  "parameters": {
    "project_key": "TEST"
  }
}
```

**Expected Behavior:** Success - returns project details

**Verification:**
- Project key, name, description returned
- Lead information included
- Issue types available for project

---

### 3.5 Get Project - With Expand

**Test Name:** `project_get_expanded`

**Input:**
```json
{
  "tool": "mcp__jira-agent__get_project",
  "parameters": {
    "project_key": "TEST",
    "expand": "issueTypes,lead,description"
  }
}
```

**Expected Behavior:** Success - returns expanded project data

**Verification:**
- Issue types array populated
- Lead user details included
- Full description text returned

---

### 3.6 Get Project - Not Found

**Test Name:** `project_get_not_found`

**Input:**
```json
{
  "tool": "mcp__jira-agent__get_project",
  "parameters": {
    "project_key": "NONEXISTENT"
  }
}
```

**Expected Behavior:** Failure with project not found error

**Verification:**
- 404 error returned
- Clear error message

---

### 3.7 Create Project (Admin Required)

**Test Name:** `project_create`

**Input:**
```json
{
  "tool": "mcp__jira-agent__create_project",
  "parameters": {
    "key": "NEWPROJ",
    "name": "New Test Project",
    "project_type_key": "software",
    "project_template_key": "com.pyxis.greenhopper.jira:gh-simplified-kanban-classic",
    "lead_account_id": "557058:f3a1b2c3-d4e5-6789-abcd-ef0123456789"
  }
}
```

**Expected Behavior:** Success (if admin) or 403 Forbidden

**Verification:**
- Project created with specified key and name
- Kanban board initialized
- Lead assigned correctly

---

### 3.8 Create Project - With Optional Fields

**Test Name:** `project_create_full`

**Input:**
```json
{
  "tool": "mcp__jira-agent__create_project",
  "parameters": {
    "key": "FULLPROJ",
    "name": "Full Featured Project",
    "project_type_key": "software",
    "project_template_key": "com.pyxis.greenhopper.jira:gh-simplified-scrum-classic",
    "lead_account_id": "557058:f3a1b2c3-d4e5-6789-abcd-ef0123456789",
    "description": "A fully configured project for testing",
    "url": "https://example.com/project",
    "assignee_type": "PROJECT_LEAD"
  }
}
```

**Expected Behavior:** Success - project created with all options

**Verification:**
- Description populated
- URL set
- Default assignee type configured

---

### 3.9 Create Project - Duplicate Key

**Test Name:** `project_create_duplicate`

**Input:**
```json
{
  "tool": "mcp__jira-agent__create_project",
  "parameters": {
    "key": "TEST",
    "name": "Duplicate Project",
    "project_type_key": "software",
    "project_template_key": "com.pyxis.greenhopper.jira:gh-simplified-kanban-classic",
    "lead_account_id": "557058:f3a1b2c3-d4e5-6789-abcd-ef0123456789"
  }
}
```

**Expected Behavior:** Failure - duplicate key error

**Verification:**
- Error indicates project key already exists
- No project created

---

### 3.10 Update Project

**Test Name:** `project_update`

**Input:**
```json
{
  "tool": "mcp__jira-agent__update_project",
  "parameters": {
    "project_key": "TEST",
    "name": "Updated Project Name",
    "description": "Updated description"
  }
}
```

**Expected Behavior:** Success - project updated

**Verification:**
- Name changed
- Description changed
- Key unchanged

---

### 3.11 Update Project - Change Lead

**Test Name:** `project_update_lead`

**Input:**
```json
{
  "tool": "mcp__jira-agent__update_project",
  "parameters": {
    "project_key": "TEST",
    "lead_account_id": "557058:new-lead-account-id"
  }
}
```

**Expected Behavior:** Success - lead changed

**Verification:**
- New lead assigned
- Previous lead removed

---

### 3.12 Delete Project

**Test Name:** `project_delete`

**Input:**
```json
{
  "tool": "mcp__jira-agent__delete_project",
  "parameters": {
    "project_key": "TESTDEL"
  }
}
```

**Expected Behavior:** Success - project moved to recycle bin

**Verification:**
- Project no longer in active list
- Can be restored from recycle bin (enable_undo=true default)

---

### 3.13 Delete Project - Permanent

**Test Name:** `project_delete_permanent`

**Input:**
```json
{
  "tool": "mcp__jira-agent__delete_project",
  "parameters": {
    "project_key": "TESTDEL",
    "enable_undo": false
  }
}
```

**Expected Behavior:** Success - project permanently deleted

**Verification:**
- Project cannot be restored
- All issues permanently removed

---

## 4. Comment Operations Tests

### 4.1 List Comments on Issue

**Test Name:** `comment_list`

**Input:**
```json
{
  "tool": "mcp__jira-agent__get_comments",
  "parameters": {
    "issue_key": "TEST-123"
  }
}
```

**Expected Behavior:** Success - returns comments

**Verification:**
- List of comments returned
- Each has ID, body, author, created date
- Ordered by creation date (default)

---

### 4.2 List Comments - With Ordering

**Test Name:** `comment_list_ordered`

**Input:**
```json
{
  "tool": "mcp__jira-agent__get_comments",
  "parameters": {
    "issue_key": "TEST-123",
    "order_by": "-created"
  }
}
```

**Expected Behavior:** Success - comments in reverse order

**Verification:**
- Newest comments first
- Order consistent with request

---

### 4.3 List Comments - Paginated

**Test Name:** `comment_list_paginated`

**Input:**
```json
{
  "tool": "mcp__jira-agent__get_comments",
  "parameters": {
    "issue_key": "TEST-123",
    "start_at": 5,
    "max_results": 10
  }
}
```

**Expected Behavior:** Success - paginated results

**Verification:**
- Starts from offset 5
- Maximum 10 comments returned
- Total count provided

---

### 4.4 Add Comment

**Test Name:** `comment_add`

**Input:**
```json
{
  "tool": "mcp__jira-agent__add_comment",
  "parameters": {
    "issue_key": "TEST-123",
    "body": "This is a new comment added via API.\n\nIt supports multiple paragraphs."
  }
}
```

**Expected Behavior:** Success - comment added

**Verification:**
- Comment visible on issue
- Author is current user
- Created timestamp set
- Body preserved with formatting

---

### 4.5 Add Comment - Empty Body

**Test Name:** `comment_add_empty`

**Input:**
```json
{
  "tool": "mcp__jira-agent__add_comment",
  "parameters": {
    "issue_key": "TEST-123",
    "body": ""
  }
}
```

**Expected Behavior:** Failure - empty body not allowed

**Verification:**
- Error indicates body is required
- No comment created

---

### 4.6 Update Comment

**Test Name:** `comment_update`

**Input:**
```json
{
  "tool": "mcp__jira-agent__update_comment",
  "parameters": {
    "issue_key": "TEST-123",
    "comment_id": "10001",
    "body": "Updated comment text with new information."
  }
}
```

**Expected Behavior:** Success - comment updated

**Verification:**
- Comment body changed
- Updated timestamp modified
- Author unchanged

---

### 4.7 Update Comment - Not Found

**Test Name:** `comment_update_not_found`

**Input:**
```json
{
  "tool": "mcp__jira-agent__update_comment",
  "parameters": {
    "issue_key": "TEST-123",
    "comment_id": "99999999",
    "body": "This should fail"
  }
}
```

**Expected Behavior:** Failure - comment not found

**Verification:**
- 404 error returned
- Clear error message

---

### 4.8 Delete Comment

**Test Name:** `comment_delete`

**Input:**
```json
{
  "tool": "mcp__jira-agent__delete_comment",
  "parameters": {
    "issue_key": "TEST-123",
    "comment_id": "10001"
  }
}
```

**Expected Behavior:** Success - comment deleted

**Verification:**
- Comment no longer visible
- List comments excludes deleted comment

---

### 4.9 Delete Comment - Permission Denied

**Test Name:** `comment_delete_forbidden`

**Input:**
```json
{
  "tool": "mcp__jira-agent__delete_comment",
  "parameters": {
    "issue_key": "TEST-123",
    "comment_id": "10002"
  }
}
```

**Expected Behavior:** Failure if user lacks permission

**Verification:**
- 403 error if not author/admin
- Comment unchanged

---

## 5. User Operations Tests

### 5.1 Get User by Account ID

**Test Name:** `user_get`

**Input:**
```json
{
  "tool": "mcp__jira-agent__get_user",
  "parameters": {
    "account_id": "557058:f3a1b2c3-d4e5-6789-abcd-ef0123456789"
  }
}
```

**Expected Behavior:** Success - returns user details

**Verification:**
- Display name returned
- Email address (if visible)
- Avatar URL
- Account status (active/inactive)

---

### 5.2 Get User - Not Found

**Test Name:** `user_get_not_found`

**Input:**
```json
{
  "tool": "mcp__jira-agent__get_user",
  "parameters": {
    "account_id": "invalid-account-id"
  }
}
```

**Expected Behavior:** Failure - user not found

**Verification:**
- 404 error returned
- Clear error message

---

### 5.3 Search Users

**Test Name:** `user_search`

**Input:**
```json
{
  "tool": "mcp__jira-agent__find_users",
  "parameters": {
    "query": "john"
  }
}
```

**Expected Behavior:** Success - returns matching users

**Verification:**
- Users with "john" in name or email returned
- Account IDs included for each user
- Display names shown

---

### 5.4 Search Users - No Results

**Test Name:** `user_search_empty`

**Input:**
```json
{
  "tool": "mcp__jira-agent__find_users",
  "parameters": {
    "query": "xyznonexistentuserxyz"
  }
}
```

**Expected Behavior:** Success - empty results

**Verification:**
- Empty array returned
- No error thrown

---

### 5.5 Search Users - Paginated

**Test Name:** `user_search_paginated`

**Input:**
```json
{
  "tool": "mcp__jira-agent__find_users",
  "parameters": {
    "query": "a",
    "start_at": 10,
    "max_results": 5
  }
}
```

**Expected Behavior:** Success - paginated results

**Verification:**
- Results start from offset 10
- Maximum 5 users returned

---

### 5.6 Get Assignable Users - By Project

**Test Name:** `user_assignable_project`

**Input:**
```json
{
  "tool": "mcp__jira-agent__get_assignable_users",
  "parameters": {
    "project_key": "TEST"
  }
}
```

**Expected Behavior:** Success - returns assignable users

**Verification:**
- Only users with assign permission returned
- Account IDs included

---

### 5.7 Get Assignable Users - By Issue

**Test Name:** `user_assignable_issue`

**Input:**
```json
{
  "tool": "mcp__jira-agent__get_assignable_users",
  "parameters": {
    "issue_key": "TEST-123"
  }
}
```

**Expected Behavior:** Success - returns assignable users for issue

**Verification:**
- Users who can be assigned to specific issue
- May differ from project-level based on permissions

---

### 5.8 Get Assignable Users - With Query Filter

**Test Name:** `user_assignable_filtered`

**Input:**
```json
{
  "tool": "mcp__jira-agent__get_assignable_users",
  "parameters": {
    "project_key": "TEST",
    "query": "dev"
  }
}
```

**Expected Behavior:** Success - filtered assignable users

**Verification:**
- Only users matching "dev" query returned
- Still filtered by assignment permission

---

## 6. Issue Link Operations Tests

### 6.1 Get Link Types

**Test Name:** `link_types_get`

**Input:**
```json
{
  "tool": "mcp__jira-agent__get_issue_link_types",
  "parameters": {}
}
```

**Expected Behavior:** Success - returns available link types

**Verification:**
- List of link types returned
- Each has ID, name, inward/outward descriptions
- Common types: blocks, is blocked by, relates to, duplicates

---

### 6.2 Create Link Between Issues

**Test Name:** `link_create`

**Input:**
```json
{
  "tool": "mcp__jira-agent__create_issue_link",
  "parameters": {
    "type": "{\"name\": \"Blocks\"}",
    "properties": "{\"inwardIssue\": {\"key\": \"TEST-100\"}, \"outwardIssue\": {\"key\": \"TEST-101\"}}",
    "required": "[\"type\", \"inwardIssue\", \"outwardIssue\"]"
  }
}
```

**Expected Behavior:** Success - link created

**Verification:**
- Link visible on both issues
- Direction correct (TEST-100 blocks TEST-101)
- Link ID returned

---

### 6.3 Create Link - Same Issue

**Test Name:** `link_create_self`

**Input:**
```json
{
  "tool": "mcp__jira-agent__create_issue_link",
  "parameters": {
    "type": "{\"name\": \"Relates\"}",
    "properties": "{\"inwardIssue\": {\"key\": \"TEST-100\"}, \"outwardIssue\": {\"key\": \"TEST-100\"}}",
    "required": "[\"type\", \"inwardIssue\", \"outwardIssue\"]"
  }
}
```

**Expected Behavior:** Failure - cannot link to self

**Verification:**
- Error indicates same issue
- No link created

---

### 6.4 Create Link - Invalid Type

**Test Name:** `link_create_invalid_type`

**Input:**
```json
{
  "tool": "mcp__jira-agent__create_issue_link",
  "parameters": {
    "type": "{\"name\": \"InvalidLinkType\"}",
    "properties": "{\"inwardIssue\": {\"key\": \"TEST-100\"}, \"outwardIssue\": {\"key\": \"TEST-101\"}}",
    "required": "[\"type\", \"inwardIssue\", \"outwardIssue\"]"
  }
}
```

**Expected Behavior:** Failure - invalid link type

**Verification:**
- Error indicates link type not found
- Suggests valid types

---

### 6.5 Get Link Details

**Test Name:** `link_get`

**Input:**
```json
{
  "tool": "mcp__jira-agent__get_issue_link",
  "parameters": {
    "link_id": "12345"
  }
}
```

**Expected Behavior:** Success - returns link details

**Verification:**
- Link type information
- Inward and outward issue keys
- Link ID confirmed

---

### 6.6 Get Link - Not Found

**Test Name:** `link_get_not_found`

**Input:**
```json
{
  "tool": "mcp__jira-agent__get_issue_link",
  "parameters": {
    "link_id": "99999999"
  }
}
```

**Expected Behavior:** Failure - link not found

**Verification:**
- 404 error returned
- Clear error message

---

### 6.7 Delete Link

**Test Name:** `link_delete`

**Input:**
```json
{
  "tool": "mcp__jira-agent__delete_issue_link",
  "parameters": {
    "link_id": "12345"
  }
}
```

**Expected Behavior:** Success - link deleted

**Verification:**
- Link no longer exists
- Removed from both issues
- Get link returns 404

---

### 6.8 Delete Link - Not Found

**Test Name:** `link_delete_not_found`

**Input:**
```json
{
  "tool": "mcp__jira-agent__delete_issue_link",
  "parameters": {
    "link_id": "99999999"
  }
}
```

**Expected Behavior:** Failure - link not found

**Verification:**
- 404 error returned
- No action taken

---

## 7. Error Handling Tests

### 7.1 Network Timeout

**Test Name:** `error_network_timeout`

**Setup:** Simulate network delay or use unreachable host

**Input:** Any API call

**Expected Behavior:** Failure with timeout error

**Verification:**
- Clear timeout message
- Suggests checking network connectivity

---

### 7.2 Rate Limiting

**Test Name:** `error_rate_limit`

**Setup:** Make many rapid API calls

**Input:** Multiple rapid API calls

**Expected Behavior:** 429 Too Many Requests

**Verification:**
- Error indicates rate limiting
- Retry-After header respected if provided

---

### 7.3 Invalid JSON Response

**Test Name:** `error_invalid_json`

**Setup:** Mock server returning invalid JSON

**Input:** Any API call

**Expected Behavior:** Failure with parse error

**Verification:**
- Clear error about response format
- Original response logged for debugging

---

### 7.4 Permission Denied

**Test Name:** `error_permission_denied`

**Input:** Operation on restricted resource

**Expected Behavior:** 403 Forbidden

**Verification:**
- Clear permission error message
- Indicates which permission is required

---

## Appendix: Test Data Setup

### Required Test Data

Before running tests, ensure the following exists in your Jira instance:

1. **Projects**
   - `TEST` - Active project with issues
   - `TESTDEL` - Project for deletion tests (create fresh each time)

2. **Issues**
   - `TEST-123` - Standard issue for read/update tests
   - Issues with subtasks for deletion tests
   - Issues with comments for comment tests
   - Issues with links for link tests

3. **Users**
   - At least 2 users with project access
   - One user with admin permissions

4. **Link Types**
   - Default Jira link types should be available

### Cleanup Procedures

After running tests:

1. Delete any test-created issues (prefix: `[TEST]`)
2. Restore deleted projects from recycle bin
3. Remove test comments
4. Delete test links
