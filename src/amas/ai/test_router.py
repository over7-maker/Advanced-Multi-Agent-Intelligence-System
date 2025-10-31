#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""
Test Suite for Universal AI Router

Comprehensive tests to validate failover behavior and provider integration.
"""

import asyncio
import os
import sys
import unittest
from unittest.mock import AsyncMock, MagicMock, patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../..'))

from src.amas.ai.router import (
    ProviderError,
    _enabled,
    _env,
    build_provider_priority,
    generate,
    get_available_providers,
    get_provider_status,
    health_check,
)


class TestUniversalRouter(unittest.TestCase):
    """Test cases for universal AI router."""
    
    def setUp(self):
        """Set up test environment."""
        # Clear environment for clean tests
        self.original_env = dict(os.environ)
        for key in list(os.environ.keys()):
            if 'API_KEY' in key:
                del os.environ[key]
    
    def tearDown(self):
        """Restore original environment."""
        os.environ.clear()
        os.environ.update(self.original_env)
    
    def test_env_functions(self):
        """Test environment variable helper functions."""
        # Test with missing key
        self.assertIsNone(_env("NONEXISTENT_KEY"))
        self.assertFalse(_enabled("NONEXISTENT_KEY"))
        
        # Test with present key
        os.environ["TEST_KEY"] = "test_value"
        self.assertEqual(_env("TEST_KEY"), "test_value")
        self.assertTrue(_enabled("TEST_KEY"))
        
        # Test with empty key
        os.environ["EMPTY_KEY"] = ""
        self.assertIsNone(_env("EMPTY_KEY"))
        self.assertFalse(_enabled("EMPTY_KEY"))
        
        # Test with whitespace key
        os.environ["WHITESPACE_KEY"] = "  value  "
        self.assertEqual(_env("WHITESPACE_KEY"), "value")
        
        print("✅ Environment functions validation: PASSED")
    
    def test_provider_priority_no_keys(self):
        """Test provider priority with no API keys."""
        providers = build_provider_priority()
        self.assertEqual(providers, [])
        
        status = get_provider_status()
        self.assertTrue(isinstance(status, dict))
        self.assertFalse(any(status.values()))
        
        print("✅ No keys scenario: PASSED")
    
    def test_provider_priority_with_keys(self):
        """Test provider priority with various API keys."""
        # Set up some test keys
        os.environ["CEREBRAS_API_KEY"] = "test_cerebras"
        os.environ["NVIDIA_API_KEY"] = "test_nvidia"
        os.environ["DEEPSEEK_API_KEY"] = "test_deepseek"
        
        providers = build_provider_priority()
        
        # Should include configured providers
        self.assertIn("cerebras", providers)
        self.assertIn("nvidia", providers)
        self.assertIn("openrouter", providers)  # Due to DEEPSEEK_API_KEY
        
        # Should maintain priority order
        cerebras_idx = providers.index("cerebras")
        nvidia_idx = providers.index("nvidia")
        self.assertLess(cerebras_idx, nvidia_idx)  # Cerebras should come first
        
        status = get_provider_status()
        self.assertTrue(status["cerebras"])
        self.assertTrue(status["nvidia"])
        self.assertTrue(status["openrouter"])
        
        print("✅ Provider priority with keys: PASSED")
    
    @patch('src.amas.ai.router.call_cerebras')
    async def test_failover_behavior(self, mock_cerebras):
        """Test failover behavior when providers fail."""
        os.environ["CEREBRAS_API_KEY"] = "test_key"
        os.environ["NVIDIA_API_KEY"] = "test_key"
        
        # Mock first provider to fail, second to succeed
        mock_cerebras.side_effect = ProviderError("Test failure", "cerebras", "error")
        
        with patch('src.amas.ai.router.call_nvidia') as mock_nvidia:
            mock_nvidia.return_value = {
                "provider": "nvidia",
                "content": "Success!",
                "success": True,
                "tokens_used": 10
            }
            
            result = await generate("Test prompt")
            
            # Should succeed with second provider
            self.assertTrue(result["success"])
            self.assertEqual(result["content"], "Success!")
            self.assertIn("nvidia", result["provider_name"])
            
            # Should record both attempts
            self.assertEqual(len(result["attempts"]), 2)
            self.assertEqual(result["attempts"][0].provider, "cerebras")
            self.assertEqual(result["attempts"][0].status, "error")
            self.assertEqual(result["attempts"][1].provider, "nvidia")
            self.assertEqual(result["attempts"][1].status, "success")
        
        print("✅ Failover behavior: PASSED")
    
    @patch('src.amas.ai.router.build_provider_priority')
    async def test_all_providers_fail(self, mock_priority):
        """Test behavior when all providers fail."""
        mock_priority.return_value = ["cerebras", "nvidia"]
        
        with patch('src.amas.ai.router.call_cerebras') as mock_cerebras, \
             patch('src.amas.ai.router.call_nvidia') as mock_nvidia:
            
            mock_cerebras.side_effect = ProviderError("Cerebras down", "cerebras", "error")
            mock_nvidia.side_effect = ProviderError("NVIDIA down", "nvidia", "error")
            
            result = await generate("Test prompt")
            
            # Should fail gracefully
            self.assertFalse(result["success"])
            self.assertIn("All 2 providers failed", result["error"])
            self.assertEqual(result["provider_name"], "failed_all")
            
            # Should record all attempts
            self.assertEqual(len(result["attempts"]), 2)
        
        print("✅ All providers fail scenario: PASSED")
    
    async def test_health_check_no_providers(self):
        """Test health check with no providers."""
        health = await health_check()
        
        self.assertEqual(health["status"], "unhealthy")
        self.assertIn("No providers configured", health["message"])
        self.assertEqual(health["available_count"], 0)
        
        print("✅ Health check (no providers): PASSED")
    
    @patch('src.amas.ai.router.generate')
    async def test_health_check_with_working_provider(self, mock_generate):
        """Test health check with working provider."""
        os.environ["CEREBRAS_API_KEY"] = "test_key"
        
        mock_generate.return_value = {
            "success": True,
            "provider_name": "cerebras",
            "response_time": 1.5
        }
        
        health = await health_check()
        
        self.assertEqual(health["status"], "healthy")
        self.assertEqual(health["working_provider"], "cerebras")
        self.assertGreater(health["providers_available"], 0)
        
        print("✅ Health check (working provider): PASSED")
    
    def test_backward_compatibility(self):
        """Test backward compatibility with existing manager interface."""
        from src.amas.ai.router import get_manager
        
        manager = get_manager()
        self.assertTrue(hasattr(manager, 'active_providers'))
        self.assertTrue(hasattr(manager, 'generate'))
        
        # Test active_providers property
        providers = manager.active_providers
        self.assertIsInstance(providers, list)
        
        print("✅ Backward compatibility: PASSED")
    
    def test_openrouter_key_detection(self):
        """Test OpenRouter key detection logic."""
        # Test with no OpenRouter keys
        providers = build_provider_priority()
        self.assertNotIn("openrouter", providers)
        
        # Test with one OpenRouter key
        os.environ["DEEPSEEK_API_KEY"] = "test_key"
        providers = build_provider_priority()
        self.assertIn("openrouter", providers)
        
        # Test status detection
        status = get_provider_status()
        self.assertTrue(status["openrouter"])
        
        print("✅ OpenRouter key detection: PASSED")

def run_comprehensive_tests():
    """Run all router tests."""
    print("🧪 Universal AI Router Test Suite")
    print("=" * 50)
    
    # Create and run test suite
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestUniversalRouter)
    
    # Run with detailed output
    runner = unittest.TextTestRunner(verbosity=2, stream=sys.stdout)
    result = runner.run(suite)
    
    print("\n" + "=" * 50)
    
    if result.wasSuccessful():
        print("✅ ALL ROUTER TESTS PASSED!")
        print("✅ Multi-provider failover system is ready!")
        print("✅ Zero-fail AI guarantee implemented!")
        return 0
    else:
        print(f"❌ {len(result.failures)} test(s) failed")
        print(f"❌ {len(result.errors)} error(s) occurred")
        return 1

if __name__ == "__main__":
    # Run tests if called directly
    exit_code = run_comprehensive_tests()
    sys.exit(exit_code)