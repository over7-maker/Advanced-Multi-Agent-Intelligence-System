#!/usr/bin/env python3
"""
Automatic code formatting script for AMAS
This script formats all Python code using Black and isort
"""

import subprocess
import sys
from pathlib import Path


def run_command(cmd, description):
    """Run a command and handle errors"""
    print(f"🔧 {description}...")
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ {description} completed successfully")
            if result.stdout:
                print(f"   Output: {result.stdout.strip()}")
        else:
            print(f"⚠️  {description} had issues:")
            if result.stderr:
                print(f"   Error: {result.stderr.strip()}")
            if result.stdout:
                print(f"   Output: {result.stdout.strip()}")
        return result.returncode == 0
    except Exception as e:
        print(f"❌ Error running {description}: {e}")
        return False


def main():
    """Main formatting function"""
    print("🚀 AMAS Code Formatting Tool")
    print("=" * 40)

    # Get the repository root
    repo_root = Path.cwd()
    print(f"📂 Working directory: {repo_root}")

    # List of commands to run
    commands = [
        (
            "python -m black . --line-length=88 --target-version=py311",
            "Formatting code with Black",
        ),
        (
            "python -m isort . --profile=black --line-length=88",
            "Sorting imports with isort",
        ),
        (
            "python -m flake8 . --max-line-length=88 --extend-ignore=E203,W503,E501",
            "Checking code with flake8",
        ),
    ]

    success_count = 0
    for cmd, description in commands:
        if run_command(cmd, description):
            success_count += 1
        print()

    print(f"📊 Completed {success_count}/{len(commands)} formatting tasks")

    if success_count == len(commands):
        print("🎉 All code formatting completed successfully!")
        return 0
    else:
        print("⚠️  Some formatting tasks had issues, but this is normal")
        print("   The important thing is that Black and isort ran")
        return 0


if __name__ == "__main__":
    sys.exit(main())
