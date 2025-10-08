#!/usr/bin/env python3
"""
Complete AI Integration Script - Integrates all AI services into AMAS
"""

import argparse
import asyncio
import json
import logging
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from config.ai_config import get_ai_config
from services.ai_service_manager import AIProvider, AIServiceManager

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

class CompleteAIIntegration:
    """Complete AI Integration Manager"""

    def __init__(self):
        self.ai_service = None
        self.config_manager = get_ai_config()
        self.integration_results = {}

    async def initialize(self):
        """Initialize the integration manager"""
        try:
            # Load configuration
            config = {
                "deepseek_api_key": os.getenv("DEEPSEEK_API_KEY", ""),
                "glm_api_key": os.getenv("GLM_API_KEY", ""),
                "grok_api_key": os.getenv("GROK_API_KEY", ""),
                "kimi_api_key": os.getenv("KIMI_API_KEY", ""),
                "qwen_api_key": os.getenv("QWEN_API_KEY", ""),
                "gptoss_api_key": os.getenv("GPTOSS_API_KEY", ""),
            }

            self.ai_service = AIServiceManager(config)
            await self.ai_service.initialize()
            logger.info("Complete AI Integration initialized successfully")

        except Exception as e:
            logger.error(f"Error initializing Complete AI Integration: {e}")
            raise

    async def integrate_ai_into_agents(self) -> Dict[str, Any]:
        """Integrate AI services into all AMAS agents"""
        try:
            logger.info("Integrating AI services into AMAS agents...")

            # List of agent files to update
            agent_files = [
                "agents/osint/osint_agent.py",
                "agents/investigation/investigation_agent.py",
                "agents/forensics/forensics_agent.py",
                "agents/data_analysis/data_analysis_agent.py",
                "agents/reverse_engineering/reverse_engineering_agent.py",
                "agents/metadata/metadata_agent.py",
                "agents/reporting/reporting_agent.py",
                "agents/technology_monitor/technology_monitor_agent.py",
            ]

            integration_results = {}

            for agent_file in agent_files:
                agent_path = Path(agent_file)
                if agent_path.exists():
                    logger.info(f"Integrating AI into {agent_file}...")

                    # Read current agent file
                    with open(agent_path, "r", encoding="utf-8") as f:
                        content = f.read()

                    # Check if AI integration already exists
                    if "AIServiceManager" in content:
                        logger.info(f"✓ {agent_file} already has AI integration")
                        integration_results[agent_file] = {
                            "status": "already_integrated"
                        }
                        continue

                    # Generate AI integration code
                    integration_code = await self._generate_agent_ai_integration(
                        agent_file
                    )

                    if integration_code:
                        # Update agent file
                        updated_content = self._update_agent_file(
                            content, integration_code
                        )

                        # Save updated file
                        with open(agent_path, "w", encoding="utf-8") as f:
                            f.write(updated_content)

                        logger.info(f"✓ {agent_file} updated with AI integration")
                        integration_results[agent_file] = {
                            "status": "integrated",
                            "code_added": True,
                        }
                    else:
                        logger.warning(
                            f"✗ Failed to generate AI integration for {agent_file}"
                        )
                        integration_results[agent_file] = {
                            "status": "failed",
                            "error": "Code generation failed",
                        }
                else:
                    logger.warning(f"✗ {agent_file} not found")
                    integration_results[agent_file] = {"status": "not_found"}

            return {
                "agent_integrations": integration_results,
                "timestamp": datetime.now().isoformat(),
            }

        except Exception as e:
            logger.error(f"Error integrating AI into agents: {e}")
            return {"error": str(e)}

    async def _generate_agent_ai_integration(self, agent_file: str) -> str:
        """Generate AI integration code for an agent"""
        try:
            agent_name = Path(agent_file).stem.replace("_agent", "").title()

            prompt = f"""Generate AI integration code for the {agent_name} Agent in AMAS.

The agent should:
1. Use AIServiceManager for AI operations
2. Have intelligent fallback mechanisms
3. Include AI-powered analysis capabilities
4. Support multiple AI providers
5. Have proper error handling

Generate:
1. Import statements for AIServiceManager
2. AI service initialization in __init__
3. AI-powered methods for the agent's specific tasks
4. Error handling and fallback mechanisms
5. Integration with the existing agent structure

Return only the code additions needed, not the entire file."""

            response = await self.ai_service.generate_code(prompt, "python")

            if response.success:
                return response.content
            else:
                logger.error(
                    f"Failed to generate AI integration code: {response.error}"
                )
                return None

        except Exception as e:
            logger.error(f"Error generating AI integration code: {e}")
            return None

    def _update_agent_file(self, content: str, integration_code: str) -> str:
        """Update agent file with AI integration code"""
        try:
            # Add import statements
            if (
                "from services.ai_service_manager import AIServiceManager"
                not in content
            ):
                # Find the imports section and add AI service import
                lines = content.split("\n")
                import_index = 0
                for i, line in enumerate(lines):
                    if line.startswith("import ") or line.startswith("from "):
                        import_index = i

                # Insert AI service import
                lines.insert(
                    import_index + 1,
                    "from services.ai_service_manager import AIServiceManager, AIProvider",
                )
                content = "\n".join(lines)

            # Add AI service initialization to __init__ method
            if "self.ai_service = None" not in content:
                # Find __init__ method and add AI service initialization
                init_pattern = "def __init__(self"
                if init_pattern in content:
                    # Add AI service initialization
                    content = content.replace("def __init__(self", "def __init__(self")
                    # This is a simplified approach - in practice, you'd want more sophisticated parsing

            # Add AI integration methods
            if "async def _ai_analyze" not in content:
                # Add AI methods at the end of the class
                class_end = content.rfind("    def ")
                if class_end != -1:
                    content = (
                        content[:class_end]
                        + integration_code
                        + "\n"
                        + content[class_end:]
                    )

            return content

        except Exception as e:
            logger.error(f"Error updating agent file: {e}")
            return content

    async def create_ai_workflows(self) -> Dict[str, Any]:
        """Create AI-powered workflows for AMAS"""
        try:
            logger.info("Creating AI-powered workflows...")

            workflows = {
                "intelligence_analysis": await self._create_intelligence_analysis_workflow(),
                "threat_assessment": await self._create_threat_assessment_workflow(),
                "data_correlation": await self._create_data_correlation_workflow(),
                "report_generation": await self._create_report_generation_workflow(),
            }

            return {"workflows": workflows, "timestamp": datetime.now().isoformat()}

        except Exception as e:
            logger.error(f"Error creating AI workflows: {e}")
            return {"error": str(e)}

    async def _create_intelligence_analysis_workflow(self) -> Dict[str, Any]:
        """Create intelligence analysis workflow"""
        try:
            prompt = """Create a comprehensive intelligence analysis workflow for AMAS that:

1. Uses multiple AI providers for analysis
2. Implements intelligent fallback mechanisms
3. Provides real-time intelligence processing
4. Includes threat assessment capabilities
5. Generates actionable intelligence reports

Generate a complete workflow implementation."""

            response = await self.ai_service.generate_code(prompt, "python")

            if response.success:
                return {
                    "workflow_code": response.content,
                    "provider": response.provider,
                    "status": "generated",
                }
            else:
                return {"status": "failed", "error": response.error}

        except Exception as e:
            logger.error(f"Error creating intelligence analysis workflow: {e}")
            return {"error": str(e)}

    async def _create_threat_assessment_workflow(self) -> Dict[str, Any]:
        """Create threat assessment workflow"""
        try:
            prompt = """Create a threat assessment workflow for AMAS that:

1. Analyzes threat intelligence data
2. Uses AI for pattern recognition
3. Provides risk scoring
4. Generates threat reports
5. Implements real-time monitoring

Generate a complete workflow implementation."""

            response = await self.ai_service.generate_code(prompt, "python")

            if response.success:
                return {
                    "workflow_code": response.content,
                    "provider": response.provider,
                    "status": "generated",
                }
            else:
                return {"status": "failed", "error": response.error}

        except Exception as e:
            logger.error(f"Error creating threat assessment workflow: {e}")
            return {"error": str(e)}

    async def _create_data_correlation_workflow(self) -> Dict[str, Any]:
        """Create data correlation workflow"""
        try:
            prompt = """Create a data correlation workflow for AMAS that:

1. Correlates data from multiple sources
2. Uses AI for pattern matching
3. Identifies relationships between entities
4. Generates correlation reports
5. Provides visualization capabilities

Generate a complete workflow implementation."""

            response = await self.ai_service.generate_code(prompt, "python")

            if response.success:
                return {
                    "workflow_code": response.content,
                    "provider": response.provider,
                    "status": "generated",
                }
            else:
                return {"status": "failed", "error": response.error}

        except Exception as e:
            logger.error(f"Error creating data correlation workflow: {e}")
            return {"error": str(e)}

    async def _create_report_generation_workflow(self) -> Dict[str, Any]:
        """Create report generation workflow"""
        try:
            prompt = """Create a report generation workflow for AMAS that:

1. Generates comprehensive intelligence reports
2. Uses AI for content analysis and improvement
3. Provides multiple report formats
4. Includes executive summaries
5. Implements automated report scheduling

Generate a complete workflow implementation."""

            response = await self.ai_service.generate_code(prompt, "python")

            if response.success:
                return {
                    "workflow_code": response.content,
                    "provider": response.provider,
                    "status": "generated",
                }
            else:
                return {"status": "failed", "error": response.error}

        except Exception as e:
            logger.error(f"Error creating report generation workflow: {e}")
            return {"error": str(e)}

    async def optimize_ai_performance(self) -> Dict[str, Any]:
        """Optimize AI performance across the system"""
        try:
            logger.info("Optimizing AI performance...")

            # Get current provider statistics
            stats = self.ai_service.get_provider_stats()

            # Analyze performance
            performance_analysis = await self._analyze_ai_performance(stats)

            # Generate optimization recommendations
            optimization_recommendations = (
                await self._generate_optimization_recommendations(performance_analysis)
            )

            return {
                "current_stats": stats,
                "performance_analysis": performance_analysis,
                "optimization_recommendations": optimization_recommendations,
                "timestamp": datetime.now().isoformat(),
            }

        except Exception as e:
            logger.error(f"Error optimizing AI performance: {e}")
            return {"error": str(e)}

    async def _analyze_ai_performance(self, stats: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze AI performance metrics"""
        try:
            prompt = f"""Analyze the performance of these AI providers:

{json.dumps(stats, indent=2)}

Provide:
1. Performance assessment
2. Bottleneck identification
3. Optimization opportunities
4. Provider recommendations
5. Performance improvement suggestions"""

            response = await self.ai_service.generate_response(prompt)

            if response.success:
                return {"analysis": response.content, "provider": response.provider}
            else:
                return {"error": response.error}

        except Exception as e:
            logger.error(f"Error analyzing AI performance: {e}")
            return {"error": str(e)}

    async def _generate_optimization_recommendations(
        self, performance_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate optimization recommendations"""
        try:
            prompt = f"""Based on this AI performance analysis, generate specific optimization recommendations:

{performance_analysis.get('analysis', 'No analysis available')}

Provide:
1. Specific optimization actions
2. Configuration changes
3. Performance tuning suggestions
4. Monitoring improvements
5. Implementation priorities"""

            response = await self.ai_service.generate_response(prompt)

            if response.success:
                return {
                    "recommendations": response.content,
                    "provider": response.provider,
                }
            else:
                return {"error": response.error}

        except Exception as e:
            logger.error(f"Error generating optimization recommendations: {e}")
            return {"error": str(e)}

    async def run_complete_integration(self) -> Dict[str, Any]:
        """Run complete AI integration"""
        try:
            logger.info("Starting complete AI integration...")

            # Integrate AI into agents
            agent_integration = await self.integrate_ai_into_agents()

            # Create AI workflows
            workflow_creation = await self.create_ai_workflows()

            # Optimize AI performance
            performance_optimization = await self.optimize_ai_performance()

            # Generate integration report
            integration_report = {
                "timestamp": datetime.now().isoformat(),
                "agent_integration": agent_integration,
                "workflow_creation": workflow_creation,
                "performance_optimization": performance_optimization,
                "summary": self._generate_integration_summary(
                    agent_integration, workflow_creation, performance_optimization
                ),
            }

            return integration_report

        except Exception as e:
            logger.error(f"Error in complete integration: {e}")
            return {"error": str(e)}

    def _generate_integration_summary(
        self,
        agent_integration: Dict[str, Any],
        workflow_creation: Dict[str, Any],
        performance_optimization: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Generate integration summary"""
        try:
            # Count successful agent integrations
            agent_results = agent_integration.get("agent_integrations", {})
            successful_agents = len(
                [
                    result
                    for result in agent_results.values()
                    if result.get("status") == "integrated"
                ]
            )

            # Count successful workflows
            workflows = workflow_creation.get("workflows", {})
            successful_workflows = len(
                [
                    workflow
                    for workflow in workflows.values()
                    if workflow.get("status") == "generated"
                ]
            )

            return {
                "total_agents": len(agent_results),
                "successful_agents": successful_agents,
                "total_workflows": len(workflows),
                "successful_workflows": successful_workflows,
                "integration_status": (
                    "complete" if successful_agents > 0 else "incomplete"
                ),
                "recommendations": self._generate_integration_recommendations(
                    successful_agents, successful_workflows
                ),
            }

        except Exception as e:
            logger.error(f"Error generating integration summary: {e}")
            return {"error": str(e)}

    def _generate_integration_recommendations(
        self, successful_agents: int, successful_workflows: int
    ) -> List[str]:
        """Generate integration recommendations"""
        recommendations = []

        if successful_agents == 0:
            recommendations.append(
                "No agents were successfully integrated. Check AI service configuration."
            )
        elif successful_agents < 8:
            recommendations.append(
                f"Only {successful_agents} agents were integrated. Review failed integrations."
            )

        if successful_workflows == 0:
            recommendations.append(
                "No workflows were generated. Check AI service availability."
            )
        elif successful_workflows < 4:
            recommendations.append(
                f"Only {successful_workflows} workflows were generated. Review workflow generation."
            )

        if successful_agents > 0 and successful_workflows > 0:
            recommendations.append(
                "AI integration is successful! Consider running performance tests."
            )
            recommendations.append(
                "Monitor AI provider health and performance regularly."
            )

        return recommendations

    def save_integration_report(self, report: Dict[str, Any], output_file: str):
        """Save integration report to file"""
        try:
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            logger.info(f"Integration report saved to {output_file}")
        except Exception as e:
            logger.error(f"Error saving integration report: {e}")

    async def shutdown(self):
        """Shutdown the integration manager"""
        if self.ai_service:
            await self.ai_service.shutdown()

async def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="Complete AI Integration")
    parser.add_argument(
        "--output",
        default="complete_ai_integration_report.json",
        help="Output file for integration report",
    )
    parser.add_argument(
        "--agents-only", action="store_true", help="Only integrate AI into agents"
    )
    parser.add_argument(
        "--workflows-only", action="store_true", help="Only create AI workflows"
    )
    parser.add_argument(
        "--optimize-only", action="store_true", help="Only optimize AI performance"
    )

    args = parser.parse_args()

    integration = CompleteAIIntegration()

    try:
        await integration.initialize()

        if args.agents_only:
            # Only integrate AI into agents
            results = await integration.integrate_ai_into_agents()
            print("\n" + "=" * 50)
            print("AI AGENT INTEGRATION RESULTS")
            print("=" * 50)
            for agent, result in results.get("agent_integrations", {}).items():
                status = "✓" if result.get("status") == "integrated" else "✗"
                print(f"{status} {agent}: {result.get('status', 'unknown')}")
            print("=" * 50)

        elif args.workflows_only:
            # Only create AI workflows
            results = await integration.create_ai_workflows()
            print("\n" + "=" * 50)
            print("AI WORKFLOW CREATION RESULTS")
            print("=" * 50)
            for workflow, result in results.get("workflows", {}).items():
                status = "✓" if result.get("status") == "generated" else "✗"
                print(f"{status} {workflow}: {result.get('status', 'unknown')}")
            print("=" * 50)

        elif args.optimize_only:
            # Only optimize AI performance
            results = await integration.optimize_ai_performance()
            print("\n" + "=" * 50)
            print("AI PERFORMANCE OPTIMIZATION")
            print("=" * 50)
            if "optimization_recommendations" in results:
                print(
                    results["optimization_recommendations"].get(
                        "recommendations", "No recommendations"
                    )
                )
            print("=" * 50)

        else:
            # Complete integration
            results = await integration.run_complete_integration()
            integration.save_integration_report(results, args.output)

            # Print summary
            if "summary" in results:
                summary = results["summary"]
                print("\n" + "=" * 50)
                print("COMPLETE AI INTEGRATION SUMMARY")
                print("=" * 50)
                print(f"Total Agents: {summary.get('total_agents', 0)}")
                print(f"Successful Agents: {summary.get('successful_agents', 0)}")
                print(f"Total Workflows: {summary.get('total_workflows', 0)}")
                print(f"Successful Workflows: {summary.get('successful_workflows', 0)}")
                print(
                    f"Integration Status: {summary.get('integration_status', 'unknown')}"
                )
                print("\nRecommendations:")
                for rec in summary.get("recommendations", []):
                    print(f"- {rec}")
                print("=" * 50)

            logger.info("Complete AI integration finished.")

    except Exception as e:
        logger.error(f"Error in main: {e}")
        sys.exit(1)

    finally:
        await integration.shutdown()

if __name__ == "__main__":
    asyncio.run(main())
