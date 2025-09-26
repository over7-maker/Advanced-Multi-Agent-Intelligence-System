#!/usr/bin/env python3
"""
Advanced Multi-Agent AI Service Manager
Manages 6 different AI APIs with intelligent fallback and load balancing
"""

import os
import json
import time
import random
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from openai import OpenAI
import requests

@dataclass
class AIProvider:
    name: str
    api_key: str
    model: str
    base_url: str
    priority: int
    max_tokens: int
    temperature: float
    is_active: bool = True
    last_used: float = 0
    success_count: int = 0
    failure_count: int = 0

class AIServiceManager:
    def __init__(self):
        """Initialize AI service manager with all 6 API providers"""
        self.providers = self._initialize_providers()
        self.current_provider_index = 0
        self.fallback_enabled = True
        
    def _initialize_providers(self) -> List[AIProvider]:
        """Initialize all 6 AI providers with their configurations"""
        providers = [
            AIProvider(
                name="DeepSeek",
                api_key=os.getenv('DEEPSEEK_API_KEY', ''),
                model="deepseek/deepseek-chat-v3.1:free",
                base_url="https://openrouter.ai/api/v1",
                priority=1,
                max_tokens=4000,
                temperature=0.7
            ),
            AIProvider(
                name="GLM",
                api_key=os.getenv('GLM_API_KEY', ''),
                model="z-ai/glm-4.5-air:free",
                base_url="https://openrouter.ai/api/v1",
                priority=2,
                max_tokens=4000,
                temperature=0.7
            ),
            AIProvider(
                name="Grok",
                api_key=os.getenv('GROK_API_KEY', ''),
                model="x-ai/grok-4-fast:free",
                base_url="https://openrouter.ai/api/v1",
                priority=3,
                max_tokens=4000,
                temperature=0.7
            ),
            AIProvider(
                name="Kimi",
                api_key=os.getenv('KIMI_API_KEY', ''),
                model="moonshotai/kimi-k2:free",
                base_url="https://openrouter.ai/api/v1",
                priority=4,
                max_tokens=4000,
                temperature=0.7
            ),
            AIProvider(
                name="Qwen",
                api_key=os.getenv('QWEN_API_KEY', ''),
                model="qwen/qwen3-coder:free",
                base_url="https://openrouter.ai/api/v1",
                priority=5,
                max_tokens=4000,
                temperature=0.7
            ),
            AIProvider(
                name="GPTOSS",
                api_key=os.getenv('GPTOSS_API_KEY', ''),
                model="openai/gpt-oss-120b:free",
                base_url="https://openrouter.ai/api/v1",
                priority=6,
                max_tokens=4000,
                temperature=0.7
            )
        ]
        
        # Filter out providers without API keys
        active_providers = [p for p in providers if p.api_key]
        print(f"🤖 Initialized {len(active_providers)}/{len(providers)} AI providers")
        return active_providers
    
    def get_available_providers(self) -> List[AIProvider]:
        """Get list of available and active providers"""
        return [p for p in self.providers if p.is_active and p.api_key]
    
    def get_best_provider(self) -> Optional[AIProvider]:
        """Get the best available provider based on priority and performance"""
        available = self.get_available_providers()
        if not available:
            return None
            
        # Sort by priority, then by success rate
        available.sort(key=lambda p: (p.priority, -p.success_count / max(1, p.success_count + p.failure_count)))
        return available[0]
    
    def get_next_provider(self) -> Optional[AIProvider]:
        """Get next provider in round-robin fashion"""
        available = self.get_available_providers()
        if not available:
            return None
            
        provider = available[self.current_provider_index % len(available)]
        self.current_provider_index = (self.current_provider_index + 1) % len(available)
        return provider
    
    def generate_response(self, 
                         prompt: str, 
                         system_prompt: str = None,
                         max_tokens: int = None,
                         temperature: float = None,
                         use_fallback: bool = True) -> Tuple[Optional[str], Optional[str], Optional[str]]:
        """
        Generate AI response using available providers with fallback
        
        Returns:
            Tuple of (response_text, provider_name, error_message)
        """
        if not self.get_available_providers():
            return None, None, "No AI providers available"
        
        # Try primary provider first
        provider = self.get_best_provider()
        if provider:
            response, error = self._try_provider(provider, prompt, system_prompt, max_tokens, temperature)
            if response:
                return response, provider.name, None
        
        # Try fallback providers if enabled
        if use_fallback and self.fallback_enabled:
            for provider in self.get_available_providers():
                if provider == self.get_best_provider():
                    continue  # Skip already tried provider
                    
                response, error = self._try_provider(provider, prompt, system_prompt, max_tokens, temperature)
                if response:
                    return response, provider.name, None
        
        return None, None, "All AI providers failed"
    
    def _try_provider(self, 
                     provider: AIProvider, 
                     prompt: str, 
                     system_prompt: str = None,
                     max_tokens: int = None,
                     temperature: float = None) -> Tuple[Optional[str], Optional[str]]:
        """Try to get response from a specific provider"""
        try:
            client = OpenAI(
                base_url=provider.base_url,
                api_key=provider.api_key
            )
            
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})
            
            completion = client.chat.completions.create(
                model=provider.model,
                messages=messages,
                max_tokens=max_tokens or provider.max_tokens,
                temperature=temperature or provider.temperature,
                extra_headers={
                    "HTTP-Referer": "https://github.com/over7-maker/Advanced-Multi-Agent-Intelligence-System",
                    "X-Title": "AMAS - Advanced Multi-Agent Intelligence System"
                }
            )
            
            response_text = completion.choices[0].message.content
            provider.success_count += 1
            provider.last_used = time.time()
            
            return response_text, None
            
        except Exception as e:
            provider.failure_count += 1
            error_msg = f"Provider {provider.name} failed: {str(e)}"
            print(f"❌ {error_msg}")
            return None, error_msg
    
    def analyze_code(self, code: str, language: str = "python") -> Tuple[Optional[str], Optional[str]]:
        """Analyze code using AI providers"""
        system_prompt = f"""You are an expert code analyst. Analyze the provided {language} code for:
1. Code quality and best practices
2. Potential bugs and issues
3. Security vulnerabilities
4. Performance optimizations
5. Code structure and maintainability

Provide detailed analysis with specific recommendations."""
        
        prompt = f"Analyze this {language} code:\n\n```{language}\n{code}\n```"
        
        return self.generate_response(prompt, system_prompt)
    
    def generate_issue_response(self, issue_title: str, issue_body: str) -> Tuple[Optional[str], Optional[str]]:
        """Generate response for GitHub issues"""
        system_prompt = """You are a helpful AI assistant for a GitHub repository. Generate professional, helpful responses to issues that:
1. Acknowledge the issue
2. Provide helpful suggestions or solutions
3. Ask clarifying questions if needed
4. Be friendly and professional
5. Keep responses concise but informative"""
        
        prompt = f"Issue Title: {issue_title}\n\nIssue Description: {issue_body}\n\nGenerate a helpful response:"
        
        return self.generate_response(prompt, system_prompt)
    
    def generate_security_analysis(self, code: str) -> Tuple[Optional[str], Optional[str]]:
        """Generate security analysis of code"""
        system_prompt = """You are a cybersecurity expert. Analyze the code for:
1. Security vulnerabilities
2. Hardcoded secrets or credentials
3. Input validation issues
4. Authentication/authorization problems
5. Data exposure risks
6. Injection vulnerabilities

Provide specific security recommendations."""
        
        prompt = f"Perform security analysis on this code:\n\n```\n{code}\n```"
        
        return self.generate_response(prompt, system_prompt)
    
    def generate_performance_analysis(self, code: str) -> Tuple[Optional[str], Optional[str]]:
        """Generate performance analysis of code"""
        system_prompt = """You are a performance optimization expert. Analyze the code for:
1. Performance bottlenecks
2. Memory usage issues
3. Algorithmic complexity
4. I/O optimization opportunities
5. Caching strategies
6. Resource management

Provide specific performance recommendations."""
        
        prompt = f"Analyze performance of this code:\n\n```\n{code}\n```"
        
        return self.generate_response(prompt, system_prompt)
    
    def get_provider_stats(self) -> Dict[str, Any]:
        """Get statistics for all providers"""
        stats = {}
        for provider in self.providers:
            total_requests = provider.success_count + provider.failure_count
            success_rate = (provider.success_count / total_requests * 100) if total_requests > 0 else 0
            
            stats[provider.name] = {
                'active': provider.is_active,
                'has_key': bool(provider.api_key),
                'success_count': provider.success_count,
                'failure_count': provider.failure_count,
                'success_rate': f"{success_rate:.1f}%",
                'last_used': provider.last_used,
                'priority': provider.priority
            }
        return stats
    
    def test_all_providers(self) -> Dict[str, Any]:
        """Test all providers with a simple prompt"""
        test_prompt = "Hello! Please respond with 'AI provider test successful' and your name."
        results = {}
        
        for provider in self.get_available_providers():
            print(f"🧪 Testing {provider.name}...")
            response, error = self._try_provider(provider, test_prompt)
            
            results[provider.name] = {
                'success': response is not None,
                'response': response,
                'error': error,
                'provider': provider.name
            }
            
            if response:
                print(f"✅ {provider.name}: {response[:100]}...")
            else:
                print(f"❌ {provider.name}: {error}")
        
        return results
    
    def disable_provider(self, provider_name: str):
        """Disable a specific provider"""
        for provider in self.providers:
            if provider.name == provider_name:
                provider.is_active = False
                print(f"🚫 Disabled provider: {provider_name}")
                break
    
    def enable_provider(self, provider_name: str):
        """Enable a specific provider"""
        for provider in self.providers:
            if provider.name == provider_name:
                provider.is_active = True
                print(f"✅ Enabled provider: {provider_name}")
                break

def main():
    """Test the AI service manager"""
    print("🤖 Advanced Multi-Agent AI Service Manager")
    print("=" * 60)
    
    # Initialize manager
    manager = AIServiceManager()
    
    # Show provider status
    print("\n📊 Provider Status:")
    stats = manager.get_provider_stats()
    for name, stat in stats.items():
        status = "✅ Active" if stat['active'] and stat['has_key'] else "❌ Inactive"
        print(f"  {name}: {status} (Success Rate: {stat['success_rate']})")
    
    # Test all providers
    print("\n🧪 Testing All Providers:")
    results = manager.test_all_providers()
    
    working_providers = [name for name, result in results.items() if result['success']]
    print(f"\n✅ Working Providers: {', '.join(working_providers)}")
    
    if working_providers:
        # Test code analysis
        print("\n🔍 Testing Code Analysis:")
        test_code = """
def calculate_fibonacci(n):
    if n <= 1:
        return n
    return calculate_fibonacci(n-1) + calculate_fibonacci(n-2)
"""
        
        response, provider, error = manager.analyze_code(test_code)
        if response:
            print(f"✅ Code analysis successful using {provider}")
            print(f"Response: {response[:200]}...")
        else:
            print(f"❌ Code analysis failed: {error}")
    
    return len(working_providers) > 0

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)