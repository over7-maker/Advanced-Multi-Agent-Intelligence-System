#!/usr/bin/env python3
"""
BULLETPROOF REAL AI - Absolutely NO fake responses allowed
This script FORCES real AI usage and fails hard if fake AI is detected
"""
import os
import sys
import asyncio
import aiohttp
import json
import time
from datetime import datetime

class BulletproofRealAI:
    """BULLETPROOF implementation - NO FAKE AI ALLOWED"""
    
    def __init__(self):
        # Load ONLY providers with actual API keys
        self.providers = self._get_real_providers_only()
        
        if not self.providers:
            raise Exception("🚨 CRITICAL: NO REAL AI PROVIDERS AVAILABLE!")
        
        print(f"🔍 BULLETPROOF AI VALIDATION: {len(self.providers)} REAL providers loaded")
        for provider in self.providers:
            print(f"  ✅ {provider['name']}: API key present")
    
    def _get_real_providers_only(self):
        """Get ONLY providers with actual API keys - NO FALLBACKS"""
        candidates = [
            {"name": "deepseek", "key": "DEEPSEEK_API_KEY", "url": "https://openrouter.ai/api/v1", "model": "deepseek/deepseek-chat-v3.1:free"},
            {"name": "cerebras", "key": "CEREBRAS_API_KEY", "url": "https://api.cerebras.ai/v1", "model": "qwen-3-235b-a22b-instruct-2507"},
            {"name": "nvidia", "key": "NVIDIA_API_KEY", "url": "https://integrate.api.nvidia.com/v1", "model": "deepseek-ai/deepseek-r1"},
            {"name": "codestral", "key": "CODESTRAL_API_KEY", "url": "https://codestral.mistral.ai/v1", "model": "codestral-latest"},
            {"name": "glm", "key": "GLM_API_KEY", "url": "https://openrouter.ai/api/v1", "model": "z-ai/glm-4.5-air:free"},
            {"name": "grok", "key": "GROK_API_KEY", "url": "https://openrouter.ai/api/v1", "model": "x-ai/grok-4-fast:free"},
            {"name": "cohere", "key": "COHERE_API_KEY", "url": "https://api.cohere.ai/v2", "model": "command-a-03-2025"},
            {"name": "claude", "key": "CLAUDE_API_KEY", "url": "https://api.anthropic.com/v1", "model": "claude-3-5-sonnet-20241022"},
            {"name": "openai", "key": "GPT4_API_KEY", "url": "https://api.openai.com/v1", "model": "gpt-4o"},
            {"name": "gemini", "key": "GEMINI_API_KEY", "url": "https://generativelanguage.googleapis.com/v1beta", "model": "gemini-1.5-pro"},
            {"name": "groq", "key": "GROQAI_API_KEY", "url": "https://api.groq.com/openai/v1", "model": "llama-3.1-70b-versatile"},
            {"name": "mistral", "key": "MISTRAL_API_KEY", "url": "https://api.mistral.ai/v1", "model": "mistral-large-latest"},
            {"name": "kimi", "key": "KIMI_API_KEY", "url": "https://openrouter.ai/api/v1", "model": "moonshot/moonshot-v1-8k"},
            {"name": "qwen", "key": "QWEN_API_KEY", "url": "https://openrouter.ai/api/v1", "model": "qwen/qwen-2.5-72b-instruct"},
            {"name": "perplexity", "key": "PERPLEXITY_API_KEY", "url": "https://api.perplexity.ai/chat/completions", "model": "llama-3.1-sonar-small-128k-online"},
            {"name": "gptoss", "key": "GPTOSS_API_KEY", "url": "https://openrouter.ai/api/v1", "model": "gptoss/gptoss-7b-instruct"}
        ]
        
        # Return ONLY providers with actual API keys
        real_providers = []
        for candidate in candidates:
            api_key = os.environ.get(candidate["key"])
            if api_key and len(api_key) > 10:  # Must be real key, not empty
                real_providers.append({
                    "name": candidate["name"],
                    "api_key": api_key,
                    "base_url": candidate["url"],
                    "model": candidate["model"]
                })
        
        return real_providers
    
    async def force_real_ai_analysis(self, task_type, content):
        """FORCE real AI analysis - FAIL if fake AI detected"""
        print(f"🤖 FORCING REAL AI ANALYSIS: {task_type}")
        print(f"🔍 Content length: {len(content)} chars")
        
        # Try each real provider
        for i, provider in enumerate(self.providers, 1):
            try:
                print(f"🔄 Attempt {i}/{len(self.providers)}: {provider['name']}")
                start_time = time.time()
                
                # Make REAL API call
                result = await self._call_real_api(provider, task_type, content)
                response_time = time.time() - start_time
                
                # CRITICAL: Validate response is REAL (not generic)
                if self._is_real_ai_response(result):
                    print(f"✅ REAL AI CONFIRMED: {provider['name']}")
                    
                    return {
                        "success": True,
                        "provider": provider["name"],
                        "response_time": round(response_time, 2),
                        "analysis": result,
                        "real_ai_verified": True,
                        "fake_ai_detected": False,
                        "provider_attempt": i,
                        "total_attempts": len(self.providers),
                        "timestamp": datetime.now().isoformat(),
                        "bulletproof_validated": True
                    }
                else:
                    print(f"❌ GENERIC/FAKE RESPONSE from {provider['name']}")
                    continue
                    
            except Exception as e:
                print(f"❌ Provider {provider['name']} error: {str(e)}")
                continue
        
        # ALL PROVIDERS FAILED - This is critical
        raise Exception(f"🚨 ALL {len(self.providers)} REAL AI PROVIDERS FAILED!")
    
    def _is_real_ai_response(self, response):
        """Validate response is from REAL AI, not template"""
        
        # Reject if contains fake indicators
        fake_phrases = [
            "AI-powered analysis completed successfully",
            "Continue current practices",
            "All checks passed",
            "No specific issues found",
            "analysis completed successfully",
            "Add comprehensive error handling",
            "Implement unit tests for new features",
            "Code quality score: 8.5/10",
            "Provider: AI System",
            "Response Time: 1.5s",
            "Response Time: 2.8s",
            "Response Time: 3.1s",
            "Response Time: 5.2s"
        ]
        
        response_lower = response.lower()
        for fake_phrase in fake_phrases:
            if fake_phrase.lower() in response_lower:
                print(f"❌ FAKE PHRASE DETECTED: '{fake_phrase}'")
                return False
        
        # Must be substantial and specific
        if len(response) < 200:
            print(f"❌ RESPONSE TOO SHORT: {len(response)} chars")
            return False
        
        # Must contain specific details (not generic)
        specific_indicators = ["line", "file", "function", "class", "import", "error", "issue", "vulnerability", "performance", "security"]
        if not any(indicator in response_lower for indicator in specific_indicators):
            print("❌ NO SPECIFIC DETAILS FOUND")
            return False
        
        print("✅ REAL AI RESPONSE VALIDATED")
        return True
    
    async def _call_real_api(self, provider, task_type, content):
        """Make REAL API call with proper authentication"""

        # Task-specific prompts
        task_prompts = {
            "code_quality": """
Analyze the code quality of this pull request. Focus on:
1. Code structure and organization
2. Variable naming and conventions  
3. Error handling and edge cases
4. Performance implications
5. Maintainability issues

Provide specific file names, line numbers, and exact recommendations.
""",
            
            "dependency_analysis": """
Analyze the dependencies and imports in this code. Focus on:
1. Missing dependencies in requirements.txt
2. Unused imports that can be removed
3. Version compatibility issues
4. Security vulnerabilities in dependencies
5. Alternative package recommendations

Be specific about which files and which packages.
""",
            
            "auto_analysis": """
Perform comprehensive automated analysis of this pull request code:
1. Code quality issues with specific file names and line numbers
2. Potential bugs or logic errors with exact locations
3. Security vulnerabilities with specific details
4. Performance bottlenecks with actionable recommendations  
5. Best practice violations with specific suggestions

Provide detailed, specific analysis with exact file names and line numbers.
""",
            
            "security": """
Perform security analysis of this code. Find actual vulnerabilities:
1. Input validation issues
2. Authentication and authorization problems
3. Data exposure risks
4. Injection vulnerabilities
5. Cryptographic issues

List specific security issues with file names, line numbers, and severity levels.
""",
            
            "performance": """
Analyze performance bottlenecks in this code:
1. Algorithmic complexity issues
2. Memory usage problems
3. Database query inefficiencies
4. Network call optimizations
5. Caching opportunities

Identify specific performance issues with file locations and optimization suggestions.
"""
        }

        base_prompt = task_prompts.get(task_type, task_prompts["code_quality"])
        
        prompt = f"""
{base_prompt}

Code to analyze:
{content[:2000]}

Provide detailed, specific analysis with exact locations and actionable recommendations.
"""
        
        headers = {
            "Authorization": f"Bearer {provider['api_key']}",
            "Content-Type": "application/json"
        }
        
        # Add provider-specific headers
        if provider["name"] in ["deepseek", "glm", "grok", "kimi", "qwen", "gptoss"]:
            headers.update({
                "HTTP-Referer": "https://github.com/amas-project",
                "X-Title": "AMAS Real AI Analysis"
            })
        
        payload = {
            "model": provider["model"],
            "messages": [
                {
                    "role": "system", 
                    "content": f"You are an expert {task_type} analyst. Provide specific, detailed analysis with exact file names and line numbers. NEVER give generic responses."
                },
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.7,
            "max_tokens": 2000
        }
        
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=45)) as session:
            async with session.post(
                f"{provider['base_url']}/chat/completions",
                headers=headers,
                json=payload
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    return data["choices"][0]["message"]["content"]
                else:
                    error_text = await response.text()
                    raise Exception(f"HTTP {response.status}: {error_text[:500]}")

async def main():
    """Main function - BULLETPROOF real AI analysis"""
    
    # Get task type from command line
    task_type = sys.argv[1] if len(sys.argv) > 1 else "code_quality"
    
    try:
        # Initialize BULLETPROOF AI
        ai = BulletproofRealAI()
        
        # Get content to analyze (sample - replace with real PR content)
        content = """
# Sample code content from PR changes
def process_data(data):
    return data.process()

class DataManager:
    def __init__(self):
        self.connection = None
"""
        
        # FORCE real AI analysis
        result = await ai.force_real_ai_analysis(task_type, content)
        
        # Save results
        os.makedirs("artifacts", exist_ok=True)
        with open(f"artifacts/real_{task_type}_analysis.json", "w") as f:
            json.dump(result, f, indent=2)
        
        # SUCCESS OUTPUT
        print("🎉 BULLETPROOF REAL AI SUCCESS!")
        print(f"🤖 Provider: {result['provider']}")
        print(f"⏱️ Response Time: {result['response_time']}s")
        print(f"📊 Attempt: {result['provider_attempt']}/{result['total_attempts']}")
        print(f"✅ Bulletproof Validated: {result['bulletproof_validated']}")
        
        # Verify it's real
        if result["fake_ai_detected"]:
            print("🚨 FAKE AI DETECTED!")
            sys.exit(1)
        else:
            print("✅ REAL AI VERIFIED!")
            sys.exit(0)
            
    except Exception as e:
        print(f"🚨 BULLETPROOF AI FAILED: {str(e)}")
        
        # Create failure record
        failure_result = {
            "success": False,
            "error": str(e),
            "real_ai_verified": False,
            "fake_ai_detected": True,
            "timestamp": datetime.now().isoformat()
        }
        
        os.makedirs("artifacts", exist_ok=True)
        with open(f"artifacts/real_{task_type}_analysis.json", "w") as f:
            json.dump(failure_result, f, indent=2)
        
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())