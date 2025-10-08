#!/usr/bin/env python3
"""

AMAS Environment Validation Script
Validates API keys and provider configuration
"""

import json
import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from amas.providers.manager import provider_manager, validate_environment


def main():
    """Main validation function"""

    print("🔍 AMAS Environment Validation")
    print("=" * 50)

    try:
        # Validate environment
        result = validate_environment()

        # Print results
        print(f"\n📊 Validation Results:")
        print(f"  Valid: {'✅ Yes' if result['valid'] else '❌ No'}")
        print(f"  Enabled Providers: {result['enabled_providers']}")
        print(f"  Total Configured: {result['total_configured']}")

        if result["missing_required"]:
            print(f"\n❌ Missing Required Providers:")
            for provider in result["missing_required"]:
                print(f"  - {provider}")

        if result["warnings"]:
            print(f"\n⚠️ Warnings:")
            for warning in result["warnings"]:
                print(f"  - {warning}")

        if result["recommendations"]:
            print(f"\n💡 Recommendations:")
            for rec in result["recommendations"]:
                print(f"  - {rec}")

        # Show provider status
        print(f"\n📋 Provider Status:")
        status = provider_manager.get_provider_status()

        for name, info in status.items():
            if info["available"]:
                icon = "✅"
                status_text = "ENABLED"
            elif info["status"] == "missing_key":
                icon = "✖️"
                status_text = "MISSING KEY"
            else:
                icon = "❌"
                status_text = info["status"].upper()

            print(f"  {icon} {name:15} {status_text:12} (Priority: {info['priority']})")

        # Show environment variables (without values)
        print(f"\n🔑 Environment Variables:")
        env_vars = [
            "OPENAI_API_KEY",
            "GEMINIAI_API_KEY",
            "GROQAI_API_KEY",
            "COHERE_API_KEY",
            "ANTHROPIC_API_KEY",
            "HUGGINGFACE_API_KEY",
            "NVIDIAAI_API_KEY",
            "REPLICATE_API_KEY",
            "TOGETHERAI_API_KEY",
            "PERPLEXITY_API_KEY",
            "DEEPSEEK_API_KEY",
            "MISTRALAI_API_KEY",
            "OLLAMA_API_KEY",
            "LOCALAI_API_KEY",
            "CUSTOM_API_KEY",
        ]

        for var in env_vars:
            value = os.getenv(var)
            if value:
                # Show only first 8 characters for security
                masked = value[:8] + "..." if len(value) > 8 else "***"
                print(f"  ✅ {var:20} = {masked}")
            else:
                print(f"  ✖️ {var:20} = (not set)")

        # Quick start instructions
        print(f"\n🚀 Quick Start Instructions:")
        if not result["valid"]:
            print("  1. Copy .env.example to .env")
            print("  2. Add at least 2-3 API keys from the list above")
            print("  3. Run this script again to validate")
        else:
            print("  ✅ Your environment is properly configured!")
            print("  ✅ You can now run: python -m amas")

        # Exit with appropriate code
        sys.exit(0 if result["valid"] else 1)

    except Exception as e:
        print(f"❌ Validation failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
