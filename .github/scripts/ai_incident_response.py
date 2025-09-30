#!/usr/bin/env python3
"""
AI Incident Response Automation Script
Automated incident triage and response using multiple AI models
"""

import os
import asyncio
import requests
from openai import OpenAI
from typing import Dict, List, Any, Optional
import time
import json
from datetime import datetime


class AIIncidentResponse:
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
        self.issue_title = os.environ.get("ISSUE_TITLE", "")
        self.issue_body = os.environ.get("ISSUE_BODY", "")

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
                        "role": "Primary Incident Analyst",
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
                        "role": "Threat Assessment Specialist",
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
                        "role": "Strategic Response Advisor",
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
                        "role": "Technical Response Specialist",
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
                        "role": "Incident Research Specialist",
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
                        "role": "Response Validation Specialist",
                        "priority": 6,
                    }
                )
            except Exception as e:
                print(f"Failed to initialize GPTOSS agent: {e}")

        # Sort by priority
        self.agents.sort(key=lambda x: x["priority"])

        if not self.agents:
            print("⚠️ No AI agents available - cannot perform incident response")
            return

        print(f"🚨 Initialized {len(self.agents)} AI agents for incident response:")
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
                    "X-Title": "AMAS Incident Response System",
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
            print(f"✅ {agent['name']} completed incident analysis")
            return result

        except Exception as e:
            print(f"❌ {agent['name']} failed: {e}")
            return None

    def analyze_incident_severity(self, title: str, body: str) -> str:
        """Analyze incident severity based on content"""
        content = f"{title} {body}".lower()

        # Critical indicators
        critical_indicators = [
            "critical",
            "urgent",
            "breach",
            "compromise",
            "attack",
            "exploit",
            "zero-day",
        ]
        high_indicators = [
            "high",
            "severe",
            "malware",
            "phishing",
            "suspicious",
            "anomaly",
        ]
        medium_indicators = ["medium", "moderate", "warning", "alert", "unusual"]

        critical_count = sum(
            1 for indicator in critical_indicators if indicator in content
        )
        high_count = sum(1 for indicator in high_indicators if indicator in content)
        medium_count = sum(1 for indicator in medium_indicators if indicator in content)

        if critical_count >= 2:
            return "CRITICAL"
        elif critical_count >= 1 or high_count >= 2:
            return "HIGH"
        elif high_count >= 1 or medium_count >= 2:
            return "MEDIUM"
        else:
            return "LOW"

    async def process_incident(self) -> Dict[str, Any]:
        """Process incident using multiple agents"""
        if not self.agents:
            return {"error": "No agents available"}

        print("🚨 Starting Multi-Agent Incident Response...")

        # Analyze incident severity
        severity = self.analyze_incident_severity(self.issue_title, self.issue_body)
        print(f"📊 Incident Severity: {severity}")

        # Step 1: Initial Incident Assessment (DeepSeek or first available agent)
        primary_agent = self.agents[0]
        assessment_prompt = f"""
        Analyze this security incident and provide:
        - Incident classification and severity assessment
        - Initial impact analysis
        - Potential attack vectors and methods
        - Immediate threat indicators
        - Preliminary containment recommendations
        - Evidence collection priorities
        
        Incident Details:
        Title: {self.issue_title}
        Description: {self.issue_body}
        Severity: {severity}
        """

        incident_assessment = await self.call_agent(primary_agent, assessment_prompt)
        if not incident_assessment:
            return {"error": "Incident assessment failed"}

        # Step 2: Threat Analysis (GLM or second agent)
        analysis_agent = self.agents[1] if len(self.agents) > 1 else self.agents[0]
        threat_prompt = f"""
        Provide detailed threat analysis including:
        - Threat actor identification and attribution
        - Attack techniques and procedures (TTPs)
        - Indicators of compromise (IOCs)
        - Threat intelligence correlation
        - Attack timeline reconstruction
        - Threat actor motivations and objectives
        - Counter-intelligence recommendations
        
        Incident Assessment:
        {incident_assessment}
        """

        threat_analysis = await self.call_agent(
            analysis_agent, threat_prompt, incident_assessment
        )
        if not threat_analysis:
            threat_analysis = "Threat analysis failed - using incident assessment only"

        # Step 3: Response Strategy (Grok or third agent)
        strategy_agent = self.agents[2] if len(self.agents) > 2 else self.agents[0]
        strategy_prompt = f"""
        Develop comprehensive response strategy including:
        - Immediate response actions and priorities
        - Containment and isolation strategies
        - Evidence preservation procedures
        - Communication and notification plans
        - Recovery and restoration procedures
        - Lessons learned and improvement recommendations
        - Resource allocation and team coordination
        
        Threat Analysis:
        {threat_analysis}
        """

        response_strategy = await self.call_agent(
            strategy_agent, strategy_prompt, threat_analysis
        )
        if not response_strategy:
            response_strategy = "Response strategy failed - review threat analysis"

        # Step 4: Technical Response (Kimi or fourth agent)
        technical_agent = self.agents[3] if len(self.agents) > 3 else self.agents[0]
        technical_prompt = f"""
        Provide technical response procedures including:
        - Technical containment measures
        - System isolation and quarantine procedures
        - Network security adjustments
        - Malware analysis and removal procedures
        - System hardening recommendations
        - Monitoring and detection enhancements
        - Technical implementation steps
        
        Response Strategy:
        {response_strategy}
        """

        technical_response = await self.call_agent(
            technical_agent, technical_prompt, response_strategy
        )
        if not technical_response:
            technical_response = "Technical response failed - review response strategy"

        return {
            "severity": severity,
            "incident_assessment": incident_assessment,
            "threat_analysis": threat_analysis,
            "response_strategy": response_strategy,
            "technical_response": technical_response,
            "agents_used": [agent["name"] for agent in self.agents],
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime()),
        }

    def generate_incident_report(self, results: Dict[str, Any]) -> str:
        """Generate comprehensive incident response report"""
        if "error" in results:
            return f"# Incident Response Failed\n\nError: {results['error']}"

        severity_emoji = {"CRITICAL": "🔴", "HIGH": "🟠", "MEDIUM": "🟡", "LOW": "🟢"}

        report = f"""# 🚨 AMAS Incident Response Report

**Generated:** {results['timestamp']}  
**Agents Used:** {', '.join(results['agents_used'])}  
**Severity:** {severity_emoji.get(results['severity'], '⚪')} {results['severity']}

---

## 📊 Executive Summary

This report presents comprehensive incident response analysis conducted by multiple AI agents working in coordination to assess and respond to the security incident.

---

## 🔍 Step 1: Incident Assessment

**Agent:** {results['agents_used'][0] if results['agents_used'] else 'Unknown'}

{results['incident_assessment']}

---

## 🎯 Step 2: Threat Analysis

**Agent:** {results['agents_used'][1] if len(results['agents_used']) > 1 else results['agents_used'][0] if results['agents_used'] else 'Unknown'}

{results['threat_analysis']}

---

## 🏛️ Step 3: Response Strategy

**Agent:** {results['agents_used'][2] if len(results['agents_used']) > 2 else results['agents_used'][0] if results['agents_used'] else 'Unknown'}

{results['response_strategy']}

---

## 🔧 Step 4: Technical Response

**Agent:** {results['agents_used'][3] if len(results['agents_used']) > 3 else results['agents_used'][0] if results['agents_used'] else 'Unknown'}

{results['technical_response']}

---

## 📈 Key Response Insights

- **Incident Severity:** {results['severity']} - Assessed by multi-agent analysis
- **Primary Threats:** Identified through coordinated intelligence gathering
- **Response Priorities:** Prioritized based on threat analysis
- **Technical Actions:** Areas requiring immediate attention

---

## 🔄 Immediate Actions Required

1. **Critical Actions:** Implement high-priority response measures
2. **Containment:** Isolate affected systems and networks
3. **Investigation:** Conduct thorough forensic analysis
4. **Recovery:** Restore systems with enhanced security

---

*Report generated by AMAS Multi-Agent Incident Response System*
*Powered by: {', '.join(results['agents_used']) if results['agents_used'] else 'AI Agents'}*
"""
        return report

    async def run(self):
        """Main execution function"""
        print("🚀 Starting AMAS Incident Response System...")

        # Create artifacts directory
        os.makedirs("artifacts", exist_ok=True)

        # Process incident
        results = await self.process_incident()

        # Generate report
        report = self.generate_incident_report(results)

        # Save report
        report_path = "artifacts/incident_response_report.md"
        with open(report_path, "w", encoding="utf-8") as f:
            f.write(report)

        print(f"📋 Incident response report saved to {report_path}")
        print("✅ Incident Response Complete!")

        return results


async def main():
    responder = AIIncidentResponse()
    await responder.run()


if __name__ == "__main__":
    print("🚨 AMAS Incident Response System")
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
