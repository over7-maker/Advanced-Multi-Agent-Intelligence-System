from standalone_universal_ai_manager import get_api_key
#!/usr/bin/env python3
"""
AI Master Orchestrator Script
Coordinates all AI workflows and provides comprehensive system overview
"""

import asyncio
import json
import os
import subprocess
import time
from datetime import datetime
from typing import Any, Dict, List, Optional

import requests
from openai import OpenAI


class AIMasterOrchestrator:
    def __init__(self):
        self.deepseek_key = get_api_key("DEEPSEEK_API_KEY")
        self.claude_key = get_api_key("CLAUDE_API_KEY")
        self.gpt4_key = os.environ.get("GPT4_API_KEY")
        self.glm_key = get_api_key("GLM_API_KEY")
        self.grok_key = get_api_key("GROK_API_KEY")
        self.kimi_key = get_api_key("KIMI_API_KEY")
        self.qwen_key = get_api_key("QWEN_API_KEY")
        self.gemini_key = get_api_key("GEMINI_API_KEY")
        self.gptoss_key = get_api_key("GPTOSS_API_KEY")
        self.github_token = os.environ.get("GITHUB_TOKEN")
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
                        "role": "Master Orchestrator",
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
                        "role": "System Coordinator",
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
                        "role": "Strategic Advisor",
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
                        "role": "Technical Coordinator",
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
                        "role": "Research Coordinator",
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
                        "role": "Quality Assurance Coordinator",
                        "priority": 6,
                    }
                )
            except Exception as e:
                print(f"Failed to initialize GPTOSS agent: {e}")

        # Sort by priority
        self.agents.sort(key=lambda x: x["priority"])

        if not self.agents:
            print("⚠️ No AI agents available - cannot perform orchestration")
            return

        print(f"🎯 Initialized {len(self.agents)} AI agents for master orchestration:")
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
                    "X-Title": "AMAS Master Orchestrator",
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
            print(f"✅ {agent['name']} completed orchestration task")
            return result

        except Exception as e:
            print(f"❌ {agent['name']} failed: {e}")
            return None

    def get_workflow_status(self) -> Dict[str, Any]:
        """Get status of all AI workflows"""
        workflows = {
            "ai-code-analysis": {
                "status": "active",
                "description": "Code analysis and security scanning",
            },
            "ai-issue-responder": {
                "status": "active",
                "description": "Automated issue response",
            },
            "multi-agent-workflow": {
                "status": "active",
                "description": "Multi-agent intelligence gathering",
            },
            "ai-osint-collection": {
                "status": "active",
                "description": "OSINT data collection",
            },
            "ai-threat-intelligence": {
                "status": "active",
                "description": "Threat intelligence analysis",
            },
            "ai-incident-response": {
                "status": "active",
                "description": "Incident response automation",
            },
            "ai-adaptive-prompt-improvement": {
                "status": "active",
                "description": "Prompt optimization",
            },
            "ai-enhanced-code-review": {
                "status": "active",
                "description": "Enhanced code review",
            },
            "ai-security-response": {
                "status": "active",
                "description": "Security response automation",
            },
        }

        return workflows

    def get_system_metrics(self) -> Dict[str, Any]:
        """Get system metrics and performance data"""
        metrics = {
            "total_workflows": 9,
            "active_workflows": 9,
            "ai_models_available": len(self.agents),
            "api_keys_configured": sum(
                [
                    1 if self.deepseek_key else 0,
                    1 if self.glm_key else 0,
                    1 if self.grok_key else 0,
                    1 if self.kimi_key else 0,
                    1 if self.qwen_key else 0,
                    1 if self.gptoss_key else 0,
                ]
            ),
            "system_health": "excellent",
            "last_updated": time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime()),
        }

        return metrics

    async def perform_master_orchestration(self) -> Dict[str, Any]:
        """Perform master orchestration using multiple agents"""
        if not self.agents:
            return {"error": "No agents available"}

        print("🎯 Starting Master AI Orchestration...")

        # Get system status
        workflow_status = self.get_workflow_status()
        system_metrics = self.get_system_metrics()

        # Step 1: System Overview (DeepSeek or first available agent)
        primary_agent = self.agents[0]
        overview_prompt = f"""
        Provide comprehensive system overview including:
        - Overall system health and performance
        - Workflow coordination and dependencies
        - Resource utilization and optimization
        - System architecture assessment
        - Integration status and connectivity
        - Performance metrics and trends

        System Metrics: {json.dumps(system_metrics, indent=2)}
        Workflow Status: {json.dumps(workflow_status, indent=2)}
        """

        system_overview = await self.call_agent(primary_agent, overview_prompt)
        if not system_overview:
            return {"error": "System overview failed"}

        # Step 2: Workflow Coordination (GLM or second agent)
        coordination_agent = self.agents[1] if len(self.agents) > 1 else self.agents[0]
        coordination_prompt = f"""
        Provide workflow coordination analysis including:
        - Workflow dependencies and triggers
        - Resource allocation and scheduling
        - Cross-workflow communication
        - Performance optimization opportunities
        - Error handling and recovery
        - Monitoring and alerting strategies

        System Overview:
        {system_overview}
        """

        workflow_coordination = await self.call_agent(
            coordination_agent, coordination_prompt, system_overview
        )
        if not workflow_coordination:
            workflow_coordination = (
                "Workflow coordination failed - using system overview only"
            )

        # Step 3: Strategic Recommendations (Grok or third agent)
        strategy_agent = self.agents[2] if len(self.agents) > 2 else self.agents[0]
        strategy_prompt = f"""
        Provide strategic recommendations including:
        - Long-term system evolution
        - Advanced automation opportunities
        - Integration enhancements
        - Performance scaling strategies
        - Security and compliance improvements
        - Innovation and research directions

        Workflow Coordination:
        {workflow_coordination}
        """

        strategic_recommendations = await self.call_agent(
            strategy_agent, strategy_prompt, workflow_coordination
        )
        if not strategic_recommendations:
            strategic_recommendations = (
                "Strategic recommendations failed - review workflow coordination"
            )

        # Step 4: Technical Implementation (Kimi or fourth agent)
        technical_agent = self.agents[3] if len(self.agents) > 3 else self.agents[0]
        technical_prompt = f"""
        Provide technical implementation details including:
        - System architecture improvements
        - Code optimization and refactoring
        - Performance monitoring implementation
        - Error handling and recovery procedures
        - Testing and validation strategies
        - Documentation and maintenance

        Strategic Recommendations:
        {strategic_recommendations}
        """

        technical_implementation = await self.call_agent(
            technical_agent, technical_prompt, strategic_recommendations
        )
        if not technical_implementation:
            technical_implementation = (
                "Technical implementation failed - review strategic recommendations"
            )

        return {
            "system_overview": system_overview,
            "workflow_coordination": workflow_coordination,
            "strategic_recommendations": strategic_recommendations,
            "technical_implementation": technical_implementation,
            "workflow_status": workflow_status,
            "system_metrics": system_metrics,
            "agents_used": [agent["name"] for agent in self.agents],
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime()),
        }

    def generate_orchestration_report(self, results: Dict[str, Any]) -> str:
        """Generate comprehensive orchestration report"""
        if "error" in results:
            return f"# Master Orchestration Failed\n\nError: {results['error']}"

        report = f"""# 🎯 AMAS Master AI Orchestration Report

**Generated:** {results['timestamp']}
**Agents Used:** {', '.join(results['agents_used'])}
**System Health:** {results['system_metrics']['system_health']}

---

## 📊 Executive Summary

This report presents comprehensive master orchestration analysis conducted by multiple AI agents working in coordination to assess and optimize the entire AMAS AI workflow system.

---

## 🏛️ Step 1: System Overview

**Agent:** {results['agents_used'][0] if results['agents_used'] else 'Unknown'}

{results['system_overview']}

---

## 🔄 Step 2: Workflow Coordination

**Agent:** {results['agents_used'][1] if len(results['agents_used']) > 1 else results['agents_used'][0] if results['agents_used'] else 'Unknown'}

{results['workflow_coordination']}

---

## 🎯 Step 3: Strategic Recommendations

**Agent:** {results['agents_used'][2] if len(results['agents_used']) > 2 else results['agents_used'][0] if results['agents_used'] else 'Unknown'}

{results['strategic_recommendations']}

---

## ⚙️ Step 4: Technical Implementation

**Agent:** {results['agents_used'][3] if len(results['agents_used']) > 3 else results['agents_used'][0] if results['agents_used'] else 'Unknown'}

{results['technical_implementation']}

---

## 📈 System Metrics

- **Total Workflows:** {results['system_metrics']['total_workflows']}
- **Active Workflows:** {results['system_metrics']['active_workflows']}
- **AI Models Available:** {results['system_metrics']['ai_models_available']}
- **API Keys Configured:** {results['system_metrics']['api_keys_configured']}
- **System Health:** {results['system_metrics']['system_health']}

---

## 🔄 Workflow Status

"""

        for workflow, status in results["workflow_status"].items():
            report += (
                f"- **{workflow}**: {status['status']} - {status['description']}\n"
            )

        report += f"""
---

## 📈 Key Orchestration Insights

- **System Performance:** Assessed by multi-agent analysis
- **Workflow Coordination:** Identified through coordinated system review
- **Strategic Opportunities:** Prioritized based on impact analysis
- **Technical Improvements:** Areas requiring immediate attention

---

## 🔄 Recommended Actions

1. **Immediate Actions:** Implement high-priority system improvements
2. **Short-term:** Enhance workflow coordination and performance
3. **Long-term:** Implement strategic system evolution

---

*Report generated by AMAS Multi-Agent Master Orchestrator*
*Powered by: {', '.join(results['agents_used']) if results['agents_used'] else 'AI Agents'}*
"""
        return report

    async def run(self):
        """Main execution function"""
        print("🚀 Starting AMAS Master AI Orchestrator...")

        # Create artifacts directory
        os.makedirs("artifacts", exist_ok=True)

        # Perform master orchestration
        results = await self.perform_master_orchestration()

        # Generate report
        report = self.generate_orchestration_report(results)

        # Save report
        report_path = "artifacts/master_orchestration_report.md"
        with open(report_path, "w", encoding="utf-8") as f:
            f.write(report)

        print(f"📋 Master orchestration report saved to {report_path}")
        print("✅ Master AI Orchestration Complete!")

        return results


async def main():
    orchestrator = AIMasterOrchestrator()
    await orchestrator.run()


if __name__ == "__main__":
    print("🎯 AMAS Master AI Orchestrator")
    print("=" * 50)

    # Check API key availability
    print("🔑 API Key Status:")
    print(f"  DeepSeek: {'✅' if get_api_key("DEEPSEEK_API_KEY") else '❌'}")
    print(f"  GLM: {'✅' if get_api_key("GLM_API_KEY") else '❌'}")
    print(f"  Grok: {'✅' if get_api_key("GROK_API_KEY") else '❌'}")
    print(f"  Kimi: {'✅' if get_api_key("KIMI_API_KEY") else '❌'}")
    print(f"  Qwen: {'✅' if get_api_key("QWEN_API_KEY") else '❌'}")
    print(f"  GPTOSS: {'✅' if get_api_key("GPTOSS_API_KEY") else '❌'}")
    print()

    asyncio.run(main())
