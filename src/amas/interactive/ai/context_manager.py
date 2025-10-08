"""
AMAS Context Manager - Advanced Context Management
Advanced Multi-Agent Intelligence System - Interactive Mode

This module provides intelligent context management for maintaining
conversation history, user preferences, and contextual awareness
across multiple interactions.
"""

import json
import logging
import time
from collections import deque
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple

# Rich for enhanced output
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

@dataclass
class ContextEntry:
    """Context entry data structure"""

    timestamp: datetime
    command: str
    intent: str
    target: str
    result: Dict[str, Any]
    session_id: str
    user_id: Optional[str] = None
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}

@dataclass
class UserProfile:
    """User profile data structure"""

    user_id: str
    preferences: Dict[str, Any]
    command_history: List[str]
    preferred_agents: List[str]
    common_intents: Dict[str, int]
    created_at: datetime
    last_active: datetime
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}

class ContextManager:
    """Advanced Context Management System"""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.console = Console()
        self.logger = logging.getLogger(__name__)

        # Context storage
        self.context_history: deque = deque(
            maxlen=config.get("max_context_length", 100)
        )
        self.user_profiles: Dict[str, UserProfile] = {}
        self.session_contexts: Dict[str, List[ContextEntry]] = {}

        # Context analysis
        self.intent_patterns = {}
        self.user_behavior_patterns = {}
        self.contextual_suggestions = {}

        # Performance tracking
        self.context_stats = {
            "total_contexts": 0,
            "context_hits": 0,
            "suggestion_accuracy": 0.0,
            "average_context_size": 0.0,
        }

        # Initialize context analysis
        self._initialize_context_analysis()

    def _initialize_context_analysis(self):
        """Initialize context analysis components"""
        # Common intent patterns
        self.intent_patterns = {
            "follow_up": ["also", "and", "then", "next", "also check", "also analyze"],
            "comparison": ["compare", "vs", "versus", "difference", "similar"],
            "repeat": ["again", "repeat", "same", "do the same"],
            "modify": ["but", "however", "instead", "change", "modify"],
            "elaborate": ["more", "details", "explain", "elaborate", "tell me more"],
        }

        # User behavior patterns
        self.user_behavior_patterns = {
            "security_focused": ["scan", "audit", "security", "vulnerability"],
            "development_focused": ["code", "analyze", "review", "test"],
            "research_focused": ["research", "investigate", "gather", "intelligence"],
            "monitoring_focused": ["monitor", "performance", "status", "health"],
        }

    def add_context(
        self,
        command: str,
        intent: str,
        target: str,
        result: Dict[str, Any],
        session_id: str,
        user_id: Optional[str] = None,
    ) -> str:
        """Add new context entry"""
        context_id = f"ctx_{int(time.time() * 1000)}"

        context_entry = ContextEntry(
            timestamp=datetime.now(),
            command=command,
            intent=intent,
            target=target,
            result=result,
            session_id=session_id,
            user_id=user_id,
            metadata={
                "context_id": context_id,
                "command_length": len(command),
                "result_size": len(str(result)),
            },
        )

        # Add to context history
        self.context_history.append(context_entry)

        # Add to session context
        if session_id not in self.session_contexts:
            self.session_contexts[session_id] = []
        self.session_contexts[session_id].append(context_entry)

        # Update user profile
        if user_id:
            self._update_user_profile(user_id, context_entry)

        # Update statistics
        self.context_stats["total_contexts"] += 1
        self._update_context_stats()

        self.logger.info(f"Added context: {intent} for {target}")
        return context_id

    def get_context(self, session_id: str, limit: int = 10) -> List[ContextEntry]:
        """Get context for specific session"""
        if session_id in self.session_contexts:
            return self.session_contexts[session_id][-limit:]
        return []

    def get_recent_context(self, limit: int = 10) -> List[ContextEntry]:
        """Get recent context across all sessions"""
        return list(self.context_history)[-limit:]

    def analyze_context(self, current_command: str, session_id: str) -> Dict[str, Any]:
        """Analyze current command in context"""
        analysis = {
            "is_follow_up": False,
            "is_comparison": False,
            "is_repeat": False,
            "is_modification": False,
            "suggested_intent": None,
            "contextual_suggestions": [],
            "user_pattern": None,
            "confidence": 0.0,
        }

        # Get recent context for session
        recent_context = self.get_context(session_id, 5)

        if not recent_context:
            return analysis

        # Analyze command patterns
        command_lower = current_command.lower()

        # Check for follow-up patterns
        for pattern in self.intent_patterns["follow_up"]:
            if pattern in command_lower:
                analysis["is_follow_up"] = True
                analysis["confidence"] += 0.3
                break

        # Check for comparison patterns
        for pattern in self.intent_patterns["comparison"]:
            if pattern in command_lower:
                analysis["is_comparison"] = True
                analysis["confidence"] += 0.4
                break

        # Check for repeat patterns
        for pattern in self.intent_patterns["repeat"]:
            if pattern in command_lower:
                analysis["is_repeat"] = True
                analysis["confidence"] += 0.5
                break

        # Check for modification patterns
        for pattern in self.intent_patterns["modify"]:
            if pattern in command_lower:
                analysis["is_modification"] = True
                analysis["confidence"] += 0.3
                break

        # Analyze user behavior pattern
        analysis["user_pattern"] = self._analyze_user_pattern(recent_context)

        # Generate contextual suggestions
        analysis["contextual_suggestions"] = self._generate_contextual_suggestions(
            current_command, recent_context, analysis
        )

        # Suggest intent based on context
        if analysis["is_follow_up"] and recent_context:
            last_intent = recent_context[-1].intent
            analysis["suggested_intent"] = last_intent
            analysis["confidence"] += 0.2

        return analysis

    def _analyze_user_pattern(
        self, recent_context: List[ContextEntry]
    ) -> Optional[str]:
        """Analyze user behavior pattern"""
        if not recent_context:
            return None

        # Count intent occurrences
        intent_counts = {}
        for context in recent_context:
            intent = context.intent
            intent_counts[intent] = intent_counts.get(intent, 0) + 1

        # Find most common intent
        if intent_counts:
            most_common_intent = max(intent_counts.items(), key=lambda x: x[1])

            # Map to behavior pattern
            for pattern, keywords in self.user_behavior_patterns.items():
                if any(keyword in most_common_intent for keyword in keywords):
                    return pattern

        return None

    def _generate_contextual_suggestions(
        self, command: str, recent_context: List[ContextEntry], analysis: Dict[str, Any]
    ) -> List[str]:
        """Generate contextual suggestions based on history"""
        suggestions = []

        if not recent_context:
            return suggestions

        last_context = recent_context[-1]

        # Follow-up suggestions
        if analysis["is_follow_up"]:
            if last_context.intent == "security_scan":
                suggestions.extend(
                    [
                        "Try 'analyze code quality of the same target'",
                        "Run 'research intelligence on the target'",
                        "Check 'performance monitoring for the target'",
                    ]
                )
            elif last_context.intent == "code_analysis":
                suggestions.extend(
                    [
                        "Try 'security scan of the same target'",
                        "Run 'test coverage analysis'",
                        "Check 'documentation generation'",
                    ]
                )

        # Comparison suggestions
        if analysis["is_comparison"]:
            suggestions.extend(
                [
                    "Use 'compare security scores'",
                    "Try 'analyze differences in code quality'",
                    "Run 'performance comparison analysis'",
                ]
            )

        # Repeat suggestions
        if analysis["is_repeat"]:
            suggestions.extend(
                [
                    f"Repeat '{last_context.intent}' on different target",
                    "Try similar analysis with different parameters",
                    "Run comprehensive analysis",
                ]
            )

        # Modification suggestions
        if analysis["is_modification"]:
            suggestions.extend(
                [
                    "Modify the previous command with new parameters",
                    "Try a different approach to the same target",
                    "Adjust the analysis scope",
                ]
            )

        # General suggestions based on user pattern
        user_pattern = analysis.get("user_pattern")
        if user_pattern == "security_focused":
            suggestions.extend(
                [
                    "Try 'threat analysis' for comprehensive security",
                    "Run 'incident response' if issues found",
                    "Check 'vulnerability assessment'",
                ]
            )
        elif user_pattern == "development_focused":
            suggestions.extend(
                [
                    "Try 'code review' for quality assessment",
                    "Run 'performance optimization' analysis",
                    "Check 'testing coordination'",
                ]
            )

        return suggestions[:5]  # Limit to 5 suggestions

    def _update_user_profile(self, user_id: str, context_entry: ContextEntry):
        """Update user profile with new context"""
        if user_id not in self.user_profiles:
            self.user_profiles[user_id] = UserProfile(
                user_id=user_id,
                preferences={},
                command_history=[],
                preferred_agents=[],
                common_intents={},
                created_at=datetime.now(),
                last_active=datetime.now(),
            )

        profile = self.user_profiles[user_id]

        # Update command history
        profile.command_history.append(context_entry.command)
        if len(profile.command_history) > 100:  # Keep last 100 commands
            profile.command_history = profile.command_history[-100:]

        # Update common intents
        intent = context_entry.intent
        profile.common_intents[intent] = profile.common_intents.get(intent, 0) + 1

        # Update last active
        profile.last_active = datetime.now()

        # Update preferred agents based on successful results
        if context_entry.result.get("success", False):
            agents = context_entry.result.get("agents_used", [])
            for agent in agents:
                if agent not in profile.preferred_agents:
                    profile.preferred_agents.append(agent)

    def _update_context_stats(self):
        """Update context statistics"""
        if self.context_history:
            total_size = sum(len(str(ctx)) for ctx in self.context_history)
            self.context_stats["average_context_size"] = total_size / len(
                self.context_history
            )

    def get_user_profile(self, user_id: str) -> Optional[UserProfile]:
        """Get user profile"""
        return self.user_profiles.get(user_id)

    def update_user_preferences(self, user_id: str, preferences: Dict[str, Any]):
        """Update user preferences"""
        if user_id in self.user_profiles:
            self.user_profiles[user_id].preferences.update(preferences)
        else:
            self.user_profiles[user_id] = UserProfile(
                user_id=user_id,
                preferences=preferences,
                command_history=[],
                preferred_agents=[],
                common_intents={},
                created_at=datetime.now(),
                last_active=datetime.now(),
            )

    def get_contextual_recommendations(
        self, session_id: str, current_intent: str
    ) -> List[str]:
        """Get contextual recommendations based on session history"""
        recent_context = self.get_context(session_id, 10)
        recommendations = []

        if not recent_context:
            return recommendations

        # Analyze recent intents
        recent_intents = [ctx.intent for ctx in recent_context[-5:]]
        intent_counts = {}
        for intent in recent_intents:
            intent_counts[intent] = intent_counts.get(intent, 0) + 1

        # Find patterns
        if len(set(recent_intents)) == 1:  # Same intent repeated
            recommendations.append(f"Consider trying different analysis types")
            recommendations.append(f"Explore complementary intents")

        # Security-focused recommendations
        if "security" in current_intent.lower():
            recommendations.extend(
                [
                    "Try 'threat analysis' for comprehensive security assessment",
                    "Run 'incident response' if vulnerabilities found",
                    "Consider 'compliance checking' for regulatory requirements",
                ]
            )

        # Code analysis recommendations
        elif "code" in current_intent.lower():
            recommendations.extend(
                [
                    "Try 'performance monitoring' for optimization",
                    "Run 'testing coordination' for quality assurance",
                    "Consider 'documentation generation' for code docs",
                ]
            )

        # Intelligence gathering recommendations
        elif (
            "intelligence" in current_intent.lower()
            or "research" in current_intent.lower()
        ):
            recommendations.extend(
                [
                    "Try 'threat analysis' for security intelligence",
                    "Run 'osint investigation' for deeper research",
                    "Consider 'incident response' if threats detected",
                ]
            )

        return recommendations[:5]  # Limit to 5 recommendations

    def export_context(self, session_id: str, file_path: str):
        """Export context for specific session"""
        try:
            context_data = []
            for context in self.get_context(session_id):
                context_dict = asdict(context)
                # Convert datetime to string
                context_dict["timestamp"] = context.timestamp.isoformat()
                context_data.append(context_dict)

            with open(file_path, "w") as f:
                json.dump(context_data, f, indent=2)

            self.console.print(f"✅ Context exported to {file_path}", style="green")

        except Exception as e:
            self.console.print(f"❌ Failed to export context: {e}", style="red")

    def clear_context(self, session_id: Optional[str] = None):
        """Clear context for session or all sessions"""
        if session_id:
            if session_id in self.session_contexts:
                del self.session_contexts[session_id]
                self.console.print(
                    f"✅ Context cleared for session {session_id}", style="green"
                )
        else:
            self.context_history.clear()
            self.session_contexts.clear()
            self.console.print("✅ All context cleared", style="green")

    def get_context_stats(self) -> Dict[str, Any]:
        """Get context statistics"""
        return self.context_stats.copy()

    def display_context_summary(self, session_id: Optional[str] = None):
        """Display context summary"""
        if session_id:
            context = self.get_context(session_id)
            title = f"📊 Context Summary - Session {session_id}"
        else:
            context = list(self.context_history)
            title = "📊 Context Summary - All Sessions"

        if not context:
            self.console.print("No context available", style="yellow")
            return

        # Create summary table
        table = Table(title=title)
        table.add_column("Time", style="cyan", width=12)
        table.add_column("Command", style="white", width=30)
        table.add_column("Intent", style="green", width=20)
        table.add_column("Target", style="blue", width=20)
        table.add_column("Success", style="yellow", width=8)

        for ctx in context[-10:]:  # Show last 10 entries
            success = "✅" if ctx.result.get("success", False) else "❌"
            command = ctx.command[:27] + "..." if len(ctx.command) > 30 else ctx.command

            table.add_row(
                ctx.timestamp.strftime("%H:%M:%S"),
                command,
                ctx.intent.replace("_", " ").title(),
                ctx.target[:17] + "..." if len(ctx.target) > 20 else ctx.target,
                success,
            )

        self.console.print(table)

        # Show statistics
        stats_table = Table(title="📈 Context Statistics")
        stats_table.add_column("Metric", style="cyan")
        stats_table.add_column("Value", style="green")

        stats_table.add_row("Total Contexts", str(len(context)))
        stats_table.add_row(
            "Unique Intents", str(len(set(ctx.intent for ctx in context)))
        )
        stats_table.add_row(
            "Unique Targets", str(len(set(ctx.target for ctx in context)))
        )

        # Success rate
        successful = len([ctx for ctx in context if ctx.result.get("success", False)])
        success_rate = (successful / len(context)) * 100 if context else 0
        stats_table.add_row("Success Rate", f"{success_rate:.1f}%")

        self.console.print(stats_table)
