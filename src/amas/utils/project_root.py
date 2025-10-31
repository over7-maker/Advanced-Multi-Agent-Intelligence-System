#!/usr/bin/env python3
"""
Improved Project Root Finding Utility
Implements robust project root detection with security hardening and comprehensive validation
"""

import logging
import os
import sys
from pathlib import Path
from typing import List, Optional, Set

logger = logging.getLogger(__name__)

# Maximum traversal depth to prevent infinite loops
MAX_TRAVERSAL_DEPTH = 20

# Project root indicators in order of preference
PROJECT_ROOT_INDICATORS = [
    ".git",  # Git repository
    "pyproject.toml",  # Python project configuration
    "setup.py",  # Python package setup
    "requirements.txt",  # Python dependencies
    "Pipfile",  # Pipenv configuration
    "poetry.lock",  # Poetry lock file
    "Cargo.toml",  # Rust project
    "package.json",  # Node.js project
    "composer.json",  # PHP project
    "go.mod",  # Go module
    "pom.xml",  # Maven project
    "build.gradle",  # Gradle project
    "Makefile",  # Make-based project
    "Dockerfile",  # Docker project
    "docker-compose.yml",  # Docker Compose project
    "README.md",  # Project documentation
    "LICENSE",  # Project license
    "CHANGELOG.md",  # Project changelog
]

# Security: Directories to avoid during traversal
RESTRICTED_DIRECTORIES = {
    "/",  # Root directory
    "/home",  # User home directories
    "/etc",  # System configuration
    "/var",  # Variable data
    "/tmp",  # Temporary files
    "/proc",  # Process information
    "/sys",  # System information
    "/dev",  # Device files
    "/mnt",  # Mount points
    "/media",  # Removable media
    "/opt",  # Optional software
    "/usr",  # User programs
    "/bin",  # Essential binaries
    "/sbin",  # System binaries
    "/lib",  # Libraries
    "/lib64",  # 64-bit libraries
    "/boot",  # Boot files
    "/root",  # Root user home
}

# Security: File patterns to avoid
RESTRICTED_FILE_PATTERNS = {
    ".env",  # Environment files
    ".env.local",  # Local environment files
    ".env.production",  # Production environment files
    "secrets.json",  # Secrets files
    "config.json",  # Configuration files
    "credentials.json",  # Credentials files
    "private_key.pem",  # Private keys
    "id_rsa",  # SSH private key
    "id_dsa",  # SSH private key
    "id_ecdsa",  # SSH private key
    "id_ed25519",  # SSH private key
    "known_hosts",  # SSH known hosts
    "authorized_keys",  # SSH authorized keys
    "passwd",  # Password file
    "shadow",  # Shadow password file
    "group",  # Group file
    "gshadow",  # Group shadow file
}


class ProjectRootError(Exception):
    """Exception raised when project root cannot be determined"""

    pass


class SecurityError(Exception):
    """Exception raised when security restrictions are violated"""

    pass


def is_restricted_directory(path: str) -> bool:
    """Check if directory is in restricted list"""
    try:
        resolved_path = os.path.realpath(os.path.abspath(path))
        return any(
            resolved_path.startswith(restricted)
            for restricted in RESTRICTED_DIRECTORIES
        )
    except (OSError, ValueError):
        return True


def is_restricted_file(path: str) -> bool:
    """Check if file matches restricted patterns"""
    filename = os.path.basename(path)
    return filename in RESTRICTED_FILE_PATTERNS


def validate_path_security(path: str) -> bool:
    """Validate that path is safe to traverse"""
    try:
        # Check if path exists and is accessible
        if not os.path.exists(path):
            return False

        # Check if it's a directory
        if not os.path.isdir(path):
            return False

        # Check if it's in restricted directories
        if is_restricted_directory(path):
            return False

        # Check if we can read the directory
        if not os.access(path, os.R_OK):
            return False

        return True
    except (OSError, ValueError, PermissionError):
        return False


def find_project_root(start_path: Optional[str] = None) -> str:
    """
    Find project root directory with comprehensive validation and security checks

    Args:
        start_path: Starting directory for search. If None, uses current working directory.

    Returns:
        str: Absolute path to project root directory

    Raises:
        ProjectRootError: If project root cannot be determined
        SecurityError: If security restrictions are violated
    """
    if start_path is None:
        start_path = os.getcwd()

    # Validate starting path
    if not validate_path_security(start_path):
        raise SecurityError(f"Starting path is not safe to traverse: {start_path}")

    # Convert to absolute path and resolve symlinks
    try:
        current_path = os.path.realpath(os.path.abspath(start_path))
    except (OSError, ValueError) as e:
        raise ProjectRootError(f"Cannot resolve starting path: {e}")

    depth = 0
    original_path = current_path

    logger.debug(f"Starting project root search from: {current_path}")

    # Traverse up the directory tree
    while current_path != os.path.dirname(current_path) and depth < MAX_TRAVERSAL_DEPTH:
        # Security check: ensure we're not in restricted directories
        if is_restricted_directory(current_path):
            logger.warning(f"Reached restricted directory: {current_path}")
            break

        # Check for project root indicators
        for indicator in PROJECT_ROOT_INDICATORS:
            indicator_path = os.path.join(current_path, indicator)

            # Security check: avoid restricted files
            if is_restricted_file(indicator_path):
                logger.debug(f"Skipping restricted file: {indicator_path}")
                continue

            try:
                if os.path.exists(indicator_path):
                    # Additional validation for specific indicators
                    if indicator == ".git" and not os.path.isdir(indicator_path):
                        continue

                    logger.info(
                        f"Found project root at: {current_path} (indicator: {indicator})"
                    )
                    return current_path
            except (OSError, ValueError, PermissionError) as e:
                logger.debug(f"Cannot access {indicator_path}: {e}")
                continue

        # Move up one directory
        parent_path = os.path.dirname(current_path)
        if parent_path == current_path:
            # Reached root directory
            break

        current_path = parent_path
        depth += 1

    # If no project root found, try fallback strategies
    logger.warning(
        f"No project root found after traversing {depth} levels from {original_path}"
    )

    # Fallback 1: Check if current directory has any project-like files
    fallback_indicators = ["README.md", "LICENSE", "CHANGELOG.md", "requirements.txt"]
    for indicator in fallback_indicators:
        indicator_path = os.path.join(original_path, indicator)
        if os.path.exists(indicator_path) and not is_restricted_file(indicator_path):
            logger.info(
                f"Using fallback project root: {original_path} (indicator: {indicator})"
            )
            return original_path

    # Fallback 2: Use the original directory if it's safe
    if validate_path_security(original_path):
        logger.warning(
            f"Using original directory as fallback project root: {original_path}"
        )
        return original_path

    # Final fallback: Use current working directory
    cwd = os.getcwd()
    if validate_path_security(cwd):
        logger.warning(f"Using current working directory as final fallback: {cwd}")
        return cwd

    raise ProjectRootError(
        f"Could not determine project root from {start_path}. "
        f"Traversed {depth} levels and checked {len(PROJECT_ROOT_INDICATORS)} indicators. "
        f"Please ensure you're running from within a valid project directory."
    )


def get_project_root() -> str:
    """
    Get project root with caching for performance

    Returns:
        str: Absolute path to project root directory
    """
    # Use module-level caching
    if not hasattr(get_project_root, "_cached_root"):
        try:
            get_project_root._cached_root = find_project_root()
            logger.info(f"Project root cached: {get_project_root._cached_root}")
        except (ProjectRootError, SecurityError) as e:
            logger.error(f"Failed to find project root: {e}")
            # Use current working directory as absolute fallback
            get_project_root._cached_root = os.getcwd()
            logger.warning(
                f"Using current working directory as fallback: {get_project_root._cached_root}"
            )

    return get_project_root._cached_root


def clear_project_root_cache():
    """Clear the project root cache (useful for testing)"""
    if hasattr(get_project_root, "_cached_root"):
        delattr(get_project_root, "_cached_root")
        logger.debug("Project root cache cleared")


def validate_project_structure(project_root: str) -> bool:
    """
    Validate that the project root has a reasonable structure

    Args:
        project_root: Path to project root directory

    Returns:
        bool: True if project structure is valid
    """
    try:
        if not os.path.exists(project_root) or not os.path.isdir(project_root):
            return False

        # Check for at least one of these essential files/directories
        essential_items = [
            "src",
            "lib",
            "app",
            "main.py",
            "index.py",
            "app.py",
            "package.json",
            "setup.py",
            "pyproject.toml",
            "Cargo.toml",
        ]

        for item in essential_items:
            item_path = os.path.join(project_root, item)
            if os.path.exists(item_path):
                return True

        return False
    except (OSError, ValueError):
        return False


def get_relative_path_from_root(
    file_path: str, project_root: Optional[str] = None
) -> str:
    """
    Get relative path from project root

    Args:
        file_path: Path to file
        project_root: Project root directory (if None, will be determined)

    Returns:
        str: Relative path from project root
    """
    if project_root is None:
        project_root = get_project_root()

    try:
        return os.path.relpath(file_path, project_root)
    except ValueError:
        # If paths are on different drives (Windows), return absolute path
        return os.path.abspath(file_path)


def add_project_root_to_path(project_root: Optional[str] = None):
    """
    Add project root to Python path if not already present

    Args:
        project_root: Project root directory (if None, will be determined)
    """
    if project_root is None:
        project_root = get_project_root()

    if project_root not in sys.path:
        sys.path.insert(0, project_root)
        logger.debug(f"Added project root to Python path: {project_root}")


# Convenience function for backward compatibility
def find_project_root_legacy() -> str:
    """
    Legacy function for backward compatibility
    Uses the old logic but with security improvements
    """
    try:
        return find_project_root()
    except (ProjectRootError, SecurityError):
        # Fallback to current working directory
        return os.getcwd()


if __name__ == "__main__":
    # Test the project root finding
    try:
        root = find_project_root()
        print(f"Project root found: {root}")

        # Validate project structure
        if validate_project_structure(root):
            print("Project structure is valid")
        else:
            print("Warning: Project structure may be invalid")

    except Exception as e:
        print(f"Error finding project root: {e}")
        sys.exit(1)
