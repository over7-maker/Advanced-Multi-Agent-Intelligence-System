#!/usr/bin/env python3
"""
Verification script for Cursor AI Integration
Tests that all components are properly configured
"""

import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent.parent

def check_file_exists(file_path: Path, description: str) -> bool:
    """Check if a file exists"""
    exists = file_path.exists()
    status = "✅" if exists else "❌"
    print(f"{status} {description}: {file_path}")
    return exists

def check_import(module: str, description: str) -> bool:
    """Check if a module can be imported"""
    try:
        __import__(module)
        print(f"✅ {description}: {module}")
        return True
    except ImportError:
        print(f"❌ {description}: {module} (not installed)")
        return False

def check_executable(file_path: Path, description: str) -> bool:
    """Check if a file is executable"""
    exists = file_path.exists()
    if not exists:
        print(f"❌ {description}: {file_path} (not found)")
        return False
    
    is_executable = file_path.stat().st_mode & 0o111
    status = "✅" if is_executable else "⚠️"
    print(f"{status} {description}: {file_path} {'(executable)' if is_executable else '(not executable)'}")
    return is_executable

def check_vscode_config() -> bool:
    """Check VS Code configuration files"""
    print("\n📁 VS Code Configuration:")
    vscode_dir = PROJECT_ROOT / ".vscode"
    
    results = []
    results.append(check_file_exists(vscode_dir / "tasks.json", "Tasks configuration"))
    results.append(check_file_exists(vscode_dir / "settings.json", "Settings configuration"))
    results.append(check_file_exists(vscode_dir / "keybindings.json", "Keybindings configuration"))
    results.append(check_file_exists(vscode_dir / "extensions.json", "Extensions configuration"))
    
    return all(results)

def check_scripts() -> bool:
    """Check AI analysis scripts"""
    print("\n🔧 AI Analysis Scripts:")
    scripts_dir = PROJECT_ROOT / ".github" / "scripts"
    
    results = []
    results.append(check_file_exists(scripts_dir / "cursor_ai_diagnostics.py", "Diagnostics script"))
    results.append(check_file_exists(scripts_dir / "ai_watch_daemon.py", "Watch daemon script"))
    results.append(check_executable(scripts_dir / "cursor_ai_diagnostics.py", "Diagnostics script"))
    results.append(check_executable(scripts_dir / "ai_watch_daemon.py", "Watch daemon script"))
    
    return all(results)

def check_dependencies() -> bool:
    """Check Python dependencies"""
    print("\n📦 Python Dependencies:")
    
    results = []
    results.append(check_import("aiohttp", "aiohttp"))
    results.append(check_import("watchdog", "watchdog"))
    
    # Check if AI router can be imported
    sys.path.insert(0, str(PROJECT_ROOT / "src"))
    try:
        from amas.ai.enhanced_router_v2 import generate_with_fallback
        print("✅ AI Router: amas.ai.enhanced_router_v2")
        results.append(True)
    except ImportError as e:
        print(f"❌ AI Router: amas.ai.enhanced_router_v2 ({e})")
        results.append(False)
    
    return all(results)

def check_git_hooks() -> bool:
    """Check Git hooks"""
    print("\n🔗 Git Hooks:")
    
    pre_commit = PROJECT_ROOT / ".git" / "hooks" / "pre-commit"
    results = []
    results.append(check_file_exists(pre_commit, "Pre-commit hook"))
    results.append(check_executable(pre_commit, "Pre-commit hook"))
    
    return all(results)

def check_documentation() -> bool:
    """Check documentation files"""
    print("\n📚 Documentation:")
    
    results = []
    results.append(check_file_exists(
        PROJECT_ROOT / ".github" / "scripts" / "CURSOR_AI_INTEGRATION_README.md",
        "Integration README"
    ))
    results.append(check_file_exists(
        PROJECT_ROOT / "CURSOR_AI_INTEGRATION_SETUP.md",
        "Setup guide"
    ))
    
    return all(results)

def test_diagnostics_script() -> bool:
    """Test that diagnostics script can run"""
    print("\n🧪 Testing Diagnostics Script:")
    
    script = PROJECT_ROOT / ".github" / "scripts" / "cursor_ai_diagnostics.py"
    
    if not script.exists():
        print("❌ Diagnostics script not found")
        return False
    
    # Test with --help or a simple test
    try:
        result = subprocess.run(
            [sys.executable, str(script), "--help"],
            capture_output=True,
            text=True,
            timeout=5
        )
        # Script should show usage (exit code 1) or work (exit code 0)
        if result.returncode in [0, 1]:
            print("✅ Diagnostics script is executable")
            return True
        else:
            print(f"⚠️ Diagnostics script returned code {result.returncode}")
            return False
    except subprocess.TimeoutExpired:
        print("⚠️ Diagnostics script test timed out")
        return False
    except Exception as e:
        print(f"⚠️ Diagnostics script test error: {e}")
        return False

def main():
    """Run all verification checks"""
    print("=" * 70)
    print("🔍 Cursor AI Integration Verification")
    print("=" * 70)
    
    checks = [
        ("VS Code Configuration", check_vscode_config),
        ("AI Analysis Scripts", check_scripts),
        ("Python Dependencies", check_dependencies),
        ("Git Hooks", check_git_hooks),
        ("Documentation", check_documentation),
        ("Script Execution", test_diagnostics_script),
    ]
    
    results = {}
    for name, check_func in checks:
        try:
            results[name] = check_func()
        except Exception as e:
            print(f"❌ Error checking {name}: {e}")
            results[name] = False
    
    # Summary
    print("\n" + "=" * 70)
    print("📊 Verification Summary")
    print("=" * 70)
    
    all_passed = True
    for name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status}: {name}")
        if not passed:
            all_passed = False
    
    print("\n" + "=" * 70)
    if all_passed:
        print("✅ All checks passed! Cursor AI Integration is ready to use.")
        print("\n🚀 Quick Start:")
        print("   1. Open any Python file")
        print("   2. Press Ctrl+Shift+A to analyze")
        print("   3. View results in Problems panel (Ctrl+Shift+M)")
        return 0
    else:
        print("❌ Some checks failed. Please review the output above.")
        print("\n💡 Common fixes:")
        print("   - Install missing dependencies: pip install watchdog aiohttp")
        print("   - Make scripts executable: chmod +x .github/scripts/*.py")
        print("   - Make pre-commit hook executable: chmod +x .git/hooks/pre-commit")
        return 1

if __name__ == "__main__":
    sys.exit(main())

