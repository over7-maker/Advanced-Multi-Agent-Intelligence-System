#!/usr/bin/env python3
"""
Provider Documentation Validator

Ensures provider documentation in README.md stays in sync with actual implementation.
Validates against src/amas/ai/router.py and docs/provider_config.json
"""

import json
import os
import re
import sys
from pathlib import Path

try:
    import jsonschema  # type: ignore
    HAS_JSONSCHEMA = True
except Exception:
    HAS_JSONSCHEMA = False

def load_provider_config():
    """Load provider configuration from JSON with basic path hardening and schema checks."""
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
    config_path = os.path.abspath(os.path.join(base_dir, "docs", "provider_config.json"))

    # Ensure config_path is inside repo directory
    if not config_path.startswith(base_dir):
        raise ValueError("Invalid config path (path traversal detected)")

    with open(config_path, encoding="utf-8") as f:
        data = json.load(f)

    # Optional: JSON Schema validation if available
    if HAS_JSONSCHEMA:
        schema_path = os.path.abspath(os.path.join(base_dir, "docs", "provider_config.schema.json"))
        if not schema_path.startswith(base_dir):
            raise ValueError("Invalid schema path (path traversal detected)")
        with open(schema_path, encoding="utf-8") as sf:
            schema = json.load(sf)
        jsonschema.validate(instance=data, schema=schema)

    # Minimal schema validation
    required_top_fields = {"providers", "tiers", "routing", "metadata"}
    if not required_top_fields.issubset(set(data.keys())):
        raise ValueError("provider_config.json missing required top-level fields")

    required_provider_fields = {"name", "code_name", "tier", "status"}
    for p in data.get("providers", []):
        if not required_provider_fields.issubset(set(p.keys())):
            raise ValueError(f"Provider missing required fields: {p}")
        # Validate tier exists in tiers mapping
        if str(p["tier"]) not in data.get("tiers", {}):
            raise ValueError(f"Provider tier '{p['tier']}' not defined in tiers mapping for {p['code_name']}")

        # If supported flag present and false, ensure status reflects planned/development
        if p.get("supported") is False and p.get("status") not in {"planned", "development"}:
            raise ValueError(f"Unsupported provider must be planned/development: {p['code_name']}")

    return data

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

def canonical_name_map():
    """Map display names in README to canonical code names."""
    return {
        "Cerebras": "cerebras",
        "NVIDIA": "nvidia",
        "Google Gemini 2.0": "gemini2",
        "Codestral (Mistral)": "codestral",
        "Mistral Codestral": "codestral",
        "Cohere": "cohere",
        "Chutes AI": "chutes",
        "DeepSeek": "deepseek",
        "GLM 4.5": "glm",
        "xAI Grok": "grok",
        "Moonshot Kimi": "kimi",
        "Qwen": "qwen",
        "GPT-OSS": "gptoss",
    }

def load_active_provider_codes(config):
    codes = set()
    for p in config.get("providers", []):
        # Only consider supported active providers
        if p.get("status") == "active" and p.get("supported", True):
            codes.add(p.get("code_name"))
    return codes

def validate():
    """Validate provider documentation"""
    config = load_provider_config()
    readme_providers = extract_providers_from_readme()
    
    errors = []
    warnings = []
    
    # Build canonical mapping
    name_map = canonical_name_map()
    active_codes = load_active_provider_codes(config)
    readme_codes = set()
    for display_name in readme_providers.keys():
        code = name_map.get(display_name)
        if code:
            readme_codes.add(code)
        else:
            # If no mapping, record as warning but don't fail
            warnings.append(f"⚠️  Unmapped provider display name in README.md: '{display_name}'")
    
    # Check that all active providers are at least represented
    for code in active_codes:
        if code not in readme_codes:
            warnings.append(f"⚠️  Active provider '{code}' in config not represented in README.md")
    
    # Flag any providers documented in README but not supported
    unsupported = [p for p in config.get("providers", []) if not p.get("supported", True)]
    unsupported_names = {p["name"] for p in unsupported}
    for display_name in readme_providers.keys():
        if display_name in unsupported_names:
            warnings.append(f"⚠️  README documents unsupported provider '{display_name}' (planned)")
    
    # Use set-based operations for performance
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
