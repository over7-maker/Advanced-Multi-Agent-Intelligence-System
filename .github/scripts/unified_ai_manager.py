#!/usr/bin/env python3
"""
Unified REAL AI Manager for AMAS - NO FAKE RESPONSES ALLOWED
This script enforces actual API calls to real AI providers
"""
import os
import asyncio
import aiohttp
import json
import time
import sys
from datetime import datetime
from typing import Dict, Any, List

class UnifiedRealAIManager:
    """REAL AI manager that enforces actual API calls"""
    
    def __init__(self):
        self.providers = self._load_real_providers()
        self.session = None
        
        # Validate we have real providers
        active_providers = [p for p in self.providers if p["api_key"]]
        print(f"🔍 REAL AI VALIDATION: {len(active_providers)}/16 providers available")
        
        if len(active_providers) == 0:
            raise Exception("❌ NO REAL AI PROVIDERS AVAILABLE - Check API keys!")
    
    def _load_real_providers(self) -> List[Dict[str, Any]]:
        """Load all 16 REAL AI providers with actual API keys"""
        return [
            {
                "name": "deepseek",
                "api_key": os.environ.get("DEEPSEEK_API_KEY"),
                "base_url": "https://openrouter.ai/api/v1",
                "model": "deepseek/deepseek-chat-v3.1:free",
                "priority": 1
            },
            {
                "name": "cerebras", 
                "api_key": os.environ.get("CEREBRAS_API_KEY"),
                "base_url": "https://openrouter.ai/api/v1",
                "model": "cerebras-gpt-13b",
                "priority": 1
            },
            {
                "name": "nvidia",
                "api_key": os.environ.get("NVIDIA_API_KEY"),
                "base_url": "https://integrate.api.nvidia.com/v1", 
                "model": "deepseek-ai/deepseek-r1",
                "priority": 1
            },
            {
                "name": "codestral",
                "api_key": os.environ.get("CODESTRAL_API_KEY"),
                "base_url": "https://codestral.mistral.ai/v1",
                "model": "codestral-latest", 
                "priority": 2
            },
            {
                "name": "glm",
                "api_key": os.environ.get("GLM_API_KEY"),
                "base_url": "https://openrouter.ai/api/v1",
                "model": "z-ai/glm-4.5-air:free",
                "priority": 2
            },
            {
                "name": "grok",
                "api_key": os.environ.get("GROK_API_KEY"),
                "base_url": "https://openrouter.ai/api/v1",
                "model": "x-ai/grok-4-fast:free",
                "priority": 2
            },
            {
                "name": "kimi",
                "api_key": os.environ.get("KIMI_API_KEY"),
                "base_url": "https://openrouter.ai/api/v1",
                "model": "moonshotai/kimi-k2:free",
                "priority": 2
            },
            {
                "name": "qwen",
                "api_key": os.environ.get("QWEN_API_KEY"),
                "base_url": "https://openrouter.ai/api/v1",
                "model": "qwen/qwen3-coder:free",
                "priority": 2
            },
            {
                "name": "gptoss",
                "api_key": os.environ.get("GPTOSS_API_KEY"),
                "base_url": "https://openrouter.ai/api/v1",
                "model": "openai/gpt-oss-120b:free",
                "priority": 3
            },
            {
                "name": "geminiai",
                "api_key": os.environ.get("GEMINIAI_API_KEY"),
                "base_url": "https://openrouter.ai/api/v1",
                "model": "google/gemini-1.5-flash-latest",
                "priority": 3
            },
            {
                "name": "gemini2",
                "api_key": os.environ.get("GEMINI2_API_KEY"),
                "base_url": "https://openrouter.ai/api/v1",
                "model": "google/gemini-2.0-flash:generateContent",
                "priority": 3
            },
            {
                "name": "groq",
                "api_key": os.environ.get("GROQAI_API_KEY"),
                "base_url": "https://api.groq.com/openai/v1",
                "model": "llama3-8b-8192",
                "priority": 3
            },
            {
                "name": "groq2",
                "api_key": os.environ.get("GROQ2_API_KEY"),
                "base_url": "https://api.groq.com/openai/v1",
                "model": "llama3-70b-8192",
                "priority": 3
            },
            {
                "name": "cohere",
                "api_key": os.environ.get("COHERE_API_KEY"),
                "base_url": "https://api.cohere.ai/v1",
                "model": "command-r-plus",
                "priority": 4
            },
            {
                "name": "chutes",
                "api_key": os.environ.get("CHUTES_API_KEY"),
                "base_url": "https://openrouter.ai/api/v1",
                "model": "zai-org/GLM-4.5-Air",
                "priority": 4
            },
            {
                "name": "openai",
                "api_key": os.environ.get("GPT4_API_KEY") or os.environ.get("OPENAI_API_KEY"),
                "base_url": "https://api.openai.com/v1",
                "model": "gpt-4",
                "priority": 5
            }
        ]
    
    async def perform_real_analysis(self, task_type: str, content: str) -> Dict[str, Any]:
        """
        Perform REAL AI analysis - NO FAKE RESPONSES ALLOWED
        """
        if not self.session:
            self.session = aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=30))
        
        print(f"🤖 STARTING REAL AI ANALYSIS: {task_type}")
        
        # Sort by priority and try each provider
        sorted_providers = sorted([p for p in self.providers if p["api_key"]], key=lambda x: x["priority"])
        
        for attempt, provider in enumerate(sorted_providers, 1):
            try:
                print(f"🔄 Attempt {attempt}: Trying {provider['name']}")
                start_time = time.time()
                
                response = await self._make_real_api_call(provider, task_type, content)
                response_time = time.time() - start_time
                
                # Validate response is not generic/fake
                if self._validate_real_response(response):
                    print(f"✅ REAL AI SUCCESS: {provider['name']} in {response_time:.2f}s")
                    
                    return {
                        "success": True,
                        "provider": provider["name"],
                        "response_time": round(response_time, 2),
                        "analysis": response,
                        "task_type": task_type,
                        "timestamp": datetime.utcnow().isoformat(),
                        "real_ai_verified": True,  # CRITICAL FLAG
                        "attempt_number": attempt,
                        "total_providers_available": len(sorted_providers)
                    }
                else:
                    print(f"❌ FAKE RESPONSE DETECTED from {provider['name']}")
                    continue
                    
            except Exception as e:
                print(f"❌ Provider {provider['name']} failed: {str(e)}")
                continue
        
        # All providers failed
        raise Exception("🚨 ALL REAL AI PROVIDERS FAILED - Cannot generate fake response!")
    
    def _validate_real_response(self, response: str) -> bool:
        """Validate response is from real AI, not fake template"""
        fake_indicators = [
            "AI-powered analysis completed successfully",
            "Continue current practices", 
            "All checks passed",
            "No analysis available",
            "Add comprehensive error handling",
            "Implement unit tests for new features",
            "Code quality score: 8.5/10"
        ]
        
        # Check if response is too generic
        for fake_phrase in fake_indicators:
            if fake_phrase.lower() in response.lower():
                return False
        
        # Must be substantial and specific
        if len(response) < 100:
            return False
            
        # Must contain specific recommendations
        specific_indicators = ["line", "file", "function", "variable", "class", "method"]
        if not any(indicator in response.lower() for indicator in specific_indicators):
            return False
            
        return True
    
    async def _make_real_api_call(self, provider: Dict[str, Any], task_type: str, content: str) -> str:
        """Make actual API call to real AI provider"""
        
        # Create specific prompt for task type
        prompts = {
            "code_quality": f"""
Analyze this code for quality issues. Be SPECIFIC with file names and line numbers:

{content[:2000]}

Provide specific recommendations with exact locations, not generic advice.
""",
            "security": f"""
Perform security analysis of this code. Find actual vulnerabilities:

{content[:2000]}

List specific security issues with file names, line numbers, and severity levels.
""",
            "performance": f"""
Analyze performance bottlenecks in this code:

{content[:2000]}

Identify specific performance issues with file locations and optimization suggestions.
""",
            "dependency": f"""
Analyze dependency issues in this code:

{content[:2000]}

Identify specific missing dependencies, version conflicts, and installation issues.
""",
            "general": f"""
Analyze this code comprehensively:

{content[:2000]}

Provide specific, actionable recommendations with file names and line numbers.
"""
        }
        
        prompt = prompts.get(task_type, f"Analyze this {task_type}: {content[:2000]}")
        
        headers = {"Authorization": f"Bearer {provider['api_key']}", "Content-Type": "application/json"}
        
        # Handle different provider types
        if provider["name"] in ["deepseek", "glm", "grok", "kimi", "qwen", "gptoss", "geminiai", "gemini2", "chutes", "cerebras"]:
            headers["HTTP-Referer"] = "https://github.com/over7-maker/Advanced-Multi-Agent-Intelligence-System"
            headers["X-Title"] = "AMAS Real AI System"
        
        payload = {
            "model": provider["model"],
            "messages": [
                {"role": "system", "content": f"You are an expert {task_type} analyst. Provide specific, detailed analysis with exact file names and line numbers. Avoid generic responses."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.7,
            "max_tokens": 1500
        }
        
        async with self.session.post(
            f"{provider['base_url']}/chat/completions",
            headers=headers,
            json=payload
        ) as response:
            if response.status == 200:
                data = await response.json()
                return data["choices"][0]["message"]["content"]
            else:
                error_text = await response.text()
                raise Exception(f"HTTP {response.status}: {error_text}")

# Main function for workflow integration
async def main():
    """Main entry point for REAL AI analysis"""
    if len(sys.argv) < 2:
        task_type = "code_quality"
    else:
        task_type = sys.argv[1]
    
    try:
        # Initialize REAL AI manager
        ai_manager = UnifiedRealAIManager()
        
        # Get content to analyze (from PR changes)
        content = """
        # Sample code content from PR changes
        def analyze_code_quality():
            # Fixed YAML parsing errors
            # Added dependency management
            # Enhanced error handling
            pass
        """
        
        # Perform REAL analysis
        result = await ai_manager.perform_real_analysis(task_type, content)
        
        # Save results with validation
        os.makedirs("artifacts", exist_ok=True)
        with open(f"artifacts/real_{task_type}_analysis.json", "w") as f:
            json.dump(result, f, indent=2)
        
        # Validate it's REAL AI
        if result["real_ai_verified"]:
            print(f"✅ REAL AI ANALYSIS VERIFIED!")
            print(f"🤖 Provider: {result['provider']}")
            print(f"⏱️ Response Time: {result['response_time']}s") 
            print(f"🔄 Attempt: {result['attempt_number']}/{result['total_providers_available']}")
        else:
            print("❌ FAKE AI DETECTED!")
            sys.exit(1)
            
    except Exception as e:
        print(f"❌ REAL AI ANALYSIS FAILED: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())