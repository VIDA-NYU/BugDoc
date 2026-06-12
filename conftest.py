"""
Shared pytest configuration and fixtures.

This file is automatically loaded by pytest and provides shared
fixtures and configuration for all test modules.
"""

import os
import tempfile

import pytest


@pytest.fixture(scope="session")
def temp_dir():
    """Provide a temporary directory for tests that persists for the session."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir


@pytest.fixture(scope="function")
def isolated_temp_dir():
    """Provide an isolated temporary directory for a single test."""
    with tempfile.TemporaryDirectory() as tmpdir:
        original_cwd = os.getcwd()
        try:
            os.chdir(tmpdir)
            yield tmpdir
        finally:
            os.chdir(original_cwd)


@pytest.fixture(autouse=True)
def cleanup_test_files():
    """Clean up test artifact files after each test."""
    yield
    # Clean up temporary test files
    for f in ["test.adb", "test.vt"]:
        if os.path.exists(f):
            try:
                os.remove(f)
            except OSError:
                pass
