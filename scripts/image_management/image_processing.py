#!/usr/bin/env python3
"""Image metadata scrubbing script.

This script processes images in the repository by:
1. Removing metadata (EXIF, XMP, etc.)
2. Setting DPI to 72
3. Resizing to max width of 800px while maintaining aspect ratio
4. Preserving image quality

Supports common image formats including:
- JPEG/JPG
- PNG
- GIF
- TIFF
"""

import argparse
import logging
import sys
from pathlib import Path

from PIL import ExifTags, Image

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Constants
MAX_WIDTH = 800
TARGET_DPI = 72


def is_close_enough(a, b, rel_tol=1e-2):
    """Check if two numbers are close enough, accounting for floating point precision."""
    return abs(a - b) <= rel_tol * abs(b)


class ImageMetadata:
    """Class to handle image metadata operations."""

    def __init__(self, image_path: Path):
        """Initialize with image path."""
        self.path = image_path
        self.metadata = {}
        self._load_metadata()

    def _load_metadata(self):
        """Load all available metadata from image."""
        try:
            with Image.open(self.path) as img:
                # Get EXIF data
                if hasattr(img, "_getexif") and img._getexif():
                    exif = img._getexif()
                    if exif:
                        for tag_id in exif:
                            try:
                                tag = ExifTags.TAGS.get(tag_id, tag_id)
                                self.metadata[f"EXIF_{tag}"] = str(exif[tag_id])
                            except Exception:
                                continue

                # Get other image info
                self.metadata["FORMAT"] = img.format
                self.metadata["MODE"] = img.mode
                self.metadata["SIZE"] = img.size

                # Get DPI info
                if "dpi" in img.info:
                    self.metadata["DPI"] = img.info["dpi"]

                # Get all available info except DPI
                for k, v in img.info.items():
                    if k != "dpi" and isinstance(v, (str, int, float)):
                        self.metadata[k] = v

        except Exception as e:
            logger.error(f"Error loading metadata from {self.path}: {str(e)}")

    def has_metadata(self) -> bool:
        """Check if image has any metadata beyond basic format info."""
        basic_info = {"FORMAT", "MODE", "SIZE", "DPI"}
        return len(set(self.metadata.keys()) - basic_info) > 0

    def get_metadata_summary(self) -> str:
        """Get a formatted summary of metadata."""
        if not self.has_metadata():
            return "No metadata found"

        summary = []
        for k, v in self.metadata.items():
            if k not in {"FORMAT", "MODE", "SIZE", "DPI"}:
                summary.append(f"{k}: {v}")
        return "\n".join(summary)


def get_image_files(directory: Path) -> list[Path]:
    """Find all image files in the directory recursively.

    Args:
        directory: Root directory to search

    Returns:
        List of paths to image files
    """
    image_extensions = {".jpg", ".jpeg", ".png", ".gif", ".tiff", ".bmp"}
    image_files = []

    for ext in image_extensions:
        image_files.extend(directory.rglob(f"*{ext}"))
        image_files.extend(directory.rglob(f"*{ext.upper()}"))

    return sorted(image_files)


def check_images(image_files: list[Path]) -> tuple[list[Path], list[Path]]:
    """Check which images have metadata or need resizing/DPI adjustment.

    Args:
        image_files: List of image paths to check

    Returns:
        Tuple of (images needing processing, images without issues)
    """
    needs_processing = []
    no_issues = []

    for path in image_files:
        needs_work = False
        metadata = ImageMetadata(path)

        # Check metadata
        if metadata.has_metadata():
            needs_work = True

        # Check size and DPI
        with Image.open(path) as img:
            width, height = img.size
            if width > MAX_WIDTH:
                needs_work = True

            dpi = img.info.get("dpi", (None, None))
            if dpi and (
                not is_close_enough(dpi[0], TARGET_DPI) or not is_close_enough(dpi[1], TARGET_DPI)
            ):
                needs_work = True

        if needs_work:
            needs_processing.append(path)
        else:
            no_issues.append(path)

    return needs_processing, no_issues


def process_image(image_path: Path, dry_run: bool = False) -> bool:
    """Process an image: remove metadata, resize, and set DPI.

    Args:
        image_path: Path to the image file
        dry_run: If True, only check for issues without modifying

    Returns:
        True if successful, False if failed
    """
    try:
        metadata = ImageMetadata(image_path)

        if dry_run:
            with Image.open(image_path) as img:
                width, height = img.size
                dpi = img.info.get("dpi", (None, None))

                if metadata.has_metadata():
                    logger.info(f"Found metadata in {image_path}:")
                    logger.info(metadata.get_metadata_summary())

                if width > MAX_WIDTH:
                    logger.info(f"Image needs resizing: {width}x{height}")

                if dpi and (
                    not is_close_enough(dpi[0], TARGET_DPI)
                    or not is_close_enough(dpi[1], TARGET_DPI)
                ):
                    logger.info(f"Current DPI: {dpi}, target: {TARGET_DPI}")
            return True

        # Process the image
        with Image.open(image_path) as img:
            # Calculate new size if needed
            width, height = img.size
            if width > MAX_WIDTH:
                ratio = MAX_WIDTH / width
                new_size = (MAX_WIDTH, int(height * ratio))
                img = img.resize(new_size, Image.Resampling.LANCZOS)

            # Create new image without metadata
            data = list(img.getdata())
            image_clean = Image.new(img.mode, img.size)
            image_clean.putdata(data)

            # Set DPI
            dpi = (TARGET_DPI, TARGET_DPI)

            # Save with optimal settings for each format
            save_kwargs = {"dpi": dpi}
            if image_path.suffix.lower() in {".jpg", ".jpeg"}:
                save_kwargs.update({"quality": 95, "optimize": True})
            elif image_path.suffix.lower() == ".png":
                save_kwargs.update({"optimize": True})

            # Save back to original file
            image_clean.save(image_path, **save_kwargs)

            # Verify changes
            check_metadata = ImageMetadata(image_path)
            with Image.open(image_path) as verify_img:
                current_width = verify_img.size[0]
                current_dpi = verify_img.info.get("dpi", (None, None))

                if check_metadata.has_metadata():
                    logger.error(f"Failed to remove all metadata from {image_path}")
                    return False

                if current_width > MAX_WIDTH:
                    logger.error(f"Failed to resize {image_path}")
                    return False

                if current_dpi and (
                    not is_close_enough(current_dpi[0], TARGET_DPI)
                    or not is_close_enough(current_dpi[1], TARGET_DPI)
                ):
                    logger.error(f"Failed to set DPI for {image_path}")
                    return False

            logger.info(f"Successfully processed {image_path}")
            return True

    except Exception as e:
        logger.error(f"Failed to process {image_path}: {str(e)}")
        return False


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Process images in the repository: remove metadata, resize, and set DPI"
    )
    parser.add_argument(
        "--directory",
        type=str,
        default=".",
        help="Root directory to process (default: current directory)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Check for issues without modifying files",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Only check if any images need processing and exit with status 1 if found",
    )
    args = parser.parse_args()

    root_dir = Path(args.directory).resolve()
    if not root_dir.exists():
        logger.error(f"Directory not found: {root_dir}")
        sys.exit(1)

    logger.info(f"Searching for images in {root_dir}")
    image_files = get_image_files(root_dir)

    if not image_files:
        logger.info("No image files found")
        sys.exit(0)

    logger.info(f"Found {len(image_files)} image files")

    # Check which images need processing
    needs_processing, no_issues = check_images(image_files)

    if args.check:
        if needs_processing:
            logger.error(f"Found {len(needs_processing)} images needing processing:")
            for path in needs_processing:
                logger.error(f"  {path}")
            sys.exit(1)
        logger.info("No images need processing")
        sys.exit(0)

    if not needs_processing:
        logger.info("No images need processing")
        sys.exit(0)

    logger.info(f"Found {len(needs_processing)} images needing processing")

    if args.dry_run:
        for path in needs_processing:
            process_image(path, dry_run=True)
        sys.exit(0)

    # Process each image
    success_count = 0
    for image_path in needs_processing:
        if process_image(image_path):
            success_count += 1

    # Print summary
    logger.info(f"Successfully processed {success_count} of {len(needs_processing)} images")

    # Exit with error if any images failed
    if success_count < len(needs_processing):
        sys.exit(1)


if __name__ == "__main__":
    main()
