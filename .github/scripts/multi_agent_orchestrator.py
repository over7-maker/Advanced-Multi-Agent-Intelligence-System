#!/usr/bin/env python3
"""
Multi-Agent Orchestrator Script
Coordinates multiple AI agents for comprehensive analysis
"""

import os
import asyncio
from openai import OpenAI
from typing import Dict, List, Any, Optional
import time

class MultiAgentOrchestrator:
    def __init__(self):
        self.deepseek_key = os.environ.get('DEEPSEEK_API_KEY')
        self.glm_key = os.environ.get('GLM_API_KEY')
        self.grok_key = os.environ.get('GROK_API_KEY')
        self.kimi_key = os.environ.get('KIMI_API_KEY')
        self.qwen_key = os.environ.get('QWEN_API_KEY')
        self.gptoss_key = os.environ.get('GPTOSS_API_KEY')
        
        # Initialize AI clients with intelligent fallback priority
        self.agents = []
        
        # DeepSeek agent (most reliable)
        if self.deepseek_key:
            try:
                self.agents.append({
                    'name': 'DeepSeek',
                    'client': OpenAI(
                        base_url="https://api.deepseek.com/v1",
                        api_key=self.deepseek_key,
                    ),
                    'model': 'deepseek-chat',
                    'role': 'OSINT Collector',
                    'description': 'Gathers initial intelligence and data',
                    'priority': 1
                })
            except Exception as e:
                print(f"Failed to initialize DeepSeek agent: {e}")
        
        # GLM agent
        if self.glm_key:
            try:
                self.agents.append({
                    'name': 'GLM',
                    'client': OpenAI(
                        base_url="https://openrouter.ai/api/v1",
                        api_key=self.glm_key,
                    ),
                    'model': 'z-ai/glm-4.5-air:free',
                    'role': 'Threat Analyst',
                    'description': 'Analyzes threats and patterns',
                    'priority': 2
                })
            except Exception as e:
                print(f"Failed to initialize GLM agent: {e}")
        
        # Grok agent
        if self.grok_key:
            try:
                self.agents.append({
                    'name': 'Grok',
                    'client': OpenAI(
                        base_url="https://openrouter.ai/api/v1",
                        api_key=self.grok_key,
                    ),
                    'model': 'x-ai/grok-4-fast:free',
                    'role': 'Strategic Advisor',
                    'description': 'Provides recommendations and strategy',
                    'priority': 3
                })
            except Exception as e:
                print(f"Failed to initialize Grok agent: {e}")
        
        # Kimi agent
        if self.kimi_key:
            try:
                self.agents.append({
                    'name': 'Kimi',
                    'client': OpenAI(
                        base_url="https://openrouter.ai/api/v1",
                        api_key=self.kimi_key,
                    ),
                    'model': 'moonshot/moonshot-v1-8k:free',
                    'role': 'Technical Specialist',
                    'description': 'Provides technical analysis and implementation',
                    'priority': 4
                })
            except Exception as e:
                print(f"Failed to initialize Kimi agent: {e}")
        
        # Qwen agent
        if self.qwen_key:
            try:
                self.agents.append({
                    'name': 'Qwen',
                    'client': OpenAI(
                        base_url="https://openrouter.ai/api/v1",
                        api_key=self.qwen_key,
                    ),
                    'model': 'qwen/qwen-2.5-7b-instruct:free',
                    'role': 'Research Assistant',
                    'description': 'Conducts research and fact-checking',
                    'priority': 5
                })
            except Exception as e:
                print(f"Failed to initialize Qwen agent: {e}")
        
        # GPTOSS agent
        if self.gptoss_key:
            try:
                self.agents.append({
                    'name': 'GPTOSS',
                    'client': OpenAI(
                        base_url="https://openrouter.ai/api/v1",
                        api_key=self.gptoss_key,
                    ),
                    'model': 'openai/gpt-3.5-turbo:free',
                    'role': 'Quality Assurance',
                    'description': 'Reviews and validates outputs',
                    'priority': 6
                })
            except Exception as e:
                print(f"Failed to initialize GPTOSS agent: {e}")
        
        # Sort by priority
        self.agents.sort(key=lambda x: x['priority'])
        
        if not self.agents:
            print("⚠️ No AI agents available - cannot perform analysis")
            return
        
        print(f"🤖 Initialized {len(self.agents)} AI agents:")
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
                    "HTTP-Referer": "https://github.com/AMAS-Intelligence-System",
                    "X-Title": "AMAS Multi-Agent Analysis",
                }
            
            response = agent['client'].chat.completions.create(
                extra_headers=extra_headers if extra_headers else None,
                model=agent['model'],
                messages=[
                    {"role": "system", "content": f"You are {agent['role']} for the AMAS Intelligence System. {agent['description']}"},
                    {"role": "user", "content": full_prompt}
                ],
                temperature=0.7,
                max_tokens=1500
            )
            
            result = response.choices[0].message.content
            print(f"✅ {agent['name']} completed analysis")
            return result
            
        except Exception as e:
            print(f"❌ {agent['name']} failed: {e}")
            return None
    
    async def run_intelligence_analysis(self) -> Dict[str, Any]:
        """Run multi-agent intelligence analysis"""
        if not self.agents:
            return {"error": "No agents available"}
        
        print("🚀 Starting Multi-Agent Intelligence Analysis...")
        
        # Step 1: OSINT Collection (DeepSeek or first available agent)
        osint_agent = self.agents[0]  # Use first available agent
        initial_prompt = """
        Gather comprehensive open source intelligence on recent cyber attacks targeting financial institutions.
        Focus on:
        - Attack vectors and methods
        - Affected organizations
        - Timeline of events
        - Attribution indicators
        - Impact assessment
        """
        
        osint_result = await self.call_agent(osint_agent, initial_prompt)
        if not osint_result:
            return {"error": "OSINT collection failed"}
        
        # Step 2: Threat Analysis (GLM or second agent)
        analysis_agent = self.agents[1] if len(self.agents) > 1 else self.agents[0]
        analysis_prompt = f"""
        Analyze this intelligence data and extract:
        - Threat actors and their tactics, techniques, and procedures (TTPs)
        - Attack patterns and methodologies
        - Vulnerabilities being exploited
        - Potential future targets
        - Risk assessment for different sectors
        
        Intelligence Data:
        {osint_result}
        """
        
        analysis_result = await self.call_agent(analysis_agent, analysis_prompt, osint_result)
        if not analysis_result:
            analysis_result = "Threat analysis failed - using OSINT data only"
        
        # Step 3: Strategic Recommendations (Grok or third agent)
        strategy_agent = self.agents[2] if len(self.agents) > 2 else self.agents[0]
        strategy_prompt = f"""
        Based on the intelligence and threat analysis, provide:
        - Immediate defensive measures
        - Long-term strategic recommendations
        - Priority actions for security teams
        - Risk mitigation strategies
        - Monitoring and detection improvements
        
        Analysis Data:
        {analysis_result}
        """
        
        strategy_result = await self.call_agent(strategy_agent, strategy_prompt, analysis_result)
        if not strategy_result:
            strategy_result = "Strategic recommendations failed - review analysis data"
        
        return {
            'osint': osint_result,
            'analysis': analysis_result,
            'strategy': strategy_result,
            'agents_used': [agent['name'] for agent in self.agents],
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S UTC', time.gmtime())
        }
    
    def generate_report(self, results: Dict[str, Any]) -> str:
        """Generate comprehensive intelligence report"""
        if 'error' in results:
            return f"# Multi-Agent Analysis Failed\n\nError: {results['error']}"
        
        report = f"""# 🤖 AMAS Multi-Agent Intelligence Report

**Generated:** {results['timestamp']}  
**Agents Used:** {', '.join(results['agents_used'])}

---

## 📊 Executive Summary

This report presents a comprehensive intelligence analysis conducted by multiple AI agents working in coordination to assess recent cyber threats targeting financial institutions.

---

## 🔍 Step 1: Open Source Intelligence (OSINT)

**Agent:** {results['agents_used'][0] if results['agents_used'] else 'Unknown'}

{results['osint']}

---

## 🎯 Step 2: Threat Analysis

**Agent:** {results['agents_used'][1] if len(results['agents_used']) > 1 else results['agents_used'][0] if results['agents_used'] else 'Unknown'}

{results['analysis']}

---

## 💡 Step 3: Strategic Recommendations

**Agent:** {results['agents_used'][2] if len(results['agents_used']) > 2 else results['agents_used'][0] if results['agents_used'] else 'Unknown'}

{results['strategy']}

---

## 📈 Key Insights

- **Threat Level:** Assessed by multi-agent analysis
- **Primary Concerns:** Identified through coordinated intelligence gathering
- **Recommended Actions:** Prioritized based on threat analysis
- **Monitoring Focus:** Areas requiring enhanced surveillance

---

## 🔄 Next Steps

1. **Immediate Actions:** Implement high-priority defensive measures
2. **Short-term:** Enhance monitoring and detection capabilities
3. **Long-term:** Develop strategic countermeasures and resilience

---

*Report generated by AMAS Multi-Agent Intelligence System*
*Powered by: {', '.join(results['agents_used']) if results['agents_used'] else 'AI Agents'}*
"""
        return report
    
    async def run(self):
        """Main execution function"""
        print("🚀 Starting AMAS Multi-Agent Orchestrator...")
        
        # Create artifacts directory
        os.makedirs("artifacts", exist_ok=True)
        
        # Run intelligence analysis
        results = await self.run_intelligence_analysis()
        
        # Generate report
        report = self.generate_report(results)
        
        # Save report
        report_path = "artifacts/multi_agent_report.md"
        with open(report_path, "w", encoding="utf-8") as f:
            f.write(report)
        
        print(f"📋 Report saved to {report_path}")
        print("✅ Multi-Agent Analysis Complete!")
        
        return results

async def main():
    orchestrator = MultiAgentOrchestrator()
    await orchestrator.run()

if __name__ == "__main__":
    print("🔍 AMAS Multi-Agent Intelligence System")
    print("=" * 50)
    
    # Check API key availability
    print("🔑 API Key Status:")
    print(f"  DeepSeek: {'✅' if os.getenv('DEEPSEEK_API_KEY') else '❌'}")
    print(f"  GLM: {'✅' if os.getenv('GLM_API_KEY') else '❌'}")
    print(f"  Grok: {'✅' if os.getenv('GROK_API_KEY') else '❌'}")
    print()
    
    asyncio.run(main())
