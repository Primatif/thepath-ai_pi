"""Generate the log files pages."""

from pathlib import Path

import mkdocs_gen_files

# Collect all markdown files from the logs directory
logs_dir = Path("docs/meta/logs")
nav = mkdocs_gen_files.Nav()

for path in sorted((logs_dir).rglob("*.md"), reverse=True):
    # Convert the path to docs-relative
    doc_path = path.relative_to("docs")

    # Skip index.md as it's handled separately
    if path.name == "index.md":
        continue

    # Get the date from the filename (assuming YYYY-MM-DD.md format)
    date = path.stem

    # Add to navigation
    nav[f"Development Logs/{date}"] = doc_path.as_posix()

# Write the navigation file
with mkdocs_gen_files.open("log_pages.yml", "w") as nav_file:
    nav_file.writelines(nav.build_literate_nav())
