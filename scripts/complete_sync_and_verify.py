#!/usr/bin/env python3
"""
Complete Sync and Verification Script
Performs complete synchronization and verification of local and GitHub setup.
"""

import os
import sys
import subprocess
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent

# Windows encoding fix
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

def run_script(script_name: str) -> bool:
    """Run a Python script and return success status."""
    script_path = PROJECT_ROOT / "scripts" / script_name
    if not script_path.exists():
        print(f"[ERROR] Script not found: {script_name}")
        return False
    
    print(f"\n{'='*70}")
    print(f"Running: {script_name}")
    print(f"{'='*70}")
    
    try:
        result = subprocess.run(
            [sys.executable, str(script_path)],
            cwd=PROJECT_ROOT,
            capture_output=False
        )
        return result.returncode == 0
    except Exception as e:
        print(f"[ERROR] Failed to run {script_name}: {e}")
        return False

def main():
    """Complete sync and verification process."""
    print("=" * 70)
    print("COMPLETE SYNC AND VERIFICATION")
    print("=" * 70)
    print("\nThis script will:")
    print("  1. Verify current setup")
    print("  2. Sync from GitHub (if network available)")
    print("  3. Run final verification")
    print("\nStarting process...\n")
    
    # Step 1: Verify setup
    print("\n[STEP 1/3] Verifying current setup...")
    if not run_script("verify_complete_setup.py"):
        print("\n[WARNING] Verification found issues. Continuing anyway...")
    
    # Step 2: Sync from GitHub
    print("\n[STEP 2/3] Syncing from GitHub...")
    response = input("Sync from GitHub now? (y/n): ").strip().lower()
    if response == 'y':
        if not run_script("sync_from_github.py"):
            print("\n[WARNING] GitHub sync had issues (may be network related)")
    else:
        print("[SKIP] Skipping GitHub sync")
    
    # Step 3: Final verification
    print("\n[STEP 3/3] Final verification...")
    if not run_script("verify_complete_setup.py"):
        print("\n[WARNING] Final verification found issues")
        print("[INFO] Review the issues above and fix as needed")
    else:
        print("\n[SUCCESS] All verifications passed!")
    
    print("\n" + "=" * 70)
    print("SYNC AND VERIFICATION COMPLETE")
    print("=" * 70)
    print("\nYour local environment is ready for development!")
    print("\nQuick commands:")
    print("  python scripts/sync_from_github.py    # Pull latest changes")
    print("  python scripts/sync_to_github.py      # Push local changes")
    print("  python scripts/run_local_workflows.py --list  # List workflows")
    print("=" * 70)

if __name__ == "__main__":
    main()


