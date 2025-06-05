#!/usr/bin/env python

"""Ensure version consistency across pyproject.toml, __init__.py, and CHANGELOG.md."""

import re
import sys
from pathlib import Path

PYPROJECT = Path("pyproject.toml")
INIT = Path("src/app/__init__.py")
CHANGELOG = Path("CHANGELOG.md")


def extract_version_from_pyproject(path: Path) -> str | None:
    """Extract the version from the pyproject.toml.

    The version is extracted from the [project] table in the pyproject.toml file.
    """
    content = path.read_text(encoding="utf-8")
    # The regex pattern matches the version line in the pyproject.toml file.
    # The version is extracted from the [project] table.
    match = re.search(r"^version\s*=\s*[\"'](.+?)[\"']", content, flags=re.MULTILINE)
    return match.group(1) if match else None


def extract_version_from_init(path: Path) -> str | None:
    """Extract the version from the __init__.py.

    The version is extracted from the __version__ variable in the __init__.py file.
    """
    content = path.read_text(encoding="utf-8")
    # The regex pattern matches the __version__ line in the __init__.py file.
    # The version is extracted from the __version__ variable.
    match = re.search(r'^__version__\s*=\s*[\'"](.+?)[\'"]', content)
    return match.group(1) if match else None


def extract_version_from_changelog(path: Path) -> str | None:
    """Extract the version from the CHANGELOG.md.

    The version is extracted from the first top-level heading in the CHANGELOG.md file.
    The heading should be in the format: ## [X.Y.Z]

    Args:
        path (Path): The path to the CHANGELOG.md file.

    Returns:
        str | None: The version extracted from the CHANGELOG.md file.

    """
    content = path.read_text(encoding="utf-8")
    # The regex pattern matches the first top-level heading in the CHANGELOG.md file.
    # The version is extracted from the heading.
    match = re.search(r"^##\s*\[(\d+\.\d+\.\d+)\]", content, flags=re.MULTILINE)
    return match.group(1) if match else None


def main() -> int:
    """Checks that the version is the same in pyproject.toml, __init__.py, and CHANGELOG.md."""
    pyproject_version = extract_version_from_pyproject(PYPROJECT)
    init_version = extract_version_from_init(INIT)
    changelog_version = extract_version_from_changelog(CHANGELOG)

    if not all([pyproject_version, init_version, changelog_version]):
        # If any of the versions is missing, print a message and return 1.
        print("❌ Could not extract version from one or more files.")
        print(f"pyproject.toml: {pyproject_version}")
        print(f"__init__.py:     {init_version}")
        print(f"CHANGELOG.md:    {changelog_version}")
        return 1

    if pyproject_version != init_version or pyproject_version != changelog_version:
        # If the versions don't match, print a message and return 1.
        print("❌ Version mismatch:")
        print(f"pyproject.toml: {pyproject_version}")
        print(f"__init__.py:     {init_version}")
        print(f"CHANGELOG.md:    {changelog_version}")
        return 1

    # If all versions match, print a message and return 0.
    print(f"✅ Version match: {pyproject_version}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
