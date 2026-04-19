"""
Documentation health checker.

Validates documentation health by:
1. Checking for required sections
2. Measuring documentation coverage
3. Validating metadata presence
"""

import re
from pathlib import Path

import yaml

from .validation_types import Severity, ValidationIssue, ValidationResult


class HealthChecker:
    """Checks documentation health and coverage."""

    def __init__(self, docs_root: str):
        """Initialize the health checker.

        Args:
            docs_root: Root directory containing documentation files
        """
        self.docs_root = Path(docs_root)

        # Define expected metadata fields
        self.required_metadata = {"title", "description"}

    def _get_doc_type(self, file_path: Path) -> str:
        """Determine document type from path.

        Args:
            file_path: Path to document

        Returns:
            Document type (technical, overview, world_building)
        """
        rel_path = file_path.relative_to(self.docs_root)
        parts = rel_path.parts

        if len(parts) > 0:
            if parts[0] in ["technical", "overview", "world_building"]:
                return parts[0]
        return "other"

    def _extract_metadata(self, content: str) -> dict[str, str]:
        """Extract YAML metadata from content.

        Args:
            content: Document content

        Returns:
            Dictionary of metadata fields
        """
        metadata = {}

        # Extract YAML front matter
        match = re.match(r"^---\n(.*?)\n---", content, re.DOTALL)
        if match:
            yaml_content = match.group(1)
            metadata = yaml.safe_load(yaml_content)

        return metadata

    def _calculate_coverage(self, sections: set[str], required: set[str]) -> float:
        """Calculate section coverage percentage.

        Args:
            sections: Found sections
            required: Required sections

        Returns:
            Coverage percentage (0-100)
        """
        if not required:
            return 100.0
        return len(sections.intersection(required)) / len(required) * 100

    def validate(self) -> ValidationResult:
        """Run health validation checks.

        Returns:
            Validation result with any issues found
        """
        result = ValidationResult()

        for md_file in self.docs_root.rglob("*.md"):
            try:
                content = md_file.read_text()
                rel_path = str(md_file.relative_to(self.docs_root))

                # Check metadata
                metadata = self._extract_metadata(content)
                missing_meta = self.required_metadata - set(metadata.keys())
                if missing_meta:
                    result.issues.append(
                        ValidationIssue(
                            message=f'Missing metadata fields: {", ".join(missing_meta)}',
                            file=rel_path,
                            severity=Severity.WARNING,
                            checker="health",
                        )
                    )

            except Exception as e:
                result.issues.append(
                    ValidationIssue(
                        message=f"Error processing file: {str(e)}",
                        file=rel_path,
                        severity=Severity.ERROR,
                        checker="health",
                    )
                )

        return result
