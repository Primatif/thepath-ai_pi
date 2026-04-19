#!/usr/bin/env python3

import logging
import re
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


def fix_trailing_whitespace(content: str) -> str:
    """Remove trailing whitespace from each line."""
    lines = content.splitlines()
    return "\n".join(line.rstrip() for line in lines)


def fix_consecutive_blank_lines(content: str) -> str:
    """Ensure no more than one consecutive blank line."""
    return re.sub(r"\n{3,}", "\n\n", content)


def fix_list_spacing(content: str) -> str:
    """Ensure proper spacing around lists."""
    # Add blank line before lists if not present
    content = re.sub(r"([^\n])\n([-*])", r"\1\n\n\2", content)
    # Add blank line after lists if not present
    content = re.sub(r"([-*][^\n]+)\n([^-*\n])", r"\1\n\n\2", content)
    return content


def fix_heading_spacing(content: str) -> str:
    """Ensure proper spacing around headings."""
    # Add blank line before headings if not present
    content = re.sub(r"([^\n])\n(#+\s)", r"\1\n\n\2", content)
    # Add blank line after headings if not present
    content = re.sub(r"(#+[^\n]+)\n([^#\n])", r"\1\n\n\2", content)
    return content


def fix_code_block_spacing(content: str) -> str:
    """Ensure proper spacing around code blocks."""
    # Add blank line before code blocks if not present
    content = re.sub(r"([^\n])\n(```)", r"\1\n\n\2", content)
    # Add blank line after code blocks if not present
    content = re.sub(r"(```)\n([^\n])", r"\1\n\n\2", content)
    return content


def fix_admonition_spacing(content: str) -> str:
    """Ensure proper spacing around admonitions."""
    # Add blank line before admonitions if not present
    content = re.sub(r"([^\n])\n(!!! )", r"\1\n\n\2", content)
    # Add blank line after admonitions if not present
    content = re.sub(r"(!!!.*\n.*)\n([^!\n])", r"\1\n\n\2", content)
    return content


def format_markdown_file(file_path: Path) -> bool:
    """Format a markdown file according to project standards."""
    try:
        content = file_path.read_text()
        original_content = content

        # Apply formatting fixes
        content = fix_trailing_whitespace(content)
        content = fix_consecutive_blank_lines(content)
        content = fix_list_spacing(content)
        content = fix_heading_spacing(content)
        content = fix_code_block_spacing(content)
        content = fix_admonition_spacing(content)

        # Ensure file ends with a single newline
        content = content.rstrip() + "\n"

        # Only write if changes were made
        if content != original_content:
            file_path.write_text(content)
            logger.info(f"Formatted {file_path}")
            return True
        return False

    except Exception as e:
        logger.error(f"Error formatting {file_path}: {str(e)}")
        return False


def find_markdown_files(directory: Path) -> list[Path]:
    """Find all markdown files in directory recursively."""
    return list(directory.rglob("*.md"))


def main():
    """Main function to format all markdown files."""
    # Get the project root directory
    project_root = Path(__file__).resolve().parents[3]
    docs_dir = project_root / "docs"

    if not docs_dir.exists():
        logger.error(f"Docs directory not found at {docs_dir}")
        return

    markdown_files = find_markdown_files(docs_dir)
    if not markdown_files:
        logger.info("No markdown files found")
        return

    formatted_count = 0
    for file_path in markdown_files:
        if format_markdown_file(file_path):
            formatted_count += 1

    logger.info(f"Formatted {formatted_count} of {len(markdown_files)} files")


if __name__ == "__main__":
    main()
