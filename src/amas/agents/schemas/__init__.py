"""
Agent Response Schemas
Pydantic schemas for agent response validation
"""

from pydantic import BaseModel, Field
from typing import Any, Dict, List, Optional
from datetime import datetime


class BaseAgentResponse(BaseModel):
    """Base schema for all agent responses"""
    success: bool = Field(..., description="Whether the operation was successful")
    summary: Optional[str] = Field(None, description="Summary of the result")
    quality_score: Optional[float] = Field(None, ge=0.0, le=1.0, description="Quality score (0-1)")
    insights: Optional[List[str]] = Field(default_factory=list, description="Key insights")
    recommendations: Optional[List[str]] = Field(default_factory=list, description="Recommendations")


class SecurityAnalysisResult(BaseAgentResponse):
    """Schema for SecurityExpertAgent responses"""
    vulnerabilities: List[Dict[str, Any]] = Field(default_factory=list, description="List of vulnerabilities")
    security_headers: Dict[str, Any] = Field(default_factory=dict, description="Security headers analysis")
    ssl_analysis: Optional[Dict[str, Any]] = Field(None, description="SSL/TLS certificate analysis")
    technology_stack: Optional[Dict[str, Any]] = Field(None, description="Detected technology stack")
    risk_level: Optional[str] = Field(None, description="Overall risk level (Critical/High/Medium/Low)")
    compliance_status: Optional[Dict[str, Any]] = Field(None, description="Compliance status")


class IntelligenceReport(BaseAgentResponse):
    """Schema for IntelligenceGatheringAgent responses"""
    dns_information: Optional[Dict[str, Any]] = Field(None, description="DNS records")
    whois_information: Optional[Dict[str, Any]] = Field(None, description="WHOIS data")
    geolocation: Optional[Dict[str, Any]] = Field(None, description="IP geolocation data")
    threat_intelligence: Optional[List[Dict[str, Any]]] = Field(default_factory=list, description="Threat intelligence findings")
    digital_footprint: Optional[Dict[str, Any]] = Field(None, description="Digital footprint analysis")
    confidence_score: Optional[float] = Field(None, ge=0.0, le=1.0, description="Confidence in findings")


class CodeAnalysisResult(BaseAgentResponse):
    """Schema for CodeAnalysisAgent responses"""
    code_quality: Optional[Dict[str, Any]] = Field(None, description="Code quality metrics")
    security_issues: List[Dict[str, Any]] = Field(default_factory=list, description="Security vulnerabilities")
    performance_issues: List[Dict[str, Any]] = Field(default_factory=list, description="Performance issues")
    code_smells: List[Dict[str, Any]] = Field(default_factory=list, description="Code smells detected")
    dependencies: Optional[Dict[str, Any]] = Field(None, description="Dependency analysis")
    test_coverage: Optional[float] = Field(None, ge=0.0, le=1.0, description="Test coverage percentage")
    refactoring_suggestions: List[Dict[str, Any]] = Field(default_factory=list, description="Refactoring recommendations")


class PerformanceReport(BaseAgentResponse):
    """Schema for PerformanceAgent responses"""
    bottlenecks: List[Dict[str, Any]] = Field(default_factory=list, description="Performance bottlenecks")
    optimizations: List[Dict[str, Any]] = Field(default_factory=list, description="Optimization recommendations")
    metrics: Optional[Dict[str, Any]] = Field(None, description="Performance metrics")
    resource_usage: Optional[Dict[str, Any]] = Field(None, description="Resource usage analysis")
    scalability_assessment: Optional[str] = Field(None, description="Scalability assessment")


class DocumentationResult(BaseAgentResponse):
    """Schema for DocumentationAgent responses"""
    documentation: Optional[str] = Field(None, description="Generated documentation")
    api_spec: Optional[Dict[str, Any]] = Field(None, description="API specification (OpenAPI)")
    diagrams: Optional[List[str]] = Field(default_factory=list, description="Generated diagrams")
    examples: Optional[List[str]] = Field(default_factory=list, description="Code examples")
    completeness_score: Optional[float] = Field(None, ge=0.0, le=1.0, description="Documentation completeness")


class TestingResult(BaseAgentResponse):
    """Schema for TestingAgent responses"""
    test_cases: List[Dict[str, Any]] = Field(default_factory=list, description="Generated test cases")
    coverage_analysis: Optional[Dict[str, Any]] = Field(None, description="Test coverage analysis")
    test_code: Optional[str] = Field(None, description="Generated test code")
    test_strategy: Optional[str] = Field(None, description="Testing strategy recommendations")
    coverage_percentage: Optional[float] = Field(None, ge=0.0, le=1.0, description="Coverage percentage")


class DeploymentPlan(BaseAgentResponse):
    """Schema for DeploymentAgent responses"""
    dockerfile: Optional[str] = Field(None, description="Generated Dockerfile")
    kubernetes_manifests: Optional[Dict[str, str]] = Field(None, description="K8s manifest files")
    cicd_pipeline: Optional[Dict[str, Any]] = Field(None, description="CI/CD pipeline configuration")
    infrastructure_code: Optional[Dict[str, str]] = Field(None, description="Infrastructure as Code")
    deployment_strategy: Optional[str] = Field(None, description="Deployment strategy")
    rollback_plan: Optional[Dict[str, Any]] = Field(None, description="Rollback procedures")


class MonitoringConfig(BaseAgentResponse):
    """Schema for MonitoringAgent responses"""
    prometheus_metrics: Optional[List[Dict[str, Any]]] = Field(default_factory=list, description="Prometheus metric definitions")
    grafana_dashboards: Optional[List[Dict[str, Any]]] = Field(default_factory=list, description="Grafana dashboard configs")
    alert_rules: Optional[List[Dict[str, Any]]] = Field(default_factory=list, description="Alert rules")
    sli_slo: Optional[Dict[str, Any]] = Field(None, description="SLI/SLO definitions")
    observability_stack: Optional[List[str]] = Field(default_factory=list, description="Recommended observability tools")


class DataAnalysisResult(BaseAgentResponse):
    """Schema for DataAgent responses"""
    statistical_summary: Optional[Dict[str, Any]] = Field(None, description="Statistical summary")
    patterns: List[Dict[str, Any]] = Field(default_factory=list, description="Detected patterns")
    anomalies: List[Dict[str, Any]] = Field(default_factory=list, description="Anomalies detected")
    visualizations: Optional[List[str]] = Field(default_factory=list, description="Visualization recommendations")
    predictions: Optional[Dict[str, Any]] = Field(None, description="Predictive analytics results")
    data_quality: Optional[Dict[str, Any]] = Field(None, description="Data quality assessment")


class APIDesignResult(BaseAgentResponse):
    """Schema for APIAgent responses"""
    api_spec: Optional[Dict[str, Any]] = Field(None, description="OpenAPI specification")
    endpoints: List[Dict[str, Any]] = Field(default_factory=list, description="API endpoints")
    authentication: Optional[Dict[str, Any]] = Field(None, description="Authentication strategy")
    rate_limiting: Optional[Dict[str, Any]] = Field(None, description="Rate limiting configuration")
    versioning_strategy: Optional[str] = Field(None, description="API versioning approach")
    testing_strategy: Optional[Dict[str, Any]] = Field(None, description="API testing strategy")


class IntegrationPlan(BaseAgentResponse):
    """Schema for IntegrationAgent responses"""
    integration_pattern: Optional[str] = Field(None, description="Recommended integration pattern")
    webhook_config: Optional[Dict[str, Any]] = Field(None, description="Webhook configuration")
    oauth2_flow: Optional[Dict[str, Any]] = Field(None, description="OAuth2 flow implementation")
    data_sync_strategy: Optional[Dict[str, Any]] = Field(None, description="Data synchronization strategy")
    error_handling: Optional[Dict[str, Any]] = Field(None, description="Error handling patterns")
    implementation_code: Optional[str] = Field(None, description="Integration implementation code")


class ResearchReport(BaseAgentResponse):
    """Schema for ResearchAgent responses"""
    findings: List[Dict[str, Any]] = Field(default_factory=list, description="Research findings")
    sources: List[Dict[str, Any]] = Field(default_factory=list, description="Information sources")
    citations: List[str] = Field(default_factory=list, description="Citations and references")
    trends: Optional[List[str]] = Field(default_factory=list, description="Technology trends identified")
    recommendations: Optional[List[str]] = Field(default_factory=list, description="Research-based recommendations")


__all__ = [
    'BaseAgentResponse',
    'SecurityAnalysisResult',
    'IntelligenceReport',
    'CodeAnalysisResult',
    'PerformanceReport',
    'DocumentationResult',
    'TestingResult',
    'DeploymentPlan',
    'MonitoringConfig',
    'DataAnalysisResult',
    'APIDesignResult',
    'IntegrationPlan',
    'ResearchReport'
]

