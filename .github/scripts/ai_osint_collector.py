#!/usr/bin/env python3
"""
AI OSINT Data Collector Script
Automated intelligence gathering using multiple AI models
"""

import asyncio
import json
import os
import time
from datetime import datetime
from typing import Any, Dict, List, Optional

import requests
from openai import OpenAI

class AIOSINTCollector:
    def __init__(self):
        self.deepseek_key = os.environ.get("DEEPSEEK_API_KEY")
        self.claude_key = os.environ.get("CLAUDE_API_KEY")
        self.gpt4_key = os.environ.get("GPT4_API_KEY")
        self.glm_key = os.environ.get("GLM_API_KEY")
        self.grok_key = os.environ.get("GROK_API_KEY")
        self.kimi_key = os.environ.get("KIMI_API_KEY")
        self.qwen_key = os.environ.get("QWEN_API_KEY")
        self.gemini_key = os.environ.get("GEMINI_API_KEY")
        self.gptoss_key = os.environ.get("GPTOSS_API_KEY")
        self.repo_name = os.environ.get("REPO_NAME")
        self.issue_number = os.environ.get("ISSUE_NUMBER")

        # Initialize AI clients with intelligent fallback priority
        self.agents = []

        # Priority order: DeepSeek (most reliable), Claude, GPT-4, GLM, Grok, Kimi, Qwen, Gemini, GPTOSS
        if self.deepseek_key:
            try:
                self.agents.append(
                    {
                        "name": "DeepSeek",
                        "client": OpenAI(
                            base_url="https://api.deepseek.com/v1",
                            api_key=self.deepseek_key,
                        ),
                        "model": "deepseek-chat",
                        "role": "Primary Intelligence Analyst",
                        "priority": 1,
                    }
                )
            except Exception as e:
                print(f"Failed to initialize DeepSeek agent: {e}")

        if self.glm_key:
            try:
                self.agents.append(
                    {
                        "name": "GLM",
                        "client": OpenAI(
                            base_url="https://openrouter.ai/api/v1",
                            api_key=self.glm_key,
                        ),
                        "model": "z-ai/glm-4.5-air:free",
                        "role": "Threat Intelligence Specialist",
                        "priority": 2,
                    }
                )
            except Exception as e:
                print(f"Failed to initialize GLM agent: {e}")

        if self.grok_key:
            try:
                self.agents.append(
                    {
                        "name": "Grok",
                        "client": OpenAI(
                            base_url="https://openrouter.ai/api/v1",
                            api_key=self.grok_key,
                        ),
                        "model": "x-ai/grok-4-fast:free",
                        "role": "Strategic Intelligence Advisor",
                        "priority": 3,
                    }
                )
            except Exception as e:
                print(f"Failed to initialize Grok agent: {e}")

        if self.kimi_key:
            try:
                self.agents.append(
                    {
                        "name": "Kimi",
                        "client": OpenAI(
                            base_url="https://openrouter.ai/api/v1",
                            api_key=self.kimi_key,
                        ),
                        "model": "moonshot/moonshot-v1-8k:free",
                        "role": "Technical Intelligence Analyst",
                        "priority": 4,
                    }
                )
            except Exception as e:
                print(f"Failed to initialize Kimi agent: {e}")

        if self.qwen_key:
            try:
                self.agents.append(
                    {
                        "name": "Qwen",
                        "client": OpenAI(
                            base_url="https://openrouter.ai/api/v1",
                            api_key=self.qwen_key,
                        ),
                        "model": "qwen/qwen-2.5-7b-instruct:free",
                        "role": "Research Intelligence Specialist",
                        "priority": 5,
                    }
                )
            except Exception as e:
                print(f"Failed to initialize Qwen agent: {e}")

        if self.gptoss_key:
            try:
                self.agents.append(
                    {
                        "name": "GPTOSS",
                        "client": OpenAI(
                            base_url="https://openrouter.ai/api/v1",
                            api_key=self.gptoss_key,
                        ),
                        "model": "openai/gpt-3.5-turbo:free",
                        "role": "Quality Assurance Analyst",
                        "priority": 6,
                    }
                )
            except Exception as e:
                print(f"Failed to initialize GPTOSS agent: {e}")

        # Sort by priority
        self.agents.sort(key=lambda x: x["priority"])

        if not self.agents:
            print("⚠️ No AI agents available - cannot perform OSINT collection")
            return

        print(f"🔍 Initialized {len(self.agents)} AI agents for OSINT collection:")
        for agent in self.agents:
            print(f"  - {agent['name']}: {agent['role']}")

    async def call_agent(
        self, agent: Dict[str, Any], prompt: str, context: str = ""
    ) -> Optional[str]:
        """Call a specific AI agent with error handling"""
        try:
            print(f"🤖 {agent['name']} ({agent['role']}) is working...")

            full_prompt = f"{prompt}\n\nContext: {context}" if context else prompt

            extra_headers = {}
            if "openrouter.ai" in str(agent["client"].base_url):
                extra_headers = {
                    "HTTP-Referer": f"https://github.com/{self.repo_name}",
                    "X-Title": "AMAS OSINT Intelligence Collection",
                }

            response = agent["client"].chat.completions.create(
                extra_headers=extra_headers if extra_headers else None,
                model=agent["model"],
                messages=[
                    {
                        "role": "system",
                        "content": f"You are {agent['role']} for the AMAS Intelligence System. {agent.get('description', '')}",
                    },
                    {"role": "user", "content": full_prompt},
                ],
                temperature=0.7,
                max_tokens=2000,
            )

            result = response.choices[0].message.content
            print(f"✅ {agent['name']} completed OSINT analysis")
            return result

        except Exception as e:
            print(f"❌ {agent['name']} failed: {e}")
            return None

    async def collect_cybersecurity_intelligence(self) -> Dict[str, Any]:
        """Collect cybersecurity intelligence using multiple agents"""
        if not self.agents:
            return {"error": "No agents available"}

        print("🔍 Starting Multi-Agent OSINT Collection...")

        # Step 1: Primary Intelligence Gathering (DeepSeek or first available agent)
        primary_agent = self.agents[0]
        intelligence_prompt = """
        Gather comprehensive open source intelligence on recent cybersecurity threats and trends.
        Focus on:
        - Recent cyber attacks and breaches
        - New malware and threat actors
        - Security vulnerabilities and exploits
        - Industry security trends
        - Threat intelligence indicators
        - Emerging attack vectors
        - Security research findings
        """

        primary_intelligence = await self.call_agent(primary_agent, intelligence_prompt)
        if not primary_intelligence:
            return {"error": "Primary intelligence collection failed"}

        # Step 2: Threat Analysis (GLM or second agent)
        analysis_agent = self.agents[1] if len(self.agents) > 1 else self.agents[0]
        analysis_prompt = f"""
        Analyze this intelligence data and provide:
        - Threat actor identification and attribution
        - Attack patterns and methodologies
        - Risk assessment for different sectors
        - Vulnerability analysis
        - Threat landscape overview
        - Security recommendations

        Intelligence Data:
        {primary_intelligence}
        """

        threat_analysis = await self.call_agent(
            analysis_agent, analysis_prompt, primary_intelligence
        )
        if not threat_analysis:
            threat_analysis = "Threat analysis failed - using primary intelligence only"

        # Step 3: Strategic Assessment (Grok or third agent)
        strategy_agent = self.agents[2] if len(self.agents) > 2 else self.agents[0]
        strategy_prompt = f"""
        Based on the intelligence and threat analysis, provide:
        - Strategic threat assessment
        - Priority threat indicators
        - Defensive recommendations
        - Monitoring and detection strategies
        - Risk mitigation approaches
        - Future threat predictions

        Analysis Data:
        {threat_analysis}
        """

        strategic_assessment = await self.call_agent(
            strategy_agent, strategy_prompt, threat_analysis
        )
        if not strategic_assessment:
            strategic_assessment = "Strategic assessment failed - review analysis data"

        # Step 4: Technical Analysis (Kimi or fourth agent)
        technical_agent = self.agents[3] if len(self.agents) > 3 else self.agents[0]
        technical_prompt = f"""
        Provide technical analysis focusing on:
        - Technical indicators of compromise (IOCs)
        - Malware analysis and characteristics
        - Network security implications
        - System vulnerabilities
        - Technical countermeasures
        - Implementation recommendations

        Intelligence Context:
        {strategic_assessment}
        """

        technical_analysis = await self.call_agent(
            technical_agent, technical_prompt, strategic_assessment
        )
        if not technical_analysis:
            technical_analysis = (
                "Technical analysis failed - review strategic assessment"
            )

        return {
            "primary_intelligence": primary_intelligence,
            "threat_analysis": threat_analysis,
            "strategic_assessment": strategic_assessment,
            "technical_analysis": technical_analysis,
            "agents_used": [agent["name"] for agent in self.agents],
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime()),
        }

    def generate_osint_report(self, results: Dict[str, Any]) -> str:
        """Generate comprehensive OSINT intelligence report"""
        if "error" in results:
            return f"# OSINT Collection Failed\n\nError: {results['error']}"

        report = f"""# 🔍 AMAS OSINT Intelligence Report

**Generated:** {results['timestamp']}
**Agents Used:** {', '.join(results['agents_used'])}

---

## 📊 Executive Summary

This report presents comprehensive open source intelligence (OSINT) analysis conducted by multiple AI agents working in coordination to assess current cybersecurity threats and trends.

---

## 🕵️ Step 1: Primary Intelligence Gathering

**Agent:** {results['agents_used'][0] if results['agents_used'] else 'Unknown'}

{results['primary_intelligence']}

---

## 🎯 Step 2: Threat Analysis

**Agent:** {results['agents_used'][1] if len(results['agents_used']) > 1 else results['agents_used'][0] if results['agents_used'] else 'Unknown'}

{results['threat_analysis']}

---

## 🏛️ Step 3: Strategic Assessment

**Agent:** {results['agents_used'][2] if len(results['agents_used']) > 2 else results['agents_used'][0] if results['agents_used'] else 'Unknown'}

{results['strategic_assessment']}

---

## 🔧 Step 4: Technical Analysis

**Agent:** {results['agents_used'][3] if len(results['agents_used']) > 3 else results['agents_used'][0] if results['agents_used'] else 'Unknown'}

{results['technical_analysis']}

---

## 📈 Key Intelligence Insights

- **Threat Level:** Assessed by multi-agent analysis
- **Primary Concerns:** Identified through coordinated intelligence gathering
- **Strategic Recommendations:** Prioritized based on threat analysis
- **Technical Indicators:** Areas requiring enhanced monitoring

---

## 🔄 Recommended Actions

1. **Immediate Actions:** Implement high-priority defensive measures
2. **Short-term:** Enhance monitoring and detection capabilities
3. **Long-term:** Develop strategic countermeasures and resilience

---

*Report generated by AMAS Multi-Agent OSINT Collection System*
*Powered by: {', '.join(results['agents_used']) if results['agents_used'] else 'AI Agents'}*
"""
        return report

    async def run(self):
        """Main execution function"""
        print("🚀 Starting AMAS OSINT Collection System...")

        # Create artifacts directory
        os.makedirs("artifacts", exist_ok=True)

        # Collect intelligence
        results = await self.collect_cybersecurity_intelligence()

        # Generate report
        report = self.generate_osint_report(results)

        # Save report
        report_path = "artifacts/osint_report.md"
        with open(report_path, "w", encoding="utf-8") as f:
            f.write(report)

        print(f"📋 OSINT report saved to {report_path}")
        print("✅ OSINT Collection Complete!")

        return results

async def main():
    collector = AIOSINTCollector()
    await collector.run()

if __name__ == "__main__":
    print("🔍 AMAS OSINT Intelligence Collection System")
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
