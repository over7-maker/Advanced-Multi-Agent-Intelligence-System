#!/usr/bin/env python3
"""
Fix YAML Syntax - Fix all broken YAML in workflow files
"""

import logging
import os
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

import yaml

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class YAMLSyntaxFixer:
    """Fix YAML syntax issues in workflow files"""

    def __init__(self):
        self.fix_results = {}

    def fix_broken_run_commands(self, workflow_file: str) -> Dict[str, Any]:
        """Fix broken run commands in workflow files"""
        try:
            with open(workflow_file, "r", encoding="utf-8") as f:
                content = f.read()

            fixes_applied = 0

            # Fix broken run commands with backslashes and quotes
            patterns = [
                # Pattern 1: Broken run commands with backslashes
                (
                    r'run: "if \[ -n \\"([^"]+)\\" \]; then\\n  python scripts/([^"]+)\\ \|\| echo "Script completed with warnings"\n        \\ --files \$([^"]+) --output ([^"]+) --([^"]+)\\\n        \\ \|\| echo \\"([^"]+)\\"\\nelse\\n  python scripts/([^"]+)\\\n        \\ --directory \. --output ([^"]+) --([^"]+) --extensions\\\n        \\ \.py \.js \.ts \|\| echo \\"([^"]+)\\"\\nfi\\n"',
                    r'run: |\n        if [ -n "$\3" ]; then\n          python scripts/\2 --files $\3 --output \4 --\5 || echo "\6"\n        else\n          python scripts/\7 --directory . --output \8 --\9 --extensions .py .js .ts || echo "\10"\n        fi',
                ),
                # Pattern 2: Simple broken run commands
                (
                    r'run: "([^"]*)\\n([^"]*)\\n([^"]*)\\n"',
                    r"run: |\n        \1\n        \2\n        \3",
                ),
                # Pattern 3: Broken pytest commands
                (
                    r'run: "if \[ -d \\"([^"]+)\\" \]; then\\n  python -m pytest ([^"]+)\\\n        \\ -v --tb=short \|\| echo \\"([^"]+)\\"\\nelse\\n \\\n        \\ echo \\"([^"]+)\\"\\nfi\\n"',
                    r'run: |\n        if [ -d "\1" ]; then\n          python -m pytest \2 -v --tb=short || echo "\3"\n        else\n          echo "\4"\n        fi',
                ),
                # Pattern 4: Broken documentation commands
                (
                    r'run: "if \[ -d \\"([^"]+)\\" \]; then\\n  cd ([^"]+) && make html \|\| echo \\"([^"]+)\\"\\nelse\\n \\\n        \\ echo \\"([^"]+)\\"\\nfi\\n"',
                    r'run: |\n        if [ -d "\1" ]; then\n          cd \2 && make html || echo "\3"\n        else\n          echo "\4"\n        fi',
                ),
            ]

            for pattern, replacement in patterns:
                if re.search(pattern, content):
                    content = re.sub(pattern, replacement, content)
                    fixes_applied += 1

            # Write back if fixes were applied
            if fixes_applied > 0:
                with open(workflow_file, "w", encoding="utf-8") as f:
                    f.write(content)

            return {"fixed": True, "fixes_applied": fixes_applied}

        except Exception as e:
            return {"fixed": False, "error": str(e), "fixes_applied": 0}

    def fix_all_workflow_yaml(self) -> Dict[str, Any]:
        """Fix all workflow YAML files"""
        try:
            logger.info("Fixing YAML syntax in all workflows...")

            workflow_files = [
                ".github/workflows/ai_development.yml",
                ".github/workflows/ai_complete_workflow.yml",
                ".github/workflows/ai_simple_workflow.yml",
            ]

            workflow_fixes = {}

            for workflow_file in workflow_files:
                if Path(workflow_file).exists():
                    logger.info(f"Fixing YAML syntax in {workflow_file}...")

                    # Fix broken run commands
                    run_fixes = self.fix_broken_run_commands(workflow_file)

                    workflow_fixes[workflow_file] = {
                        "run_commands": run_fixes,
                        "total_fixes": run_fixes.get("fixes_applied", 0),
                    }
                else:
                    workflow_fixes[workflow_file] = {"error": "File not found"}

            return {
                "workflow_fixes": workflow_fixes,
                "total_workflows": len(workflow_files),
                "fixed_workflows": len(
                    [w for w in workflow_fixes.values() if w.get("total_fixes", 0) > 0]
                ),
                "timestamp": datetime.now().isoformat(),
            }

        except Exception as e:
            logger.error(f"Error fixing YAML syntax: {e}")
            return {"error": str(e)}


def main():
    """Main function"""
    import argparse

    parser = argparse.ArgumentParser(description="Fix YAML Syntax")
    parser.add_argument(
        "--output",
        default="yaml_syntax_fix_report.json",
        help="Output file for fix report",
    )

    args = parser.parse_args()

    fixer = YAMLSyntaxFixer()

    try:
        # Fix all workflow YAML
        results = fixer.fix_all_workflow_yaml()

        # Print summary
        print("\n" + "=" * 50)
        print("YAML SYNTAX FIX SUMMARY")
        print("=" * 50)

        total_workflows = results.get("total_workflows", 0)
        fixed_workflows = results.get("fixed_workflows", 0)
        print(f"Total Workflows: {total_workflows}")
        print(f"Fixed Workflows: {fixed_workflows}")

        # Show details for each workflow
        for workflow, fixes in results.get("workflow_fixes", {}).items():
            total_fixes = fixes.get("total_fixes", 0)
            print(f"\n{workflow}:")
            print(f"  Total Fixes: {total_fixes}")
            print(
                f"  Run Commands: {fixes.get('run_commands', {}).get('fixes_applied', 0)}"
            )

        print("=" * 50)

        logger.info("YAML syntax fixing complete.")

    except Exception as e:
        logger.error(f"Error in main: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
