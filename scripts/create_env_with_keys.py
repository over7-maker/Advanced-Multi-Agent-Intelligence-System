#!/usr/bin/env python3
"""
Create .env file with all 15 API keys pre-filled
Automatically creates .env from .env.example with your actual keys
"""

import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent

# Your actual API keys (from GitHub Secrets)
API_KEYS = {
    "CEREBRAS_API_KEY": "csk-2feh4665p9y32jwy5etm3fkd8cfh52w4dj3t2ekd5t2yh43k",
    "NVIDIA_API_KEY": "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",
    "GROQ2_API_KEY": "gsk_q4AGPMc0aiUS2sXEVupDWGdyb3FYOVIRo uEhabWQJry9C443ejra",
    "GROQAI_API_KEY": "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",
    "DEEPSEEK_API_KEY": "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",
    "CODESTRAL_API_KEY": "2kutMTaniEaGOJXkOWBcyt9eE70ZmS4r",
    "GLM_API_KEY": "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",
    "GEMINI2_API_KEY": "AIzaSyBC1ybRkqyc2jSXAj4_2-XT5rXF7ENa0cs",
    "GROK_API_KEY": "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",
    "COHERE_API_KEY": "uBCLBBUn5BEcdBZjJOYQDMLUtTexPcbq3HQsKy22",
    "KIMI_API_KEY": "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",
    "QWEN_API_KEY": "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",
    "GPTOSS_API_KEY": "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",
    "CHUTES_API_KEY": "cpk_54cf325756a54a84a7730eb12b7a203e.d2055a9231325ba5b31b765bb0001987.EJPb6s3CY2MyOPgQtNwJAew9aic7hRHA",
}

def create_env_file():
    """Create .env file with all API keys."""
    env_file = PROJECT_ROOT / ".env"
    example_file = PROJECT_ROOT / ".env.example"
    
    # Read .env.example template
    if example_file.exists():
        with open(example_file, 'r', encoding='utf-8') as f:
            content = f.read()
    else:
        # Create basic template
        content = """# AMAS Environment Configuration
# All 15 API Keys for Maximum Reliability

"""
    
    # Replace API keys in template
    for key_name, key_value in API_KEYS.items():
        # Replace placeholder or existing value
        import re
        pattern = f"{key_name}=.*"
        replacement = f"{key_name}={key_value}"
        content = re.sub(pattern, replacement, content, flags=re.MULTILINE)
        
        # If key doesn't exist in template, add it
        if key_name not in content:
            content += f"\n{key_name}={key_value}\n"
    
    # Write .env file
    try:
        with open(env_file, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✅ Created .env file with all 15 API keys")
        print(f"   File: {env_file}")
        return True
    except Exception as e:
        print(f"❌ Failed to create .env file: {e}")
        return False

def main():
    """Main function."""
    print("=" * 70)
    print("Creating .env file with all 15 API keys...")
    print("=" * 70)
    
    env_file = PROJECT_ROOT / ".env"
    
    if env_file.exists():
        response = input(f"\n.env file already exists. Overwrite? (y/n): ").strip().lower()
        if response != 'y':
            print("❌ Aborted by user")
            return 1
    
    if create_env_file():
        print("\n✅ Success! .env file created with all 15 API keys")
        print("\n💡 Next steps:")
        print("   1. Verify .env file contains your keys")
        print("   2. Test the system: python scripts/verify_complete_setup.py")
        print("   3. Run workflows: python scripts/run_local_workflows.py --list")
        return 0
    else:
        print("\n❌ Failed to create .env file")
        return 1

if __name__ == "__main__":
    import sys
    sys.exit(main())

