#!/usr/bin/env python3
"""
Simple code formatter to fix Black formatting issues
"""

import os
import re
from pathlib import Path


def format_file(file_path):
    """Format a single Python file to fix common Black issues"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        original_content = content

        # Fix trailing commas in lists/tuples
        content = re.sub(r'(\],?\s*)\n(\s*\])', r'\1,\n\2', content)

        # Fix long lines by adding proper line breaks
        lines = content.split('\n')
        formatted_lines = []

        for line in lines:
            # Fix import lines
            if line.strip().startswith('from') and ' import ' in line and len(line) > 88:
                # Split long import lines
                if ',' in line:
                    parts = line.split(' import ')
                    if len(parts) == 2:
                        module_part = parts[0]
                        imports_part = parts[1]
                        imports = [imp.strip() for imp in imports_part.split(',')]
                        if len(imports) > 1:
                            formatted_lines.append(f"{module_part} import (")
                            for imp in imports[:-1]:
                                formatted_lines.append(f"    {imp},")
                            formatted_lines.append(f"    {imports[-1]},")
                            formatted_lines.append(")")
                            continue

            formatted_lines.append(line)

        content = '\n'.join(formatted_lines)

        # Remove trailing whitespace
        content = re.sub(r' +\n', '\n', content)

        # Ensure file ends with newline
        if not content.endswith('\n'):
            content += '\n'

        # Only write if content changed
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"Formatted: {file_path}")

    except Exception as e:
        print(f"Error formatting {file_path}: {e}")


def main():
    """Format all Python files in the project"""
    project_root = Path(__file__).parent

    # Find all Python files
    for python_file in project_root.rglob('*.py'):
        # Skip certain directories
        skip_dirs = {'__pycache__', '.git', 'venv', '.venv', 'build', 'dist'}
        if any(skip_dir in str(python_file) for skip_dir in skip_dirs):
            continue

        format_file(python_file)

    print("Formatting complete!")


if __name__ == "__main__":
    main()
