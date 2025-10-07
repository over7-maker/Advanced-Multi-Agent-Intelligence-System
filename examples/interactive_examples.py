#!/usr/bin/env python3
"""
AMAS Interactive Mode Examples
Advanced Multi-Agent Intelligence System - Interactive Mode

This file contains comprehensive examples demonstrating the capabilities
of the AMAS Interactive Mode system.
"""

import asyncio
import sys
from pathlib import Path

# Add src directory to Python path
sys.path.append(str(Path(__file__).parent.parent / "src"))

from amas.interactive.ai.context_manager import ContextManager
from amas.interactive.ai.intent_classifier import IntentClassifier
from amas.interactive.ai.nlp_engine import NLPEngine
from amas.interactive.core.agent_coordinator import AgentCoordinator
from amas.interactive.core.interactive_cli import AMASInteractiveCLI
from amas.interactive.core.task_manager import TaskManager
from amas.interactive.core.visual_interface import VisualInterface
from amas.interactive.utils.config_manager import ConfigManager
from amas.interactive.utils.logger import InteractiveLogger


class AMASInteractiveExamples:
    """Comprehensive examples for AMAS Interactive Mode"""

    def __init__(self):
        self.console = Console()
        self.setup_components()

    def setup_components(self):
        """Setup example components"""
        # Load configuration
        self.config_manager = ConfigManager()
        self.config = self.config_manager.load_config()

        # Initialize components
        self.nlp_engine = NLPEngine(self.config.get("nlp", {}))
        self.intent_classifier = IntentClassifier(self.config.get("intent", {}))
        self.logger = InteractiveLogger()
        self.context_manager = ContextManager(self.config.get("context", {}))

    def example_1_nlp_processing(self):
        """Example 1: Natural Language Processing"""
        print("\n" + "=" * 60)
        print("🧠 Example 1: Natural Language Processing")
        print("=" * 60)

        commands = [
            "scan google.com for vulnerabilities",
            "analyze the code quality of my React application",
            "research the latest AI security threats",
            "monitor the performance of our website",
            "document the API endpoints in our project",
        ]

        for command in commands:
            print(f"\n📝 Command: '{command}'")

            # Process with NLP
            result = asyncio.run(self.nlp_engine.process_command(command))

            # Display results
            print(f"🎯 Intent: {result['intent']}")
            print(f"🎯 Target: {result['target']}")
            print(f"📊 Confidence: {result['confidence']:.1%}")

            if result["entities"]:
                print(f"🏷️  Entities: {[e['text'] for e in result['entities']]}")

            if result["suggestions"]:
                print(f"💡 Suggestions: {result['suggestions'][:2]}")

    def example_2_intent_classification(self):
        """Example 2: Intent Classification"""
        print("\n" + "=" * 60)
        print("🎯 Example 2: Intent Classification")
        print("=" * 60)

        commands = [
            "check security of github.com/microsoft/vscode",
            "review the code quality of my Python project",
            "investigate suspicious activity on our network",
            "optimize the performance of our database",
            "create documentation for our API",
        ]

        for command in commands:
            print(f"\n📝 Command: '{command}'")

            # Process with NLP first
            nlp_result = asyncio.run(self.nlp_engine.process_command(command))

            # Classify intent
            intent_result = asyncio.run(
                self.intent_classifier.classify_intent(command, nlp_result, [])
            )

            # Display results
            print(f"🎯 Intent: {intent_result['intent']}")
            print(f"📊 Confidence: {intent_result['confidence']:.1%}")
            print(f"🤖 Suggested Agents: {intent_result['suggested_agents']}")

            if intent_result["reasoning"]:
                print(f"🧠 Reasoning: {intent_result['reasoning'][0]}")

    def example_3_agent_coordination(self):
        """Example 3: Agent Coordination"""
        print("\n" + "=" * 60)
        print("🤖 Example 3: Agent Coordination")
        print("=" * 60)

        # Mock orchestrator for example
        class MockOrchestrator:
            pass

        orchestrator = MockOrchestrator()
        coordinator = AgentCoordinator(orchestrator, self.config.get("agents", {}))

        # Display agent status
        agent_status = coordinator.get_agent_status()
        print(f"📊 Total Agents: {agent_status['total_agents']}")
        print(f"✅ Available Agents: {agent_status['available_agents']}")
        print(f"🔄 Busy Agents: {agent_status['busy_agents']}")

        print("\n🤖 Agent Details:")
        for agent_id, agent_info in agent_status["agents"].items():
            print(
                f"  • {agent_info['name']}: {agent_info['status']} "
                f"(Success Rate: {agent_info['success_rate']:.1%})"
            )

    def example_4_task_management(self):
        """Example 4: Task Management"""
        print("\n" + "=" * 60)
        print("📋 Example 4: Task Management")
        print("=" * 60)

        task_manager = TaskManager(self.config.get("tasks", {}))

        # Display task statistics
        stats = task_manager.get_stats()
        print(f"📊 Total Tasks: {stats['total_tasks']}")
        print(f"✅ Completed Tasks: {stats['completed_tasks']}")
        print(f"❌ Failed Tasks: {stats['failed_tasks']}")
        print(f"📈 Success Rate: {stats['success_rate']:.1%}")
        print(f"⏱️  Average Duration: {stats['average_duration']:.2f}s")

        # Display queue status
        queue_status = task_manager.get_queue_status()
        print(f"\n📋 Queue Status:")
        print(f"  • Queue Length: {queue_status['queue_length']}")
        print(f"  • Active Tasks: {queue_status['active_tasks']}")
        print(f"  • Completed Tasks: {queue_status['completed_tasks']}")

    def example_5_context_management(self):
        """Example 5: Context Management"""
        print("\n" + "=" * 60)
        print("🧠 Example 5: Context Management")
        print("=" * 60)

        session_id = "example_session"

        # Add some context entries
        commands = [
            "scan google.com for vulnerabilities",
            "analyze the code quality of my project",
            "research AI security trends",
        ]

        for i, command in enumerate(commands):
            # Simulate NLP processing
            nlp_result = asyncio.run(self.nlp_engine.process_command(command))
            intent_result = asyncio.run(
                self.intent_classifier.classify_intent(command, nlp_result, [])
            )

            # Add context
            context_id = self.context_manager.add_context(
                command=command,
                intent=intent_result["intent"],
                target=nlp_result["target"],
                result={
                    "success": True,
                    "agents_used": intent_result["suggested_agents"],
                },
                session_id=session_id,
            )

            print(f"📝 Added context: {context_id}")

        # Analyze context
        analysis = self.context_manager.analyze_context(
            "do the same for microsoft.com", session_id
        )

        print(f"\n🧠 Context Analysis:")
        print(f"  • Is Follow-up: {analysis['is_follow_up']}")
        print(f"  • Is Comparison: {analysis['is_comparison']}")
        print(f"  • User Pattern: {analysis['user_pattern']}")
        print(f"  • Confidence: {analysis['confidence']:.1%}")

        if analysis["contextual_suggestions"]:
            print(f"  • Suggestions: {analysis['contextual_suggestions'][:2]}")

    def example_6_visual_interface(self):
        """Example 6: Visual Interface"""
        print("\n" + "=" * 60)
        print("🎨 Example 6: Visual Interface")
        print("=" * 60)

        visual_interface = VisualInterface(self.console, self.config.get("ui", {}))

        # Display system status
        system_info = {
            "session_id": "example_session",
            "version": "2.0.0",
            "mode": "Interactive",
            "agent_count": 7,
            "model_count": 9,
        }

        visual_interface.display_welcome(system_info)

        # Display help
        help_data = {
            "content": """
# 🎯 AMAS Interactive Commands

## Core Commands
- `help` - Show this help
- `status` - Display system status
- `history` - Show task history

## Security Operations
- `scan [target]` - Security vulnerability scan
- `audit [target]` - Security audit

## Code Analysis
- `analyze code in [path/repo]` - Code quality analysis
- `review [repository]` - Code review
            """
        }

        visual_interface.display_help(help_data)

    def example_7_configuration_management(self):
        """Example 7: Configuration Management"""
        print("\n" + "=" * 60)
        print("⚙️ Example 7: Configuration Management")
        print("=" * 60)

        # Display configuration summary
        self.config_manager.display_config_summary()

        # Display agent configurations
        self.config_manager.display_agent_configs()

        # Validate configuration
        issues = self.config_manager.validate_config()
        if issues:
            print(f"\n⚠️  Configuration Issues Found:")
            for issue in issues:
                print(f"  • {issue}")
        else:
            print(f"\n✅ Configuration is valid")

    def example_8_logging_system(self):
        """Example 8: Logging System"""
        print("\n" + "=" * 60)
        print("📊 Example 8: Logging System")
        print("=" * 60)

        # Set session
        self.logger.set_session("example_session")

        # Log various events
        self.logger.info("Example session started")
        self.logger.task_start("task_001", "security_scan", "google.com")
        self.logger.agent_activity("security_expert", "scanning target")
        self.logger.task_complete("task_001", "security_scan", 3.24)
        self.logger.user_action("scanned google.com")
        self.logger.performance_metric("response_time", 3.24, "s")

        # Display logging summary
        self.logger.display_log_summary()

    def example_9_complete_workflow(self):
        """Example 9: Complete Workflow"""
        print("\n" + "=" * 60)
        print("🔄 Example 9: Complete Workflow")
        print("=" * 60)

        # Simulate a complete security analysis workflow
        workflow_commands = [
            "scan github.com/microsoft/vscode",
            "analyze the code quality of the same repository",
            "research security best practices for TypeScript",
            "create a comprehensive security report",
        ]

        session_id = "workflow_session"

        for i, command in enumerate(workflow_commands, 1):
            print(f"\n🔄 Step {i}: {command}")

            # Process command
            nlp_result = asyncio.run(self.nlp_engine.process_command(command))
            intent_result = asyncio.run(
                self.intent_classifier.classify_intent(command, nlp_result, [])
            )

            # Add context
            self.context_manager.add_context(
                command=command,
                intent=intent_result["intent"],
                target=nlp_result["target"],
                result={
                    "success": True,
                    "agents_used": intent_result["suggested_agents"],
                    "step": i,
                },
                session_id=session_id,
            )

            print(
                f"  ✅ Processed: {intent_result['intent']} "
                f"({intent_result['confidence']:.1%})"
            )
            print(f"  🤖 Agents: {', '.join(intent_result['suggested_agents'])}")

        # Analyze workflow context
        analysis = self.context_manager.analyze_context(
            "generate a summary of all findings", session_id
        )

        print(f"\n📊 Workflow Analysis:")
        print(f"  • Total Steps: {len(workflow_commands)}")
        print(
            f"  • Context Entries: {len(self.context_manager.get_context(session_id))}"
        )
        print(f"  • User Pattern: {analysis['user_pattern']}")
        print(f"  • Is Follow-up: {analysis['is_follow_up']}")

    def run_all_examples(self):
        """Run all examples"""
        print("🚀 AMAS Interactive Mode Examples")
        print("Advanced Multi-Agent Intelligence System")
        print("=" * 60)

        try:
            self.example_1_nlp_processing()
            self.example_2_intent_classification()
            self.example_3_agent_coordination()
            self.example_4_task_management()
            self.example_5_context_management()
            self.example_6_visual_interface()
            self.example_7_configuration_management()
            self.example_8_logging_system()
            self.example_9_complete_workflow()

            print("\n" + "=" * 60)
            print("🎉 All examples completed successfully!")
            print("=" * 60)

        except Exception as e:
            print(f"\n❌ Error running examples: {e}")
            import traceback

            traceback.print_exc()


def main():
    """Main function"""
    examples = AMASInteractiveExamples()
    examples.run_all_examples()


if __name__ == "__main__":
    main()
