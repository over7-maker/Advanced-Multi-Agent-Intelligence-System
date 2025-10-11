#!/usr/bin/env python3
"""
Universal AI Workflow Integration
Centralized AI integration for all workflows
"""

import asyncio
import json
import os
from datetime import datetime
from typing import Dict, List, Any, Optional

# Import the ultimate fallback manager
try:
    from ultimate_16_api_fallback_manager import generate_ai_response, generate_ai_response_with_context
    ULTIMATE_MANAGER_AVAILABLE = True
except ImportError:
    ULTIMATE_MANAGER_AVAILABLE = False
    print("⚠️  Ultimate 16-API Fallback Manager not available, using fallback")

async def generate_workflow_ai_response(
    prompt: str,
    context: Optional[Dict] = None,
    max_tokens: int = 1000,
    temperature: float = 0.7,
    **kwargs
) -> Dict[str, Any]:
    """
    Generate AI response for workflow integration
    
    Args:
        prompt: The prompt to send to AI
        context: Optional context information
        max_tokens: Maximum tokens to generate
        temperature: Response creativity (0.0-1.0)
        **kwargs: Additional parameters
    
    Returns:
        Dict containing response and metadata
    """
    try:
        if ULTIMATE_MANAGER_AVAILABLE:
            # Use the ultimate fallback manager
            response = await generate_ai_response(
                prompt=prompt,
                max_tokens=max_tokens,
                temperature=temperature,
                **kwargs
            )
            
            return {
                "success": True,
                "response": response,
                "provider": "Ultimate Fallback Manager",
                "timestamp": datetime.now().isoformat(),
                "context": context,
                "parameters": {
                    "max_tokens": max_tokens,
                    "temperature": temperature,
                    **kwargs
                }
            }
        else:
            # Fallback response
            return {
                "success": False,
                "response": "AI service temporarily unavailable",
                "provider": "Fallback",
                "timestamp": datetime.now().isoformat(),
                "context": context,
                "error": "Ultimate Fallback Manager not available"
            }
            
    except Exception as e:
        return {
            "success": False,
            "response": f"Error generating response: {str(e)}",
            "provider": "Error",
            "timestamp": datetime.now().isoformat(),
            "context": context,
            "error": str(e)
        }

async def generate_workflow_ai_response_with_context(
    messages: List[Dict[str, str]],
    max_tokens: int = 1000,
    temperature: float = 0.7,
    **kwargs
) -> Dict[str, Any]:
    """
    Generate AI response with context messages
    
    Args:
        messages: List of message dictionaries with 'role' and 'content'
        max_tokens: Maximum tokens to generate
        temperature: Response creativity (0.0-1.0)
        **kwargs: Additional parameters
    
    Returns:
        Dict containing response and metadata
    """
    try:
        if ULTIMATE_MANAGER_AVAILABLE:
            # Use the ultimate fallback manager with context
            result = await generate_ai_response_with_context(
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature,
                **kwargs
            )
            
            return {
                "success": True,
                "response": result.get("content", ""),
                "provider": result.get("provider", "Unknown"),
                "timestamp": datetime.now().isoformat(),
                "context": {
                    "message_count": len(messages),
                    "last_message": messages[-1] if messages else None
                },
                "parameters": {
                    "max_tokens": max_tokens,
                    "temperature": temperature,
                    **kwargs
                }
            }
        else:
            # Fallback response
            return {
                "success": False,
                "response": "AI service temporarily unavailable",
                "provider": "Fallback",
                "timestamp": datetime.now().isoformat(),
                "context": {
                    "message_count": len(messages),
                    "last_message": messages[-1] if messages else None
                },
                "error": "Ultimate Fallback Manager not available"
            }
            
    except Exception as e:
        return {
            "success": False,
            "response": f"Error generating response: {str(e)}",
            "provider": "Error",
            "timestamp": datetime.now().isoformat(),
            "context": {
                "message_count": len(messages),
                "last_message": messages[-1] if messages else None
            },
            "error": str(e)
        }

def save_workflow_results(
    results: Dict[str, Any],
    filename: str,
    directory: str = "workflow_results"
) -> str:
    """
    Save workflow results to file
    
    Args:
        results: Results dictionary to save
        filename: Name of the file to save
        directory: Directory to save in
    
    Returns:
        Path to saved file
    """
    try:
        # Create directory if it doesn't exist
        os.makedirs(directory, exist_ok=True)
        
        # Add timestamp if not present
        if "timestamp" not in results:
            results["timestamp"] = datetime.now().isoformat()
        
        # Create file path
        file_path = os.path.join(directory, filename)
        
        # Save as JSON
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        return file_path
        
    except Exception as e:
        print(f"Error saving workflow results: {e}")
        return ""

def get_workflow_ai_providers() -> List[str]:
    """
    Get list of available AI providers
    
    Returns:
        List of provider names
    """
    if ULTIMATE_MANAGER_AVAILABLE:
        try:
            from ultimate_16_api_fallback_manager import Ultimate16APIFallbackManager
            manager = Ultimate16APIFallbackManager()
            return list(manager.providers.keys())
        except:
            return ["Ultimate Fallback Manager"]
    else:
        return ["Fallback"]

def test_workflow_integration() -> Dict[str, Any]:
    """
    Test the workflow integration
    
    Returns:
        Test results dictionary
    """
    test_results = {
        "timestamp": datetime.now().isoformat(),
        "tests": {},
        "overall_success": True
    }
    
    # Test 1: Basic import
    try:
        from universal_ai_workflow_integration import generate_workflow_ai_response
        test_results["tests"]["import"] = {"success": True, "message": "Import successful"}
    except Exception as e:
        test_results["tests"]["import"] = {"success": False, "message": str(e)}
        test_results["overall_success"] = False
    
    # Test 2: Provider availability
    try:
        providers = get_workflow_ai_providers()
        test_results["tests"]["providers"] = {
            "success": True, 
            "message": f"Found {len(providers)} providers",
            "providers": providers
        }
    except Exception as e:
        test_results["tests"]["providers"] = {"success": False, "message": str(e)}
        test_results["overall_success"] = False
    
    return test_results

# Example usage
async def main():
    """Example usage of the workflow integration"""
    print("🧪 Testing Universal AI Workflow Integration")
    print("=" * 50)
    
    # Test basic response
    result = await generate_workflow_ai_response(
        "Say 'Hello from workflow integration!'",
        max_tokens=50
    )
    
    print(f"✅ Basic Response: {result['response']}")
    print(f"✅ Provider: {result['provider']}")
    print(f"✅ Success: {result['success']}")
    
    # Test context response
    messages = [
        {"role": "user", "content": "Hello!"},
        {"role": "assistant", "content": "Hi there! How can I help you?"},
        {"role": "user", "content": "What's 2+2?"}
    ]
    
    context_result = await generate_workflow_ai_response_with_context(
        messages=messages,
        max_tokens=50
    )
    
    print(f"\n✅ Context Response: {context_result['response']}")
    print(f"✅ Provider: {context_result['provider']}")
    print(f"✅ Success: {context_result['success']}")
    
    # Test integration
    test_results = test_workflow_integration()
    print(f"\n✅ Integration Test: {'PASSED' if test_results['overall_success'] else 'FAILED'}")
    
    # Save results
    save_workflow_results(result, "test_result.json")
    print("✅ Results saved to workflow_results/test_result.json")

if __name__ == "__main__":
    asyncio.run(main())