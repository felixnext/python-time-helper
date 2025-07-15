"""Tests for logging improvements - replacing print with proper logging."""

import logging
from datetime import datetime

import pytest

from time_helper.convert import any_to_datetime


def test_timestamp_without_timezone_should_log_warning(caplog: pytest.LogCaptureFixture) -> None:
    """Test that parsing timestamp without timezone logs a warning.

    Currently the code uses print() to warn about missing timezone.
    After fix, it should use proper logging.
    """
    # Clear any existing log records
    caplog.clear()

    # Parse a timestamp without timezone
    timestamp = 1234567890

    with caplog.at_level(logging.WARNING):
        result = any_to_datetime(timestamp)

    # Should parse correctly
    assert result is not None
    assert isinstance(result, datetime)

    # Should have logged a warning
    assert len(caplog.records) > 0
    assert any("timezone" in record.message.lower() for record in caplog.records)
    assert any("UTC" in record.message for record in caplog.records)
    assert any(record.levelname == "WARNING" for record in caplog.records)


def test_timestamp_with_timezone_should_not_log_warning(caplog: pytest.LogCaptureFixture) -> None:
    """Test that parsing timestamp with timezone doesn't log a warning."""
    # Clear any existing log records
    caplog.clear()

    # Parse a datetime string (not timestamp) which doesn't trigger the warning
    datetime_str = "2023-01-15T10:30:00"

    with caplog.at_level(logging.WARNING):
        result = any_to_datetime(datetime_str)

    # Should parse correctly
    assert result is not None
    assert isinstance(result, datetime)

    # Should NOT have logged a warning about timezone
    warning_records = [r for r in caplog.records if r.levelname == "WARNING" and "timezone" in r.message]
    assert len(warning_records) == 0


def test_logging_format_includes_module_name(caplog: pytest.LogCaptureFixture) -> None:
    """Test that log messages include the module name for debugging."""
    caplog.clear()

    timestamp = 1234567890

    with caplog.at_level(logging.WARNING):
        any_to_datetime(timestamp)

    # Check that at least one record has the expected attributes
    assert len(caplog.records) > 0
    record = caplog.records[0]

    # Should have module information
    assert hasattr(record, "name")
    assert "time_helper" in record.name or "convert" in record.name


def test_no_print_statements_remain() -> None:
    """Test that print statements have been replaced with logging.

    This test will fail until we implement the fix.
    """
    # Import the module to check
    # Get the source code
    import inspect

    import time_helper.convert

    source = inspect.getsource(time_helper.convert)

    # Check for print statements (excluding comments and strings)
    lines = source.split("\n")
    for i, line in enumerate(lines):
        # Skip comment lines
        stripped = line.strip()
        if stripped.startswith("#"):
            continue

        # Check for print( but not in strings
        if "print(" in line and not (line.strip().startswith('"') or line.strip().startswith("'")):
            # This is a simple check - could be more sophisticated
            # to handle edge cases like print in strings
            pytest.fail(f"Found print statement at line {i + 1}: {line.strip()}")


def test_logger_configuration() -> None:
    """Test that the logger is properly configured."""
    import time_helper.convert

    # The module should have a logger
    assert hasattr(time_helper.convert, "logger") or hasattr(time_helper.convert, "_logger")

    # Get the logger (try both naming conventions)
    logger = getattr(time_helper.convert, "logger", None) or getattr(time_helper.convert, "_logger", None)

    if logger is not None:
        # Should be a Logger instance
        assert isinstance(logger, logging.Logger)

        # Should have appropriate name
        assert "time_helper" in logger.name or "convert" in logger.name


def test_logging_level_respects_environment(caplog: pytest.LogCaptureFixture) -> None:
    """Test that logging level can be controlled."""
    caplog.clear()

    # Test with different log levels
    timestamp = 1234567890

    # Set to ERROR level - should not see WARNING
    with caplog.at_level(logging.ERROR):
        any_to_datetime(timestamp)
        error_and_above = [r for r in caplog.records if r.levelname in ["ERROR", "CRITICAL"]]
        warnings = [r for r in caplog.records if r.levelname == "WARNING"]
        # We should not capture warnings when level is ERROR
        assert len(warnings) == 0 or len(error_and_above) > len(warnings)

    caplog.clear()

    # Set to DEBUG level - should see everything
    with caplog.at_level(logging.DEBUG):
        any_to_datetime(timestamp)
        # Should have some records
        assert len(caplog.records) > 0


def test_logging_integration_with_standard_logging() -> None:
    """Test that time_helper logging integrates with standard Python logging."""
    # Create a custom handler to capture logs
    captured_logs = []

    class ListHandler(logging.Handler):
        def emit(self, record: logging.LogRecord) -> None:
            captured_logs.append(self.format(record))

    handler = ListHandler()
    handler.setLevel(logging.WARNING)

    # Add handler to root logger temporarily
    root_logger = logging.getLogger()
    root_logger.addHandler(handler)

    try:
        # Trigger the warning
        timestamp = 1234567890
        any_to_datetime(timestamp)

        # Should have captured the warning
        assert len(captured_logs) > 0
        assert any("timezone" in log.lower() for log in captured_logs)

    finally:
        # Clean up
        root_logger.removeHandler(handler)
