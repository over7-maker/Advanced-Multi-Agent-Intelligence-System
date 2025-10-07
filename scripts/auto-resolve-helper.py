#!/usr/bin/env python3
"""
Automated helper for resolving specific types of merge conflicts in PR #157
This handles common patterns but requires manual review
"""

import os
import re
import sys
from pathlib import Path
from typing import List, Optional, Tuple


class ConflictResolver:
    def __init__(self):
        self.conflict_pattern = re.compile(r"<<<<<<<.*?=======.*?>>>>>>>", re.DOTALL)
        self.import_pattern = re.compile(
            r"^\s*(from\s+[\w\.]+\s+import\s+.*|import\s+[\w\.]+.*)", re.MULTILINE
        )

    def find_conflicts(self, content: str) -> List[str]:
        """Find all conflict blocks in content"""
        return self.conflict_pattern.findall(content)

    def extract_imports_from_conflict(self, conflict_block: str) -> Tuple[set, set]:
        """Extract imports from both sides of a conflict"""
        parts = conflict_block.split("=======")
        if len(parts) != 2:
            return set(), set()

        head_part = parts[0].replace("<<<<<<< HEAD", "")
        branch_part = parts[1].split(">>>>>>>")[0]

        head_imports = set(self.import_pattern.findall(head_part))
        branch_imports = set(self.import_pattern.findall(branch_part))

        return head_imports, branch_imports

    def merge_imports(self, head_imports: set, branch_imports: set) -> List[str]:
        """Merge and sort imports from both branches"""
        all_imports = head_imports.union(branch_imports)

        # Separate standard library, third-party, and local imports
        stdlib = []
        third_party = []
        local = []

        for imp in sorted(all_imports):
            imp = imp.strip()
            if imp.startswith("import ") and "." not in imp.split()[1]:
                stdlib.append(imp)
            elif imp.startswith("from amas"):
                local.append(imp)
            else:
                third_party.append(imp)

        # Combine with proper spacing
        result = []
        if stdlib:
            result.extend(sorted(stdlib))
            result.append("")
        if third_party:
            result.extend(sorted(third_party))
            result.append("")
        if local:
            result.extend(sorted(local))

        return result

    def resolve_init_file(self, filepath: str) -> Optional[str]:
        """Special handling for __init__.py files"""
        try:
            with open(filepath, "r") as f:
                content = f.read()

            conflicts = self.find_conflicts(content)
            if not conflicts:
                print(f"No conflicts found in {filepath}")
                return None

            # For __init__.py files, we mainly care about imports and __all__
            resolved_content = content

            for conflict in conflicts:
                # Check if this conflict is about imports
                if "import" in conflict or "__all__" in conflict:
                    head_imports, branch_imports = self.extract_imports_from_conflict(
                        conflict
                    )

                    if head_imports or branch_imports:
                        merged_imports = self.merge_imports(
                            head_imports, branch_imports
                        )
                        replacement = "\n".join(merged_imports)
                        resolved_content = resolved_content.replace(
                            conflict, replacement
                        )
                        print(
                            f"Merged {len(head_imports)} + {len(branch_imports)} imports"
                        )

                    # Handle __all__ exports
                    if "__all__" in conflict:
                        # Extract all quoted strings from both sides
                        all_exports = set()
                        for match in re.findall(r'["\'](\w+)["\']', conflict):
                            all_exports.add(match)

                        if all_exports:
                            all_list = "__all__ = [\n"
                            for export in sorted(all_exports):
                                all_list += f'    "{export}",\n'
                            all_list += "]"

                            # Replace the conflict with merged __all__
                            resolved_content = resolved_content.replace(
                                conflict, all_list
                            )

            return resolved_content

        except Exception as e:
            print(f"Error processing {filepath}: {e}")
            return None

    def show_task_structure_example(self):
        """Show the correct task structure from PR #157"""
        print("\n" + "=" * 60)
        print("IMPORTANT: Task Structure Changes in PR #157")
        print("=" * 60)
        print("\nOLD structure (main branch):")
        print(
            """
task = await orchestrator.submit_task(
    title="Task Title",
    description="Task Description",
    parameters={"key": "value"},
    priority="high"
)
"""
        )
        print("\nNEW structure (PR #157):")
        print(
            """
from amas.core.unified_orchestrator_v2 import TaskPriority

task = await orchestrator.submit_task(
    description="Task Description",
    task_type="task_type",
    priority=TaskPriority.HIGH,  # Use enum!
    metadata={
        "title": "Task Title",
        "parameters": {"key": "value"},
        "required_agent_roles": ["agent_role"]
    }
)
"""
        )
        print("\n⚠️  ALWAYS use the NEW structure in resolved conflicts!")
        print("=" * 60 + "\n")


def main():
    if len(sys.argv) < 2:
        print("Usage: python auto-resolve-helper.py <command> [file]")
        print("\nCommands:")
        print("  show-structure    - Show correct task structure")
        print("  resolve-imports   - Resolve import conflicts in a file")
        print("  check            - Check for remaining conflicts")
        return

    resolver = ConflictResolver()
    command = sys.argv[1]

    if command == "show-structure":
        resolver.show_task_structure_example()

    elif command == "resolve-imports" and len(sys.argv) > 2:
        filepath = sys.argv[2]
        if "__init__.py" in filepath:
            resolved = resolver.resolve_init_file(filepath)
            if resolved:
                # Save to a .resolved file for review
                output_path = filepath + ".resolved"
                with open(output_path, "w") as f:
                    f.write(resolved)
                print(f"Resolved imports saved to: {output_path}")
                print("Review the file and if correct, copy it over:")
                print(f"  cp {output_path} {filepath}")
        else:
            print("This command currently only handles __init__.py files")

    elif command == "check":
        # Check for remaining conflicts in Python files
        conflict_files = []
        for root, dirs, files in os.walk("src"):
            for file in files:
                if file.endswith(".py"):
                    filepath = os.path.join(root, file)
                    try:
                        with open(filepath, "r") as f:
                            if "<<<<<<<" in f.read():
                                conflict_files.append(filepath)
                    except:
                        pass

        if conflict_files:
            print("Files still containing conflicts:")
            for f in conflict_files:
                print(f"  - {f}")
        else:
            print("No conflict markers found in Python files!")

    else:
        print(f"Unknown command: {command}")


if __name__ == "__main__":
    main()
