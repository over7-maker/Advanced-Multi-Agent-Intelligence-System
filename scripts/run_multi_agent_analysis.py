#!/usr/bin/env python3
"""
Run Multi-Agent Analysis for AMAS Project
This script coordinates multiple AI agents to analyze and improve the codebase
"""

import asyncio
import json
import logging
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Load environment variables
try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    logger.warning("python-dotenv not installed")

from openai import AsyncOpenAI


class MultiAgentOrchestrator:
    """Orchestrates multiple AI agents for project analysis"""

    def __init__(self):
        self.api_key = os.getenv("OPENROUTER_API_KEY", "")
        if not self.api_key or self.api_key == "your_openrouter_api_key_here":
            raise ValueError(
                "No valid OpenRouter API key found. Please configure in .env file"
            )

        self.client = AsyncOpenAI(
            api_key=self.api_key, base_url="https://openrouter.ai/api/v1"
        )

        self.agents = {
            "code_analyst": {
                "name": "Code Analysis Agent",
                "model": "deepseek/deepseek-chat-v3.1:free",
                "description": "Analyzes code quality, structure, and best practices",
            },
            "security_expert": {
                "name": "Security Expert Agent",
                "model": "grok/grok-4-fast:free",
                "description": "Identifies security vulnerabilities and suggests fixes",
            },
            "performance_optimizer": {
                "name": "Performance Optimizer Agent",
                "model": "qwen/qwen3-coder:free",
                "description": "Analyzes performance bottlenecks and optimization opportunities",
            },
            "documentation_specialist": {
                "name": "Documentation Specialist Agent",
                "model": "moonshotai/kimi-k2:free",
                "description": "Reviews and improves documentation",
            },
            "test_coverage_analyst": {
                "name": "Test Coverage Analyst",
                "model": "z-ai/glm-4.5-air:free",
                "description": "Analyzes test coverage and suggests improvements",
            },
        }

        self.results = {}

    async def analyze_with_agent(
        self, agent_id: str, files_content: Dict[str, str]
    ) -> Dict[str, Any]:
        """Run analysis with a specific agent"""
        agent = self.agents[agent_id]
        logger.info(f"Running {agent['name']}...")

        try:
            # Prepare context with file contents
            context = "Here are the key files from the AMAS project:\n\n"
            for filepath, content in files_content.items():
                context += f"File: {filepath}\n```python\n{content[:1000]}...\n```\n\n"

            # Create agent-specific prompt
            prompts = {
                "code_analyst": f"""As a Code Analysis Agent, analyze the following AMAS codebase:

{context}

Provide a detailed analysis including:
1. Code quality issues (naming, structure, patterns)
2. Best practices violations
3. Architectural concerns
4. Specific improvement suggestions with code examples
5. Priority ranking of issues

Format your response as JSON with: issues_found, suggestions, priority_items""",
                "security_expert": f"""As a Security Expert Agent, analyze the following AMAS codebase for security issues:

{context}

Provide a security analysis including:
1. Potential vulnerabilities (injection, authentication, data exposure)
2. Security best practices violations
3. Dependency security issues
4. Specific fixes with code examples
5. Risk assessment (critical/high/medium/low)

Format your response as JSON with: vulnerabilities, fixes, risk_assessment""",
                "performance_optimizer": f"""As a Performance Optimizer Agent, analyze the following AMAS codebase:

{context}

Provide performance analysis including:
1. Performance bottlenecks
2. Inefficient algorithms or data structures
3. Resource usage issues
4. Optimization opportunities with code examples
5. Performance impact estimates

Format your response as JSON with: bottlenecks, optimizations, impact_estimates""",
                "documentation_specialist": f"""As a Documentation Specialist Agent, analyze the following AMAS codebase documentation:

{context}

Provide documentation analysis including:
1. Missing documentation areas
2. Unclear or outdated documentation
3. API documentation completeness
4. User guide improvements
5. Code comment quality

Format your response as JSON with: missing_docs, improvements, priority_areas""",
                "test_coverage_analyst": f"""As a Test Coverage Analyst, analyze the following AMAS codebase testing:

{context}

Provide test analysis including:
1. Test coverage gaps
2. Missing test scenarios
3. Test quality issues
4. Specific test examples to add
5. Testing strategy recommendations

Format your response as JSON with: coverage_gaps, test_scenarios, recommendations""",
            }

            response = await self.client.chat.completions.create(
                model=agent["model"],
                messages=[
                    {
                        "role": "system",
                        "content": f"You are the {agent['name']}. {agent['description']}",
                    },
                    {"role": "user", "content": prompts[agent_id]},
                ],
                max_tokens=2000,
                temperature=0.7,
            )

            result_text = response.choices[0].message.content

            # Try to parse as JSON, fallback to text
            try:
                result = json.loads(result_text)
            except:
                result = {"analysis": result_text}

            return {"status": "success", "agent": agent_id, "results": result}

        except Exception as e:
            logger.error(f"Error with {agent['name']}: {e}")
            return {"status": "error", "agent": agent_id, "error": str(e)}

    async def load_project_files(self) -> Dict[str, str]:
        """Load key project files for analysis"""
        files_to_analyze = [
            "src/amas/main.py",
            "src/amas/core/orchestrator.py",
            "src/amas/agents/base/intelligence_agent.py",
            "src/amas/services/ai_service_manager.py",
            "src/amas/config/ai_config.py",
            "README.md",
        ]

        files_content = {}
        for filepath in files_to_analyze:
            full_path = Path(__file__).parent.parent / filepath
            if full_path.exists():
                try:
                    with open(full_path, "r", encoding="utf-8") as f:
                        files_content[filepath] = f.read()
                except Exception as e:
                    logger.warning(f"Could not read {filepath}: {e}")

        return files_content

    async def run_analysis(self) -> Dict[str, Any]:
        """Run multi-agent analysis"""
        logger.info("Starting multi-agent analysis...")

        # Load project files
        files_content = await self.load_project_files()
        logger.info(f"Loaded {len(files_content)} files for analysis")

        # Run all agents in parallel
        tasks = []
        for agent_id in self.agents:
            task = self.analyze_with_agent(agent_id, files_content)
            tasks.append(task)

        results = await asyncio.gather(*tasks)

        # Compile results
        timestamp = datetime.now().isoformat()
        analysis_results = {
            "timestamp": timestamp,
            "agents_used": list(self.agents.keys()),
            "file_analyzed": list(files_content.keys()),
            "agent_results": {},
        }

        for result in results:
            agent_id = result["agent"]
            analysis_results["agent_results"][agent_id] = result

        # Generate summary
        successful_agents = sum(1 for r in results if r["status"] == "success")
        analysis_results["summary"] = {
            "total_agents": len(self.agents),
            "successful_analyses": successful_agents,
            "failed_analyses": len(self.agents) - successful_agents,
        }

        return analysis_results

    async def generate_improvement_report(
        self, analysis_results: Dict[str, Any]
    ) -> str:
        """Generate a comprehensive improvement report"""
        logger.info("Generating improvement report...")

        report = f"""# 🤖 AMAS Multi-Agent Analysis Report

**Generated:** {analysis_results['timestamp']}
**Agents Used:** {len(analysis_results['agents_used'])}
**Files Analyzed:** {len(analysis_results['file_analyzed'])}

## 📊 Analysis Summary

"""

        # Add results from each agent
        for agent_id, result in analysis_results["agent_results"].items():
            agent_name = self.agents[agent_id]["name"]
            report += f"### {agent_name}\n\n"

            if result["status"] == "success":
                # Format the results nicely
                agent_results = result["results"]
                if isinstance(agent_results, dict):
                    for key, value in agent_results.items():
                        report += f"**{key.replace('_', ' ').title()}:**\n"
                        if isinstance(value, list):
                            for item in value:
                                report += f"- {item}\n"
                        else:
                            report += f"{value}\n"
                        report += "\n"
                else:
                    report += f"{agent_results}\n\n"
            else:
                report += (
                    f"❌ Analysis failed: {result.get('error', 'Unknown error')}\n\n"
                )

        # Add recommendations
        report += """## 🎯 Key Recommendations

Based on the multi-agent analysis, here are the top priorities:

1. **Code Quality**: Address identified code quality issues
2. **Security**: Fix any security vulnerabilities found
3. **Performance**: Implement suggested optimizations
4. **Documentation**: Update missing or outdated documentation
5. **Testing**: Improve test coverage in identified areas

## 🚀 Next Steps

1. Review each agent's findings in detail
2. Prioritize critical issues (security > bugs > performance > style)
3. Create implementation tasks for each improvement
4. Track progress through GitHub issues/PRs

---
*Generated by AMAS Multi-Agent Orchestration System*
"""

        return report


async def main():
    """Main execution function"""
    try:
        orchestrator = MultiAgentOrchestrator()

        # Run analysis
        analysis_results = await orchestrator.run_analysis()

        # Save raw results
        results_file = (
            f"multi_agent_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )
        with open(results_file, "w") as f:
            json.dump(analysis_results, f, indent=2)
        logger.info(f"Saved raw results to {results_file}")

        # Generate report
        report = await orchestrator.generate_improvement_report(analysis_results)

        # Save report
        report_file = (
            f"improvement_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        )
        with open(report_file, "w") as f:
            f.write(report)
        logger.info(f"Saved improvement report to {report_file}")

        # Display summary
        logger.info("\n" + "=" * 50)
        logger.info("Multi-Agent Analysis Complete!")
        logger.info(f"✓ Analyzed with {len(orchestrator.agents)} agents")
        logger.info(f"✓ Results saved to {results_file}")
        logger.info(f"✓ Report saved to {report_file}")
        logger.info("=" * 50)

        return 0

    except ValueError as e:
        logger.error(f"Configuration error: {e}")
        logger.info("\nPlease set up authentication first:")
        logger.info("1. Get an API key from https://openrouter.ai/keys")
        logger.info("2. Add to .env file: OPENROUTER_API_KEY=your_key")
        return 1
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
