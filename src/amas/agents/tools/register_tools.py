"""
Tool Registration
Register all available tools in the global registry
"""

import logging
from src.amas.agents.tools import register_tool
from src.amas.agents.tools.web_scraper import WebScraperTool
from src.amas.agents.tools.dns_lookup import DNSLookupTool
from src.amas.agents.tools.whois_lookup import WHOISLookupTool
from src.amas.agents.tools.ssl_analyzer import SSLAnalyzerTool
from src.amas.agents.tools.api_fetcher import APIFetcherTool

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
    """Register all available tools"""
    logger.info("Registering agent tools...")
    
    # Data collection tools
    register_tool(WebScraperTool())
    register_tool(DNSLookupTool())
    register_tool(WHOISLookupTool())
    register_tool(SSLAnalyzerTool())
    register_tool(APIFetcherTool())
    
    # Security APIs (if available)
    if SECURITY_APIS_AVAILABLE:
        try:
            register_tool(VirusTotalTool())
            register_tool(ShodanTool())
            register_tool(HaveIBeenPwnedTool())
            register_tool(AbuseIPDBTool())
            register_tool(CensysTool())
            logger.info("Security API tools registered")
        except Exception as e:
            logger.warning(f"Failed to register some security API tools: {e}")
    
    # Intelligence APIs (if available)
    if INTELLIGENCE_APIS_AVAILABLE:
        try:
            register_tool(GitHubAPITool())
            register_tool(GitLabAPITool())
            register_tool(NPMPackageTool())
            register_tool(PyPIPackageTool())
            logger.info("Intelligence API tools registered")
        except Exception as e:
            logger.warning(f"Failed to register some intelligence API tools: {e}")
    
    logger.info("Agent tools registered successfully")


# Auto-register on import
try:
    register_all_tools()
except Exception as e:
    logger.warning(f"Failed to register some tools: {e}")

