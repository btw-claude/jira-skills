# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [Unreleased]

### Added
- **Personal Access Token (PAT) Authentication** (JSKILL-26)
  - Support for `JIRA_PAT` environment variable for bearer token authentication
  - Alternative to existing Basic Auth (email + API token) method
  - PAT authentication takes precedence when both methods are configured
  - Recommended for Jira Data Center/Server deployments

- PAT support in core API client (`jira_api.py`) - JSKILL-27
- Dual authentication validation in `validate_auth.py` - JSKILL-28
- Updated documentation in `SKILL.md` with both auth options - JSKILL-29
- Comprehensive test suite for PAT authentication (26 tests) - JSKILL-30

### Changed
- Error messages now mention both authentication options
- Configuration validation supports either PAT or Basic Auth

### Backward Compatibility
- Existing Basic Auth configurations continue to work without modification
- No changes required for users currently using email + API token
