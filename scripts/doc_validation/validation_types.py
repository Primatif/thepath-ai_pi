"""
Common types and structures for documentation validation.

This module provides the core data structures used throughout the documentation
validation system. It defines:

1. Severity levels for validation issues
2. Structured validation issue representation
3. Validation result collection and statistics

These types ensure consistent handling of validation results across all validators
and provide a unified way to report and track documentation issues.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional


class Severity(Enum):
    """Severity levels for validation issues.

    Attributes:
        ERROR: Critical issues that must be fixed
        WARNING: Issues that should be addressed but aren't critical
        INFO: Informational messages about potential improvements
    """

    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


@dataclass
class ValidationIssue:
    """Represents a single validation issue found during checks.

    Attributes:
        message: Description of the issue
        file: Path to the file where the issue was found (relative to docs root)
        line: Optional line number where the issue occurs
        severity: Issue severity level
        context: Optional additional context about the issue
        checker: Name of the validator that found this issue
    """

    message: str
    file: str
    line: Optional[int] = None
    severity: Severity = Severity.ERROR
    context: Optional[str] = None
    checker: str = "unknown"

    def to_dict(self) -> dict[str, any]:
        """Convert the issue to a dictionary.

        Returns:
            Dictionary representation of the issue
        """
        return {
            "message": self.message,
            "file": self.file,
            "line": self.line,
            "severity": self.severity.value,
            "context": self.context,
            "checker": self.checker,
        }


@dataclass
class ValidationResult:
    """Collection of validation issues and statistics from a validation run.

    This class serves as both a container for validation issues and a way to
    track statistics about the validation run. It provides helper methods for
    adding issues and computing issue counts by severity.

    Attributes:
        issues: List of validation issues found
        stats: Dictionary of validation statistics (e.g., coverage percentage)
        timestamp: When the validation was performed
    """

    issues: list[ValidationIssue] = field(default_factory=list)
    stats: dict[str, any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)

    def add_issue(
        self,
        message: str,
        file: str,
        severity: Severity = Severity.ERROR,
        line: Optional[int] = None,
        context: Optional[str] = None,
        checker: str = "unknown",
    ) -> None:
        """Add a new validation issue.

        Args:
            message: Description of the issue
            file: Path to the file with the issue
            severity: Issue severity level
            line: Optional line number
            context: Optional additional context
            checker: Name of the validator that found this issue
        """
        self.issues.append(
            ValidationIssue(
                message=message,
                file=file,
                line=line,
                severity=severity,
                context=context,
                checker=checker,
            )
        )

    def add_stat(self, key: str, value: any) -> None:
        """Add a validation statistic.

        Args:
            key: Name of the statistic
            value: Value of the statistic
        """
        self.stats[key] = value

    @property
    def has_errors(self) -> bool:
        """Check if any errors were found during validation."""
        return any(i.severity == Severity.ERROR for i in self.issues)

    @property
    def error_count(self) -> int:
        """Get the total number of errors."""
        return sum(1 for i in self.issues if i.severity == Severity.ERROR)

    @property
    def warning_count(self) -> int:
        """Get the total number of warnings."""
        return sum(1 for i in self.issues if i.severity == Severity.WARNING)

    @property
    def info_count(self) -> int:
        """Get the total number of info messages."""
        return sum(1 for i in self.issues if i.severity == Severity.INFO)

    def merge(self, other: "ValidationResult") -> None:
        """Merge another validation result into this one.

        Args:
            other: Another ValidationResult to merge in
        """
        self.issues.extend(other.issues)
        self.stats.update(other.stats)
