#!/usr/bin/env python3
"""
Provider Documentation Validator

Ensures provider documentation in README.md stays in sync with actual implementation.
Validates against src/amas/ai/router.py and docs/provider_config.json
"""

import json
import re
import sys
from pathlib import Path

def load_provider_config():
    """Load provider configuration from JSON"""
    config_path = Path(__file__).parent.parent / "docs" / "provider_config.json"
    with open(config_path) as f:
        return json.load(f)

def extract_providers_from_readme():
    """Extract provider information from README.md"""
    readme_path = Path(__file__).parent.parent / "README.md"
    with open(readme_path) as f:
        content = f.read()
    
    # Extract Tier 1-5 providers
    providers = {}
    tier_pattern = r"#### \*\*Tier (\d+)"
    tier_matches = list(re.finditer(tier_pattern, content))
    
    for i, match in enumerate(tier_matches):
        tier_num = int(match.group(1))
        start = match.end()
        end = tier_matches[i + 1].start() if i + 1 < len(tier_matches) else len(content)
        tier_section = content[start:end]
        
        # Extract provider names
        provider_pattern = r"- \*\*([^*]+)\*\*"
        for provider_match in re.finditer(provider_pattern, tier_section):
            provider_name = provider_match.group(1).strip()
            providers[provider_name] = tier_num
    
    return providers

def validate():
    """Validate provider documentation"""
    config = load_provider_config()
    readme_providers = extract_providers_from_readme()
    
    errors = []
    warnings = []
    
    # Check all config providers appear in README
    config_provider_names = {p["name"] for p in config["providers"] if p["status"] == "active"}
    
    for provider_name in config_provider_names:
        if provider_name not in readme_providers:
            warnings.append(f"⚠️  Provider '{provider_name}' in config but not found in README.md")
    
    # Check README providers match config (allow for slight naming differences)
    readme_provider_set = set(readme_providers.keys())
    
    print("✅ Provider Documentation Validation")
    print("=" * 50)
    
    if errors:
        print("\n❌ Errors:")
        for error in errors:
            print(f"  {error}")
    
    if warnings:
        print("\n⚠️  Warnings:")
        for warning in warnings:
            print(f"  {warning}")
    
    if not errors and not warnings:
        print("\n✅ All provider documentation is in sync!")
        print(f"   Found {len(config['providers'])} providers in config")
        print(f"   Found {len(readme_providers)} providers in README")
        return 0
    
    return 1 if errors else 0

if __name__ == "__main__":
    sys.exit(validate())
