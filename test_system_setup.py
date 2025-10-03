#!/usr/bin/env python3
"""
Quick test to validate system setup
"""

import os
import sys

def test_imports():
    """Test critical imports"""
    print("🧪 Testing System Setup")
    print("=" * 40)
    
    try:
        # Test basic imports
        print("✅ Basic Python imports working")
        
        # Test if we can import our modules
        src_path = os.path.join(os.path.dirname(__file__), 'src')
        if src_path not in sys.path:
            sys.path.insert(0, src_path)
        
        try:
            # Direct import from file path
            import importlib.util
            
            # Test AI API Manager
            spec = importlib.util.spec_from_file_location(
                "ai_api_manager", 
                os.path.join(src_path, "amas", "core", "ai_api_manager.py")
            )
            ai_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(ai_module)
            print("✅ AI API Manager import successful")
        except Exception as e:
            print(f"❌ AI API Manager import failed: {e}")
        
        try:
            # Test Enhanced Orchestrator
            spec = importlib.util.spec_from_file_location(
                "enhanced_orchestrator", 
                os.path.join(src_path, "amas", "core", "enhanced_orchestrator.py")
            )
            orch_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(orch_module)
            print("✅ Enhanced Orchestrator import successful")
        except Exception as e:
            print(f"❌ Enhanced Orchestrator import failed: {e}")
        
        try:
            # Test API Testing Suite
            spec = importlib.util.spec_from_file_location(
                "api_testing_suite", 
                os.path.join(src_path, "amas", "core", "api_testing_suite.py")
            )
            test_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(test_module)
            print("✅ Testing Suite import successful")
        except Exception as e:
            print(f"❌ Testing Suite import failed: {e}")
        
        print("\n📋 System Structure:")
        print(f"   • Python version: {sys.version.split()[0]}")
        print(f"   • Working directory: {os.getcwd()}")
        print(f"   • Source path: {os.path.join(os.getcwd(), 'src')}")
        
        print("\n🔑 API Key Status:")
        api_keys = [
            "CEREBRAS_API_KEY", "CODESTRAL_API_KEY", "DEEPSEEK_API_KEY", 
            "GEMINIAI_API_KEY", "GLM_API_KEY", "GPTOSS_API_KEY", "GROK_API_KEY",
            "GROQAI_API_KEY", "KIMI_API_KEY", "NVIDIA_API_KEY", "QWEN_API_KEY",
            "GEMINI2_API_KEY", "GROQ2_API_KEY", "COHERE_API_KEY", "CHUTES_API_KEY"
        ]
        
        available = 0
        for key in api_keys[:5]:  # Show first 5
            if os.getenv(key):
                print(f"   ✅ {key}")
                available += 1
            else:
                print(f"   ❌ {key}")
        
        print(f"   ... (showing 5/{len(api_keys)} keys)")
        print(f"   📊 Total available: {sum(1 for k in api_keys if os.getenv(k))}/{len(api_keys)}")
        
        print("\n✅ System setup validation completed!")
        
        if available == 0:
            print("\n⚠️  Note: No API keys detected. To test the system:")
            print("   export DEEPSEEK_API_KEY='your-api-key'")
            print("   python3 demo_enhanced_system.py")
        
    except Exception as e:
        print(f"❌ System setup test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_imports()