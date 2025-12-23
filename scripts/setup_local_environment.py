#!/usr/bin/env python3
"""
Local Development Environment Setup
Sets up the complete local development environment matching GitHub Actions.
"""

import os
import sys
import subprocess
from pathlib import Path
from typing import List, Tuple

PROJECT_ROOT = Path(__file__).parent.parent

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
    except subprocess.CalledProcessError as e:
        return e.returncode, e.stdout, e.stderr
    except Exception as e:
        return 1, "", str(e)

def check_python_version() -> bool:
    """Check if Python version is compatible."""
    print("🐍 Checking Python version...")
    version = sys.version_info
    print(f"   Python {version.major}.{version.minor}.{version.micro}")
    
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Python 3.8+ required!")
        return False
    
    if version.major == 3 and version.minor >= 11:
        print("✅ Python version is excellent (3.11+)")
    else:
        print("✅ Python version is compatible")
    
    return True

def upgrade_pip() -> bool:
    """Upgrade pip to latest version."""
    print("\n📦 Upgrading pip...")
    returncode, stdout, stderr = run_command(
        [sys.executable, "-m", "pip", "install", "--upgrade", "pip", "setuptools", "wheel"],
        check=False
    )
    
    if returncode == 0:
        print("✅ pip upgraded successfully")
        return True
    else:
        print(f"⚠️  Warning: pip upgrade had issues: {stderr}")
        return False

def install_requirements() -> bool:
    """Install project requirements."""
    print("\n📦 Installing project dependencies...")
    requirements_file = PROJECT_ROOT / "requirements.txt"
    
    if not requirements_file.exists():
        print(f"❌ requirements.txt not found at {requirements_file}")
        return False
    
    # Try to install with binary wheels first
    print("   Attempting installation with binary wheels...")
    returncode, stdout, stderr = run_command(
        [sys.executable, "-m", "pip", "install", "--prefer-binary", "-r", str(requirements_file)],
        check=False
    )
    
    if returncode == 0:
        print("✅ Dependencies installed successfully")
        return True
    else:
        print(f"⚠️  Binary wheel installation had issues, trying regular install...")
        returncode2, stdout2, stderr2 = run_command(
            [sys.executable, "-m", "pip", "install", "-r", str(requirements_file)],
            check=False
        )
        
        if returncode2 == 0:
            print("✅ Dependencies installed (some packages may need compilation)")
            return True
        else:
            print(f"❌ Failed to install dependencies: {stderr2}")
            return False

def create_env_file() -> bool:
    """Create .env file template if it doesn't exist."""
    print("\n📝 Checking environment configuration...")
    env_file = PROJECT_ROOT / ".env"
    
    if env_file.exists():
        print("✅ .env file already exists")
        return True
    
    # Create template
    template = """# AMAS Environment Configuration
# Copy this file and fill in your API keys
# These keys are also stored in GitHub Secrets for GitHub Actions
# All 16 API Keys for Maximum Reliability

# Tier 1 - Premium Speed & Quality (Direct APIs)
CEREBRAS_API_KEY=your_cerebras_key_here
NVIDIA_API_KEY=your_nvidia_key_here
GROQAI_API_KEY=your_groqai_key_here

# Tier 2 - High Quality (OpenRouter Primary & Direct)
DEEPSEEK_API_KEY=your_deepseek_key_here
GLM_API_KEY=your_glm_key_here
GROK_API_KEY=your_grok_key_here
GEMINIAI_API_KEY=your_gemini_key_here
GEMINI2_API_KEY=your_gemini2_key_here

# Tier 3 - Commercial & Specialized
CLAUDE_API_KEY=your_claude_key_here
GPT4_API_KEY=your_gpt4_key_here
CODESTRAL_API_KEY=your_codestral_key_here
COHERE_API_KEY=your_cohere_key_here

# Tier 4 - OpenRouter Free Tier (Secondary)
KIMI_API_KEY=your_kimi_key_here
QWEN_API_KEY=your_qwen_key_here
GPTOSS_API_KEY=your_gptoss_key_here
GROQ2_API_KEY=your_groq2_key_here
CHUTES_API_KEY=your_chutes_key_here

# Security Configuration
JWT_SECRET_KEY=change_this_to_a_secure_random_string
ENCRYPTION_KEY=change_this_to_a_secure_random_string
AMAS_JWT_SECRET=change_this_to_a_secure_random_string
AMAS_ENCRYPTION_KEY=change_this_to_a_secure_random_string

# Optional Configuration
RATE_LIMIT_ENABLED=true
AUDIT_LOGGING=true
AMAS_AUDIT_ENABLED=true

# Redis Configuration (if using session management)
AMAS_REDIS_HOST=localhost
AMAS_REDIS_PORT=6379
AMAS_REDIS_PASSWORD=

# OIDC Configuration (if using OIDC)
AMAS_OIDC_CLIENT_ID=
AMAS_OIDC_CLIENT_SECRET=
"""
    
    try:
        with open(env_file, 'w') as f:
            f.write(template)
        print("✅ Created .env template file")
        print("   ⚠️  Please edit .env and add your API keys!")
        return True
    except Exception as e:
        print(f"❌ Failed to create .env file: {e}")
        return False

def verify_scripts() -> bool:
    """Verify that required scripts exist."""
    print("\n🔍 Verifying required scripts...")
    scripts_dir = PROJECT_ROOT / ".github" / "scripts"
    
    if not scripts_dir.exists():
        print(f"❌ Scripts directory not found: {scripts_dir}")
        return False
    
    required_scripts = [
        "enhanced_code_quality_inspector.py",
        "ai_master_orchestrator.py",
        "enhanced_automated_fixer.py",
        "multi_agent_orchestrator.py",
        "comprehensive_audit_engine.py",
    ]
    
    missing = []
    for script in required_scripts:
        script_path = scripts_dir / script
        if not script_path.exists():
            missing.append(script)
        else:
            print(f"   ✅ {script}")
    
    if missing:
        print(f"\n⚠️  Missing scripts: {', '.join(missing)}")
        return False
    
    print("✅ All required scripts found")
    return True

def run_basic_test() -> bool:
    """Run a basic test to verify installation."""
    print("\n🧪 Running basic installation test...")
    
    # Try importing key modules
    test_code = """
import sys
import io
# Set UTF-8 encoding for Windows
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

errors = []

try:
    import fastapi
    print("[OK] FastAPI imported")
except ImportError as e:
    errors.append(f"FastAPI: {e}")

try:
    import openai
    print("[OK] OpenAI imported")
except ImportError as e:
    errors.append(f"OpenAI: {e}")

try:
    import yaml
    print("[OK] PyYAML imported")
except ImportError as e:
    errors.append(f"PyYAML: {e}")

if errors:
    print("\\n[ERROR] Import errors:")
    for error in errors:
        print(f"   {error}")
    sys.exit(1)
else:
    print("\\n[SUCCESS] All basic imports successful!")
"""
    
    returncode, stdout, stderr = run_command(
        [sys.executable, "-c", test_code],
        check=False
    )
    
    print(stdout)
    if stderr:
        print(stderr)
    
    return returncode == 0

def main():
    """Main setup function."""
    print("=" * 60)
    print("🚀 AMAS Local Development Environment Setup")
    print("=" * 60)
    
    success = True
    
    # Step 1: Check Python version
    if not check_python_version():
        print("\n❌ Setup failed: Python version incompatible")
        sys.exit(1)
    
    # Step 2: Upgrade pip
    upgrade_pip()
    
    # Step 3: Install requirements
    if not install_requirements():
        print("\n⚠️  Warning: Some dependencies may not have installed correctly")
        print("   You may need to install them manually")
        success = False
    
    # Step 4: Create .env file
    create_env_file()
    
    # Step 5: Verify scripts
    if not verify_scripts():
        print("\n⚠️  Warning: Some required scripts are missing")
        success = False
    
    # Step 6: Run basic test
    if not run_basic_test():
        print("\n⚠️  Warning: Basic test had issues")
        success = False
    
    # Summary
    print("\n" + "=" * 60)
    if success:
        print("✅ Setup completed successfully!")
    else:
        print("⚠️  Setup completed with warnings")
    
    print("\n💡 Next steps:")
    print("   1. Edit .env file and add your API keys")
    print("   2. Sync from GitHub: python scripts/sync_from_github.py")
    print("   3. Test workflows: python scripts/run_local_workflows.py --list")
    print("   4. Run a workflow: python scripts/run_local_workflows.py 00-master-ai-orchestrator.yml")
    print("=" * 60)

if __name__ == "__main__":
    main()

