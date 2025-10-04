#!/usr/bin/env python3
"""
Test Dependencies Script - Test if all required packages can be imported
Part of the AI-Powered Project Upgrade System
"""

import sys
import importlib
from typing import List, Dict, Any

def test_package_import(package_name: str, import_name: str = None) -> Dict[str, Any]:
    """Test if a package can be imported"""
    if import_name is None:
        import_name = package_name
    
    try:
        importlib.import_module(import_name)
        return {
            "package": package_name,
            "status": "available",
            "error": None
        }
    except ImportError as e:
        return {
            "package": package_name,
            "status": "unavailable",
            "error": str(e)
        }

def test_all_dependencies() -> Dict[str, Any]:
    """Test all required dependencies"""
    print("🧪 Testing AI-Powered Project Upgrade System Dependencies...")
    print("=" * 80)
    
    # Core dependencies
    core_packages = [
        ("openai", "openai"),
        ("aiohttp", "aiohttp"),
        ("requests", "requests"),
        ("pyyaml", "yaml"),
        ("python-dotenv", "dotenv"),
        ("PyGithub", "github"),
        ("gitpython", "git"),
        ("beautifulsoup4", "bs4"),
        ("lxml", "lxml"),
        ("pandas", "pandas"),
        ("numpy", "numpy"),
        ("scikit-learn", "sklearn"),
        ("matplotlib", "matplotlib"),
        ("seaborn", "seaborn"),
    ]
    
    # Optional AI packages
    optional_packages = [
        ("groq", "groq"),
        ("google-generativeai", "google.generativeai"),
        # Note: cerebras-cloud-sdk is not available on PyPI, skipping
        # ("cerebras-cloud-sdk", "cerebras_cloud_sdk"),
        ("cohere", "cohere"),
    ]
    
    results = {
        "core_packages": [],
        "optional_packages": [],
        "summary": {
            "total_core": len(core_packages),
            "available_core": 0,
            "total_optional": len(optional_packages),
            "available_optional": 0
        }
    }
    
    # Test core packages
    print("📦 Testing Core Dependencies:")
    for package, import_name in core_packages:
        result = test_package_import(package, import_name)
        results["core_packages"].append(result)
        
        if result["status"] == "available":
            results["summary"]["available_core"] += 1
            print(f"  ✅ {package}")
        else:
            print(f"  ❌ {package}: {result['error']}")
    
    print()
    
    # Test optional packages
    print("🔧 Testing Optional Dependencies:")
    for package, import_name in optional_packages:
        result = test_package_import(package, import_name)
        results["optional_packages"].append(result)
        
        if result["status"] == "available":
            results["summary"]["available_optional"] += 1
            print(f"  ✅ {package}")
        else:
            print(f"  ⚠️  {package}: {result['error']} (optional)")
    
    print()
    print("=" * 80)
    print("📊 DEPENDENCY TEST SUMMARY")
    print("=" * 80)
    print(f"Core Packages: {results['summary']['available_core']}/{results['summary']['total_core']} available")
    print(f"Optional Packages: {results['summary']['available_optional']}/{results['summary']['total_optional']} available")
    
    # Determine system status
    if results["summary"]["available_core"] == results["summary"]["total_core"]:
        print("✅ All core dependencies available - System ready!")
        results["system_status"] = "ready"
    else:
        print("❌ Some core dependencies missing - System may not work properly")
        results["system_status"] = "incomplete"
    
    return results

if __name__ == "__main__":
    results = test_all_dependencies()
    
    # Exit with appropriate code
    if results["system_status"] == "ready":
        sys.exit(0)
    else:
        sys.exit(1)