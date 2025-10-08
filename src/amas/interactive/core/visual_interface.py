"""
AMAS Visual Interface - Advanced Console UI
Advanced Multi-Agent Intelligence System - Interactive Mode

This module provides a comprehensive visual interface with real-time monitoring,
progress tracking, and beautiful console output for the AMAS interactive system.
"""

import asyncio
import json
import time
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Union

from rich import print as rprint
from rich.align import Align
from rich.columns import Columns

# Rich for advanced console UI
from rich.console import Console, Group
from rich.layout import Layout
from rich.live import Live
from rich.markdown import Markdown
from rich.panel import Panel
from rich.progress import (
    BarColumn,
    MofNCompleteColumn,
    Progress,
    SpinnerColumn,
    TextColumn,
    TimeElapsedColumn,
)
from rich.prompt import Confirm, IntPrompt, Prompt
from rich.rule import Rule
from rich.spinner import Spinner
from rich.status import Status
from rich.syntax import Syntax
from rich.table import Table
from rich.text import Text
from rich.tree import Tree


class DisplayMode(Enum):
    """Display mode enumeration"""

    COMPACT = "compact"
    DETAILED = "detailed"
    MINIMAL = "minimal"
    FULL = "full"


@dataclass
class DisplayConfig:
    """Display configuration"""

    mode: DisplayMode = DisplayMode.DETAILED
    show_progress: bool = True
    show_metrics: bool = True
    show_agents: bool = True
    show_timeline: bool = True
    color_scheme: str = "default"
    refresh_rate: float = 0.1
    max_history: int = 50


class VisualInterface:
    """Advanced Visual Interface for AMAS Interactive Mode"""

    def __init__(self, console: Console, config: Dict[str, Any]):
        self.console = console
        self.config = DisplayConfig(**config.get("display", {}))

        # Display state
        self.current_layout = None
        self.live_display = None
        self.is_live_mode = False

        # Performance tracking
        self.display_stats = {
            "frames_rendered": 0,
            "average_render_time": 0.0,
            "last_render_time": 0.0,
        }

        # Initialize display components
        self._initialize_components()

    def _initialize_components(self):
        """Initialize display components"""
        self.banner = self._create_banner()
        self.status_panel = self._create_status_panel()
        self.metrics_panel = self._create_metrics_panel()
        self.agent_panel = self._create_agent_panel()
        self.timeline_panel = self._create_timeline_panel()

    def _create_banner(self) -> Panel:
        """Create system banner"""
        banner_text = """
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║    🚀 ADVANCED MULTI-AGENT INTELLIGENCE SYSTEM (AMAS) - INTERACTIVE MODE    ║
║                                                                              ║
║    🤖 7 Specialized AI Agents Ready for Command                             ║
║    🧠 9 Advanced AI Models Coordinated                                      ║
║    🔒 Enterprise-Grade Security Hardened                                     ║
║    ⚡ Next-Gen Interactive Command Interface                                  ║
║    🎯 Natural Language Processing Enabled                                    ║
║    📊 Real-Time Agent Coordination                                           ║
║    🔄 Intelligent Task Management                                            ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
        """
        return Panel(
            banner_text,
            title="🚀 AMAS Interactive System",
            border_style="cyan",
            padding=(1, 2),
        )

    def _create_status_panel(self) -> Panel:
        """Create system status panel"""
        return Panel(
            "System initializing...", title="🔋 System Status", border_style="green"
        )

    def _create_metrics_panel(self) -> Panel:
        """Create performance metrics panel"""
        return Panel(
            "No metrics available", title="📊 Performance Metrics", border_style="blue"
        )

    def _create_agent_panel(self) -> Panel:
        """Create agent status panel"""
        return Panel(
            "Agents initializing...", title="🤖 Agent Status", border_style="yellow"
        )

    def _create_timeline_panel(self) -> Panel:
        """Create activity timeline panel"""
        return Panel(
            "No activity yet", title="📈 Activity Timeline", border_style="magenta"
        )

    def display_welcome(self, system_info: Dict[str, Any]):
        """Display welcome screen with system information"""
        self.console.clear()
        self.console.print(self.banner)

        # System info panel
        info_table = Table(title="ℹ️ System Information")
        info_table.add_column("Property", style="cyan", width=20)
        info_table.add_column("Value", style="green")

        info_table.add_row("Session ID", system_info.get("session_id", "Unknown"))
        info_table.add_row("Version", system_info.get("version", "2.0.0"))
        info_table.add_row("Mode", system_info.get("mode", "Interactive"))
        info_table.add_row("Agents", str(system_info.get("agent_count", 7)))
        info_table.add_row("AI Models", str(system_info.get("model_count", 9)))
        info_table.add_row("Status", "✅ Ready")

        self.console.print(info_table)

        # Quick start panel
        quick_start = Panel(
            "🎯 Type 'help' for commands or describe what you want me to do.\n"
            "💡 Example: 'scan google.com for vulnerabilities'\n"
            "🔧 Use 'status' to check system health\n"
            "📚 Use 'history' to see previous tasks",
            title="🚀 Quick Start",
            border_style="green",
        )
        self.console.print(quick_start)

    def display_system_status(self, status_data: Dict[str, Any]):
        """Display comprehensive system status"""
        # Create status table
        status_table = Table(title="🔋 AMAS System Status")
        status_table.add_column("Component", style="cyan", width=25)
        status_table.add_column("Status", style="green", width=15)
        status_table.add_column("Details", style="yellow")

        # System components
        components = status_data.get("components", {})
        for component, info in components.items():
            status_icon = "✅" if info.get("status") == "active" else "❌"
            status_table.add_row(
                component,
                f"{status_icon} {info.get('status', 'unknown').title()}",
                info.get("details", "No details available"),
            )

        # Performance metrics
        metrics = status_data.get("metrics", {})
        if metrics:
            metrics_table = Table(title="📊 Performance Metrics")
            metrics_table.add_column("Metric", style="cyan")
            metrics_table.add_column("Value", style="green")

            for metric, value in metrics.items():
                if isinstance(value, float):
                    metrics_table.add_row(metric, f"{value:.2f}")
                else:
                    metrics_table.add_row(metric, str(value))

            # Combine tables
            combined = Group(status_table, metrics_table)
            self.console.print(combined)
        else:
            self.console.print(status_table)

    def display_agent_status(self, agents_data: Dict[str, Any]):
        """Display agent status with detailed information"""
        # Main agent table
        agent_table = Table(title="🤖 Agent Status")
        agent_table.add_column("Agent", style="cyan", width=20)
        agent_table.add_column("Status", style="green", width=12)
        agent_table.add_column("Tasks", style="yellow", width=10)
        agent_table.add_column("Performance", style="blue", width=12)
        agent_table.add_column("Last Activity", style="magenta", width=15)

        agents = agents_data.get("agents", {})
        for agent_id, agent_info in agents.items():
            status_icon = (
                "🟢"
                if agent_info.get("status") == "idle"
                else "🟡" if agent_info.get("status") == "busy" else "🔴"
            )

            agent_table.add_row(
                agent_info.get("name", agent_id),
                f"{status_icon} {agent_info.get('status', 'unknown').title()}",
                f"{agent_info.get('current_tasks', 0)}/{agent_info.get('max_tasks', 1)}",
                f"{agent_info.get('performance_score', 0):.1%}",
                (
                    agent_info.get("last_activity", "Unknown")[:19]
                    if agent_info.get("last_activity")
                    else "Unknown"
                ),
            )

        self.console.print(agent_table)

        # Agent capabilities tree
        if self.config.mode == DisplayMode.DETAILED:
            self._display_agent_capabilities(agents)

    def _display_agent_capabilities(self, agents: Dict[str, Any]):
        """Display agent capabilities as a tree"""
        tree = Tree("🎯 Agent Capabilities", style="bold blue")

        for agent_id, agent_info in agents.items():
            agent_name = agent_info.get("name", agent_id)
            agent_branch = tree.add(f"🤖 {agent_name}", style="cyan")

            capabilities = agent_info.get("capabilities", [])
            for capability in capabilities:
                agent_branch.add(f"• {capability}", style="green")

        self.console.print(tree)

    def display_task_progress(self, task_id: str, progress_data: Dict[str, Any]):
        """Display real-time task progress"""
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            MofNCompleteColumn(),
            TimeElapsedColumn(),
            console=self.console,
        ) as progress:

            task = progress.add_task(
                f"Executing {progress_data.get('intent', 'task')}...", total=100
            )

            # Update progress based on data
            current_progress = progress_data.get("progress", 0)
            progress.update(task, completed=current_progress)

            # Show agent activity
            agents = progress_data.get("agents", [])
            if agents:
                agent_text = f"Agents: {', '.join(agents)}"
                progress.update(
                    task,
                    description=f"Executing {progress_data.get('intent', 'task')}... {agent_text}",
                )

    def display_task_results(self, task_id: str, results: Dict[str, Any]):
        """Display comprehensive task results"""
        # Create results layout
        layout = Layout()
        layout.split_column(
            Layout(self._create_task_summary_table(task_id, results), name="summary"),
            Layout(self._create_detailed_results_panel(results), name="details"),
        )

        self.console.print(layout)

        # Show agent activity if available
        if "agents_used" in results:
            self._display_agent_activity(results["agents_used"])

    def _create_task_summary_table(
        self, task_id: str, results: Dict[str, Any]
    ) -> Table:
        """Create task summary table"""
        table = Table(title=f"📋 Task Summary: {task_id}")
        table.add_column("Attribute", style="cyan", width=20)
        table.add_column("Value", style="green")

        # Basic info
        table.add_row("Task ID", task_id)
        table.add_row(
            "Intent", results.get("intent", "unknown").replace("_", " ").title()
        )
        table.add_row("Target", results.get("target", "general"))
        table.add_row("Status", results.get("status", "unknown").upper())

        # Timing
        if "execution_time" in results:
            table.add_row("Duration", f"{results['execution_time']:.2f} seconds")

        # Agents
        if "agents_used" in results:
            table.add_row("Agents", ", ".join(results["agents_used"]))

        # Results summary
        if "security_score" in results:
            table.add_row("Security Score", f"{results['security_score']}/100")
        elif "code_quality_score" in results:
            table.add_row("Code Quality", f"{results['code_quality_score']}/100")
        elif "confidence_level" in results:
            table.add_row("Confidence", f"{results['confidence_level']}%")

        return table

    def _create_detailed_results_panel(self, results: Dict[str, Any]) -> Panel:
        """Create detailed results panel"""
        content = []

        # Security scan results
        if "security_score" in results:
            content.append("🔒 Security Analysis Results:")
            content.append(f"• Overall Security Score: {results['security_score']}/100")
            content.append(f"• SSL/TLS Rating: {results.get('ssl_rating', 'Unknown')}")

            vulns = results.get("vulnerabilities", {})
            content.append(
                f"• Vulnerabilities: {vulns.get('critical', 0)} Critical, "
                f"{vulns.get('high', 0)} High, {vulns.get('medium', 0)} Medium, "
                f"{vulns.get('low', 0)} Low"
            )

            if "recommendations" in results:
                content.append("\n📋 Recommendations:")
                for rec in results["recommendations"]:
                    content.append(f"• {rec}")

        # Code analysis results
        elif "code_quality_score" in results:
            content.append("📝 Code Analysis Results:")
            content.append(f"• Code Quality Score: {results['code_quality_score']}/100")

            metrics = results.get("metrics", {})
            content.append(f"• Lines of Code: {metrics.get('lines_of_code', 0):,}")
            content.append(f"• Functions: {metrics.get('functions', 0)}")
            content.append(f"• Classes: {metrics.get('classes', 0)}")
            content.append(f"• Test Coverage: {metrics.get('test_coverage', 0)}%")

            issues = results.get("issues", {})
            content.append(f"• Issues Found: {sum(issues.values())} total")
            for issue_type, count in issues.items():
                if count > 0:
                    content.append(f"  - {issue_type.title()}: {count}")

        # Intelligence gathering results
        elif "sources_analyzed" in results:
            content.append("🕵️ Intelligence Analysis Results:")
            content.append(f"• Sources Analyzed: {results['sources_analyzed']}")
            content.append(f"• Data Points: {results['data_points']}")
            content.append(f"• Confidence Level: {results['confidence_level']}%")
            content.append(
                f"• Threat Level: {results.get('threat_level', 'unknown').title()}"
            )

            if "key_findings" in results:
                content.append("\n🎯 Key Findings:")
                for finding in results["key_findings"]:
                    content.append(f"• {finding}")

        else:
            content.append("📊 Analysis Results:")
            content.append(f"• Status: {results.get('status', 'unknown')}")
            content.append(
                f"• Analysis Complete: {results.get('analysis_complete', False)}"
            )

            if "findings" in results:
                content.append(f"• Findings: {results['findings']}")

        return Panel(
            "\n".join(content), title="🔍 Detailed Results", border_style="blue"
        )

    def _display_agent_activity(self, agents: List[str]):
        """Display agent activity information"""
        if not agents:
            return

        activity_table = Table(title="🤖 Agent Activity")
        activity_table.add_column("Agent", style="cyan")
        activity_table.add_column("Status", style="green")
        activity_table.add_column("Contribution", style="yellow")

        for agent in agents:
            activity_table.add_row(agent, "✅ Completed", "Contributed to analysis")

        self.console.print(activity_table)

    def display_task_history(self, history_data: Dict[str, Any]):
        """Display task history with statistics"""
        tasks = history_data.get("tasks", [])
        if not tasks:
            self.console.print("📝 No tasks executed yet", style="yellow")
            return

        # Create history table
        history_table = Table(title="📚 Task History")
        history_table.add_column("Task ID", style="cyan", width=10)
        history_table.add_column("Command", style="white", width=30)
        history_table.add_column("Intent", style="green", width=20)
        history_table.add_column("Status", style="yellow", width=12)
        history_table.add_column("Duration", style="blue", width=10)
        history_table.add_column("Created", style="magenta", width=12)

        # Sort tasks by creation time (newest first)
        sorted_tasks = sorted(
            tasks, key=lambda t: t.get("created_at", ""), reverse=True
        )

        for task in sorted_tasks[:20]:  # Show last 20 tasks
            duration = task.get("duration", "Unknown")
            if isinstance(duration, (int, float)):
                duration = f"{duration:.1f}s"

            # Truncate command if too long
            command = task.get("command", "")
            if len(command) > 30:
                command = command[:27] + "..."

            history_table.add_row(
                task.get("id", "Unknown")[:8],
                command,
                task.get("intent", "unknown").replace("_", " ").title(),
                task.get("status", "unknown").upper(),
                duration,
                (
                    task.get("created_at", "Unknown")[:19]
                    if task.get("created_at")
                    else "Unknown"
                ),
            )

        self.console.print(history_table)

        # Show summary statistics
        self._display_history_summary(history_data)

    def _display_history_summary(self, history_data: Dict[str, Any]):
        """Display history summary statistics"""
        tasks = history_data.get("tasks", [])
        if not tasks:
            return

        # Calculate statistics
        total_tasks = len(tasks)
        completed_tasks = len([t for t in tasks if t.get("status") == "completed"])
        failed_tasks = len([t for t in tasks if t.get("status") == "failed"])
        running_tasks = len([t for t in tasks if t.get("status") == "running"])

        # Calculate average duration
        completed_with_duration = [
            t
            for t in tasks
            if t.get("status") == "completed"
            and isinstance(t.get("duration"), (int, float))
        ]
        avg_duration = 0
        if completed_with_duration:
            total_duration = sum(t.get("duration", 0) for t in completed_with_duration)
            avg_duration = total_duration / len(completed_with_duration)

        # Create summary table
        summary_table = Table(title="📈 History Summary")
        summary_table.add_column("Statistic", style="cyan")
        summary_table.add_column("Value", style="green")

        summary_table.add_row("Total Tasks", str(total_tasks))
        summary_table.add_row("Completed", str(completed_tasks))
        summary_table.add_row("Failed", str(failed_tasks))
        summary_table.add_row("Running", str(running_tasks))
        summary_table.add_row(
            "Success Rate", f"{(completed_tasks/total_tasks*100):.1f}%"
        )
        summary_table.add_row("Average Duration", f"{avg_duration:.2f}s")

        self.console.print(summary_table)

    def display_help(self, help_data: Dict[str, Any]):
        """Display comprehensive help information"""
        help_content = help_data.get("content", "")

        if help_content:
            self.console.print(Markdown(help_content))
        else:
            # Default help content
            self._display_default_help()

    def _display_default_help(self):
        """Display default help content"""
        help_text = """
# 🎯 AMAS Interactive Commands - Next Generation

## 🚀 Core Commands
- `help` - Show this comprehensive help
- `status` - Display system status and metrics
- `history` - Show task history and statistics
- `metrics` - Display performance metrics
- `config` - Show configuration information
- `agents` - List available agents and their status
- `tasks` - Show active and recent tasks
- `clear` - Clear screen and reset display
- `exit` / `quit` - Exit AMAS interactive mode

## 🔒 Security Operations
- `scan [target]` - Comprehensive security vulnerability scan
- `audit [target]` - Security audit and compliance check
- `analyze security of [target]` - Deep security analysis
- `check vulnerabilities in [target]` - Vulnerability assessment
- `monitor [target]` - Continuous security monitoring
- `threat analysis for [target]` - Advanced threat analysis

## 🕵️ Intelligence Gathering
- `research [target]` - OSINT investigation and research
- `investigate [target]` - Deep investigation and analysis
- `gather intelligence on [target]` - Intelligence collection
- `analyze threat landscape for [target]` - Threat landscape analysis
- `monitor [target] for threats` - Threat monitoring setup

## 📝 Code Analysis
- `analyze code in [path/repo]` - Code quality and structure analysis
- `review [repository]` - Code review and best practices check
- `test coverage for [project]` - Testing analysis and coverage
- `document [codebase]` - Auto-documentation generation
- `optimize [codebase]` - Performance optimization analysis

## 🔧 System Operations
- `system health` - Check system health and status
- `performance report` - Generate performance analysis
- `backup system` - Create system backup
- `update agents` - Update agent configurations
- `restart services` - Restart AMAS services

## 🎨 Advanced Features
- `create workflow [name]` - Create custom workflow
- `schedule task [command]` - Schedule recurring task
- `export results [task_id]` - Export task results
- `compare [target1] vs [target2]` - Comparative analysis
- `trend analysis for [target]` - Trend analysis over time

## 💡 Natural Language Examples
- "Scan google.com for security vulnerabilities"
- "Analyze the code quality of my React application"
- "Research the latest AI security threats"
- "Investigate suspicious activity on our network"
- "Monitor our website for performance issues"
- "Create a security audit report for our API"

## 🔄 Context Awareness
AMAS remembers your previous commands and can build upon them:
- "Do the same analysis for microsoft.com"
- "Compare these results with the previous scan"
- "Generate a report combining all findings"
- "Schedule this scan to run daily"

## ⚡ Quick Tips
- Use `Ctrl+C` to cancel running tasks
- Use `Ctrl+D` to exit gracefully
- Commands are case-insensitive
- Use quotes for multi-word targets
- Add `--verbose` for detailed output
- Use `--priority high` for urgent tasks
        """

        self.console.print(Markdown(help_text))

    def start_live_display(self, layout_func: callable):
        """Start live display mode"""
        self.is_live_mode = True
        self.live_display = Live(
            layout_func(),
            console=self.console,
            refresh_per_second=self.config.refresh_rate,
        )
        self.live_display.start()

    def stop_live_display(self):
        """Stop live display mode"""
        if self.live_display:
            self.live_display.stop()
            self.is_live_mode = False

    def update_live_display(self, layout_func: callable):
        """Update live display"""
        if self.is_live_mode and self.live_display:
            self.live_display.update(layout_func())

    def display_error(self, error: str, details: Optional[str] = None):
        """Display error message with details"""
        error_panel = Panel(
            f"❌ {error}" + (f"\n\nDetails: {details}" if details else ""),
            title="Error",
            border_style="red",
        )
        self.console.print(error_panel)

    def display_success(self, message: str, details: Optional[str] = None):
        """Display success message"""
        success_panel = Panel(
            f"✅ {message}" + (f"\n\nDetails: {details}" if details else ""),
            title="Success",
            border_style="green",
        )
        self.console.print(success_panel)

    def display_warning(self, message: str, details: Optional[str] = None):
        """Display warning message"""
        warning_panel = Panel(
            f"⚠️ {message}" + (f"\n\nDetails: {details}" if details else ""),
            title="Warning",
            border_style="yellow",
        )
        self.console.print(warning_panel)

    def display_info(self, message: str, details: Optional[str] = None):
        """Display info message"""
        info_panel = Panel(
            f"ℹ️ {message}" + (f"\n\nDetails: {details}" if details else ""),
            title="Information",
            border_style="blue",
        )
        self.console.print(info_panel)

    def clear_screen(self):
        """Clear the screen"""
        self.console.clear()

    def get_display_stats(self) -> Dict[str, Any]:
        """Get display performance statistics"""
        return self.display_stats.copy()

    def update_display_config(self, new_config: Dict[str, Any]):
        """Update display configuration"""
        for key, value in new_config.items():
            if hasattr(self.config, key):
                setattr(self.config, key, value)
