#!/usr/bin/env python3
"""
AMAS Environment Validation Script
Validates configuration and provides setup guidance
"""

import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from amas.config.minimal_config import (
    get_config_manager,
    print_setup_instructions,
    validate_setup,
)


def main():
    """Main validation function"""
    print("🔍 AMAS Environment Validation")
    print("=" * 50)

    # Get configuration manager
    config_manager = get_config_manager()

    # Show current configuration
    config = config_manager.get_config()
    print(f"Configuration Level: {config.config_level.value.upper()}")
    print(f"Available Providers: {len(config.available_providers)}")
    print()

    # Show available providers
    if config.available_providers:
        print("✅ Available Providers:")
        for provider in config.available_providers:
            print(f"  • {provider.name} (Priority: {provider.priority})")
    else:
        print("❌ No providers configured")

    print()

    # Validate configuration
    validation = validate_setup()

    if validation["valid"]:
        print("✅ Configuration is VALID")
    else:
        print("❌ Configuration is INVALID")

    # Show warnings
    if validation["warnings"]:
        print("\n⚠️  Warnings:")
        for warning in validation["warnings"]:
            print(f"  • {warning}")

    # Show errors
    if validation["errors"]:
        print("\n❌ Errors:")
        for error in validation["errors"]:
            print(f"  • {error}")

    print()

    # Show feature status
    print("🔧 Available Features:")
    features = config_manager.get_feature_status()
    for feature, available in features["features"].items():
        status = "✅" if available else "❌"
        print(f"  {status} {feature.replace('_', ' ').title()}")

    print()

    # Show recommendations
    if features["recommendations"]:
        print("💡 Recommendations:")
        for rec in features["recommendations"]:
            print(f"  • {rec}")

    print()

    # Show setup instructions if needed
    if not validation["valid"] or config.config_level.value == "minimal":
        print_setup_instructions()

    # Return appropriate exit code
    return 0 if validation["valid"] else 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
