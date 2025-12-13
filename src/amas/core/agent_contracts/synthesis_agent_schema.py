"""
Synthesis Agent Contract for AMAS

Defines the specific contract for synthesis agents including
input/output schemas and tool permissions.
"""

from typing import Dict, List, Any, Optional
from pydantic import Field
from .base_agent_contract import AgentContract, AgentRole, ToolCapability

class SynthesisAgentContract(AgentContract):
    """Contract for synthesis agents specializing in content synthesis and document generation"""
    
    # Override defaults for synthesis agents
    role: AgentRole = AgentRole.SYNTHESIS
    max_iterations: int = Field(default=3, ge=1, le=10)
    timeout_seconds: int = Field(default=300, ge=60, le=1800)  # 5 minutes max
    cost_budget_tokens: int = Field(default=10000, ge=1000, le=50000)
    
    # Synthesis-specific tools
    allowed_tools: List[ToolCapability] = Field(
        default=[
            ToolCapability.FILE_READ,
            ToolCapability.FILE_WRITE,
            ToolCapability.DOCUMENT_GENERATION,
            ToolCapability.VECTOR_SEARCH
        ]
    )
    
    # Synthesis-specific settings
    plagiarism_check_enabled: bool = Field(default=True)
    require_citations: bool = Field(default=True)
    output_format_preference: str = Field(default="structured", pattern="^(structured|narrative|mixed)$")
    template_rendering_enabled: bool = Field(default=True)
    
    def get_input_schema(self) -> Dict[str, Any]:
        """JSON schema for synthesis agent inputs"""
        return {
            "type": "object",
            "properties": {
                "content_sources": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "source_type": {
                                "type": "string",
                                "enum": ["file", "database", "api", "vector_search"]
                            },
                            "source_path": {"type": "string"},
                            "relevance_weight": {
                                "type": "number",
                                "minimum": 0.0,
                                "maximum": 1.0,
                                "default": 1.0
                            }
                        },
                        "required": ["source_type", "source_path"]
                    },
                    "minItems": 1,
                    "maxItems": 20,
                    "description": "Sources to synthesize content from"
                },
                "synthesis_objective": {
                    "type": "string",
                    "description": "Objective or goal for the synthesis",
                    "minLength": 10,
                    "maxLength": 500
                },
                "output_type": {
                    "type": "string",
                    "enum": ["report", "summary", "article", "presentation", "documentation"],
                    "default": "report",
                    "description": "Type of output to generate"
                },
                "target_audience": {
                    "type": "string",
                    "enum": ["technical", "business", "general", "academic"],
                    "default": "general",
                    "description": "Target audience for the synthesized content"
                },
                "length_preference": {
                    "type": "string",
                    "enum": ["brief", "medium", "comprehensive"],
                    "default": "medium",
                    "description": "Desired length of output"
                },
                "citation_style": {
                    "type": "string",
                    "enum": ["apa", "mla", "chicago", "ieee", "none"],
                    "default": "apa",
                    "description": "Citation style for references"
                },
                "template_name": {
                    "type": "string",
                    "description": "Template to use for rendering (if template_rendering enabled)",
                    "maxLength": 100
                },
                "quality_requirements": {
                    "type": "object",
                    "properties": {
                        "require_plagiarism_check": {"type": "boolean", "default": True},
                        "require_fact_checking": {"type": "boolean", "default": False},
                        "require_grammar_check": {"type": "boolean", "default": True},
                        "min_confidence_score": {"type": "number", "minimum": 0.0, "maximum": 1.0}
                    }
                }
            },
            "required": ["content_sources", "synthesis_objective"],
            "additionalProperties": False
        }
    
    def get_output_schema(self) -> Dict[str, Any]:
        """JSON schema for synthesis agent outputs"""
        return {
            "type": "object",
            "properties": {
                "synthesized_content": {
                    "type": "string",
                    "description": "The synthesized content/document",
                    "minLength": 100
                },
                "content_structure": {
                    "type": "object",
                    "properties": {
                        "sections": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "title": {"type": "string"},
                                    "content": {"type": "string"},
                                    "order": {"type": "integer"}
                                },
                                "required": ["title", "content", "order"]
                            }
                        },
                        "word_count": {"type": "integer", "minimum": 0},
                        "section_count": {"type": "integer", "minimum": 0}
                    },
                    "description": "Structure of the synthesized content"
                },
                "sources_used": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "source_id": {"type": "string"},
                            "source_path": {"type": "string"},
                            "contribution_percentage": {
                                "type": "number",
                                "minimum": 0.0,
                                "maximum": 100.0
                            },
                            "key_excerpts": {
                                "type": "array",
                                "items": {"type": "string"}
                            }
                        },
                        "required": ["source_id", "source_path"]
                    },
                    "minItems": 1,
                    "description": "Sources used in synthesis"
                },
                "citations": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "citation_id": {"type": "string"},
                            "source": {"type": "string"},
                            "citation_text": {"type": "string"},
                            "location_in_content": {"type": "string"}
                        },
                        "required": ["citation_id", "source", "citation_text"]
                    },
                    "description": "Citations and references"
                },
                "quality_metrics": {
                    "type": "object",
                    "properties": {
                        "plagiarism_score": {
                            "type": "number",
                            "minimum": 0.0,
                            "maximum": 1.0,
                            "description": "Lower is better (0 = original, 1 = fully plagiarized)"
                        },
                        "originality_score": {
                            "type": "number",
                            "minimum": 0.0,
                            "maximum": 1.0,
                            "description": "Higher is better"
                        },
                        "coherence_score": {
                            "type": "number",
                            "minimum": 0.0,
                            "maximum": 1.0
                        },
                        "completeness_score": {
                            "type": "number",
                            "minimum": 0.0,
                            "maximum": 1.0
                        },
                        "grammar_score": {
                            "type": "number",
                            "minimum": 0.0,
                            "maximum": 1.0
                        }
                    },
                    "required": ["plagiarism_score", "originality_score"],
                    "description": "Quality assessment metrics"
                },
                "metadata": {
                    "type": "object",
                    "properties": {
                        "generated_at": {"type": "string", "format": "date-time"},
                        "template_used": {"type": "string"},
                        "rendering_engine": {"type": "string"},
                        "processing_time_seconds": {"type": "number"}
                    },
                    "description": "Metadata about generation process"
                },
                "execution_metrics": {
                    "type": "object",
                    "properties": {
                        "sources_processed": {"type": "integer", "minimum": 0},
                        "tokens_consumed": {"type": "integer", "minimum": 0},
                        "processing_time_seconds": {"type": "number", "minimum": 0},
                        "iterations_used": {"type": "integer", "minimum": 0}
                    },
                    "description": "Execution performance metrics"
                }
            },
            "required": [
                "synthesized_content",
                "content_structure",
                "sources_used",
                "quality_metrics",
                "execution_metrics"
            ],
            "additionalProperties": False
        }

# Pre-configured synthesis agent instances
CONTENT_SYNTHESIS_AGENT = SynthesisAgentContract(
    agent_id="content_synthesis_v1",
    agent_version="1.0.0",
    plagiarism_check_enabled=True,
    require_citations=True,
    template_rendering_enabled=True,
    created_by="system"
)

DOCUMENT_GENERATION_AGENT = SynthesisAgentContract(
    agent_id="document_generation_v1",
    agent_version="1.0.0",
    plagiarism_check_enabled=True,
    require_citations=False,  # Documents may not need citations
    template_rendering_enabled=True,
    output_format_preference="structured",
    timeout_seconds=600,  # 10 minutes for complex documents
    cost_budget_tokens=20000,
    created_by="system"
)
