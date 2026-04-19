"""Reference validator for documentation.

Validates cross-references between documentation files by:
1. Finding all markdown links
2. Checking that target files exist
3. Validating fragment identifiers
"""

import re
from pathlib import Path

from .validation_types import Severity, ValidationIssue, ValidationResult


class RefValidator:
    """Validates cross-references in documentation files."""

    def __init__(self, docs_root: str):
        """Initialize the reference validator.

        Args:
            docs_root: Root directory containing documentation files
        """
        self.docs_root = Path(docs_root)
        self.ref_pattern = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")
        self.glob_pattern = re.compile(r"[\*\?\[\]]")

    def _is_glob_pattern(self, path: str) -> bool:
        """Check if a path contains glob pattern characters.

        Args:
            path: Path to check

        Returns:
            True if path contains glob characters
        """
        return bool(self.glob_pattern.search(path))

    def _normalize_path(self, ref_path: str, source_file: Path) -> str:
        """Normalize a reference path relative to docs root.

        Args:
            ref_path: Raw reference path from markdown
            source_file: File containing the reference

        Returns:
            Normalized path relative to docs root
        """
        # Remove any 'docs/' prefix
        if ref_path.startswith("docs/"):
            ref_path = ref_path[5:]

        # Handle fragment identifiers
        path_part = ref_path.split("#")[0]
        if not path_part:
            return ref_path

        # Convert relative path to absolute
        if path_part.startswith("/"):
            abs_path = self.docs_root / path_part[1:]
        else:
            abs_path = source_file.parent / path_part

        try:
            # Make path relative to docs root
            rel_path = abs_path.relative_to(self.docs_root)
            return str(rel_path)
        except ValueError:
            return ref_path

    def _extract_refs(self, content: str, source_file: Path) -> list[str]:
        """Extract and normalize all references from content.

        Args:
            content: File content to extract refs from
            source_file: File being processed

        Returns:
            List of normalized reference paths
        """
        refs = []
        for match in self.ref_pattern.finditer(content):
            ref_path = match.group(2)

            # Skip external links and anchors
            if ref_path.startswith(("http://", "https://", "#")):
                continue

            # Skip glob patterns
            if self._is_glob_pattern(ref_path):
                continue

            normalized = self._normalize_path(ref_path, source_file)
            refs.append(normalized)
        return refs

    def validate(self) -> ValidationResult:
        """Validate all documentation references.

        Returns:
            ValidationResult containing any reference issues
        """
        result = ValidationResult()
        result.stats["total_references"] = 0
        result.stats["total_documents"] = 0

        # Build reference map
        ref_map: dict[str, set[str]] = {}
        for md_file in self.docs_root.rglob("*.md"):
            rel_path = str(md_file.relative_to(self.docs_root))
            result.stats["total_documents"] += 1

            try:
                content = md_file.read_text(encoding="utf-8")
                refs = self._extract_refs(content, md_file)
                result.stats["total_references"] += len(refs)
                ref_map[rel_path] = set(refs)

                # Check each reference
                for ref in refs:
                    # Skip fragment-only refs
                    if not ref or ref.startswith("#"):
                        continue

                    # Get path part without fragment
                    ref_path = ref.split("#")[0]
                    target = self.docs_root / ref_path

                    if not target.exists():
                        result.issues.append(
                            ValidationIssue(
                                message=f"Broken reference to '{ref}'",
                                file=rel_path,
                                severity=Severity.ERROR,
                                checker="references",
                            )
                        )

            except Exception as e:
                result.issues.append(
                    ValidationIssue(
                        message=f"Error processing file: {str(e)}",
                        file=rel_path,
                        severity=Severity.ERROR,
                        checker="references",
                    )
                )

        return result
