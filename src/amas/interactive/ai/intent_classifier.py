"""
AMAS Intent Classifier - AI-Powered Command Understanding
Advanced Multi-Agent Intelligence System - Interactive Mode

This module provides advanced intent classification using machine learning
and pattern matching to understand user commands and determine appropriate
agent coordination strategies.
"""

import asyncio
import json
import logging
import re
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

# Rich for enhanced output
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

@dataclass
class IntentResult:
    """Intent classification result"""

    intent: str
    confidence: float
    parameters: Dict[str, Any]
    reasoning: List[str]
    suggested_agents: List[str]
    metadata: Dict[str, Any]

class IntentClassifier:
    """Advanced Intent Classification System"""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.console = Console()
        self.logger = logging.getLogger(__name__)

        # Intent patterns and rules
        self.intent_patterns = {}
        self.intent_keywords = {}
        self.intent_weights = {}
        self.context_rules = {}

        # Performance tracking
        self.classification_stats = {
            "total_classifications": 0,
            "correct_classifications": 0,
            "average_confidence": 0.0,
            "intent_distribution": {},
        }

        # Initialize patterns
        self._initialize_intent_patterns()
        self._initialize_context_rules()

    def _initialize_intent_patterns(self):
        """Initialize intent classification patterns"""
        self.intent_patterns = {
            "security_scan": {
                "patterns": [
                    r"scan\s+(.+)",
                    r"check\s+security\s+of\s+(.+)",
                    r"analyze\s+security\s+of\s+(.+)",
                    r"audit\s+(.+)",
                    r"vulnerability\s+scan\s+(.+)",
                    r"security\s+analysis\s+of\s+(.+)",
                    r"penetration\s+test\s+(.+)",
                    r"security\s+audit\s+of\s+(.+)",
                ],
                "keywords": [
                    "scan",
                    "security",
                    "vulnerability",
                    "audit",
                    "penetration",
                    "check",
                ],
                "weight": 1.0,
                "agents": ["security_expert", "intelligence_gathering"],
            },
            "code_analysis": {
                "patterns": [
                    r"analyze\s+code\s+(.+)",
                    r"review\s+code\s+(.+)",
                    r"check\s+code\s+quality\s+of\s+(.+)",
                    r"code\s+analysis\s+of\s+(.+)",
                    r"review\s+(.+)",
                    r"analyze\s+(.+)",
                    r"code\s+review\s+(.+)",
                    r"quality\s+check\s+(.+)",
                ],
                "keywords": [
                    "code",
                    "analyze",
                    "review",
                    "quality",
                    "function",
                    "class",
                    "method",
                ],
                "weight": 0.9,
                "agents": ["code_analysis", "security_expert"],
            },
            "intelligence_gathering": {
                "patterns": [
                    r"research\s+(.+)",
                    r"investigate\s+(.+)",
                    r"gather\s+intelligence\s+on\s+(.+)",
                    r"osint\s+(.+)",
                    r"intelligence\s+on\s+(.+)",
                    r"investigation\s+of\s+(.+)",
                    r"look\s+into\s+(.+)",
                    r"find\s+out\s+about\s+(.+)",
                ],
                "keywords": [
                    "research",
                    "investigate",
                    "intelligence",
                    "osint",
                    "gather",
                    "find",
                ],
                "weight": 0.95,
                "agents": ["intelligence_gathering", "security_expert"],
            },
            "performance_monitoring": {
                "patterns": [
                    r"monitor\s+(.+)",
                    r"check\s+performance\s+of\s+(.+)",
                    r"analyze\s+performance\s+of\s+(.+)",
                    r"performance\s+analysis\s+of\s+(.+)",
                    r"optimize\s+(.+)",
                    r"speed\s+up\s+(.+)",
                    r"improve\s+performance\s+of\s+(.+)",
                ],
                "keywords": [
                    "monitor",
                    "performance",
                    "optimize",
                    "speed",
                    "memory",
                    "cpu",
                ],
                "weight": 0.85,
                "agents": ["performance_monitor", "code_analysis"],
            },
            "documentation_generation": {
                "patterns": [
                    r"document\s+(.+)",
                    r"generate\s+documentation\s+for\s+(.+)",
                    r"create\s+docs\s+for\s+(.+)",
                    r"write\s+documentation\s+for\s+(.+)",
                    r"documentation\s+for\s+(.+)",
                    r"docs\s+for\s+(.+)",
                ],
                "keywords": [
                    "document",
                    "docs",
                    "write",
                    "generate",
                    "create",
                    "documentation",
                ],
                "weight": 0.8,
                "agents": ["documentation_specialist", "code_analysis"],
            },
            "testing_coordination": {
                "patterns": [
                    r"test\s+(.+)",
                    r"run\s+tests\s+for\s+(.+)",
                    r"testing\s+of\s+(.+)",
                    r"quality\s+assurance\s+for\s+(.+)",
                    r"qa\s+for\s+(.+)",
                    r"test\s+coverage\s+for\s+(.+)",
                ],
                "keywords": [
                    "test",
                    "testing",
                    "qa",
                    "quality",
                    "assurance",
                    "coverage",
                ],
                "weight": 0.9,
                "agents": ["testing_coordinator", "code_analysis"],
            },
            "threat_analysis": {
                "patterns": [
                    r"threat\s+analysis\s+of\s+(.+)",
                    r"analyze\s+threats\s+for\s+(.+)",
                    r"threat\s+assessment\s+of\s+(.+)",
                    r"security\s+threats\s+in\s+(.+)",
                    r"risk\s+analysis\s+of\s+(.+)",
                    r"threat\s+landscape\s+for\s+(.+)",
                ],
                "keywords": [
                    "threat",
                    "risk",
                    "danger",
                    "attack",
                    "malware",
                    "vulnerability",
                ],
                "weight": 1.0,
                "agents": ["security_expert", "intelligence_gathering"],
            },
            "incident_response": {
                "patterns": [
                    r"incident\s+response\s+for\s+(.+)",
                    r"respond\s+to\s+(.+)",
                    r"handle\s+incident\s+(.+)",
                    r"emergency\s+response\s+for\s+(.+)",
                    r"fix\s+(.+)",
                    r"resolve\s+(.+)",
                ],
                "keywords": [
                    "incident",
                    "emergency",
                    "respond",
                    "handle",
                    "fix",
                    "resolve",
                ],
                "weight": 1.0,
                "agents": [
                    "security_expert",
                    "intelligence_gathering",
                    "integration_manager",
                ],
            },
            "system_health": {
                "patterns": [
                    r"system\s+health",
                    r"health\s+check",
                    r"system\s+status",
                    r"check\s+system",
                    r"diagnose\s+system",
                    r"system\s+diagnostics",
                ],
                "keywords": ["system", "health", "status", "check", "diagnose"],
                "weight": 0.7,
                "agents": ["performance_monitor", "integration_manager"],
            },
            "backup_restore": {
                "patterns": [
                    r"backup\s+(.+)",
                    r"create\s+backup\s+of\s+(.+)",
                    r"restore\s+(.+)",
                    r"recover\s+(.+)",
                    r"save\s+(.+)",
                ],
                "keywords": ["backup", "restore", "recover", "save", "archive"],
                "weight": 0.8,
                "agents": ["integration_manager"],
            },
        }

        # Initialize keyword weights
        for intent, data in self.intent_patterns.items():
            self.intent_keywords[intent] = data["keywords"]
            self.intent_weights[intent] = data["weight"]

    def _initialize_context_rules(self):
        """Initialize context-based classification rules"""
        self.context_rules = {
            "github_repo": {
                "intent_boost": {
                    "code_analysis": 0.2,
                    "documentation_generation": 0.1,
                    "testing_coordination": 0.1,
                }
            },
            "url_domain": {
                "intent_boost": {"security_scan": 0.3, "intelligence_gathering": 0.2}
            },
            "file_path": {
                "intent_boost": {"code_analysis": 0.3, "documentation_generation": 0.2}
            },
            "urgent_keywords": {
                "intent_boost": {"incident_response": 0.4, "security_scan": 0.2}
            },
        }

    async def classify_intent(
        self,
        command: str,
        nlp_result: Dict[str, Any],
        context_history: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """Classify user intent with advanced reasoning"""
        try:
            self.classification_stats["total_classifications"] += 1

            # Preprocess command
            processed_command = command.lower().strip()

            # Extract entities for context
            entities = nlp_result.get("entities", [])
            entity_types = [e.get("label", "") for e in entities]

            # Get base intent scores
            intent_scores = self._calculate_base_scores(processed_command)

            # Apply context-based boosts
            intent_scores = self._apply_context_boosts(
                intent_scores, entities, context_history
            )

            # Apply pattern matching
            intent_scores = self._apply_pattern_matching(
                intent_scores, processed_command
            )

            # Select best intent
            best_intent = max(intent_scores.items(), key=lambda x: x[1])
            intent_name, confidence = best_intent

            # Generate reasoning
            reasoning = self._generate_reasoning(
                intent_name, confidence, entities, context_history
            )

            # Get suggested agents
            suggested_agents = self.intent_patterns.get(intent_name, {}).get(
                "agents", []
            )

            # Create result
            result = IntentResult(
                intent=intent_name,
                confidence=confidence,
                parameters=self._extract_parameters(processed_command, intent_name),
                reasoning=reasoning,
                suggested_agents=suggested_agents,
                metadata={
                    "all_scores": intent_scores,
                    "entity_types": entity_types,
                    "context_length": len(context_history),
                    "timestamp": datetime.now().isoformat(),
                },
            )

            # Update statistics
            self._update_classification_stats(intent_name, confidence)

            return self._result_to_dict(result)

        except Exception as e:
            self.logger.error(f"Intent classification failed: {e}")
            return {
                "intent": "unknown",
                "confidence": 0.0,
                "parameters": {},
                "reasoning": [f"Classification error: {e}"],
                "suggested_agents": [],
                "metadata": {"error": str(e)},
            }

    def _calculate_base_scores(self, command: str) -> Dict[str, float]:
        """Calculate base intent scores using keyword matching"""
        scores = {}
        words = set(command.split())

        for intent, data in self.intent_patterns.items():
            keywords = data["keywords"]
            weight = data["weight"]

            # Calculate keyword matches
            matches = len(words.intersection(set(keywords)))
            if matches > 0:
                # Base score from keyword matches
                base_score = min(matches * 0.2, 0.8)

                # Apply intent weight
                scores[intent] = base_score * weight
            else:
                scores[intent] = 0.0

        return scores

    def _apply_context_boosts(
        self,
        scores: Dict[str, float],
        entities: List[Dict[str, Any]],
        context_history: List[Dict[str, Any]],
    ) -> Dict[str, float]:
        """Apply context-based boosts to intent scores"""
        boosted_scores = scores.copy()

        # Apply entity-based boosts
        for entity in entities:
            entity_type = entity.get("label", "")
            entity_text = entity.get("text", "").lower()

            # GitHub repository boost
            if "github_repo" in entity_type or "github.com" in entity_text:
                for intent, boost in self.context_rules["github_repo"][
                    "intent_boost"
                ].items():
                    if intent in boosted_scores:
                        boosted_scores[intent] += boost

            # URL domain boost
            elif "url" in entity_type or "domain" in entity_type:
                for intent, boost in self.context_rules["url_domain"][
                    "intent_boost"
                ].items():
                    if intent in boosted_scores:
                        boosted_scores[intent] += boost

            # File path boost
            elif "file_path" in entity_type:
                for intent, boost in self.context_rules["file_path"][
                    "intent_boost"
                ].items():
                    if intent in boosted_scores:
                        boosted_scores[intent] += boost

        # Apply urgent keyword boost
        urgent_keywords = [
            "urgent",
            "emergency",
            "critical",
            "asap",
            "immediately",
            "now",
        ]
        command_words = set(
            " ".join([e.get("text", "") for e in entities]).lower().split()
        )
        if any(keyword in command_words for keyword in urgent_keywords):
            for intent, boost in self.context_rules["urgent_keywords"][
                "intent_boost"
            ].items():
                if intent in boosted_scores:
                    boosted_scores[intent] += boost

        # Apply context history boost
        if context_history:
            recent_intents = [ctx.get("intent", "") for ctx in context_history[-5:]]
            for intent in recent_intents:
                if intent in boosted_scores:
                    boosted_scores[intent] += 0.1  # Small boost for recent intents

        # Cap scores at 1.0
        for intent in boosted_scores:
            boosted_scores[intent] = min(boosted_scores[intent], 1.0)

        return boosted_scores

    def _apply_pattern_matching(
        self, scores: Dict[str, float], command: str
    ) -> Dict[str, float]:
        """Apply pattern matching to refine scores"""
        pattern_scores = scores.copy()

        for intent, data in self.intent_patterns.items():
            patterns = data["patterns"]
            weight = data["weight"]

            for pattern in patterns:
                match = re.search(pattern, command, re.IGNORECASE)
                if match:
                    # Strong boost for pattern match
                    pattern_boost = 0.4 * weight
                    pattern_scores[intent] = min(
                        pattern_scores[intent] + pattern_boost, 1.0
                    )
                    break  # Only apply first matching pattern

        return pattern_scores

    def _generate_reasoning(
        self,
        intent: str,
        confidence: float,
        entities: List[Dict[str, Any]],
        context_history: List[Dict[str, Any]],
    ) -> List[str]:
        """Generate reasoning for intent classification"""
        reasoning = []

        # Base reasoning
        reasoning.append(f"Classified as '{intent}' with {confidence:.1%} confidence")

        # Entity-based reasoning
        if entities:
            entity_types = [e.get("label", "") for e in entities]
            reasoning.append(f"Detected entities: {', '.join(set(entity_types))}")

        # Pattern match reasoning
        if confidence > 0.7:
            reasoning.append("Strong pattern match detected")
        elif confidence > 0.5:
            reasoning.append("Moderate keyword match")
        else:
            reasoning.append("Weak match, using fallback classification")

        # Context reasoning
        if context_history:
            recent_intents = [ctx.get("intent", "") for ctx in context_history[-3:]]
            if intent in recent_intents:
                reasoning.append("Intent matches recent command history")

        # Confidence reasoning
        if confidence > 0.9:
            reasoning.append("Very high confidence classification")
        elif confidence > 0.7:
            reasoning.append("High confidence classification")
        elif confidence > 0.5:
            reasoning.append("Medium confidence classification")
        else:
            reasoning.append("Low confidence classification")

        return reasoning

    def _extract_parameters(self, command: str, intent: str) -> Dict[str, Any]:
        """Extract parameters from command based on intent"""
        parameters = {}

        # Extract target from command
        patterns = self.intent_patterns.get(intent, {}).get("patterns", [])
        for pattern in patterns:
            match = re.search(pattern, command, re.IGNORECASE)
            if match and match.groups():
                parameters["target"] = match.group(1).strip()
                break

        # Extract additional parameters based on intent
        if intent == "security_scan":
            if "deep" in command:
                parameters["scan_type"] = "deep"
            if "quick" in command:
                parameters["scan_type"] = "quick"
            if "vulnerabilities" in command:
                parameters["focus"] = "vulnerabilities"

        elif intent == "code_analysis":
            if "security" in command:
                parameters["focus"] = "security"
            if "performance" in command:
                parameters["focus"] = "performance"
            if "quality" in command:
                parameters["focus"] = "quality"

        elif intent == "intelligence_gathering":
            if "osint" in command:
                parameters["method"] = "osint"
            if "social" in command:
                parameters["method"] = "social_media"

        return parameters

    def _update_classification_stats(self, intent: str, confidence: float):
        """Update classification statistics"""
        # Update intent distribution
        if intent not in self.classification_stats["intent_distribution"]:
            self.classification_stats["intent_distribution"][intent] = 0
        self.classification_stats["intent_distribution"][intent] += 1

        # Update average confidence
        total = self.classification_stats["total_classifications"]
        current_avg = self.classification_stats["average_confidence"]
        self.classification_stats["average_confidence"] = (
            current_avg * (total - 1) + confidence
        ) / total

    def _result_to_dict(self, result: IntentResult) -> Dict[str, Any]:
        """Convert IntentResult to dictionary"""
        return {
            "intent": result.intent,
            "confidence": result.confidence,
            "parameters": result.parameters,
            "reasoning": result.reasoning,
            "suggested_agents": result.suggested_agents,
            "metadata": result.metadata,
        }

    def get_classification_stats(self) -> Dict[str, Any]:
        """Get classification statistics"""
        return self.classification_stats.copy()

    def display_classification_analysis(self, result: Dict[str, Any]):
        """Display detailed classification analysis"""
        # Main result table
        table = Table(title="🎯 Intent Classification Analysis")
        table.add_column("Property", style="cyan", width=20)
        table.add_column("Value", style="green")

        table.add_row("Intent", result["intent"].replace("_", " ").title())
        table.add_row("Confidence", f"{result['confidence']:.1%}")
        table.add_row("Suggested Agents", ", ".join(result["suggested_agents"]))

        # Parameters
        if result["parameters"]:
            table.add_row("Parameters", str(result["parameters"]))

        self.console.print(table)

        # Reasoning panel
        if result["reasoning"]:
            reasoning_panel = Panel(
                "\n".join(f"• {reason}" for reason in result["reasoning"]),
                title="🧠 Classification Reasoning",
                border_style="blue",
            )
            self.console.print(reasoning_panel)

        # All scores panel
        if "all_scores" in result.get("metadata", {}):
            scores = result["metadata"]["all_scores"]
            scores_table = Table(title="📊 All Intent Scores")
            scores_table.add_column("Intent", style="cyan")
            scores_table.add_column("Score", style="green")

            for intent, score in sorted(
                scores.items(), key=lambda x: x[1], reverse=True
            ):
                scores_table.add_row(intent.replace("_", " ").title(), f"{score:.3f}")

            self.console.print(scores_table)
