#!/usr/bin/env python3
"""
Update Version Files for AMAS Releases
AI-enhanced version management with intelligent version bumping
"""

import argparse
import os
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple

class AIVersionManager:
    """AI-enhanced version management system"""

    def __init__(self):
        self.version_files = {
            "pyproject.toml": r'version\s*=\s*["\']([^"\']+)["\']',
            "setup.py": r'version\s*=\s*["\']([^"\']+)["\']',
            "src/amas/__init__.py": r'__version__\s*=\s*["\']([^"\']+)["\']',
            "package.json": r'"version"\s*:\s*["\']([^"\']+)["\']',
        }

        self.version_pattern = re.compile(
            r"^v?(\d+)\.(\d+)\.(\d+)(?:-([a-zA-Z0-9.-]+))?$"
        )

    def parse_version(self, version: str) -> Tuple[int, int, int, str]:
        """Parse version string into components"""
        version = version.lstrip("v")
        match = self.version_pattern.match(version)

        if not match:
            raise ValueError(f"Invalid version format: {version}")

        major, minor, patch, prerelease = match.groups()
        return int(major), int(minor), int(patch), prerelease or ""

    def bump_version(self, current_version: str, bump_type: str) -> str:
        """Intelligently bump version based on type"""
        major, minor, patch, prerelease = self.parse_version(current_version)

        if bump_type == "major":
            return f"{major + 1}.0.0"
        elif bump_type == "minor":
            return f"{major}.{minor + 1}.0"
        elif bump_type == "patch":
            return f"{major}.{minor}.{patch + 1}"
        elif bump_type == "prerelease":
            if prerelease:
                # Increment prerelease version
                prerelease_parts = prerelease.split(".")
                if prerelease_parts[-1].isdigit():
                    prerelease_parts[-1] = str(int(prerelease_parts[-1]) + 1)
                else:
                    prerelease_parts.append("1")
                return f"{major}.{minor}.{patch}-{'.'.join(prerelease_parts)}"
            else:
                return f"{major}.{minor}.{patch + 1}-alpha.1"
        else:
            raise ValueError(f"Invalid bump type: {bump_type}")

    def find_version_in_file(self, file_path: Path, pattern: str) -> Tuple[str, int]:
        """Find current version in file"""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            match = re.search(pattern, content)
            if match:
                return match.group(1), match.start()
            return None, -1
        except Exception as e:
            print(f"Warning: Could not read {file_path}: {e}")
            return None, -1

    def update_version_in_file(
        self, file_path: Path, pattern: str, old_version: str, new_version: str
    ) -> bool:
        """Update version in file"""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            # Replace version
            new_content = re.sub(
                pattern, lambda m: m.group(0).replace(old_version, new_version), content
            )

            if new_content != content:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(new_content)
                return True
            return False
        except Exception as e:
            print(f"Error updating {file_path}: {e}")
            return False

    def update_all_version_files(self, new_version: str) -> Dict[str, bool]:
        """Update all version files"""
        results = {}

        for file_path, pattern in self.version_files.items():
            path = Path(file_path)
            if path.exists():
                # Find current version
                current_version, _ = self.find_version_in_file(path, pattern)

                if current_version:
                    print(f"📝 Updating {file_path}: {current_version} → {new_version}")
                    success = self.update_version_in_file(
                        path, pattern, current_version, new_version
                    )
                    results[file_path] = success
                else:
                    print(f"⚠️ No version found in {file_path}")
                    results[file_path] = False
            else:
                print(f"⚠️ File not found: {file_path}")
                results[file_path] = False

        return results

    def generate_version_info(self, version: str) -> str:
        """Generate version information for documentation"""
        major, minor, patch, prerelease = self.parse_version(version)

        version_info = f"""# Version Information

## AMAS {version}

**Release Date**: {datetime.now().strftime("%Y-%m-%d")}
**Version Type**: {'Pre-release' if prerelease else 'Stable'}

### Version Components:
- **Major**: {major} (API compatibility)
- **Minor**: {minor} (new features)
- **Patch**: {patch} (bug fixes)
- **Pre-release**: {prerelease or 'None'}

### Compatibility:
- **Python**: >=3.9
- **Dependencies**: See requirements.txt
- **Platform**: Cross-platform

### Installation:
```bash
pip install amas=={version}
```

### Docker:
```bash
docker pull amas/amas:{version}
```

---
*Generated by AI Version Manager*
"""

        return version_info

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="AI-enhanced version management")
    parser.add_argument("--version", required=True, help="New version (e.g., v1.0.0)")
    parser.add_argument(
        "--type",
        default="minor",
        choices=["major", "minor", "patch", "prerelease"],
        help="Version bump type",
    )
    parser.add_argument(
        "--auto-bump",
        action="store_true",
        help="Automatically bump version based on type",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be changed without making changes",
    )
    parser.add_argument(
        "--output",
        default="VERSION_INFO.md",
        help="Output file for version information",
    )

    args = parser.parse_args()

    try:
        print("🤖 AI-Enhanced Version Manager")
        print("=" * 40)

        manager = AIVersionManager()

        # Determine target version
        if args.auto_bump:
            # Find current version from pyproject.toml
            current_version = None
            pyproject_path = Path("pyproject.toml")

            if pyproject_path.exists():
                current_version, _ = manager.find_version_in_file(
                    pyproject_path, manager.version_files["pyproject.toml"]
                )

            if not current_version:
                print("❌ Could not determine current version for auto-bump")
                sys.exit(1)

            target_version = manager.bump_version(current_version, args.type)
            print(
                f"📈 Auto-bumping: {current_version} → {target_version} ({args.type})"
            )
        else:
            target_version = args.version.lstrip("v")

        # Validate version format
        try:
            manager.parse_version(target_version)
        except ValueError as e:
            print(f"❌ Invalid version format: {e}")
            sys.exit(1)

        print(f"🎯 Target version: {target_version}")
        print(f"📁 Version files to update: {len(manager.version_files)}")

        if args.dry_run:
            print("\\n🔍 DRY RUN - No changes will be made")
            for file_path, pattern in manager.version_files.items():
                path = Path(file_path)
                if path.exists():
                    current_version, _ = manager.find_version_in_file(path, pattern)
                    if current_version:
                        print(f"  {file_path}: {current_version} → {target_version}")
                    else:
                        print(f"  {file_path}: No version found")
                else:
                    print(f"  {file_path}: File not found")
        else:
            # Update version files
            print("\\n📝 Updating version files...")
            results = manager.update_all_version_files(target_version)

            # Report results
            success_count = sum(1 for success in results.values() if success)
            total_count = len(results)

            print(
                f"\\n📊 Results: {success_count}/{total_count} files updated successfully"
            )

            for file_path, success in results.items():
                status = "✅" if success else "❌"
                print(f"  {status} {file_path}")

            if success_count == 0:
                print("\\n❌ No files were updated successfully")
                sys.exit(1)

            # Generate version information
            print(f"\\n📄 Generating version information...")
            version_info = manager.generate_version_info(target_version)

            with open(args.output, "w", encoding="utf-8") as f:
                f.write(version_info)

            print(f"✅ Version information saved to: {args.output}")

            # Update CHANGELOG.md if it exists
            changelog_path = Path("CHANGELOG.md")
            if changelog_path.exists():
                print("\\n📝 Updating CHANGELOG.md...")
                try:
                    with open(changelog_path, "r", encoding="utf-8") as f:
                        changelog_content = f.read()

                    # Add new version entry if not already present
                    if f"## [{target_version}]" not in changelog_content:
                        new_entry = f"## [{target_version}] - {datetime.now().strftime('%Y-%m-%d')}\\n\\n### Added\\n- Version {target_version} release\\n\\n"

                        # Insert after the first ## heading
                        lines = changelog_content.split("\\n")
                        insert_index = 0
                        for i, line in enumerate(lines):
                            if line.startswith("## ") and i > 0:
                                insert_index = i
                                break

                        lines.insert(insert_index, new_entry)
                        new_changelog = "\\n".join(lines)

                        with open(changelog_path, "w", encoding="utf-8") as f:
                            f.write(new_changelog)

                        print("✅ CHANGELOG.md updated")
                    else:
                        print("ℹ️ CHANGELOG.md already contains this version")
                except Exception as e:
                    print(f"⚠️ Could not update CHANGELOG.md: {e}")

        print(f"\\n🎉 Version management completed successfully!")
        return True

    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
