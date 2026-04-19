#!/usr/bin/env python3
"""
Documentation validation script.

This script provides a unified interface for running all documentation validation
checks and generating comprehensive reports. It:

1. Runs all validation checks (references, health)
2. Generates detailed reports with issues and statistics
3. Saves results to a temporary directory for tracking
4. Provides clear terminal output for immediate feedback

The validation results are saved to .reports/doc_validation_report.json for further
processing or integration with other tools.
"""

import json
import logging
import sys
import uuid
from datetime import datetime
from pathlib import Path

from doc_validation import HealthChecker, RefValidator, Severity, ValidationResult

# Create a logger
logger = logging.getLogger(__name__)


def validate_docs(docs_root: str) -> ValidationResult:
    """Run documentation validation.

    Args:
        docs_root: Root directory containing documentation

    Returns:
        Combined validation result
    """
    print("Running documentation validation...")

    result = ValidationResult()

    # Run health checks
    health = HealthChecker(docs_root)
    result.merge(health.validate())

    # Run reference checks
    refs = RefValidator(docs_root)
    result.merge(refs.validate())

    return result


def save_report(result: ValidationResult, reports_dir: Path) -> Path:
    """Save validation report with unique filename.

    Args:
        result: Validation result to save
        reports_dir: Directory to save report in

    Returns:
        Path to saved report file
    """
    # Generate unique filename using timestamp and UUID
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    unique_id = str(uuid.uuid4())[:8]  # Use first 8 chars of UUID
    filename = f"doc_validation_{timestamp}_{unique_id}.json"

    # Create report data
    report = {
        "id": unique_id,
        "timestamp": datetime.now().isoformat(),
        "summary": {
            "total_errors": len([i for i in result.issues if i.severity == Severity.ERROR]),
            "total_warnings": len([i for i in result.issues if i.severity == Severity.WARNING]),
        },
        "issues": [i.to_dict() for i in result.issues],
        "stats": result.stats,
    }

    # Save report
    report_path = reports_dir / filename
    with open(report_path, "w") as f:
        json.dump(report, f, indent=2)

    # Create symlink to latest report
    latest_link = reports_dir / "latest.json"
    if latest_link.exists():
        latest_link.unlink()
    latest_link.symlink_to(filename)

    return report_path


def main():
    """Main entry point."""
    if len(sys.argv) != 2:
        print("Usage: validate_docs.py <docs_root>")
        sys.exit(1)

    docs_root = sys.argv[1]

    # First, format all documentation
    logger.info("Formatting documentation...")
    import format_docs

    format_docs.main()

    # Then proceed with validation
    logger.info("Validating documentation...")

    print("\nGenerating report...")
    result = validate_docs(docs_root)

    # Create .reports directory in project root
    reports_dir = Path(docs_root).parent / ".reports"
    reports_dir.mkdir(exist_ok=True)

    print("\nSaving results...")
    report_path = save_report(result, reports_dir)

    print("\nDocumentation Validation Report")
    print(f"Generated: {datetime.now().isoformat()}")
    print("\nSummary:")
    print("--------")
    print(f"Total Errors: {len([i for i in result.issues if i.severity == Severity.ERROR])}")
    print(f"Total Warnings: {len([i for i in result.issues if i.severity == Severity.WARNING])}")

    print("\nReferences Validation")
    print("---------------------")
    ref_issues = [i for i in result.issues if i.checker == "references"]
    print(f"Errors: {len([i for i in ref_issues if i.severity == Severity.ERROR])}")
    print(f"Warnings: {len([i for i in ref_issues if i.severity == Severity.WARNING])}")
    print("\nStatistics:")
    for k, v in result.stats.items():
        if k.startswith("total_"):
            print(f"- {k}: {v}")

    print("\nHealth Validation")
    print("-----------------")
    health_issues = [i for i in result.issues if i.checker == "health"]
    print(f"Errors: {len([i for i in health_issues if i.severity == Severity.ERROR])}")
    print(f"Warnings: {len([i for i in health_issues if i.severity == Severity.WARNING])}")
    print("\nStatistics:")
    for k, v in result.stats.items():
        if k == "coverage_percentage":
            print(f"- {k}: {v}")

    if result.issues:
        print("\nIssues:")
        for issue in result.issues:
            print(f"[{issue.severity}] {issue.file}")
            print(f"  {issue.message}")

    print("\nDocumentation validation complete")
    print(f"Report saved to: {report_path}")
    print(f"Latest report symlinked at: {reports_dir}/latest.json")


if __name__ == "__main__":
    main()
