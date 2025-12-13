"""
Research Agent Contract for AMAS

Defines the specific contract for research agents including
input/output schemas and tool permissions.
"""

from typing import Dict, List, Any, Optional
from pydantic import Field
from .base_agent_contract import AgentContract, AgentRole, ToolCapability

class ResearchAgentContract(AgentContract):
    """Contract for research agents specializing in information gathering"""
    
    # Override defaults for research agents
    role: AgentRole = AgentRole.RESEARCH
    max_iterations: int = Field(default=8, ge=1, le=50)
    timeout_seconds: int = Field(default=600, ge=60, le=1800)  # 10 minutes max
    cost_budget_tokens: int = Field(default=20000, ge=1000, le=100000)
    
    # Research-specific tools
    allowed_tools: List[ToolCapability] = Field(
        default=[
            ToolCapability.WEB_SEARCH,
            ToolCapability.API_CALL,
            ToolCapability.FILE_READ,
            ToolCapability.VECTOR_SEARCH,
            ToolCapability.DOCUMENT_GENERATION
        ]
    )
    
    # Research-specific settings
    max_search_results: int = Field(default=20, ge=5, le=100)
    search_depth: str = Field(default="comprehensive", pattern="^(basic|standard|comprehensive|deep)$")
    fact_checking_enabled: bool = Field(default=True)
    source_diversity_required: bool = Field(default=True)
    
    def get_input_schema(self) -> Dict[str, Any]:
        """JSON schema for research agent inputs"""
        return {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Research query or question",
                    "minLength": 10,
                    "maxLength": 1000
                },
                "research_scope": {
                    "type": "string",
                    "enum": ["focused", "broad", "comprehensive"],
                    "default": "broad",
                    "description": "Scope of research to conduct"
                },
                "domain_filters": {
                    "type": "array",
                    "items": {
                        "type": "string",
                        "enum": ["academic", "news", "industry", "government", "social"]
                    },
                    "maxItems": 5,
                    "description": "Domain filters for research sources"
                },
                "time_range": {
                    "type": "object",
                    "properties": {
                        "start_date": {"type": "string", "format": "date"},
                        "end_date": {"type": "string", "format": "date"}
                    },
                    "description": "Time range for research (optional)"
                },
                "output_format": {
                    "type": "string",
                    "enum": ["summary", "detailed", "structured", "citations_only"],
                    "default": "detailed",
                    "description": "Desired output format"
                },
                "max_sources": {
                    "type": "integer",
                    "minimum": 3,
                    "maximum": 50,
                    "default": 15,
                    "description": "Maximum number of sources to research"
                },
                "language": {
                    "type": "string",
                    "default": "en",
                    "pattern": "^[a-z]{2}$",
                    "description": "Language code for research (ISO 639-1)"
                }
            },
            "required": ["query"],
            "additionalProperties": False
        }
    
    def get_output_schema(self) -> Dict[str, Any]:
        """JSON schema for research agent outputs"""
        return {
            "type": "object",
            "properties": {
                "research_summary": {
                    "type": "string",
                    "description": "Executive summary of research findings",
                    "minLength": 100,
                    "maxLength": 5000
                },
                "key_findings": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "finding": {"type": "string", "minLength": 20},
                            "confidence_level": {
                                "type": "string",
                                "enum": ["low", "medium", "high", "very_high"]
                            },
                            "supporting_sources": {
                                "type": "array",
                                "items": {"type": "string"},
                                "minItems": 1
                            }
                        },
                        "required": ["finding", "confidence_level", "supporting_sources"]
                    },
                    "minItems": 1,
                    "maxItems": 20,
                    "description": "Key research findings with confidence levels"
                },
                "sources": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "url": {"type": "string", "format": "uri"},
                            "title": {"type": "string", "minLength": 1},
                            "author": {"type": "string"},
                            "publication_date": {"type": "string", "format": "date"},
                            "domain": {
                                "type": "string",
                                "enum": ["academic", "news", "industry", "government", "social", "other"]
                            },
                            "credibility_score": {
                                "type": "number",
                                "minimum": 0.0,
                                "maximum": 1.0
                            },
                            "relevance_score": {
                                "type": "number",
                                "minimum": 0.0,
                                "maximum": 1.0
                            },
                            "excerpt": {"type": "string", "maxLength": 500}
                        },
                        "required": ["url", "title", "domain", "credibility_score", "relevance_score"]
                    },
                    "minItems": 3,
                    "description": "Source citations with credibility assessment"
                },
                "research_methodology": {
                    "type": "object",
                    "properties": {
                        "search_terms_used": {
                            "type": "array",
                            "items": {"type": "string"}
                        },
                        "databases_searched": {
                            "type": "array",
                            "items": {"type": "string"}
                        },
                        "total_sources_reviewed": {"type": "integer", "minimum": 0},
                        "filtering_criteria": {"type": "string"},
                        "limitations": {"type": "string"}
                    },
                    "description": "Methodology used for research"
                },
                "confidence_assessment": {
                    "type": "object",
                    "properties": {
                        "overall_confidence": {
                            "type": "string",
                            "enum": ["low", "medium", "high", "very_high"]
                        },
                        "data_completeness": {
                            "type": "number",
                            "minimum": 0.0,
                            "maximum": 1.0
                        },
                        "source_diversity": {
                            "type": "number",
                            "minimum": 0.0,
                            "maximum": 1.0
                        },
                        "temporal_coverage": {
                            "type": "number",
                            "minimum": 0.0,
                            "maximum": 1.0
                        },
                        "potential_biases": {
                            "type": "array",
                            "items": {"type": "string"}
                        }
                    },
                    "required": ["overall_confidence", "data_completeness", "source_diversity"],
                    "description": "Assessment of research confidence and limitations"
                },
                "execution_metrics": {
                    "type": "object",
                    "properties": {
                        "search_queries_executed": {"type": "integer", "minimum": 0},
                        "api_calls_made": {"type": "integer", "minimum": 0},
                        "tokens_consumed": {"type": "integer", "minimum": 0},
                        "processing_time_seconds": {"type": "number", "minimum": 0},
                        "cache_hit_rate": {
                            "type": "number",
                            "minimum": 0.0,
                            "maximum": 1.0
                        }
                    },
                    "description": "Execution performance metrics"
                }
            },
            "required": [
                "research_summary",
                "key_findings",
                "sources",
                "confidence_assessment",
                "execution_metrics"
            ],
            "additionalProperties": False
        }

# Pre-configured research agent instances
WEB_RESEARCH_AGENT = ResearchAgentContract(
    agent_id="web_research_v1",
    agent_version="1.0.0",
    max_search_results=25,
    search_depth="comprehensive",
    fact_checking_enabled=True,
    source_diversity_required=True,
    created_by="system"
)

ACADEMIC_RESEARCH_AGENT = ResearchAgentContract(
    agent_id="academic_research_v1",
    agent_version="1.0.0",
    max_search_results=15,
    search_depth="deep",
    fact_checking_enabled=True,
    source_diversity_required=True,
    timeout_seconds=1200,  # 20 minutes for thorough academic research
    cost_budget_tokens=50000,
    created_by="system"
)

NEWS_RESEARCH_AGENT = ResearchAgentContract(
    agent_id="news_research_v1",
    agent_version="1.0.0",
    max_search_results=30,
    search_depth="standard",
    fact_checking_enabled=True,
    source_diversity_required=True,
    timeout_seconds=300,  # 5 minutes for timely news research
    cost_budget_tokens=15000,
    created_by="system"
)
