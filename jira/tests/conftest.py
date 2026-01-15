"""Pytest configuration for jira tests.

This module contains shared fixtures and configuration for all test modules.

JSKILL-34: Use pytest fixtures for sys.path manipulation
JSKILL-38: Add documentation for module-level path manipulation
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest


# Module-level sys.path manipulation (not a fixture)
# ------------------------------------------------
# This path manipulation is intentionally done at module level rather than
# as a pytest fixture because:
#
# 1. Import resolution happens at test collection time, before fixtures run
# 2. Test modules need to import from the scripts directory (jira_api,
#    validate_auth) at the top of the file using standard import statements
# 3. If this were a fixture, the imports would fail during collection because
#    the fixture hasn't executed yet
# 4. Module-level code in conftest.py runs once when pytest loads the test
#    directory, making it the appropriate place for path setup
#
# Alternative approaches like adding __init__.py files or using relative
# imports were considered but this approach keeps the scripts directory
# structure clean and explicit.
_scripts_path = str(Path(__file__).parent.parent / "scripts")
if _scripts_path not in sys.path:
    sys.path.insert(0, _scripts_path)
