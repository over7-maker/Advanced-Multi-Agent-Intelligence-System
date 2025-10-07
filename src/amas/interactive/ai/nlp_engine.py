"""
AMAS Natural Language Processing Engine
Advanced Multi-Agent Intelligence System - Interactive Mode

This module provides advanced natural language processing capabilities
for interpreting user commands and extracting meaningful information
for agent coordination and task execution.
"""

import asyncio
import json
import logging
import re
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple, Union

# NLP libraries
try:
    import spacy
    from spacy import displacy

    SPACY_AVAILABLE = True
except ImportError:
    SPACY_AVAILABLE = False

try:
    import nltk
    from nltk.chunk import ne_chunk
    from nltk.corpus import stopwords
    from nltk.tag import pos_tag
    from nltk.tokenize import sent_tokenize, word_tokenize

    NLTK_AVAILABLE = True
except ImportError:
    NLTK_AVAILABLE = False

# Rich for enhanced output
from rich.console import Console
from rich.panel import Panel
from rich.table import Table


@dataclass
class Entity:
    """Named entity data structure"""

    text: str
    label: str
    start: int
    end: int
    confidence: float = 1.0
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


@dataclass
class Intent:
    """Intent data structure"""

    name: str
    confidence: float
    parameters: Dict[str, Any] = None
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.parameters is None:
            self.parameters = {}
        if self.metadata is None:
            self.metadata = {}


@dataclass
class CommandAnalysis:
    """Command analysis result"""

    original_command: str
    processed_text: str
    entities: List[Entity]
    intent: Intent
    sentiment: str
    confidence: float
    suggestions: List[str] = None
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.suggestions is None:
            self.suggestions = []
        if self.metadata is None:
            self.metadata = {}


class NLPEngine:
    """Advanced Natural Language Processing Engine"""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.console = Console()
        self.logger = logging.getLogger(__name__)

        # Initialize NLP models
        self.nlp_model = None
        self.stop_words = set()
        self.intent_patterns = {}
        self.entity_patterns = {}

        # Performance tracking
        self.processing_stats = {
            "commands_processed": 0,
            "average_processing_time": 0.0,
            "intent_accuracy": 0.0,
            "entity_extraction_accuracy": 0.0,
        }

        # Initialize components
        self._initialize_nlp_models()
        self._load_intent_patterns()
        self._load_entity_patterns()

    def _initialize_nlp_models(self):
        """Initialize NLP models and resources"""
        try:
            # Initialize spaCy model
            if SPACY_AVAILABLE:
                try:
                    self.nlp_model = spacy.load("en_core_web_sm")
                    self.logger.info("Loaded spaCy English model")
                except OSError:
                    self.logger.warning(
                        "spaCy English model not found, using basic processing"
                    )
                    self.nlp_model = None

            # Initialize NLTK resources
            if NLTK_AVAILABLE:
                try:
                    nltk.download("punkt", quiet=True)
                    nltk.download("stopwords", quiet=True)
                    nltk.download("averaged_perceptron_tagger", quiet=True)
                    nltk.download("maxent_ne_chunker", quiet=True)
                    nltk.download("words", quiet=True)

                    self.stop_words = set(stopwords.words("english"))
                    self.logger.info("Loaded NLTK resources")
                except Exception as e:
                    self.logger.warning(f"Failed to load NLTK resources: {e}")

        except Exception as e:
            self.logger.error(f"Failed to initialize NLP models: {e}")

    def _load_intent_patterns(self):
        """Load intent recognition patterns"""
        self.intent_patterns = {
            "security_scan": [
                r"scan\s+(.+)",
                r"check\s+security\s+of\s+(.+)",
                r"analyze\s+security\s+of\s+(.+)",
                r"audit\s+(.+)",
                r"vulnerability\s+scan\s+(.+)",
                r"security\s+analysis\s+of\s+(.+)",
            ],
            "code_analysis": [
                r"analyze\s+code\s+(.+)",
                r"review\s+code\s+(.+)",
                r"check\s+code\s+quality\s+of\s+(.+)",
                r"code\s+analysis\s+of\s+(.+)",
                r"review\s+(.+)",
                r"analyze\s+(.+)",
            ],
            "intelligence_gathering": [
                r"research\s+(.+)",
                r"investigate\s+(.+)",
                r"gather\s+intelligence\s+on\s+(.+)",
                r"osint\s+(.+)",
                r"intelligence\s+on\s+(.+)",
                r"investigation\s+of\s+(.+)",
            ],
            "performance_monitoring": [
                r"monitor\s+(.+)",
                r"check\s+performance\s+of\s+(.+)",
                r"analyze\s+performance\s+of\s+(.+)",
                r"performance\s+analysis\s+of\s+(.+)",
                r"optimize\s+(.+)",
            ],
            "documentation_generation": [
                r"document\s+(.+)",
                r"generate\s+documentation\s+for\s+(.+)",
                r"create\s+docs\s+for\s+(.+)",
                r"write\s+documentation\s+for\s+(.+)",
            ],
            "testing_coordination": [
                r"test\s+(.+)",
                r"run\s+tests\s+for\s+(.+)",
                r"testing\s+of\s+(.+)",
                r"quality\s+assurance\s+for\s+(.+)",
            ],
            "threat_analysis": [
                r"threat\s+analysis\s+of\s+(.+)",
                r"analyze\s+threats\s+for\s+(.+)",
                r"threat\s+assessment\s+of\s+(.+)",
                r"security\s+threats\s+in\s+(.+)",
            ],
            "incident_response": [
                r"incident\s+response\s+for\s+(.+)",
                r"respond\s+to\s+(.+)",
                r"handle\s+incident\s+(.+)",
                r"emergency\s+response\s+for\s+(.+)",
            ],
        }

    def _load_entity_patterns(self):
        """Load entity extraction patterns"""
        self.entity_patterns = {
            "url": r"https?://[^\s]+|www\.[^\s]+|[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}",
            "github_repo": r"github\.com/[a-zA-Z0-9_.-]+/[a-zA-Z0-9_.-]+",
            "ip_address": r"\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b",
            "email": r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",
            "file_path": r"(?:/[^/\s]+)+|(?:[A-Za-z]:[\\/][^\\/\s]+)+",
            "domain": r"[a-zA-Z0-9]([a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(\.[a-zA-Z0-9]([a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*",
            "version": r"v?\d+\.\d+(?:\.\d+)?(?:-[a-zA-Z0-9]+)?",
            "port": r":\d{1,5}\b",
        }

    async def process_command(self, command: str) -> Dict[str, Any]:
        """Process user command with advanced NLP"""
        start_time = datetime.now()

        try:
            self.processing_stats["commands_processed"] += 1

            # Clean and preprocess command
            processed_text = self._preprocess_text(command)

            # Extract entities
            entities = await self._extract_entities(processed_text)

            # Determine intent
            intent = await self._classify_intent(processed_text, entities)

            # Analyze sentiment
            sentiment = self._analyze_sentiment(processed_text)

            # Extract target
            target = self._extract_target(processed_text, entities)

            # Generate suggestions
            suggestions = self._generate_suggestions(processed_text, intent, entities)

            # Create analysis result
            analysis = CommandAnalysis(
                original_command=command,
                processed_text=processed_text,
                entities=entities,
                intent=intent,
                sentiment=sentiment,
                confidence=intent.confidence,
                suggestions=suggestions,
                metadata={
                    "processing_time": (datetime.now() - start_time).total_seconds(),
                    "timestamp": datetime.now().isoformat(),
                },
            )

            # Update performance stats
            processing_time = (datetime.now() - start_time).total_seconds()
            self._update_performance_stats(processing_time)

            # Convert to dictionary for return
            return self._analysis_to_dict(analysis)

        except Exception as e:
            self.logger.error(f"Command processing failed: {e}")
            return {
                "original_command": command,
                "processed_text": command.lower().strip(),
                "entities": [],
                "intent": {"name": "unknown", "confidence": 0.0},
                "sentiment": "neutral",
                "target": "general",
                "confidence": 0.0,
                "suggestions": [],
                "error": str(e),
            }

    def _preprocess_text(self, text: str) -> str:
        """Preprocess text for analysis"""
        # Convert to lowercase
        text = text.lower().strip()

        # Remove extra whitespace
        text = re.sub(r"\s+", " ", text)

        # Remove special characters but keep important ones
        text = re.sub(r"[^\w\s@.:/]", "", text)

        return text

    async def _extract_entities(self, text: str) -> List[Entity]:
        """Extract named entities from text"""
        entities = []

        try:
            # Extract using regex patterns
            for entity_type, pattern in self.entity_patterns.items():
                matches = re.finditer(pattern, text, re.IGNORECASE)
                for match in matches:
                    entity = Entity(
                        text=match.group(),
                        label=entity_type,
                        start=match.start(),
                        end=match.end(),
                        confidence=0.9,
                        metadata={"pattern": pattern},
                    )
                    entities.append(entity)

            # Extract using spaCy if available
            if self.nlp_model:
                doc = self.nlp_model(text)
                for ent in doc.ents:
                    # Check if not already extracted by regex
                    if not any(
                        e.text == ent.text and e.start == ent.start_char
                        for e in entities
                    ):
                        entity = Entity(
                            text=ent.text,
                            label=ent.label_,
                            start=ent.start_char,
                            end=ent.end_char,
                            confidence=0.8,
                            metadata={"spacy_label": ent.label_},
                        )
                        entities.append(entity)

            # Extract using NLTK if available
            if NLTK_AVAILABLE:
                tokens = word_tokenize(text)
                pos_tags = pos_tag(tokens)
                chunks = ne_chunk(pos_tags)

                for chunk in chunks:
                    if hasattr(chunk, "label"):
                        entity_text = " ".join([token for token, pos in chunk.leaves()])
                        entity = Entity(
                            text=entity_text,
                            label=chunk.label(),
                            start=text.find(entity_text),
                            end=text.find(entity_text) + len(entity_text),
                            confidence=0.7,
                            metadata={"nltk_label": chunk.label()},
                        )
                        entities.append(entity)

        except Exception as e:
            self.logger.error(f"Entity extraction failed: {e}")

        return entities

    async def _classify_intent(self, text: str, entities: List[Entity]) -> Intent:
        """Classify user intent"""
        best_intent = Intent(name="unknown", confidence=0.0)

        try:
            # Pattern-based intent classification
            for intent_name, patterns in self.intent_patterns.items():
                for pattern in patterns:
                    match = re.search(pattern, text, re.IGNORECASE)
                    if match:
                        confidence = 0.9

                        # Boost confidence based on entity presence
                        if entities:
                            confidence += 0.1

                        # Boost confidence for exact matches
                        if match.group(0).lower() == text.lower():
                            confidence += 0.1

                        if confidence > best_intent.confidence:
                            best_intent = Intent(
                                name=intent_name,
                                confidence=min(confidence, 1.0),
                                parameters={
                                    "match": match.group(1) if match.groups() else ""
                                },
                                metadata={"pattern": pattern},
                            )

            # Fallback to keyword-based classification
            if best_intent.confidence < 0.5:
                best_intent = self._keyword_based_intent_classification(text, entities)

        except Exception as e:
            self.logger.error(f"Intent classification failed: {e}")

        return best_intent

    def _keyword_based_intent_classification(
        self, text: str, entities: List[Entity]
    ) -> Intent:
        """Fallback keyword-based intent classification"""
        keywords = {
            "security_scan": ["scan", "security", "vulnerability", "audit", "check"],
            "code_analysis": ["code", "analyze", "review", "quality", "function"],
            "intelligence_gathering": [
                "research",
                "investigate",
                "intelligence",
                "osint",
                "gather",
            ],
            "performance_monitoring": [
                "monitor",
                "performance",
                "optimize",
                "speed",
                "memory",
            ],
            "documentation_generation": [
                "document",
                "docs",
                "write",
                "generate",
                "create",
            ],
            "testing_coordination": ["test", "testing", "qa", "quality", "assurance"],
            "threat_analysis": ["threat", "risk", "danger", "attack", "malware"],
            "incident_response": ["incident", "emergency", "respond", "handle", "fix"],
        }

        best_intent = Intent(name="general_analysis", confidence=0.3)
        text_words = set(text.split())

        for intent_name, intent_keywords in keywords.items():
            matches = len(text_words.intersection(set(intent_keywords)))
            if matches > 0:
                confidence = min(0.3 + (matches * 0.2), 0.8)
                if confidence > best_intent.confidence:
                    best_intent = Intent(
                        name=intent_name,
                        confidence=confidence,
                        parameters={
                            "matched_keywords": list(
                                text_words.intersection(set(intent_keywords))
                            )
                        },
                    )

        return best_intent

    def _analyze_sentiment(self, text: str) -> str:
        """Analyze sentiment of the text"""
        positive_words = [
            "good",
            "great",
            "excellent",
            "amazing",
            "perfect",
            "awesome",
            "fantastic",
        ]
        negative_words = [
            "bad",
            "terrible",
            "awful",
            "horrible",
            "disgusting",
            "hate",
            "worst",
        ]
        urgent_words = ["urgent", "emergency", "critical", "asap", "immediately", "now"]

        text_lower = text.lower()

        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)
        urgent_count = sum(1 for word in urgent_words if word in text_lower)

        if urgent_count > 0:
            return "urgent"
        elif positive_count > negative_count:
            return "positive"
        elif negative_count > positive_count:
            return "negative"
        else:
            return "neutral"

    def _extract_target(self, text: str, entities: List[Entity]) -> str:
        """Extract target from text and entities"""
        # Look for URL entities first
        for entity in entities:
            if entity.label in ["url", "github_repo", "domain"]:
                return entity.text

        # Look for file path entities
        for entity in entities:
            if entity.label == "file_path":
                return entity.text

        # Look for quoted strings
        quoted_match = re.search(r'"([^"]+)"', text)
        if quoted_match:
            return quoted_match.group(1)

        # Look for words after common prepositions
        prepositions = ["of", "for", "in", "on", "at", "to", "from"]
        for prep in prepositions:
            pattern = rf"{prep}\s+([a-zA-Z0-9.-]+)"
            match = re.search(pattern, text)
            if match:
                return match.group(1)

        # Fallback: return second word if available
        words = text.split()
        if len(words) > 1:
            return words[1]

        return "general"

    def _generate_suggestions(
        self, text: str, intent: Intent, entities: List[Entity]
    ) -> List[str]:
        """Generate command suggestions based on analysis"""
        suggestions = []

        # Suggest based on intent
        if intent.name == "security_scan":
            suggestions.extend(
                [
                    "Add '--deep' for comprehensive scan",
                    "Use '--format json' for structured output",
                    "Try '--vulnerabilities-only' for focused results",
                ]
            )
        elif intent.name == "code_analysis":
            suggestions.extend(
                [
                    "Add '--metrics' for detailed metrics",
                    "Use '--coverage' for test coverage analysis",
                    "Try '--security' for security-focused analysis",
                ]
            )
        elif intent.name == "intelligence_gathering":
            suggestions.extend(
                [
                    "Add '--sources all' for comprehensive research",
                    "Use '--timeframe 30d' for recent data",
                    "Try '--format report' for detailed report",
                ]
            )

        # Suggest based on entities
        if any(e.label == "url" for e in entities):
            suggestions.append("Consider adding '--timeout 60' for large sites")

        if any(e.label == "github_repo" for e in entities):
            suggestions.append("Use '--include-issues' for issue analysis")

        return suggestions[:3]  # Limit to 3 suggestions

    def _update_performance_stats(self, processing_time: float):
        """Update performance statistics"""
        total_time = (
            self.processing_stats["average_processing_time"]
            * self.processing_stats["commands_processed"]
        )
        total_time += processing_time
        self.processing_stats["average_processing_time"] = (
            total_time / self.processing_stats["commands_processed"]
        )

    def _analysis_to_dict(self, analysis: CommandAnalysis) -> Dict[str, Any]:
        """Convert analysis result to dictionary"""
        return {
            "original_command": analysis.original_command,
            "processed_text": analysis.processed_text,
            "entities": [
                {
                    "text": entity.text,
                    "label": entity.label,
                    "start": entity.start,
                    "end": entity.end,
                    "confidence": entity.confidence,
                    "metadata": entity.metadata,
                }
                for entity in analysis.entities
            ],
            "intent": {
                "name": analysis.intent.name,
                "confidence": analysis.intent.confidence,
                "parameters": analysis.intent.parameters,
                "metadata": analysis.intent.metadata,
            },
            "sentiment": analysis.sentiment,
            "target": self._extract_target(analysis.processed_text, analysis.entities),
            "confidence": analysis.confidence,
            "suggestions": analysis.suggestions,
            "metadata": analysis.metadata,
        }

    def get_processing_stats(self) -> Dict[str, Any]:
        """Get processing statistics"""
        return self.processing_stats.copy()

    def display_analysis(self, analysis: Dict[str, Any]):
        """Display analysis results in a formatted way"""
        # Create analysis table
        table = Table(title="🧠 NLP Analysis Results")
        table.add_column("Component", style="cyan", width=20)
        table.add_column("Value", style="green")

        table.add_row("Original Command", analysis["original_command"])
        table.add_row("Processed Text", analysis["processed_text"])
        table.add_row(
            "Intent",
            f"{analysis['intent']['name']} ({analysis['intent']['confidence']:.1%})",
        )
        table.add_row("Target", analysis["target"])
        table.add_row("Sentiment", analysis["sentiment"])
        table.add_row("Confidence", f"{analysis['confidence']:.1%}")

        self.console.print(table)

        # Display entities
        if analysis["entities"]:
            entity_table = Table(title="🏷️ Extracted Entities")
            entity_table.add_column("Text", style="cyan")
            entity_table.add_column("Label", style="green")
            entity_table.add_column("Confidence", style="yellow")

            for entity in analysis["entities"]:
                entity_table.add_row(
                    entity["text"], entity["label"], f"{entity['confidence']:.1%}"
                )

            self.console.print(entity_table)

        # Display suggestions
        if analysis["suggestions"]:
            suggestions_panel = Panel(
                "\n".join(f"• {suggestion}" for suggestion in analysis["suggestions"]),
                title="💡 Suggestions",
                border_style="blue",
            )
            self.console.print(suggestions_panel)
