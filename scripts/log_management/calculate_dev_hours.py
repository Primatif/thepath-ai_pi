#!/usr/bin/env python3

import re
from pathlib import Path
from typing import Optional

import yaml


def extract_yaml_block(content: str) -> Optional[dict]:
    """Extract the YAML block from a markdown file."""
    yaml_pattern = r"```yaml\n(.*?)\n```"
    match = re.search(yaml_pattern, content, re.DOTALL)
    if not match:
        return None

    try:
        return yaml.safe_load(match.group(1))
    except yaml.YAMLError:
        return None


def calculate_total_hours(logs_dir: Path) -> float:
    """Calculate total development hours from all log files."""
    total_hours = 0.0

    for log_file in logs_dir.glob("*.md"):
        if log_file.name in ["index.md", "README.md"]:
            continue

        try:
            content = log_file.read_text()
            yaml_data = extract_yaml_block(content)

            if yaml_data and "duration_hours" in yaml_data:
                hours = float(yaml_data["duration_hours"])
                total_hours += hours
        except Exception as e:
            print(f"Error processing {log_file}: {str(e)}")

    return total_hours


def update_index_page(total_hours: float):
    """Update the index.md page with total development hours."""
    index_path = Path("docs/index.md")
    if not index_path.exists():
        print(f"Warning: {index_path} does not exist")
        return

    content = index_path.read_text()

    hours_admonition = f"""!!! info "Development Progress"
    Total development time: {total_hours:.1f} hours

    This counter is automatically updated based on development logs.

"""

    # Check if admonition already exists
    if '!!! info "Development Progress"' in content:
        # Replace existing admonition up to the next section or image
        content = re.sub(
            r'!!! info "Development Progress".*?(?=\n\n[#!\[])',
            hours_admonition.strip(),
            content,
            flags=re.DOTALL,
        )
    else:
        # Add after first heading
        content = re.sub(r"(#[^\n]+\n)", f"\\1\n{hours_admonition}", content, count=1)

    index_path.write_text(content)


def main():
    """Main function to calculate hours and update index."""
    # Get the project root directory
    project_root = Path(__file__).resolve().parents[3]
    logs_dir = project_root / "docs" / "meta" / "logs"

    if not logs_dir.exists():
        print(f"Error: Logs directory not found at {logs_dir}")
        return

    total_hours = calculate_total_hours(logs_dir)
    update_index_page(total_hours)
    print(f"Total development hours: {total_hours:.1f}")
    print("Updated docs/index.md with total hours")


if __name__ == "__main__":
    main()
