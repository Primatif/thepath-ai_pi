"""Documentation validation package.

This package provides tools for validating documentation:
1. Reference validation - check links between documents
2. Health checks - verify required sections and metadata
"""

from .health_checker import HealthChecker
from .ref_validator import RefValidator
from .validation_types import Severity, ValidationIssue, ValidationResult

__all__ = [
    "ValidationResult",
    "ValidationIssue",
    "Severity",
    "RefValidator",
    "HealthChecker",
]
