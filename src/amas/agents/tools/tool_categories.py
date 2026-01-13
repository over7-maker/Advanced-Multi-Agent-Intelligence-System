"""
Tool Categories System
Maps all 60+ tools from AMAS_AGENT_TOOLS to categories for intelligent selection
"""

from enum import Enum
from typing import Dict, List, Optional, Set
from dataclasses import dataclass


class ToolCategory(Enum):
    """Tool categories for classification"""
    WEB_RESEARCH = "web_research"
    OSINT = "osint"
    DARK_WEB = "dark_web"
    SECURITY_ANALYSIS = "security_analysis"
    DATA_ANALYSIS = "data_analysis"
    OBSERVABILITY = "observability"
    ORCHESTRATION = "orchestration"
    INFRASTRUCTURE = "infrastructure"
    NETWORK_ANALYSIS = "network_analysis"
    CODE_ANALYSIS = "code_analysis"


class ExecutionMode(Enum):
    """Tool execution modes"""
    PARALLEL = "parallel"  # Can run simultaneously with other tools
    SEQUENTIAL = "sequential"  # Must run after dependencies
    INDEPENDENT = "independent"  # No dependencies
    DEPENDENT = "dependent"  # Requires other tools first


@dataclass
class ToolMetadata:
    """Metadata for tool registration"""
    name: str
    category: ToolCategory
    description: str
    execution_mode: ExecutionMode = ExecutionMode.INDEPENDENT
    dependencies: List[str] = None  # Tool names this depends on
    failover_chain: List[str] = None  # Alternative tools if this fails
    cost_tier: str = "free"  # free, low, medium, high
    requires_auth: bool = False
    avg_execution_time: float = 5.0  # seconds
    success_rate: float = 0.95  # Historical success rate
    
    def __post_init__(self):
        if self.dependencies is None:
            self.dependencies = []
        if self.failover_chain is None:
            self.failover_chain = []


# Tool category mapping - all 60+ tools from AMAS_AGENT_TOOLS
TOOL_CATEGORY_MAP: Dict[str, ToolMetadata] = {
    # ==================== WEB RESEARCH TOOLS ====================
    "agenticseek": ToolMetadata(
        name="agenticseek",
        category=ToolCategory.WEB_RESEARCH,
        description="Autonomous web browsing and research with local AI",
        execution_mode=ExecutionMode.INDEPENDENT,
        failover_chain=["searxng", "duckduckgo"],
        cost_tier="free",
        avg_execution_time=10.0
    ),
    "searxng": ToolMetadata(
        name="searxng",
        category=ToolCategory.WEB_RESEARCH,
        description="Privacy-focused meta-search engine aggregator",
        execution_mode=ExecutionMode.PARALLEL,
        failover_chain=["duckduckgo", "startpage", "bing"],
        cost_tier="free",
        avg_execution_time=3.0
    ),
    "duckduckgo": ToolMetadata(
        name="duckduckgo",
        category=ToolCategory.WEB_RESEARCH,
        description="Privacy-first search engine",
        execution_mode=ExecutionMode.PARALLEL,
        failover_chain=["startpage", "bing", "brave_search"],
        cost_tier="free",
        avg_execution_time=2.0
    ),
    "startpage": ToolMetadata(
        name="startpage",
        category=ToolCategory.WEB_RESEARCH,
        description="Anonymous search frontend",
        execution_mode=ExecutionMode.PARALLEL,
        failover_chain=["duckduckgo", "bing"],
        cost_tier="free",
        avg_execution_time=2.5
    ),
    "bing": ToolMetadata(
        name="bing",
        category=ToolCategory.WEB_RESEARCH,
        description="Comprehensive web search",
        execution_mode=ExecutionMode.PARALLEL,
        failover_chain=["google_cse", "qwant"],
        cost_tier="free",
        avg_execution_time=2.0
    ),
    "google_cse": ToolMetadata(
        name="google_cse",
        category=ToolCategory.WEB_RESEARCH,
        description="Google Custom Search Engine (100 queries/day free)",
        execution_mode=ExecutionMode.PARALLEL,
        requires_auth=True,
        failover_chain=["bing", "qwant"],
        cost_tier="low",
        avg_execution_time=2.0
    ),
    "qwant": ToolMetadata(
        name="qwant",
        category=ToolCategory.WEB_RESEARCH,
        description="EU-friendly privacy search",
        execution_mode=ExecutionMode.PARALLEL,
        failover_chain=["brave_search", "yandex"],
        cost_tier="free",
        avg_execution_time=2.5
    ),
    "brave_search": ToolMetadata(
        name="brave_search",
        category=ToolCategory.WEB_RESEARCH,
        description="Privacy-first search with free API",
        execution_mode=ExecutionMode.PARALLEL,
        requires_auth=True,
        failover_chain=["duckduckgo", "startpage"],
        cost_tier="free",
        avg_execution_time=2.0
    ),
    "yandex": ToolMetadata(
        name="yandex",
        category=ToolCategory.WEB_RESEARCH,
        description="Russian/CIS region search",
        execution_mode=ExecutionMode.PARALLEL,
        failover_chain=["bing", "qwant"],
        cost_tier="free",
        avg_execution_time=2.5
    ),
    
    # ==================== OSINT TOOLS ====================
    "fofa": ToolMetadata(
        name="fofa",
        category=ToolCategory.OSINT,
        description="FOFA cyberspace mapping and asset discovery",
        execution_mode=ExecutionMode.INDEPENDENT,
        requires_auth=True,
        failover_chain=["shodan", "censys"],
        cost_tier="medium",
        avg_execution_time=5.0
    ),
    "shodan": ToolMetadata(
        name="shodan",
        category=ToolCategory.OSINT,
        description="IoT and device discovery (1 query/month free)",
        execution_mode=ExecutionMode.PARALLEL,
        requires_auth=True,
        failover_chain=["censys", "zoomeye"],
        cost_tier="low",
        avg_execution_time=4.0
    ),
    "censys": ToolMetadata(
        name="censys",
        category=ToolCategory.OSINT,
        description="SSL/TLS certificate scanning (100 queries/day free)",
        execution_mode=ExecutionMode.PARALLEL,
        requires_auth=True,
        failover_chain=["zoomeye", "netlas"],
        cost_tier="low",
        avg_execution_time=4.5
    ),
    "zoomeye": ToolMetadata(
        name="zoomeye",
        category=ToolCategory.OSINT,
        description="Cyberspace fingerprinting",
        execution_mode=ExecutionMode.PARALLEL,
        requires_auth=True,
        failover_chain=["netlas", "criminal_ip"],
        cost_tier="low",
        avg_execution_time=4.0
    ),
    "netlas": ToolMetadata(
        name="netlas",
        category=ToolCategory.OSINT,
        description="Attack Surface Management focused",
        execution_mode=ExecutionMode.PARALLEL,
        requires_auth=True,
        failover_chain=["criminal_ip", "shodan"],
        cost_tier="free",
        avg_execution_time=3.5
    ),
    "criminal_ip": ToolMetadata(
        name="criminal_ip",
        category=ToolCategory.OSINT,
        description="Threat intelligence and context (100 queries/month free)",
        execution_mode=ExecutionMode.PARALLEL,
        requires_auth=True,
        failover_chain=["netlas", "shodan"],
        cost_tier="low",
        avg_execution_time=4.0
    ),
    
    # ==================== DARK WEB TOOLS ====================
    "robin": ToolMetadata(
        name="robin",
        category=ToolCategory.DARK_WEB,
        description="AI-powered dark web OSINT crawler",
        execution_mode=ExecutionMode.DEPENDENT,
        dependencies=["tor"],
        failover_chain=["torbot", "onionscan"],
        cost_tier="free",
        avg_execution_time=30.0
    ),
    "torbot": ToolMetadata(
        name="torbot",
        category=ToolCategory.DARK_WEB,
        description=".onion URL crawler",
        execution_mode=ExecutionMode.DEPENDENT,
        dependencies=["tor"],
        failover_chain=["onionscan", "vigilant_onion"],
        cost_tier="free",
        avg_execution_time=20.0
    ),
    "onionscan": ToolMetadata(
        name="onionscan",
        category=ToolCategory.DARK_WEB,
        description="Dark web vulnerability scanner",
        execution_mode=ExecutionMode.DEPENDENT,
        dependencies=["tor"],
        failover_chain=["vigilant_onion", "onion_ingestor"],
        cost_tier="free",
        avg_execution_time=25.0
    ),
    "vigilant_onion": ToolMetadata(
        name="vigilant_onion",
        category=ToolCategory.DARK_WEB,
        description="Continuous dark web monitoring",
        execution_mode=ExecutionMode.DEPENDENT,
        dependencies=["tor"],
        failover_chain=["onion_ingestor", "onioff"],
        cost_tier="free",
        avg_execution_time=15.0
    ),
    "onion_ingestor": ToolMetadata(
        name="onion_ingestor",
        category=ToolCategory.DARK_WEB,
        description="Automated dark web data collection",
        execution_mode=ExecutionMode.DEPENDENT,
        dependencies=["tor"],
        failover_chain=["onioff", "torbot"],
        cost_tier="free",
        avg_execution_time=18.0
    ),
    "onioff": ToolMetadata(
        name="onioff",
        category=ToolCategory.DARK_WEB,
        description="Dark web metadata analyzer",
        execution_mode=ExecutionMode.DEPENDENT,
        dependencies=["tor"],
        failover_chain=["torbot", "onionscan"],
        cost_tier="free",
        avg_execution_time=12.0
    ),
    
    # ==================== SECURITY ANALYSIS TOOLS ====================
    "sonarqube": ToolMetadata(
        name="sonarqube",
        category=ToolCategory.SECURITY_ANALYSIS,
        description="Code quality and security analysis (40+ languages)",
        execution_mode=ExecutionMode.INDEPENDENT,
        failover_chain=["semgrep", "bandit"],
        cost_tier="free",
        avg_execution_time=60.0
    ),
    "semgrep": ToolMetadata(
        name="semgrep",
        category=ToolCategory.SECURITY_ANALYSIS,
        description="Security pattern detection (2,000+ rules)",
        execution_mode=ExecutionMode.PARALLEL,
        failover_chain=["bandit", "trivy"],
        cost_tier="free",
        avg_execution_time=30.0
    ),
    "bandit": ToolMetadata(
        name="bandit",
        category=ToolCategory.SECURITY_ANALYSIS,
        description="Python-specific security scanner",
        execution_mode=ExecutionMode.PARALLEL,
        failover_chain=["semgrep", "trivy"],
        cost_tier="free",
        avg_execution_time=15.0
    ),
    "trivy": ToolMetadata(
        name="trivy",
        category=ToolCategory.SECURITY_ANALYSIS,
        description="Container and dependency vulnerability scanner",
        execution_mode=ExecutionMode.PARALLEL,
        failover_chain=["osv_scanner", "gitleaks"],
        cost_tier="free",
        avg_execution_time=20.0
    ),
    "gitleaks": ToolMetadata(
        name="gitleaks",
        category=ToolCategory.SECURITY_ANALYSIS,
        description="Secret detection in Git repositories",
        execution_mode=ExecutionMode.PARALLEL,
        failover_chain=["trufflehog", "semgrep"],
        cost_tier="free",
        avg_execution_time=10.0
    ),
    "owasp_zap": ToolMetadata(
        name="owasp_zap",
        category=ToolCategory.SECURITY_ANALYSIS,
        description="Web application security testing",
        execution_mode=ExecutionMode.INDEPENDENT,
        failover_chain=["nikto", "nmap"],
        cost_tier="free",
        avg_execution_time=120.0
    ),
    "osv_scanner": ToolMetadata(
        name="osv_scanner",
        category=ToolCategory.SECURITY_ANALYSIS,
        description="Dependency vulnerability scanner",
        execution_mode=ExecutionMode.PARALLEL,
        failover_chain=["trivy", "safety"],
        cost_tier="free",
        avg_execution_time=15.0
    ),
    
    # ==================== NETWORK ANALYSIS TOOLS ====================
    "nmap": ToolMetadata(
        name="nmap",
        category=ToolCategory.NETWORK_ANALYSIS,
        description="Network port scanner and service detection",
        execution_mode=ExecutionMode.INDEPENDENT,
        failover_chain=["masscan", "rustscan"],
        cost_tier="free",
        avg_execution_time=30.0
    ),
    "masscan": ToolMetadata(
        name="masscan",
        category=ToolCategory.NETWORK_ANALYSIS,
        description="Fast port scanner for large networks",
        execution_mode=ExecutionMode.PARALLEL,
        failover_chain=["nmap", "rustscan"],
        cost_tier="free",
        avg_execution_time=10.0
    ),
    "rustscan": ToolMetadata(
        name="rustscan",
        category=ToolCategory.NETWORK_ANALYSIS,
        description="Fast port scanner written in Rust",
        execution_mode=ExecutionMode.PARALLEL,
        failover_chain=["nmap", "masscan"],
        cost_tier="free",
        avg_execution_time=8.0
    ),
    
    # ==================== CODE ANALYSIS TOOLS ====================
    "pylint": ToolMetadata(
        name="pylint",
        category=ToolCategory.CODE_ANALYSIS,
        description="Python code quality analyzer",
        execution_mode=ExecutionMode.PARALLEL,
        failover_chain=["flake8", "black"],
        cost_tier="free",
        avg_execution_time=20.0
    ),
    "flake8": ToolMetadata(
        name="flake8",
        category=ToolCategory.CODE_ANALYSIS,
        description="Python style guide checker",
        execution_mode=ExecutionMode.PARALLEL,
        failover_chain=["pylint", "black"],
        cost_tier="free",
        avg_execution_time=5.0
    ),
    
    # ==================== DATA ANALYSIS TOOLS ====================
    "polars": ToolMetadata(
        name="polars",
        category=ToolCategory.DATA_ANALYSIS,
        description="Fast DataFrame library (5-10x faster than Pandas)",
        execution_mode=ExecutionMode.INDEPENDENT,
        failover_chain=["pandas", "duckdb"],
        cost_tier="free",
        avg_execution_time=2.0
    ),
    "duckdb": ToolMetadata(
        name="duckdb",
        category=ToolCategory.DATA_ANALYSIS,
        description="In-process OLAP database",
        execution_mode=ExecutionMode.INDEPENDENT,
        failover_chain=["polars", "pandas"],
        cost_tier="free",
        avg_execution_time=3.0
    ),
    "great_expectations": ToolMetadata(
        name="great_expectations",
        category=ToolCategory.DATA_ANALYSIS,
        description="Data quality validation framework",
        execution_mode=ExecutionMode.INDEPENDENT,
        failover_chain=["pandas", "polars"],
        cost_tier="free",
        avg_execution_time=10.0
    ),
    
    # ==================== OBSERVABILITY TOOLS ====================
    "prometheus": ToolMetadata(
        name="prometheus",
        category=ToolCategory.OBSERVABILITY,
        description="Metrics collection and monitoring",
        execution_mode=ExecutionMode.INDEPENDENT,
        cost_tier="free",
        avg_execution_time=1.0
    ),
    "grafana": ToolMetadata(
        name="grafana",
        category=ToolCategory.OBSERVABILITY,
        description="Metrics visualization and dashboards",
        execution_mode=ExecutionMode.DEPENDENT,
        dependencies=["prometheus"],
        cost_tier="free",
        avg_execution_time=0.5
    ),
    "loki": ToolMetadata(
        name="loki",
        category=ToolCategory.OBSERVABILITY,
        description="Log aggregation system",
        execution_mode=ExecutionMode.INDEPENDENT,
        cost_tier="free",
        avg_execution_time=1.0
    ),
    "jaeger": ToolMetadata(
        name="jaeger",
        category=ToolCategory.OBSERVABILITY,
        description="Distributed tracing",
        execution_mode=ExecutionMode.INDEPENDENT,
        cost_tier="free",
        avg_execution_time=1.0
    ),
    "pyroscope": ToolMetadata(
        name="pyroscope",
        category=ToolCategory.OBSERVABILITY,
        description="Continuous profiling",
        execution_mode=ExecutionMode.INDEPENDENT,
        cost_tier="free",
        avg_execution_time=2.0
    ),
    
    # ==================== EXISTING TOOLS ====================
    "web_scraper": ToolMetadata(
        name="web_scraper",
        category=ToolCategory.WEB_RESEARCH,
        description="Web scraping and content extraction",
        execution_mode=ExecutionMode.PARALLEL,
        failover_chain=["agenticseek", "api_fetcher"],
        cost_tier="free",
        avg_execution_time=5.0
    ),
    "dns_lookup": ToolMetadata(
        name="dns_lookup",
        category=ToolCategory.NETWORK_ANALYSIS,
        description="DNS record lookup",
        execution_mode=ExecutionMode.PARALLEL,
        failover_chain=["whois_lookup"],
        cost_tier="free",
        avg_execution_time=1.0
    ),
    "whois_lookup": ToolMetadata(
        name="whois_lookup",
        category=ToolCategory.NETWORK_ANALYSIS,
        description="WHOIS domain information lookup",
        execution_mode=ExecutionMode.PARALLEL,
        failover_chain=["dns_lookup"],
        cost_tier="free",
        avg_execution_time=2.0
    ),
    "ssl_analyzer": ToolMetadata(
        name="ssl_analyzer",
        category=ToolCategory.SECURITY_ANALYSIS,
        description="SSL/TLS certificate analysis",
        execution_mode=ExecutionMode.PARALLEL,
        failover_chain=["censys", "shodan"],
        cost_tier="free",
        avg_execution_time=3.0
    ),
    "api_fetcher": ToolMetadata(
        name="api_fetcher",
        category=ToolCategory.WEB_RESEARCH,
        description="Generic API data fetching",
        execution_mode=ExecutionMode.PARALLEL,
        failover_chain=["web_scraper"],
        cost_tier="free",
        avg_execution_time=2.0
    ),
    "virustotal": ToolMetadata(
        name="virustotal",
        category=ToolCategory.SECURITY_ANALYSIS,
        description="VirusTotal threat intelligence",
        execution_mode=ExecutionMode.PARALLEL,
        requires_auth=True,
        failover_chain=["abuseipdb", "shodan"],
        cost_tier="low",
        avg_execution_time=5.0
    ),
    "shodan": ToolMetadata(
        name="shodan",
        category=ToolCategory.OSINT,
        description="Shodan IoT and device search",
        execution_mode=ExecutionMode.PARALLEL,
        requires_auth=True,
        failover_chain=["censys", "fofa"],
        cost_tier="low",
        avg_execution_time=4.0
    ),
    "haveibeenpwned": ToolMetadata(
        name="haveibeenpwned",
        category=ToolCategory.OSINT,
        description="Data breach and credential exposure check",
        execution_mode=ExecutionMode.PARALLEL,
        requires_auth=True,
        failover_chain=["dehashed", "breach_directory"],
        cost_tier="low",
        avg_execution_time=2.0
    ),
    "abuseipdb": ToolMetadata(
        name="abuseipdb",
        category=ToolCategory.SECURITY_ANALYSIS,
        description="IP reputation and abuse reporting",
        execution_mode=ExecutionMode.PARALLEL,
        requires_auth=True,
        failover_chain=["virustotal", "shodan"],
        cost_tier="low",
        avg_execution_time=3.0
    ),
    "censys": ToolMetadata(
        name="censys",
        category=ToolCategory.OSINT,
        description="Censys certificate and host search",
        execution_mode=ExecutionMode.PARALLEL,
        requires_auth=True,
        failover_chain=["shodan", "fofa"],
        cost_tier="low",
        avg_execution_time=4.5
    ),
    "github_api": ToolMetadata(
        name="github_api",
        category=ToolCategory.CODE_ANALYSIS,
        description="GitHub API integration",
        execution_mode=ExecutionMode.PARALLEL,
        requires_auth=True,
        failover_chain=["gitlab_api"],
        cost_tier="free",
        avg_execution_time=2.0
    ),
    "gitlab_api": ToolMetadata(
        name="gitlab_api",
        category=ToolCategory.CODE_ANALYSIS,
        description="GitLab API integration",
        execution_mode=ExecutionMode.PARALLEL,
        requires_auth=True,
        failover_chain=["github_api"],
        cost_tier="free",
        avg_execution_time=2.0
    ),
    "npm_package": ToolMetadata(
        name="npm_package",
        category=ToolCategory.CODE_ANALYSIS,
        description="NPM package information lookup",
        execution_mode=ExecutionMode.PARALLEL,
        failover_chain=["pypi_package"],
        cost_tier="free",
        avg_execution_time=1.0
    ),
    "pypi_package": ToolMetadata(
        name="pypi_package",
        category=ToolCategory.CODE_ANALYSIS,
        description="PyPI package information lookup",
        execution_mode=ExecutionMode.PARALLEL,
        failover_chain=["npm_package"],
        cost_tier="free",
        avg_execution_time=1.0
    ),
}


def get_tools_by_category(category: ToolCategory) -> List[str]:
    """Get all tool names in a category"""
    return [
        name for name, metadata in TOOL_CATEGORY_MAP.items()
        if metadata.category == category
    ]


def get_tool_metadata(tool_name: str) -> Optional[ToolMetadata]:
    """Get metadata for a tool"""
    return TOOL_CATEGORY_MAP.get(tool_name)


def get_tools_by_execution_mode(mode: ExecutionMode) -> List[str]:
    """Get tools that support a specific execution mode"""
    return [
        name for name, metadata in TOOL_CATEGORY_MAP.items()
        if metadata.execution_mode == mode
    ]


def get_free_tools() -> List[str]:
    """Get all free-tier tools"""
    return [
        name for name, metadata in TOOL_CATEGORY_MAP.items()
        if metadata.cost_tier == "free"
    ]


def get_tool_failover_chain(tool_name: str) -> List[str]:
    """Get failover chain for a tool"""
    metadata = get_tool_metadata(tool_name)
    if metadata:
        return metadata.failover_chain
    return []


def get_tool_dependencies(tool_name: str) -> List[str]:
    """Get dependencies for a tool"""
    metadata = get_tool_metadata(tool_name)
    if metadata:
        return metadata.dependencies
    return []


__all__ = [
    'ToolCategory',
    'ExecutionMode',
    'ToolMetadata',
    'TOOL_CATEGORY_MAP',
    'get_tools_by_category',
    'get_tool_metadata',
    'get_tools_by_execution_mode',
    'get_free_tools',
    'get_tool_failover_chain',
    'get_tool_dependencies',
]

