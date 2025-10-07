#!/usr/bin/env python3
"""
Universal Multi-Agent Orchestrator with Comprehensive Fallback
Uses the Universal AI Manager for maximum reliability
"""

import asyncio
import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.amas.services.universal_ai_manager import get_universal_ai_manager


class UniversalMultiAgentOrchestrator:
    """
    Multi-agent orchestrator using Universal AI Manager
    Ensures zero failures with 16-provider fallback system
    """

    def __init__(self):
        """Initialize the orchestrator"""
        self.ai_manager = get_universal_ai_manager()
        self.investigation_results = []

        # Define agent roles
        self.agents = {
            "osint_collector": {
                "name": "OSINT Collector",
                "description": "Gathers open-source intelligence and data",
                "system_prompt": "You are an expert OSINT analyst. Gather comprehensive intelligence from publicly available sources.",
            },
            "threat_analyst": {
                "name": "Threat Analyst",
                "description": "Analyzes security threats and patterns",
                "system_prompt": "You are a cybersecurity threat analyst. Analyze threats, identify patterns, and assess risks.",
            },
            "code_analyst": {
                "name": "Code Analyst",
                "description": "Analyzes code quality and security",
                "system_prompt": "You are a senior code analyst. Review code for quality, security vulnerabilities, and best practices.",
            },
            "strategic_advisor": {
                "name": "Strategic Advisor",
                "description": "Provides recommendations and strategy",
                "system_prompt": "You are a strategic advisor. Synthesize findings and provide actionable recommendations.",
            },
            "technical_specialist": {
                "name": "Technical Specialist",
                "description": "Provides technical implementation guidance",
                "system_prompt": "You are a technical specialist. Provide detailed technical analysis and implementation guidance.",
            },
        }

        print(f"🤖 Initialized Universal Multi-Agent Orchestrator")
        print(f"📊 Available agents: {len(self.agents)}")
        print(f"🔧 AI Providers: {len(self.ai_manager.active_providers)}")

    async def call_agent(
        self,
        agent_id: str,
        prompt: str,
        context: str = "",
        strategy: str = "intelligent",
    ) -> Dict[str, Any]:
        """
        Call a specific agent with comprehensive fallback

        Args:
            agent_id: Agent identifier
            prompt: Task prompt
            context: Optional context from previous agents
            strategy: Provider selection strategy

        Returns:
            Agent response dictionary
        """
        if agent_id not in self.agents:
            raise ValueError(f"Unknown agent: {agent_id}")

        agent = self.agents[agent_id]

        print(f"\n🤖 Calling {agent['name']}...")
        print(f"   Strategy: {strategy}")

        # Prepare full prompt with context
        full_prompt = prompt
        if context:
            full_prompt = (
                f"Context from previous analysis:\n{context}\n\nTask: {prompt}"
            )

        # Use Universal AI Manager with fallback
        result = await self.ai_manager.generate(
            prompt=full_prompt,
            system_prompt=agent["system_prompt"],
            strategy=strategy,
            max_tokens=2000,
            temperature=0.7,
        )

        if result["success"]:
            print(f"✅ {agent['name']} completed successfully")
            print(f"   Provider: {result['provider_name']}")
            print(f"   Response time: {result['response_time']:.2f}s")

            return {
                "agent_id": agent_id,
                "agent_name": agent["name"],
                "success": True,
                "response": result["content"],
                "provider": result["provider_name"],
                "response_time": result["response_time"],
                "timestamp": datetime.now().isoformat(),
            }
        else:
            print(f"❌ {agent['name']} failed: {result['error']}")

            return {
                "agent_id": agent_id,
                "agent_name": agent["name"],
                "success": False,
                "error": result["error"],
                "timestamp": datetime.now().isoformat(),
            }

    async def orchestrate_investigation(
        self, topic: str, strategy: str = "intelligent"
    ) -> Dict[str, Any]:
        """
        Orchestrate a multi-phase investigation

        Args:
            topic: Investigation topic
            strategy: Provider selection strategy

        Returns:
            Complete investigation results
        """
        print("=" * 80)
        print(f"🚀 STARTING MULTI-AGENT INVESTIGATION")
        print("=" * 80)
        print(f"Topic: {topic}")
        print(f"Strategy: {strategy}")
        print(f"Timestamp: {datetime.now().isoformat()}")
        print("=" * 80)

        investigation = {
            "topic": topic,
            "strategy": strategy,
            "started_at": datetime.now().isoformat(),
            "phases": [],
            "agents_used": [],
            "success": False,
        }

        context = ""

        # Phase 1: OSINT Collection
        print("\n📍 PHASE 1: OSINT Collection")
        phase1_prompt = f"""
        Conduct comprehensive OSINT (Open Source Intelligence) collection on: {topic}
        
        Focus on:
        1. Recent developments and news
        2. Key players and organizations
        3. Technical details and specifications
        4. Potential risks and concerns
        5. Public sentiment and trends
        
        Provide structured intelligence with sources.
        """

        phase1 = await self.call_agent(
            "osint_collector", phase1_prompt, strategy=strategy
        )
        investigation["phases"].append(
            {"phase": 1, "name": "OSINT Collection", "result": phase1}
        )

        if phase1["success"]:
            context = phase1["response"]
            investigation["agents_used"].append(phase1["agent_name"])

        # Phase 2: Threat Analysis
        print("\n📍 PHASE 2: Threat Analysis")
        phase2_prompt = f"""
        Analyze potential security threats related to: {topic}
        
        Focus on:
        1. Identify threat actors and motivations
        2. Analyze attack vectors and techniques
        3. Assess risk levels and impact
        4. Identify vulnerabilities
        5. Evaluate threat intelligence
        
        Provide detailed threat assessment.
        """

        phase2 = await self.call_agent(
            "threat_analyst", phase2_prompt, context, strategy
        )
        investigation["phases"].append(
            {"phase": 2, "name": "Threat Analysis", "result": phase2}
        )

        if phase2["success"]:
            context += f"\n\n{phase2['response']}"
            investigation["agents_used"].append(phase2["agent_name"])

        # Phase 3: Code Analysis (if relevant)
        if any(
            keyword in topic.lower()
            for keyword in ["code", "software", "application", "vulnerability"]
        ):
            print("\n📍 PHASE 3: Code Analysis")
            phase3_prompt = f"""
            Analyze code-related aspects of: {topic}
            
            Focus on:
            1. Code quality and security
            2. Vulnerability patterns
            3. Best practices compliance
            4. Technical debt assessment
            5. Security recommendations
            
            Provide technical code assessment.
            """

            phase3 = await self.call_agent(
                "code_analyst", phase3_prompt, context, strategy
            )
            investigation["phases"].append(
                {"phase": 3, "name": "Code Analysis", "result": phase3}
            )

            if phase3["success"]:
                context += f"\n\n{phase3['response']}"
                investigation["agents_used"].append(phase3["agent_name"])

        # Phase 4: Strategic Recommendations
        print("\n📍 PHASE 4: Strategic Recommendations")
        phase4_prompt = f"""
        Provide strategic recommendations based on the analysis of: {topic}
        
        Focus on:
        1. Synthesize all findings
        2. Assess overall risk and impact
        3. Prioritize action items
        4. Recommend mitigation strategies
        5. Define success metrics
        
        Provide executive-level strategic recommendations.
        """

        phase4 = await self.call_agent(
            "strategic_advisor", phase4_prompt, context, strategy
        )
        investigation["phases"].append(
            {"phase": 4, "name": "Strategic Recommendations", "result": phase4}
        )

        if phase4["success"]:
            context += f"\n\n{phase4['response']}"
            investigation["agents_used"].append(phase4["agent_name"])

        # Finalize
        investigation["completed_at"] = datetime.now().isoformat()
        investigation["success"] = any(
            p["result"]["success"] for p in investigation["phases"]
        )

        return investigation

    def generate_report(self, investigation: Dict[str, Any]) -> str:
        """Generate comprehensive investigation report"""
        lines = []

        # Header
        lines.extend(
            [
                "=" * 80,
                "🔍 UNIVERSAL MULTI-AGENT INVESTIGATION REPORT",
                "=" * 80,
                "",
                f"**Topic:** {investigation['topic']}",
                f"**Strategy:** {investigation['strategy']}",
                f"**Started:** {investigation['started_at']}",
                f"**Completed:** {investigation.get('completed_at', 'In Progress')}",
                f"**Agents Used:** {', '.join(investigation['agents_used'])}",
                f"**Success:** {'✅ Yes' if investigation['success'] else '❌ No'}",
                "",
                "=" * 80,
                "",
            ]
        )

        # Phase Results
        for phase in investigation["phases"]:
            result = phase["result"]

            if result["success"]:
                lines.extend(
                    [
                        f"## Phase {phase['phase']}: {phase['name']}",
                        f"**Agent:** {result['agent_name']}",
                        f"**Provider:** {result['provider']}",
                        f"**Response Time:** {result['response_time']:.2f}s",
                        f"**Timestamp:** {result['timestamp']}",
                        "",
                        "### Response:",
                        result["response"],
                        "",
                        "-" * 80,
                        "",
                    ]
                )
            else:
                lines.extend(
                    [
                        f"## Phase {phase['phase']}: {phase['name']} (FAILED)",
                        f"**Agent:** {result['agent_name']}",
                        f"**Error:** {result.get('error', 'Unknown error')}",
                        "",
                        "-" * 80,
                        "",
                    ]
                )

        # Statistics
        stats = self.ai_manager.get_stats()
        lines.extend(
            [
                "## 📊 System Statistics",
                "",
                f"- Total Requests: {stats['total_requests']}",
                f"- Success Rate: {stats['success_rate']}",
                f"- Average Response Time: {stats['average_response_time']}",
                f"- Total Fallbacks: {stats['total_fallbacks']}",
                f"- Active Providers: {stats['active_providers']}",
                "",
                "-" * 80,
                "",
            ]
        )

        # Provider Health
        health = self.ai_manager.get_provider_health()
        lines.extend(["## 🏥 Provider Health", ""])

        for provider_id, info in health.items():
            if info["success_count"] > 0 or info["failure_count"] > 0:
                status = "✅" if info["available"] else "❌"
                lines.append(
                    f"{status} **{info['name']}**: {info['status']} - "
                    f"Success Rate: {info['success_rate']}, "
                    f"Avg Time: {info['avg_response_time']}"
                )

        lines.extend(
            [
                "",
                "=" * 80,
                "",
                f"*Report generated by Universal Multi-Agent Orchestrator*",
                f"*Timestamp: {datetime.now().isoformat()}*",
            ]
        )

        return "\n".join(lines)

    async def run(self, topic: str = None, strategy: str = "intelligent"):
        """Main execution method"""
        if not topic:
            topic = "Recent cybersecurity threats and vulnerabilities"

        # Show configuration
        print(self.ai_manager.get_config_summary())
        print()

        # Run investigation
        investigation = await self.orchestrate_investigation(topic, strategy)

        # Generate report
        report = self.generate_report(investigation)

        # Save report
        os.makedirs("artifacts", exist_ok=True)
        report_path = "artifacts/universal_multi_agent_report.md"

        with open(report_path, "w", encoding="utf-8") as f:
            f.write(report)

        # Save JSON
        json_path = "artifacts/universal_investigation_results.json"
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(investigation, f, indent=2, ensure_ascii=False)

        # Summary
        print("\n" + "=" * 80)
        print("✅ INVESTIGATION COMPLETE!")
        print("=" * 80)
        print(f"📄 Report saved to: {report_path}")
        print(f"📋 JSON saved to: {json_path}")
        print(
            f"📊 Phases completed: {len([p for p in investigation['phases'] if p['result']['success']])}/{len(investigation['phases'])}"
        )
        print(f"🤖 Agents used: {len(investigation['agents_used'])}")

        stats = self.ai_manager.get_stats()
        print(f"📈 Success rate: {stats['success_rate']}")
        print(f"⚡ Average response time: {stats['average_response_time']}")
        print("=" * 80)


async def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="Universal Multi-Agent Orchestrator")
    parser.add_argument("--topic", type=str, help="Investigation topic")
    parser.add_argument(
        "--strategy",
        type=str,
        default="intelligent",
        choices=["priority", "intelligent", "round_robin", "fastest"],
        help="Provider selection strategy",
    )

    args = parser.parse_args()

    orchestrator = UniversalMultiAgentOrchestrator()
    await orchestrator.run(topic=args.topic, strategy=args.strategy)


if __name__ == "__main__":
    asyncio.run(main())
