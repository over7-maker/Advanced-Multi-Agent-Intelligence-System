"""
Tool Registration
Register all available tools in the global registry with categories
"""

import logging
from src.amas.agents.tools import register_tool
from src.amas.agents.tools.web_scraper import WebScraperTool
from src.amas.agents.tools.dns_lookup import DNSLookupTool
from src.amas.agents.tools.whois_lookup import WHOISLookupTool
from src.amas.agents.tools.ssl_analyzer import SSLAnalyzerTool
from src.amas.agents.tools.api_fetcher import APIFetcherTool

# Import tool categories for category mapping
try:
    from src.amas.agents.tools.tool_categories import ToolCategory
except ImportError:
    ToolCategory = None

# Search Engine Tools
try:
    from src.amas.agents.tools.search_engines import (
        SearxNGTool,
        DuckDuckGoTool,
        StartpageTool,
        BingSearchTool,
        GoogleCSETool,
        QwantTool,
        BraveSearchTool,
        YandexTool
    )
    SEARCH_ENGINES_AVAILABLE = True
except ImportError:
    SEARCH_ENGINES_AVAILABLE = False

# AgenticSeek Tool
try:
    from src.amas.agents.tools.agenticseek_tool import AgenticSeekTool
    AGENTICSEEK_AVAILABLE = True
except ImportError:
    AGENTICSEEK_AVAILABLE = False

# OSINT Tools
try:
    from src.amas.agents.tools.osint_tools import (
        FOFATool,
        ZoomEyeTool,
        NetlasTool,
        CriminalIPTool
    )
    OSINT_TOOLS_AVAILABLE = True
except ImportError:
    OSINT_TOOLS_AVAILABLE = False

# Security Scanner Tools
try:
    from src.amas.agents.tools.security_scanners import (
        SemgrepTool,
        BanditTool,
        TrivyTool,
        GitleaksTool,
        OSVScannerTool
    )
    SECURITY_SCANNERS_AVAILABLE = True
except ImportError:
    SECURITY_SCANNERS_AVAILABLE = False

# Network Scanner Tools
try:
    from src.amas.agents.tools.network_scanners import (
        NmapTool,
        MasscanTool,
        RustscanTool
    )
    NETWORK_SCANNERS_AVAILABLE = True
except ImportError:
    NETWORK_SCANNERS_AVAILABLE = False

# Code Analysis Tools
try:
    from src.amas.agents.tools.code_analysis_tools import (
        PylintTool,
        Flake8Tool
    )
    CODE_ANALYSIS_AVAILABLE = True
except ImportError:
    CODE_ANALYSIS_AVAILABLE = False

# Data Analysis Tools
try:
    from src.amas.agents.tools.data_analysis_tools import (
        PolarsTool,
        DuckDBTool,
        GreatExpectationsTool
    )
    DATA_ANALYSIS_AVAILABLE = True
except ImportError:
    DATA_ANALYSIS_AVAILABLE = False

# Dark Web Tools
try:
    from src.amas.agents.tools.dark_web_tools import (
        RobinTool,
        TorBotTool,
        OnionScanTool,
        VigilantOnionTool,
        OnionIngestorTool,
        OnioffTool
    )
    DARK_WEB_TOOLS_AVAILABLE = True
except ImportError:
    DARK_WEB_TOOLS_AVAILABLE = False

# Advanced Security Tools
try:
    from src.amas.agents.tools.security_advanced_tools import (
        SonarQubeTool,
        OWASPZAPTool
    )
    ADVANCED_SECURITY_AVAILABLE = True
except ImportError:
    ADVANCED_SECURITY_AVAILABLE = False

# Observability Tools
try:
    from src.amas.agents.tools.observability_tools import (
        PrometheusTool,
        GrafanaTool,
        LokiTool,
        JaegerTool,
        PyroscopeTool
    )
    OBSERVABILITY_AVAILABLE = True
except ImportError:
    OBSERVABILITY_AVAILABLE = False

# Security APIs (optional - require API keys)
try:
    from src.amas.agents.tools.security_apis import (
        VirusTotalTool,
        ShodanTool,
        HaveIBeenPwnedTool,
        AbuseIPDBTool,
        CensysTool
    )
    SECURITY_APIS_AVAILABLE = True
except ImportError:
    SECURITY_APIS_AVAILABLE = False

# Intelligence APIs (optional - require API keys)
try:
    from src.amas.agents.tools.intelligence_apis import (
        GitHubAPITool,
        GitLabAPITool,
        NPMPackageTool,
        PyPIPackageTool
    )
    INTELLIGENCE_APIS_AVAILABLE = True
except ImportError:
    INTELLIGENCE_APIS_AVAILABLE = False

logger = logging.getLogger(__name__)


def register_all_tools():
    """Register all available tools with categories"""
    logger.info("Registering agent tools with categories...")
    
    # Tool category mapping (extended for all tools)
    tool_categories = {
        # Existing tools
        "web_scraper": ToolCategory.WEB_RESEARCH.value if ToolCategory else "web_research",
        "dns_lookup": ToolCategory.NETWORK_ANALYSIS.value if ToolCategory else "network_analysis",
        "whois_lookup": ToolCategory.NETWORK_ANALYSIS.value if ToolCategory else "network_analysis",
        "ssl_analyzer": ToolCategory.SECURITY_ANALYSIS.value if ToolCategory else "security_analysis",
        "api_fetcher": ToolCategory.WEB_RESEARCH.value if ToolCategory else "web_research",
        "virustotal": ToolCategory.SECURITY_ANALYSIS.value if ToolCategory else "security_analysis",
        "shodan": ToolCategory.OSINT.value if ToolCategory else "osint",
        "haveibeenpwned": ToolCategory.OSINT.value if ToolCategory else "osint",
        "abuseipdb": ToolCategory.SECURITY_ANALYSIS.value if ToolCategory else "security_analysis",
        "censys": ToolCategory.OSINT.value if ToolCategory else "osint",
        "github_api": ToolCategory.CODE_ANALYSIS.value if ToolCategory else "code_analysis",
        "gitlab_api": ToolCategory.CODE_ANALYSIS.value if ToolCategory else "code_analysis",
        "npm_package": ToolCategory.CODE_ANALYSIS.value if ToolCategory else "code_analysis",
        "pypi_package": ToolCategory.CODE_ANALYSIS.value if ToolCategory else "code_analysis",
        # Search engines
        "agenticseek": ToolCategory.WEB_RESEARCH.value if ToolCategory else "web_research",
        "searxng": ToolCategory.WEB_RESEARCH.value if ToolCategory else "web_research",
        "duckduckgo": ToolCategory.WEB_RESEARCH.value if ToolCategory else "web_research",
        "startpage": ToolCategory.WEB_RESEARCH.value if ToolCategory else "web_research",
        "bing": ToolCategory.WEB_RESEARCH.value if ToolCategory else "web_research",
        "google_cse": ToolCategory.WEB_RESEARCH.value if ToolCategory else "web_research",
        "qwant": ToolCategory.WEB_RESEARCH.value if ToolCategory else "web_research",
        "brave_search": ToolCategory.WEB_RESEARCH.value if ToolCategory else "web_research",
        "yandex": ToolCategory.WEB_RESEARCH.value if ToolCategory else "web_research",
        # OSINT
        "fofa": ToolCategory.OSINT.value if ToolCategory else "osint",
        "zoomeye": ToolCategory.OSINT.value if ToolCategory else "osint",
        "netlas": ToolCategory.OSINT.value if ToolCategory else "osint",
        "criminal_ip": ToolCategory.OSINT.value if ToolCategory else "osint",
        # Security scanners
        "semgrep": ToolCategory.SECURITY_ANALYSIS.value if ToolCategory else "security_analysis",
        "bandit": ToolCategory.SECURITY_ANALYSIS.value if ToolCategory else "security_analysis",
        "trivy": ToolCategory.SECURITY_ANALYSIS.value if ToolCategory else "security_analysis",
        "gitleaks": ToolCategory.SECURITY_ANALYSIS.value if ToolCategory else "security_analysis",
        "osv_scanner": ToolCategory.SECURITY_ANALYSIS.value if ToolCategory else "security_analysis",
        "sonarqube": ToolCategory.SECURITY_ANALYSIS.value if ToolCategory else "security_analysis",
        "owasp_zap": ToolCategory.SECURITY_ANALYSIS.value if ToolCategory else "security_analysis",
        # Network scanners
        "nmap": ToolCategory.NETWORK_ANALYSIS.value if ToolCategory else "network_analysis",
        "masscan": ToolCategory.NETWORK_ANALYSIS.value if ToolCategory else "network_analysis",
        "rustscan": ToolCategory.NETWORK_ANALYSIS.value if ToolCategory else "network_analysis",
        # Code analysis
        "pylint": ToolCategory.CODE_ANALYSIS.value if ToolCategory else "code_analysis",
        "flake8": ToolCategory.CODE_ANALYSIS.value if ToolCategory else "code_analysis",
        # Data analysis
        "polars": ToolCategory.DATA_ANALYSIS.value if ToolCategory else "data_analysis",
        "duckdb": ToolCategory.DATA_ANALYSIS.value if ToolCategory else "data_analysis",
        "great_expectations": ToolCategory.DATA_ANALYSIS.value if ToolCategory else "data_analysis",
        # Dark web
        "robin": ToolCategory.DARK_WEB.value if ToolCategory else "dark_web",
        "torbot": ToolCategory.DARK_WEB.value if ToolCategory else "dark_web",
        "onionscan": ToolCategory.DARK_WEB.value if ToolCategory else "dark_web",
        "vigilant_onion": ToolCategory.DARK_WEB.value if ToolCategory else "dark_web",
        "onion_ingestor": ToolCategory.DARK_WEB.value if ToolCategory else "dark_web",
        "onioff": ToolCategory.DARK_WEB.value if ToolCategory else "dark_web",
        # Observability
        "prometheus": ToolCategory.OBSERVABILITY.value if ToolCategory else "observability",
        "grafana": ToolCategory.OBSERVABILITY.value if ToolCategory else "observability",
        "loki": ToolCategory.OBSERVABILITY.value if ToolCategory else "observability",
        "jaeger": ToolCategory.OBSERVABILITY.value if ToolCategory else "observability",
        "pyroscope": ToolCategory.OBSERVABILITY.value if ToolCategory else "observability",
    }
    
    # Data collection tools
    register_tool(WebScraperTool(), category=tool_categories.get("web_scraper"))
    register_tool(DNSLookupTool(), category=tool_categories.get("dns_lookup"))
    register_tool(WHOISLookupTool(), category=tool_categories.get("whois_lookup"))
    register_tool(SSLAnalyzerTool(), category=tool_categories.get("ssl_analyzer"))
    register_tool(APIFetcherTool(), category=tool_categories.get("api_fetcher"))
    
    # Security APIs (if available)
    if SECURITY_APIS_AVAILABLE:
        try:
            register_tool(VirusTotalTool(), category=tool_categories.get("virustotal"))
            register_tool(ShodanTool(), category=tool_categories.get("shodan"))
            register_tool(HaveIBeenPwnedTool(), category=tool_categories.get("haveibeenpwned"))
            register_tool(AbuseIPDBTool(), category=tool_categories.get("abuseipdb"))
            register_tool(CensysTool(), category=tool_categories.get("censys"))
            logger.info("Security API tools registered with categories")
        except Exception as e:
            logger.warning(f"Failed to register some security API tools: {e}")
    
    # Intelligence APIs (if available)
    if INTELLIGENCE_APIS_AVAILABLE:
        try:
            register_tool(GitHubAPITool(), category=tool_categories.get("github_api"))
            register_tool(GitLabAPITool(), category=tool_categories.get("gitlab_api"))
            register_tool(NPMPackageTool(), category=tool_categories.get("npm_package"))
            register_tool(PyPIPackageTool(), category=tool_categories.get("pypi_package"))
            logger.info("Intelligence API tools registered with categories")
        except Exception as e:
            logger.warning(f"Failed to register some intelligence API tools: {e}")
    
    # Search Engine Tools
    if SEARCH_ENGINES_AVAILABLE:
        try:
            register_tool(SearxNGTool(), category=tool_categories.get("searxng"))
            register_tool(DuckDuckGoTool(), category=tool_categories.get("duckduckgo"))
            register_tool(StartpageTool(), category=tool_categories.get("startpage"))
            register_tool(BingSearchTool(), category=tool_categories.get("bing"))
            register_tool(GoogleCSETool(), category=tool_categories.get("google_cse"))
            register_tool(QwantTool(), category=tool_categories.get("qwant"))
            register_tool(BraveSearchTool(), category=tool_categories.get("brave_search"))
            register_tool(YandexTool(), category=tool_categories.get("yandex"))
            logger.info("Search engine tools registered")
        except Exception as e:
            logger.warning(f"Failed to register some search engine tools: {e}")
    
    # AgenticSeek
    if AGENTICSEEK_AVAILABLE:
        try:
            register_tool(AgenticSeekTool(), category=tool_categories.get("agenticseek"))
            logger.info("AgenticSeek tool registered")
        except Exception as e:
            logger.warning(f"Failed to register AgenticSeek: {e}")
    
    # OSINT Tools
    if OSINT_TOOLS_AVAILABLE:
        try:
            register_tool(FOFATool(), category=tool_categories.get("fofa"))
            register_tool(ZoomEyeTool(), category=tool_categories.get("zoomeye"))
            register_tool(NetlasTool(), category=tool_categories.get("netlas"))
            register_tool(CriminalIPTool(), category=tool_categories.get("criminal_ip"))
            logger.info("OSINT tools registered")
        except Exception as e:
            logger.warning(f"Failed to register some OSINT tools: {e}")
    
    # Security Scanner Tools
    if SECURITY_SCANNERS_AVAILABLE:
        try:
            register_tool(SemgrepTool(), category=tool_categories.get("semgrep"))
            register_tool(BanditTool(), category=tool_categories.get("bandit"))
            register_tool(TrivyTool(), category=tool_categories.get("trivy"))
            register_tool(GitleaksTool(), category=tool_categories.get("gitleaks"))
            register_tool(OSVScannerTool(), category=tool_categories.get("osv_scanner"))
            logger.info("Security scanner tools registered")
        except Exception as e:
            logger.warning(f"Failed to register some security scanner tools: {e}")
    
    # Network Scanner Tools
    if NETWORK_SCANNERS_AVAILABLE:
        try:
            register_tool(NmapTool(), category=tool_categories.get("nmap"))
            register_tool(MasscanTool(), category=tool_categories.get("masscan"))
            register_tool(RustscanTool(), category=tool_categories.get("rustscan"))
            logger.info("Network scanner tools registered")
        except Exception as e:
            logger.warning(f"Failed to register some network scanner tools: {e}")
    
    # Code Analysis Tools
    if CODE_ANALYSIS_AVAILABLE:
        try:
            register_tool(PylintTool(), category=tool_categories.get("pylint"))
            register_tool(Flake8Tool(), category=tool_categories.get("flake8"))
            logger.info("Code analysis tools registered")
        except Exception as e:
            logger.warning(f"Failed to register some code analysis tools: {e}")
    
    # Data Analysis Tools
    if DATA_ANALYSIS_AVAILABLE:
        try:
            register_tool(PolarsTool(), category=tool_categories.get("polars"))
            register_tool(DuckDBTool(), category=tool_categories.get("duckdb"))
            register_tool(GreatExpectationsTool(), category=tool_categories.get("great_expectations"))
            logger.info("Data analysis tools registered")
        except Exception as e:
            logger.warning(f"Failed to register some data analysis tools: {e}")
    
    # Dark Web Tools
    if DARK_WEB_TOOLS_AVAILABLE:
        try:
            register_tool(RobinTool(), category=tool_categories.get("robin"))
            register_tool(TorBotTool(), category=tool_categories.get("torbot"))
            register_tool(OnionScanTool(), category=tool_categories.get("onionscan"))
            register_tool(VigilantOnionTool(), category=tool_categories.get("vigilant_onion"))
            register_tool(OnionIngestorTool(), category=tool_categories.get("onion_ingestor"))
            register_tool(OnioffTool(), category=tool_categories.get("onioff"))
            logger.info("Dark web tools registered")
        except Exception as e:
            logger.warning(f"Failed to register some dark web tools: {e}")
    
    # Advanced Security Tools
    if ADVANCED_SECURITY_AVAILABLE:
        try:
            register_tool(SonarQubeTool(), category=tool_categories.get("sonarqube"))
            register_tool(OWASPZAPTool(), category=tool_categories.get("owasp_zap"))
            logger.info("Advanced security tools registered")
        except Exception as e:
            logger.warning(f"Failed to register some advanced security tools: {e}")
    
    # Observability Tools
    if OBSERVABILITY_AVAILABLE:
        try:
            register_tool(PrometheusTool(), category=tool_categories.get("prometheus"))
            register_tool(GrafanaTool(), category=tool_categories.get("grafana"))
            register_tool(LokiTool(), category=tool_categories.get("loki"))
            register_tool(JaegerTool(), category=tool_categories.get("jaeger"))
            register_tool(PyroscopeTool(), category=tool_categories.get("pyroscope"))
            logger.info("Observability tools registered")
        except Exception as e:
            logger.warning(f"Failed to register some observability tools: {e}")
    
    logger.info("Agent tools registered successfully with multi-tool support")


# Auto-register on import
try:
    register_all_tools()
except Exception as e:
    logger.warning(f"Failed to register some tools: {e}")

