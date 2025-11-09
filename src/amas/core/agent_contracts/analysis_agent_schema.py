"""
Analysis Agent Contract for AMAS

Defines the specific contract for analysis agents including
input/output schemas and tool permissions.
"""

from typing import Dict, List, Any, Optional
from pydantic import Field
from .base_agent_contract import AgentContract, AgentRole, ToolCapability

class AnalysisAgentContract(AgentContract):
    """Contract for analysis agents specializing in data analysis and statistical processing"""
    
    # Override defaults for analysis agents
    role: AgentRole = AgentRole.ANALYSIS
    max_iterations: int = Field(default=5, ge=1, le=20)
    timeout_seconds: int = Field(default=900, ge=60, le=3600)  # 15 minutes max
    cost_budget_tokens: int = Field(default=15000, ge=1000, le=100000)
    
    # Analysis-specific tools
    allowed_tools: List[ToolCapability] = Field(
        default=[
            ToolCapability.FILE_READ,
            ToolCapability.DATABASE_QUERY,
            ToolCapability.DATA_ANALYSIS,
            ToolCapability.DOCUMENT_GENERATION
        ]
    )
    
    # Analysis-specific settings
    statistical_validation_required: bool = Field(default=True)
    data_quality_threshold: float = Field(default=0.8, ge=0.0, le=1.0)
    require_statistical_significance: bool = Field(default=True)
    
    def get_input_schema(self) -> Dict[str, Any]:
        """JSON schema for analysis agent inputs"""
        return {
            "type": "object",
            "properties": {
                "data_source": {
                    "type": "string",
                    "description": "Source of data to analyze (file path, database table, or API endpoint)",
                    "minLength": 1,
                    "maxLength": 500
                },
                "analysis_type": {
                    "type": "string",
                    "enum": ["descriptive", "inferential", "predictive", "exploratory", "diagnostic"],
                    "default": "descriptive",
                    "description": "Type of analysis to perform"
                },
                "variables": {
                    "type": "array",
                    "items": {
                        "type": "string"
                    },
                    "minItems": 1,
                    "maxItems": 50,
                    "description": "Variables to include in analysis"
                },
                "statistical_tests": {
                    "type": "array",
                    "items": {
                        "type": "string",
                        "enum": ["t-test", "chi-square", "anova", "correlation", "regression", "clustering"]
                    },
                    "maxItems": 10,
                    "description": "Statistical tests to perform"
                },
                "output_format": {
                    "type": "string",
                    "enum": ["summary", "detailed", "visualizations", "raw_data"],
                    "default": "detailed",
                    "description": "Desired output format"
                },
                "confidence_level": {
                    "type": "number",
                    "minimum": 0.8,
                    "maximum": 0.99,
                    "default": 0.95,
                    "description": "Statistical confidence level"
                },
                "sample_size": {
                    "type": "integer",
                    "minimum": 10,
                    "maximum": 1000000,
                    "description": "Sample size for analysis (optional)"
                }
            },
            "required": ["data_source", "analysis_type"],
            "additionalProperties": False
        }
    
    def get_output_schema(self) -> Dict[str, Any]:
        """JSON schema for analysis agent outputs"""
        return {
            "type": "object",
            "properties": {
                "analysis_summary": {
                    "type": "string",
                    "description": "Executive summary of analysis findings",
                    "minLength": 100,
                    "maxLength": 5000
                },
                "key_insights": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "insight": {"type": "string", "minLength": 20},
                            "significance": {
                                "type": "string",
                                "enum": ["low", "medium", "high", "critical"]
                            },
                            "confidence": {
                                "type": "number",
                                "minimum": 0.0,
                                "maximum": 1.0
                            },
                            "supporting_statistics": {
                                "type": "object",
                                "properties": {
                                    "test_name": {"type": "string"},
                                    "p_value": {"type": "number"},
                                    "effect_size": {"type": "number"}
                                }
                            }
                        },
                        "required": ["insight", "significance", "confidence"]
                    },
                    "minItems": 1,
                    "maxItems": 20,
                    "description": "Key insights from analysis"
                },
                "statistical_results": {
                    "type": "object",
                    "properties": {
                        "tests_performed": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "test_name": {"type": "string"},
                                    "result": {"type": "string"},
                                    "p_value": {"type": "number"},
                                    "significant": {"type": "boolean"}
                                },
                                "required": ["test_name", "result", "significant"]
                            }
                        },
                        "descriptive_statistics": {
                            "type": "object",
                            "description": "Mean, median, mode, std dev, etc."
                        },
                        "data_quality_metrics": {
                            "type": "object",
                            "properties": {
                                "completeness": {"type": "number", "minimum": 0.0, "maximum": 1.0},
                                "accuracy": {"type": "number", "minimum": 0.0, "maximum": 1.0},
                                "consistency": {"type": "number", "minimum": 0.0, "maximum": 1.0}
                            }
                        }
                    },
                    "description": "Detailed statistical results"
                },
                "data_quality_assessment": {
                    "type": "object",
                    "properties": {
                        "overall_quality_score": {
                            "type": "number",
                            "minimum": 0.0,
                            "maximum": 1.0
                        },
                        "missing_data_percentage": {"type": "number", "minimum": 0.0, "maximum": 100.0},
                        "outliers_detected": {"type": "integer", "minimum": 0},
                        "data_issues": {
                            "type": "array",
                            "items": {"type": "string"}
                        }
                    },
                    "required": ["overall_quality_score"],
                    "description": "Assessment of data quality"
                },
                "recommendations": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "recommendation": {"type": "string", "minLength": 20},
                            "priority": {
                                "type": "string",
                                "enum": ["low", "medium", "high", "critical"]
                            },
                            "rationale": {"type": "string"}
                        },
                        "required": ["recommendation", "priority"]
                    },
                    "description": "Actionable recommendations based on analysis"
                },
                "execution_metrics": {
                    "type": "object",
                    "properties": {
                        "data_points_analyzed": {"type": "integer", "minimum": 0},
                        "statistical_tests_executed": {"type": "integer", "minimum": 0},
                        "processing_time_seconds": {"type": "number", "minimum": 0},
                        "tokens_consumed": {"type": "integer", "minimum": 0}
                    },
                    "description": "Execution performance metrics"
                }
            },
            "required": [
                "analysis_summary",
                "key_insights",
                "statistical_results",
                "data_quality_assessment",
                "execution_metrics"
            ],
            "additionalProperties": False
        }

# Pre-configured analysis agent instances
DATA_ANALYSIS_AGENT = AnalysisAgentContract(
    agent_id="data_analysis_v1",
    agent_version="1.0.0",
    statistical_validation_required=True,
    data_quality_threshold=0.85,
    require_statistical_significance=True,
    created_by="system"
)

STATISTICAL_ANALYSIS_AGENT = AnalysisAgentContract(
    agent_id="statistical_analysis_v1",
    agent_version="1.0.0",
    statistical_validation_required=True,
    data_quality_threshold=0.9,
    require_statistical_significance=True,
    timeout_seconds=1200,  # 20 minutes for complex statistical analysis
    cost_budget_tokens=30000,
    created_by="system"
)
