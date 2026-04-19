#!/usr/bin/env python3
"""Update mkdocs.yml with latest log files and social media posts."""

from datetime import datetime
from pathlib import Path

import yaml

# Map of section names to their emoji-prefixed versions
SECTION_NAMES = {"Logs": "📝 Logs", "Social Updates": "🔔 Social Updates"}


def get_dated_files(directory, date_format="%Y-%m-%d"):
    """Get all dated files from a directory."""
    files = []

    # Collect all .md files except index.md and README.md
    for file in directory.glob("*.md"):
        if file.name not in ["index.md", "README.md"]:
            try:
                # Parse date from filename (YYYY-MM-DD.md)
                date = datetime.strptime(file.stem, date_format)
                files.append((date, file))
            except ValueError:
                continue

    # Sort by date, newest first
    files.sort(key=lambda x: x[0], reverse=True)
    return files


def get_section_by_name(config, section_name):
    """Find a section in nav by its name, including emoji version."""
    emoji_name = SECTION_NAMES.get(section_name, section_name)
    for section in config["nav"]:
        if isinstance(section, dict):
            # Get the first (and should be only) key
            key = next(iter(section))
            if key == emoji_name:
                return section, key
    return None, None


def update_section(config, section_name, base_path, subsection=None):
    """Update a section in the config with dated files."""
    path = Path(f"docs/{base_path}")
    if subsection:
        path = path / subsection
    files = get_dated_files(path)

    section_dict, actual_name = get_section_by_name(config, section_name)
    if section_dict:
        if subsection:
            # Handle nested sections (like LinkedIn under Social Updates)
            subsection_content = [{"Overview": f"{base_path}/{subsection}/index.md"}]
            for date, file in files:
                display_date = date.strftime("%B %d, %Y")
                subsection_content.append({display_date: f"{base_path}/{subsection}/{file.name}"})

            for item in section_dict[actual_name]:
                if isinstance(item, dict) and subsection in item:
                    item[subsection] = subsection_content
                    break
        else:
            # Handle regular sections (like Logs)
            section_content = [{"Overview": f"{base_path}/index.md"}]
            for date, file in files:
                display_date = date.strftime("%B %d, %Y")
                section_content.append({display_date: f"{base_path}/{file.name}"})
            section_dict[actual_name] = section_content


def update_mkdocs():
    """Update mkdocs.yml with latest log files and social media posts."""
    # Read mkdocs.yml
    with open("mkdocs.yml") as f:
        config = yaml.safe_load(f)

    # Update Logs section
    update_section(config, "Logs", "meta/logs")

    # Update Social Updates section with LinkedIn subsection
    update_section(config, "Social Updates", "meta/social", "linkedin")

    # Write updated config
    with open("mkdocs.yml", "w") as f:
        yaml.dump(config, f, sort_keys=False, allow_unicode=True)


if __name__ == "__main__":
    update_mkdocs()
