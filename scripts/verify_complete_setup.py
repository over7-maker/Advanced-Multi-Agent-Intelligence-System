#!/usr/bin/env python3
"""
Complete Setup Verification Script
Verifies that everything is set up correctly for local and GitHub development.
"""

import os
import sys
import subprocess
import json
from pathlib import Path
from typing import Dict, List, Tuple, Optional

PROJECT_ROOT = Path(__file__).parent.parent

# Windows encoding fix
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

def run_command(cmd: List[str], check: bool = False) -> Tuple[int, str, str]:
    """Run a shell command."""
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=check,
            cwd=PROJECT_ROOT
        )
        return result.returncode, result.stdout, result.stderr
    except Exception as e:
        return 1, "", str(e)

def check_python_version() -> Tuple[bool, str]:
    """Check Python version."""
    version = sys.version_info
    version_str = f"{version.major}.{version.minor}.{version.micro}"
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        return False, f"Python {version_str} (3.8+ required)"
    return True, f"Python {version_str}"

def check_dependencies() -> Tuple[bool, List[str]]:
    """Check if key dependencies are installed."""
    required = ['fastapi', 'openai', 'yaml', 'pydantic', 'requests']
    missing = []
    
    for dep in required:
        try:
            if dep == 'yaml':
                __import__('yaml')
            else:
                __import__(dep)
        except ImportError:
            missing.append(dep)
    
    return len(missing) == 0, missing

def check_env_file() -> Tuple[bool, Optional[str]]:
    """Check if .env file exists and has content."""
    env_file = PROJECT_ROOT / ".env"
    if not env_file.exists():
        return False, ".env file not found"
    
    with open(env_file, 'r') as f:
        content = f.read()
        if 'API_KEY' not in content or 'your_' in content:
            return False, ".env file exists but not configured"
    
    return True, ".env file configured"

def check_git_repo() -> Tuple[bool, str]:
    """Check git repository status."""
    returncode, _, _ = run_command(["git", "status"], check=False)
    if returncode != 0:
        return False, "Not a git repository"
    
    returncode, stdout, _ = run_command(["git", "remote", "-v"], check=False)
    if returncode != 0 or "github.com" not in stdout.lower():
        return False, "GitHub remote not configured"
    
    return True, "Git repository configured"

def check_workflow_files() -> Tuple[bool, List[str]]:
    """Check if workflow files exist."""
    workflows_dir = PROJECT_ROOT / ".github" / "workflows"
    if not workflows_dir.exists():
        return False, []
    
    workflows = list(workflows_dir.glob("*.yml")) + list(workflows_dir.glob("*.yaml"))
    if len(workflows) == 0:
        return False, []
    
    return True, [w.name for w in workflows]

def check_scripts() -> Tuple[bool, List[str]]:
    """Check if required scripts exist."""
    scripts_dir = PROJECT_ROOT / "scripts"
    required = [
        "setup_local_environment.py",
        "sync_from_github.py",
        "sync_to_github.py",
        "run_local_workflows.py"
    ]
    
    missing = []
    for script in required:
        if not (scripts_dir / script).exists():
            missing.append(script)
    
    return len(missing) == 0, missing

def check_github_scripts() -> Tuple[bool, List[str]]:
    """Check if GitHub scripts exist."""
    scripts_dir = PROJECT_ROOT / ".github" / "scripts"
    if not scripts_dir.exists():
        return False, []
    
    required = [
        "enhanced_code_quality_inspector.py",
        "ai_master_orchestrator.py",
        "enhanced_automated_fixer.py",
        "multi_agent_orchestrator.py",
        "comprehensive_audit_engine.py"
    ]
    
    missing = []
    for script in required:
        if not (scripts_dir / script).exists():
            missing.append(script)
    
    return len(missing) == 0, missing

def check_network_connection() -> Tuple[bool, str]:
    """Check if GitHub is reachable."""
    returncode, _, _ = run_command(["git", "fetch", "origin", "--dry-run"], check=False)
    if returncode == 0:
        return True, "GitHub reachable"
    return False, "GitHub not reachable (network issue)"

def run_verification() -> Dict:
    """Run complete verification."""
    results = {
        "python_version": {},
        "dependencies": {},
        "env_file": {},
        "git_repo": {},
        "workflows": {},
        "scripts": {},
        "github_scripts": {},
        "network": {}
    }
    
    # Python version
    ok, msg = check_python_version()
    results["python_version"] = {"ok": ok, "message": msg}
    
    # Dependencies
    ok, missing = check_dependencies()
    if ok:
        results["dependencies"] = {"ok": True, "message": "All dependencies installed"}
    else:
        results["dependencies"] = {"ok": False, "message": f"Missing: {', '.join(missing)}"}
    
    # .env file
    ok, msg = check_env_file()
    results["env_file"] = {"ok": ok, "message": msg}
    
    # Git repo
    ok, msg = check_git_repo()
    results["git_repo"] = {"ok": ok, "message": msg}
    
    # Workflows
    ok, workflows = check_workflow_files()
    if ok:
        results["workflows"] = {"ok": True, "message": f"Found {len(workflows)} workflows"}
    else:
        results["workflows"] = {"ok": False, "message": "No workflow files found"}
    
    # Scripts
    ok, missing = check_scripts()
    if ok:
        results["scripts"] = {"ok": True, "message": "All scripts present"}
    else:
        results["scripts"] = {"ok": False, "message": f"Missing: {', '.join(missing)}"}
    
    # GitHub scripts
    ok, missing = check_github_scripts()
    if ok:
        results["github_scripts"] = {"ok": True, "message": "All GitHub scripts present"}
    else:
        results["github_scripts"] = {"ok": False, "message": f"Missing: {', '.join(missing)}"}
    
    # Network
    ok, msg = check_network_connection()
    results["network"] = {"ok": ok, "message": msg}
    
    return results

def print_results(results: Dict):
    """Print verification results."""
    print("=" * 70)
    print("COMPLETE SETUP VERIFICATION")
    print("=" * 70)
    
    status_symbol = "[OK]" if results["ok"] else "[FAIL]"
    print(f"\nOverall Status: {status_symbol}")
    
    print("\n" + "-" * 70)
    print("DETAILED RESULTS:")
    print("-" * 70)
    
    checks = [
        ("Python Version", "python_version"),
        ("Dependencies", "dependencies"),
        ("Environment File", "env_file"),
        ("Git Repository", "git_repo"),
        ("Workflow Files", "workflows"),
        ("Sync Scripts", "scripts"),
        ("GitHub Scripts", "github_scripts"),
        ("Network Connection", "network")
    ]
    
    for name, key in checks:
        result = results[key]
        symbol = "[OK]" if result["ok"] else "[FAIL]"
        print(f"{symbol} {name}: {result['message']}")
    
    print("\n" + "=" * 70)

def main():
    """Main verification function."""
    results = run_verification()
    
    # Calculate overall status
    all_ok = all(
        results[key]["ok"] 
        for key in ["python_version", "dependencies", "git_repo", "workflows", "scripts", "github_scripts"]
    )
    results["ok"] = all_ok
    
    print_results(results)
    
    # Save results
    results_file = PROJECT_ROOT / "setup_verification_results.json"
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n[INFO] Results saved to: {results_file.name}")
    
    # Recommendations
    print("\n" + "=" * 70)
    print("RECOMMENDATIONS:")
    print("=" * 70)
    
    if not results["dependencies"]["ok"]:
        print("\n[ACTION] Install missing dependencies:")
        print("   python scripts/setup_local_environment.py")
        print("   OR")
        print("   pip install -r requirements.txt")
    
    if not results["env_file"]["ok"]:
        print("\n[ACTION] Configure environment variables:")
        print("   1. Edit .env file")
        print("   2. Add your API keys (at least 3 recommended)")
    
    if not results["network"]["ok"]:
        print("\n[INFO] Network connection to GitHub unavailable")
        print("   - Local development still works")
        print("   - Sync when network is available")
    
    if all_ok:
        print("\n[SUCCESS] All critical checks passed!")
        print("\nNext steps:")
        print("   1. python scripts/sync_from_github.py  # Sync from GitHub")
        print("   2. python scripts/run_local_workflows.py --list  # List workflows")
        print("   3. python scripts/run_local_workflows.py 00-master-ai-orchestrator.yml  # Test workflow")
    else:
        print("\n[ACTION] Fix the issues above before proceeding")
    
    print("\n" + "=" * 70)
    
    return 0 if all_ok else 1

if __name__ == "__main__":
    sys.exit(main())


