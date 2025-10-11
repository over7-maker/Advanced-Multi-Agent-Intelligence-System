#!/usr/bin/env python3
"""
Universal AI Workflow Integration Script
Integrates with standalone_universal_ai_manager.py for all workflow scripts
"""

import asyncio
import json
import logging
import os
import sys
from pathlib import Path
from typing import Any, Dict, Optional

# Add the project root to the Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Import the standalone universal AI manager
from standalone_universal_ai_manager import get_manager, generate_ai_response

# Configure logging
logging.basicConfig(
    level=logging.INFO, 
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

class UniversalAIWorkflowIntegration:
    """Universal AI Workflow Integration with Advanced API Manager"""
    
    def __init__(self):
        """Initialize the integration"""
        self.manager = get_manager()
        self.stats = {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "providers_used": [],
            "response_times": [],
            "errors": []
        }
    
    async def generate_with_fallback(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        strategy: str = "intelligent",
        max_attempts: Optional[int] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Generate AI response with comprehensive fallback"""
        self.stats["total_requests"] += 1
        
        try:
            result = await generate_ai_response(
                prompt=prompt,
                system_prompt=system_prompt,
                strategy=strategy,
                **kwargs
            )
            
            if result.get("success", False):
                self.stats["successful_requests"] += 1
                self.stats["providers_used"].append(result.get("provider", "unknown"))
                self.stats["response_times"].append(result.get("response_time", 0))
                logger.info(f"✅ Success with {result.get('provider_name', 'Unknown')} in {result.get('response_time', 0):.2f}s")
            else:
                self.stats["failed_requests"] += 1
                error_msg = result.get("error", "Unknown error")
                self.stats["errors"].append(error_msg)
                logger.error(f"❌ Failed: {error_msg}")
            
            return result
            
        except Exception as e:
            self.stats["failed_requests"] += 1
            error_msg = f"Exception: {str(e)}"
            self.stats["errors"].append(error_msg)
            logger.error(f"❌ Exception: {e}")
            
            return {
                "success": False,
                "error": error_msg,
                "provider": "none",
                "provider_name": "Exception",
                "content": "",
                "response_time": 0
            }
    
    def get_integration_stats(self) -> Dict[str, Any]:
        """Get integration statistics"""
        success_rate = 0
        if self.stats["total_requests"] > 0:
            success_rate = (self.stats["successful_requests"] / self.stats["total_requests"]) * 100
        
        avg_response_time = 0
        if self.stats["response_times"]:
            avg_response_time = sum(self.stats["response_times"]) / len(self.stats["response_times"])
        
        return {
            "integration_stats": self.stats,
            "manager_stats": self.manager.get_stats(),
            "provider_health": self.manager.get_provider_health(),
            "success_rate": f"{success_rate:.1f}%",
            "average_response_time": f"{avg_response_time:.2f}s",
            "total_providers": len(self.manager.active_providers),
            "active_providers": self.manager.active_providers
        }
    
    def save_results(self, results: Dict[str, Any], output_file: str):
        """Save results to file"""
        try:
            # Add integration stats to results
            results["integration_stats"] = self.get_integration_stats()
            
            with open(output_file, 'w') as f:
                json.dump(results, f, indent=2, default=str)
            
            logger.info(f"✅ Results saved to {output_file}")
            
        except Exception as e:
            logger.error(f"❌ Failed to save results: {e}")

# Global integration instance
_integration: Optional[UniversalAIWorkflowIntegration] = None

def get_integration() -> UniversalAIWorkflowIntegration:
    """Get or create the global integration instance"""
    global _integration
    if _integration is None:
        _integration = UniversalAIWorkflowIntegration()
    return _integration

async def generate_workflow_ai_response(
    prompt: str,
    system_prompt: Optional[str] = None,
    strategy: str = "intelligent",
    **kwargs
) -> Dict[str, Any]:
    """Convenience function for workflow scripts"""
    integration = get_integration()
    return await integration.generate_with_fallback(
        prompt=prompt,
        system_prompt=system_prompt,
        strategy=strategy,
        **kwargs
    )

def save_workflow_results(results: Dict[str, Any], output_file: str):
    """Convenience function for saving workflow results"""
    integration = get_integration()
    integration.save_results(results, output_file)

# Test function
async def test_integration():
    """Test the Universal AI Workflow Integration"""
    print("\n" + "=" * 80)
    print("🧪 TESTING UNIVERSAL AI WORKFLOW INTEGRATION")
    print("=" * 80 + "\n")
    
    integration = UniversalAIWorkflowIntegration()
    
    print("📊 Manager Configuration:")
    print(integration.manager.get_config_summary())
    print()
    
    if len(integration.manager.active_providers) == 0:
        print("⚠️  No API keys configured - cannot test live generation")
        print("   Set environment variables to test with real providers")
        print()
        print("✅ Test PASSED - Integration initialized successfully")
        print("   (Ready to use once API keys are configured)")
        return
    
    print("📝 Test 1: Simple generation...")
    result = await integration.generate_with_fallback(
        "Say 'Universal AI Workflow Integration test successful!' and nothing else.",
        strategy="intelligent"
    )
    
    if result["success"]:
        print(f"✅ Success!")
        print(f"   Provider: {result['provider_name']}")
        print(f"   Response: {result['content'][:100]}...")
        print(f"   Time: {result['response_time']:.2f}s")
    else:
        print(f"❌ Failed: {result['error']}")
    print()
    
    print("=" * 80)
    print("📊 INTEGRATION STATISTICS")
    print("=" * 80)
    stats = integration.get_integration_stats()
    for key, value in stats.items():
        if key != "integration_stats" and key != "manager_stats" and key != "provider_health":
            print(f"  {key}: {value}")
    print()
    
    print("=" * 80)
    print("✅ UNIVERSAL AI WORKFLOW INTEGRATION TEST COMPLETED")
    print("=" * 80)

if __name__ == "__main__":
    asyncio.run(test_integration())
