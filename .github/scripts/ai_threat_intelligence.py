#!/usr/bin/env python3
"""
AI Threat Intelligence Analysis Script
Comprehensive threat analysis using multiple AI models
"""

import os
import asyncio
import requests
from openai import OpenAI
from typing import Dict, List, Any, Optional
import time
import json
from datetime import datetime

class AIThreatIntelligence:
    def __init__(self):
        self.deepseek_key = os.environ.get('DEEPSEEK_API_KEY')
        self.glm_key = os.environ.get('GLM_API_KEY')
        self.grok_key = os.environ.get('GROK_API_KEY')
        self.kimi_key = os.environ.get('KIMI_API_KEY')
        self.qwen_key = os.environ.get('QWEN_API_KEY')
        self.gptoss_key = os.environ.get('GPTOSS_API_KEY')
        self.repo_name = os.environ.get('REPO_NAME')
        self.issue_number = os.environ.get('ISSUE_NUMBER')
        
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
                    'role': 'Primary Threat Analyst',
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
                    'role': 'Threat Intelligence Specialist',
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
                    'role': 'Strategic Threat Advisor',
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
                    'role': 'Technical Threat Analyst',
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
                    'role': 'Threat Research Specialist',
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
                    'role': 'Threat Validation Specialist',
                    'priority': 6
                })
            except Exception as e:
                print(f"Failed to initialize GPTOSS agent: {e}")
        
        # Sort by priority
        self.agents.sort(key=lambda x: x['priority'])
        
        if not self.agents:
            print("⚠️ No AI agents available - cannot perform threat analysis")
            return
        
        print(f"🛡️ Initialized {len(self.agents)} AI agents for threat intelligence:")
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
                    "X-Title": "AMAS Threat Intelligence Analysis",
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
            print(f"✅ {agent['name']} completed threat analysis")
            return result
            
        except Exception as e:
            print(f"❌ {agent['name']} failed: {e}")
            return None
    
    async def analyze_threat_landscape(self) -> Dict[str, Any]:
        """Analyze threat landscape using multiple agents"""
        if not self.agents:
            return {"error": "No agents available"}
        
        print("🛡️ Starting Multi-Agent Threat Intelligence Analysis...")
        
        # Step 1: Threat Landscape Assessment (DeepSeek or first available agent)
        primary_agent = self.agents[0]
        threat_prompt = """
        Analyze the current cybersecurity threat landscape and provide:
        - Active threat actors and their capabilities
        - Recent attack campaigns and methodologies
        - Emerging threat vectors and attack surfaces
        - Threat actor motivations and objectives
        - Geographic and sectoral threat distribution
        - Threat evolution and adaptation patterns
        - Critical infrastructure targeting trends
        """
        
        threat_landscape = await self.call_agent(primary_agent, threat_prompt)
        if not threat_landscape:
            return {"error": "Threat landscape analysis failed"}
        
        # Step 2: Threat Actor Analysis (GLM or second agent)
        analysis_agent = self.agents[1] if len(self.agents) > 1 else self.agents[0]
        actor_prompt = f"""
        Analyze threat actors and provide:
        - Threat actor profiles and capabilities
        - Attack techniques and procedures (TTPs)
        - Infrastructure and tooling analysis
        - Attribution indicators and evidence
        - Threat actor relationships and collaborations
        - Evolution of threat actor capabilities
        - Counter-intelligence recommendations
        
        Threat Landscape:
        {threat_landscape}
        """
        
        threat_actors = await self.call_agent(analysis_agent, actor_prompt, threat_landscape)
        if not threat_actors:
            threat_actors = "Threat actor analysis failed - using landscape data only"
        
        # Step 3: Strategic Threat Assessment (Grok or third agent)
        strategy_agent = self.agents[2] if len(self.agents) > 2 else self.agents[0]
        strategy_prompt = f"""
        Provide strategic threat assessment including:
        - Risk prioritization and threat ranking
        - Strategic implications for organizations
        - Threat mitigation strategies
        - Intelligence requirements and gaps
        - Strategic recommendations for defense
        - Threat forecasting and predictions
        - Resource allocation recommendations
        
        Threat Analysis:
        {threat_actors}
        """
        
        strategic_assessment = await self.call_agent(strategy_agent, strategy_prompt, threat_actors)
        if not strategic_assessment:
            strategic_assessment = "Strategic assessment failed - review threat analysis"
        
        # Step 4: Technical Threat Analysis (Kimi or fourth agent)
        technical_agent = self.agents[3] if len(self.agents) > 3 else self.agents[0]
        technical_prompt = f"""
        Provide technical threat analysis focusing on:
        - Technical indicators of compromise (IOCs)
        - Malware families and characteristics
        - Attack infrastructure and C2 servers
        - Technical countermeasures and detection
        - Vulnerability exploitation patterns
        - Network security implications
        - Technical implementation recommendations
        
        Strategic Context:
        {strategic_assessment}
        """
        
        technical_analysis = await self.call_agent(technical_agent, technical_prompt, strategic_assessment)
        if not technical_analysis:
            technical_analysis = "Technical analysis failed - review strategic assessment"
        
        return {
            'threat_landscape': threat_landscape,
            'threat_actors': threat_actors,
            'strategic_assessment': strategic_assessment,
            'technical_analysis': technical_analysis,
            'agents_used': [agent['name'] for agent in self.agents],
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S UTC', time.gmtime())
        }
    
    def generate_threat_report(self, results: Dict[str, Any]) -> str:
        """Generate comprehensive threat intelligence report"""
        if 'error' in results:
            return f"# Threat Intelligence Analysis Failed\n\nError: {results['error']}"
        
        report = f"""# 🛡️ AMAS Threat Intelligence Report

**Generated:** {results['timestamp']}  
**Agents Used:** {', '.join(results['agents_used'])}

---

## 📊 Executive Summary

This report presents comprehensive threat intelligence analysis conducted by multiple AI agents working in coordination to assess current cybersecurity threats and provide actionable intelligence.

---

## 🌍 Step 1: Threat Landscape Assessment

**Agent:** {results['agents_used'][0] if results['agents_used'] else 'Unknown'}

{results['threat_landscape']}

---

## 👥 Step 2: Threat Actor Analysis

**Agent:** {results['agents_used'][1] if len(results['agents_used']) > 1 else results['agents_used'][0] if results['agents_used'] else 'Unknown'}

{results['threat_actors']}

---

## 🏛️ Step 3: Strategic Threat Assessment

**Agent:** {results['agents_used'][2] if len(results['agents_used']) > 2 else results['agents_used'][0] if results['agents_used'] else 'Unknown'}

{results['strategic_assessment']}

---

## 🔧 Step 4: Technical Threat Analysis

**Agent:** {results['agents_used'][3] if len(results['agents_used']) > 3 else results['agents_used'][0] if results['agents_used'] else 'Unknown'}

{results['technical_analysis']}

---

## 📈 Key Threat Intelligence Insights

- **Threat Level:** Assessed by multi-agent analysis
- **Primary Threats:** Identified through coordinated intelligence gathering
- **Strategic Recommendations:** Prioritized based on threat analysis
- **Technical Indicators:** Areas requiring enhanced monitoring

---

## 🔄 Recommended Actions

1. **Immediate Actions:** Implement high-priority defensive measures
2. **Short-term:** Enhance monitoring and detection capabilities
3. **Long-term:** Develop strategic countermeasures and resilience

---

*Report generated by AMAS Multi-Agent Threat Intelligence System*
*Powered by: {', '.join(results['agents_used']) if results['agents_used'] else 'AI Agents'}*
"""
        return report
    
    async def run(self):
        """Main execution function"""
        print("🚀 Starting AMAS Threat Intelligence System...")
        
        # Create artifacts directory
        os.makedirs("artifacts", exist_ok=True)
        
        # Analyze threats
        results = await self.analyze_threat_landscape()
        
        # Generate report
        report = self.generate_threat_report(results)
        
        # Save report
        report_path = "artifacts/threat_intelligence_report.md"
        with open(report_path, "w", encoding="utf-8") as f:
            f.write(report)
        
        print(f"📋 Threat intelligence report saved to {report_path}")
        print("✅ Threat Intelligence Analysis Complete!")
        
        return results

async def main():
    analyzer = AIThreatIntelligence()
    await analyzer.run()

if __name__ == "__main__":
    print("🛡️ AMAS Threat Intelligence Analysis System")
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