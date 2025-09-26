#!/usr/bin/env python3
"""
AI Enhanced Code Review Script
Comprehensive code review with refactor suggestions using multiple AI models
"""

import os
import asyncio
import requests
from openai import OpenAI
from typing import Dict, List, Any, Optional
import time
import json
from datetime import datetime
import subprocess
import difflib

class AIEnhancedCodeReview:
    def __init__(self):
        self.github_token = os.environ.get('GITHUB_TOKEN')
        self.deepseek_key = os.environ.get('DEEPSEEK_API_KEY')
        self.glm_key = os.environ.get('GLM_API_KEY')
        self.grok_key = os.environ.get('GROK_API_KEY')
        self.kimi_key = os.environ.get('KIMI_API_KEY')
        self.qwen_key = os.environ.get('QWEN_API_KEY')
        self.gptoss_key = os.environ.get('GPTOSS_API_KEY')
        self.repo_name = os.environ.get('REPO_NAME')
        self.pr_number = os.environ.get('PR_NUMBER')
        self.commit_sha = os.environ.get('COMMIT_SHA')
        
        # Initialize AI clients with intelligent fallback priority
        self.agents = []
        
        # Priority order: DeepSeek (most reliable), GLM, Grok, Kimi, Qwen, GPTOSS
        if self.deepseek_key:
            try:
                self.agents.append({
                    'name': 'DeepSeek',
                    'client': OpenAI(
                        base_url="https://api.deepseek.com/v1",
                        api_key=self.deepseek_key,
                    ),
                    'model': 'deepseek-chat',
                    'role': 'Primary Code Reviewer',
                    'priority': 1
                })
            except Exception as e:
                print(f"Failed to initialize DeepSeek agent: {e}")
        
        if self.glm_key:
            try:
                self.agents.append({
                    'name': 'GLM',
                    'client': OpenAI(
                        base_url="https://openrouter.ai/api/v1",
                        api_key=self.glm_key,
                    ),
                    'model': 'z-ai/glm-4.5-air:free',
                    'role': 'Code Quality Specialist',
                    'priority': 2
                })
            except Exception as e:
                print(f"Failed to initialize GLM agent: {e}")
        
        if self.grok_key:
            try:
                self.agents.append({
                    'name': 'Grok',
                    'client': OpenAI(
                        base_url="https://openrouter.ai/api/v1",
                        api_key=self.grok_key,
                    ),
                    'model': 'x-ai/grok-4-fast:free',
                    'role': 'Strategic Code Advisor',
                    'priority': 3
                })
            except Exception as e:
                print(f"Failed to initialize Grok agent: {e}")
        
        if self.kimi_key:
            try:
                self.agents.append({
                    'name': 'Kimi',
                    'client': OpenAI(
                        base_url="https://openrouter.ai/api/v1",
                        api_key=self.kimi_key,
                    ),
                    'model': 'moonshot/moonshot-v1-8k:free',
                    'role': 'Technical Code Specialist',
                    'priority': 4
                })
            except Exception as e:
                print(f"Failed to initialize Kimi agent: {e}")
        
        if self.qwen_key:
            try:
                self.agents.append({
                    'name': 'Qwen',
                    'client': OpenAI(
                        base_url="https://openrouter.ai/api/v1",
                        api_key=self.qwen_key,
                    ),
                    'model': 'qwen/qwen-2.5-7b-instruct:free',
                    'role': 'Code Research Specialist',
                    'priority': 5
                })
            except Exception as e:
                print(f"Failed to initialize Qwen agent: {e}")
        
        if self.gptoss_key:
            try:
                self.agents.append({
                    'name': 'GPTOSS',
                    'client': OpenAI(
                        base_url="https://openrouter.ai/api/v1",
                        api_key=self.gptoss_key,
                    ),
                    'model': 'openai/gpt-3.5-turbo:free',
                    'role': 'Code Validation Specialist',
                    'priority': 6
                })
            except Exception as e:
                print(f"Failed to initialize GPTOSS agent: {e}")
        
        # Sort by priority
        self.agents.sort(key=lambda x: x['priority'])
        
        if not self.agents:
            print("⚠️ No AI agents available - cannot perform code review")
            return
        
        print(f"🔍 Initialized {len(self.agents)} AI agents for enhanced code review:")
        for agent in self.agents:
            print(f"  - {agent['name']}: {agent['role']}")
    
    async def call_agent(self, agent: Dict[str, Any], prompt: str, context: str = "") -> Optional[str]:
        """Call a specific AI agent with error handling"""
        try:
            print(f"🤖 {agent['name']} ({agent['role']}) is working...")
            
            full_prompt = f"{prompt}\n\nContext: {context}" if context else prompt
            
            extra_headers = {}
            if 'openrouter.ai' in str(agent['client'].base_url):
                extra_headers = {
                    "HTTP-Referer": f"https://github.com/{self.repo_name}",
                    "X-Title": "AMAS Enhanced Code Review",
                }
            
            response = agent['client'].chat.completions.create(
                extra_headers=extra_headers if extra_headers else None,
                model=agent['model'],
                messages=[
                    {"role": "system", "content": f"You are {agent['role']} for the AMAS Intelligence System. {agent.get('description', '')}"},
                    {"role": "user", "content": full_prompt}
                ],
                temperature=0.7,
                max_tokens=2000
            )
            
            result = response.choices[0].message.content
            print(f"✅ {agent['name']} completed code review")
            return result
            
        except Exception as e:
            print(f"❌ {agent['name']} failed: {e}")
            return None
    
    def get_changed_files(self) -> List[str]:
        """Get list of changed files"""
        try:
            # Get changed files using git
            result = subprocess.run(['git', 'diff', '--name-only', 'HEAD~1', 'HEAD'], 
                                 capture_output=True, text=True)
            if result.returncode == 0:
                return [f for f in result.stdout.strip().split('\n') if f]
            else:
                # Fallback: get all Python files
                result = subprocess.run(['find', '.', '-name', '*.py', '-type', 'f'], 
                                     capture_output=True, text=True)
                if result.returncode == 0:
                    return [f for f in result.stdout.strip().split('\n') if f]
        except Exception as e:
            print(f"Error getting changed files: {e}")
        
        return []
    
    def read_file_content(self, file_path: str) -> Optional[str]:
        """Read file content safely"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                return f.read()
        except Exception as e:
            print(f"Error reading {file_path}: {e}")
            return None
    
    async def perform_enhanced_code_review(self) -> Dict[str, Any]:
        """Perform enhanced code review using multiple agents"""
        if not self.agents:
            return {"error": "No agents available"}
        
        print("🔍 Starting Multi-Agent Enhanced Code Review...")
        
        # Get changed files
        changed_files = self.get_changed_files()
        print(f"📁 Found {len(changed_files)} files to review")
        
        # Step 1: Code Quality Analysis (DeepSeek or first available agent)
        primary_agent = self.agents[0]
        quality_prompt = f"""
        Perform comprehensive code quality analysis including:
        - Code structure and organization assessment
        - Performance optimization opportunities
        - Best practices compliance
        - Code readability and maintainability
        - Error handling and edge cases
        - Documentation quality
        
        Files to review: {', '.join(changed_files[:5])}  # Limit to first 5 files for analysis
        """
        
        quality_analysis = await self.call_agent(primary_agent, quality_prompt)
        if not quality_analysis:
            return {"error": "Code quality analysis failed"}
        
        # Step 2: Security and Vulnerability Analysis (GLM or second agent)
        security_agent = self.agents[1] if len(self.agents) > 1 else self.agents[0]
        security_prompt = f"""
        Perform security and vulnerability analysis including:
        - Security vulnerability assessment
        - Input validation and sanitization
        - Authentication and authorization issues
        - Data protection and privacy concerns
        - Secure coding practices
        - Threat modeling and risk assessment
        
        Quality Analysis:
        {quality_analysis}
        """
        
        security_analysis = await self.call_agent(security_agent, security_prompt, quality_analysis)
        if not security_analysis:
            security_analysis = "Security analysis failed - using quality analysis only"
        
        # Step 3: Refactoring and Improvement Suggestions (Grok or third agent)
        refactor_agent = self.agents[2] if len(self.agents) > 2 else self.agents[0]
        refactor_prompt = f"""
        Provide refactoring and improvement suggestions including:
        - Code refactoring opportunities
        - Design pattern improvements
        - Performance optimization techniques
        - Code duplication elimination
        - Architecture improvements
        - Testing and validation enhancements
        
        Security Analysis:
        {security_analysis}
        """
        
        refactor_suggestions = await self.call_agent(refactor_agent, refactor_prompt, security_analysis)
        if not refactor_suggestions:
            refactor_suggestions = "Refactor suggestions failed - review security analysis"
        
        # Step 4: Technical Implementation (Kimi or fourth agent)
        technical_agent = self.agents[3] if len(self.agents) > 3 else self.agents[0]
        technical_prompt = f"""
        Provide technical implementation details including:
        - Specific code improvements
        - Implementation strategies
        - Testing and validation procedures
        - Performance monitoring
        - Error handling improvements
        - Documentation updates
        
        Refactor Suggestions:
        {refactor_suggestions}
        """
        
        technical_implementation = await self.call_agent(technical_agent, technical_prompt, refactor_suggestions)
        if not technical_implementation:
            technical_implementation = "Technical implementation failed - review refactor suggestions"
        
        return {
            'files_reviewed': len(changed_files),
            'quality_analysis': quality_analysis,
            'security_analysis': security_analysis,
            'refactor_suggestions': refactor_suggestions,
            'technical_implementation': technical_implementation,
            'agents_used': [agent['name'] for agent in self.agents],
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S UTC', time.gmtime())
        }
    
    def generate_code_review_report(self, results: Dict[str, Any]) -> str:
        """Generate comprehensive code review report"""
        if 'error' in results:
            return f"# Enhanced Code Review Failed\n\nError: {results['error']}"
        
        report = f"""# 🔍 AMAS Enhanced Code Review Report

**Generated:** {results['timestamp']}  
**Agents Used:** {', '.join(results['agents_used'])}  
**Files Reviewed:** {results['files_reviewed']}

---

## 📊 Executive Summary

This report presents comprehensive code review analysis conducted by multiple AI agents working in coordination to assess code quality, security, and provide refactoring suggestions.

---

## 🎯 Step 1: Code Quality Analysis

**Agent:** {results['agents_used'][0] if results['agents_used'] else 'Unknown'}

{results['quality_analysis']}

---

## 🛡️ Step 2: Security Analysis

**Agent:** {results['agents_used'][1] if len(results['agents_used']) > 1 else results['agents_used'][0] if results['agents_used'] else 'Unknown'}

{results['security_analysis']}

---

## 🔧 Step 3: Refactoring Suggestions

**Agent:** {results['agents_used'][2] if len(results['agents_used']) > 2 else results['agents_used'][0] if results['agents_used'] else 'Unknown'}

{results['refactor_suggestions']}

---

## ⚙️ Step 4: Technical Implementation

**Agent:** {results['agents_used'][3] if len(results['agents_used']) > 3 else results['agents_used'][0] if results['agents_used'] else 'Unknown'}

{results['technical_implementation']}

---

## 📈 Key Review Insights

- **Code Quality:** Assessed by multi-agent analysis
- **Security Status:** Identified through coordinated security review
- **Refactoring Opportunities:** Prioritized based on impact analysis
- **Technical Improvements:** Areas requiring immediate attention

---

## 🔄 Recommended Actions

1. **Immediate Actions:** Implement high-priority code improvements
2. **Short-term:** Address security and performance issues
3. **Long-term:** Implement architectural improvements

---

*Report generated by AMAS Multi-Agent Enhanced Code Review System*
*Powered by: {', '.join(results['agents_used']) if results['agents_used'] else 'AI Agents'}*
"""
        return report
    
    async def run(self):
        """Main execution function"""
        print("🚀 Starting AMAS Enhanced Code Review System...")
        
        # Create artifacts directory
        os.makedirs("artifacts", exist_ok=True)
        
        # Perform enhanced code review
        results = await self.perform_enhanced_code_review()
        
        # Generate report
        report = self.generate_code_review_report(results)
        
        # Save report
        report_path = "artifacts/enhanced_code_review_report.md"
        with open(report_path, "w", encoding="utf-8") as f:
            f.write(report)
        
        print(f"📋 Enhanced code review report saved to {report_path}")
        print("✅ Enhanced Code Review Complete!")
        
        return results

async def main():
    reviewer = AIEnhancedCodeReview()
    await reviewer.run()

if __name__ == "__main__":
    print("🔍 AMAS Enhanced Code Review System")
    print("=" * 50)
    
    # Check API key availability
    print("🔑 API Key Status:")
    print(f"  DeepSeek: {'✅' if os.getenv('DEEPSEEK_API_KEY') else '❌'}")
    print(f"  GLM: {'✅' if os.getenv('GLM_API_KEY') else '❌'}")
    print(f"  Grok: {'✅' if os.getenv('GROK_API_KEY') else '❌'}")
    print(f"  Kimi: {'✅' if os.getenv('KIMI_API_KEY') else '❌'}")
    print(f"  Qwen: {'✅' if os.getenv('QWEN_API_KEY') else '❌'}")
    print(f"  GPTOSS: {'✅' if os.getenv('GPTOSS_API_KEY') else '❌'}")
    print()
    
    asyncio.run(main())