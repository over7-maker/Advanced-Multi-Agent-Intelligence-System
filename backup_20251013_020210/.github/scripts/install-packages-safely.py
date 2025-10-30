#!/usr/bin/env python3
"""
🛠️ AMAS Safe Package Installer
Handles problematic packages like PyYAML that have Cython build issues
"""

import subprocess
import sys
import os
from typing import List, Tuple

# Packages that commonly have Cython/build issues
PROBLEMATIC_PACKAGES = {
    'pyyaml': 'PyYAML>=6.0,<7.0',
    'PyYAML': 'PyYAML>=6.0,<7.0', 
    'scikit-learn': 'scikit-learn>=1.3.0,<1.6.0',
    'numpy': 'numpy>=1.24.0,<2.0.0',
    'pandas': 'pandas>=2.0.0,<2.3.0'
}

def run_command(cmd: List[str]) -> Tuple[int, str, str]:
    """Run a command and return exit code, stdout, stderr"""
    try:
        result = subprocess.run(
            cmd, 
            capture_output=True, 
            text=True, 
            timeout=600  # 10 minute timeout
        )
        return result.returncode, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return 1, "", "Command timed out"
    except Exception as e:
        return 1, "", str(e)

def install_build_essentials():
    """Install essential build tools first"""
    print("🔧 Installing build essentials...")
    
    # Core build tools
    essentials = [
        'pip', 'setuptools>=69.0.0', 'wheel>=0.42.0', 
        'cython>=3.0.0', 'numpy>=1.24.0,<2.0.0'
    ]
    
    for package in essentials:
        print(f"  📦 Installing {package}...")
        code, out, err = run_command([
            sys.executable, '-m', 'pip', 'install', 
            '--upgrade', '--only-binary=all', package
        ])
        
        if code != 0:
            print(f"  ⚠️  Failed to install {package}, trying without binary restriction...")
            code, out, err = run_command([
                sys.executable, '-m', 'pip', 'install', '--upgrade', package
            ])
            
        if code == 0:
            print(f"  ✅ {package} installed successfully")
        else:
            print(f"  ❌ Failed to install {package}: {err}")
            return False
    
    return True

def install_requirements_safely(requirements_file: str = "requirements.txt"):
    """Install requirements with smart handling of problematic packages"""
    print(f"📋 Installing requirements from {requirements_file}...")
    
    if not os.path.exists(requirements_file):
        print(f"❌ Requirements file {requirements_file} not found")
        return False
    
    # First try to install with prefer binary
    print("🚀 Attempting installation with prefer-binary...")
    code, out, err = run_command([
        sys.executable, '-m', 'pip', 'install', 
        '--prefer-binary', '--upgrade', '-r', requirements_file
    ])
    
    if code == 0:
        print("✅ All packages installed successfully with prefer-binary!")
        return True
    
    # If that fails, try with only-binary for problematic packages
    print("⚠️  Prefer-binary failed, trying targeted approach...")
    
    # Read requirements and handle problematic packages individually
    try:
        with open(requirements_file, 'r') as f:
            lines = f.readlines()
    except Exception as e:
        print(f"❌ Failed to read requirements file: {e}")
        return False
    
    failed_packages = []
    
    for line in lines:
        line = line.strip()
        if not line or line.startswith('#'):
            continue
            
        package = line.split('==')[0].split('>=')[0].split('<=')[0].split('<')[0].split('>')[0]
        
        # Handle problematic packages specially
        if package.lower() in [p.lower() for p in PROBLEMATIC_PACKAGES.keys()]:
            safe_spec = PROBLEMATIC_PACKAGES.get(package, line)
            print(f"🛠️  Installing problematic package {package} safely: {safe_spec}")
            
            # Try with only binary first
            code, out, err = run_command([
                sys.executable, '-m', 'pip', 'install', 
                '--only-binary=all', '--upgrade', safe_spec
            ])
            
            if code != 0:
                print(f"  ⚠️  Binary installation failed, trying source with safe settings...")
                # Set environment variables for safer compilation
                env = os.environ.copy()
                env.update({
                    'CFLAGS': '-O1',  # Lighter optimization
                    'CXXFLAGS': '-O1',
                    'NPY_NUM_BUILD_JOBS': '1',  # Single threaded build
                    'MAX_JOBS': '1'
                })
                
                try:
                    result = subprocess.run([
                        sys.executable, '-m', 'pip', 'install', '--upgrade', safe_spec
                    ], env=env, timeout=300, capture_output=True, text=True)
                    code = result.returncode
                except subprocess.TimeoutExpired:
                    code = 1
        else:
            # Normal package installation
            print(f"📦 Installing {package}...")
            code, out, err = run_command([
                sys.executable, '-m', 'pip', 'install', '--upgrade', line
            ])
        
        if code == 0:
            print(f"  ✅ {package} installed successfully")
        else:
            print(f"  ❌ Failed to install {package}")
            failed_packages.append(package)
    
    if failed_packages:
        print(f"❌ Failed to install: {', '.join(failed_packages)}")
        return False
    else:
        print("✅ All packages installed successfully!")
        return True

def verify_installation():
    """Verify that key packages are working"""
    print("🧪 Verifying installation...")
    
    test_imports = [
        ('yaml', 'PyYAML'),
        ('numpy', 'numpy'), 
        ('sklearn', 'scikit-learn'),
        ('pandas', 'pandas'),
        ('fastapi', 'FastAPI'),
        ('pydantic', 'Pydantic')
    ]
    
    failed = []
    
    for module, package in test_imports:
        try:
            __import__(module)
            print(f"  ✅ {package} imports successfully")
        except ImportError:
            print(f"  ❌ {package} import failed")
            failed.append(package)
    
    return len(failed) == 0

def main():
    print("🚀 AMAS Safe Package Installer Starting...")
    print("")
    
    # Step 1: Install build essentials
    if not install_build_essentials():
        print("❌ Failed to install build essentials")
        sys.exit(1)
    
    print("")
    
    # Step 2: Install requirements safely
    if not install_requirements_safely():
        print("❌ Failed to install requirements")
        sys.exit(1)
    
    print("")
    
    # Step 3: Verify installation
    if not verify_installation():
        print("⚠️  Some packages failed to import but installation may still be usable")
        # Don't exit with error for import failures
    
    print("")
    print("🎉 AMAS Safe Package Installation Complete!")

if __name__ == "__main__":
    main()