"""Pytest configuration for jira tests.

This module contains shared fixtures and configuration for all test modules.

JSKILL-34: Use pytest fixtures for sys.path manipulation
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest


# Add scripts directory to sys.path for imports
# This runs once at test collection time, ensuring all test modules
# can import from the scripts directory
_scripts_path = str(Path(__file__).parent.parent / "scripts")
if _scripts_path not in sys.path:
    sys.path.insert(0, _scripts_path)
