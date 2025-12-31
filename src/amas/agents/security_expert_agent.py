"""
Security Expert Agent - Specialized agent for security analysis
Implements PART_3 requirements
"""

import json
import logging
import ssl
import socket
import time
from datetime import datetime
from typing import Any, Dict
from urllib.parse import urlparse, urljoin

import aiohttp
from bs4 import BeautifulSoup

from src.amas.agents.base_agent import BaseAgent
from src.amas.agents.tools import get_tool_registry
from src.amas.agents.utils.json_parser import JSONParser
from src.amas.agents.schemas import SecurityAnalysisResult

logger = logging.getLogger(__name__)


class SecurityExpertAgent(BaseAgent):
    """
    Security Expert Agent
    
    Specializes in:
    - Vulnerability assessment
    - Security auditing
    - Penetration testing
    - Threat analysis
    """
    
    def __init__(self):
        super().__init__(
            agent_id="security_expert",
            name="Security Expert",
            agent_type="security",
            system_prompt="""You are an elite cybersecurity expert with 15+ years of experience 
            in penetration testing, vulnerability assessment, and security auditing.
            
            Your expertise includes:
            • OWASP Top 10 vulnerabilities
            • Network security analysis
            • Web application security
            • API security testing
            • SSL/TLS configuration review
            • Security header analysis
            • Common vulnerability detection (SQL injection, XSS, CSRF, etc.)
            
            When analyzing a target, you:
            1. Perform comprehensive security assessment
            2. Identify specific vulnerabilities with CVE references when applicable
            3. Provide severity ratings (Critical, High, Medium, Low)
            4. Suggest concrete remediation steps
            5. Prioritize findings by risk
            
            Always provide actionable, technical recommendations.""",
            tools=[],  # Tools can be added here
            model_preference=None,  # Use local models first
            strategy="quality_first"
        )
        
        self.expertise_score = 0.95  # High expertise
        
        # Get tool registry and register security tools
        tool_registry = get_tool_registry()
        # Tools will be available via registry
        self.security_tools = [
            "web_scraper",
            "ssl_analyzer",
            "virustotal",
            "shodan",
            "haveibeenpwned",
            "abuseipdb",
            "censys"
        ]
    
    async def _perform_real_web_scraping(self, target: str) -> Dict[str, Any]:
        """Perform real web scraping to collect actual data from target"""
        collected_data = {
            "html_content": None,
            "http_headers": {},
            "status_code": None,
            "technology_indicators": [],
            "error": None
        }
        
        try:
            # Normalize target URL
            if not target.startswith(('http://', 'https://')):
                target = f"https://{target}"
            
            url = target
            logger.info(f"SecurityExpertAgent: Starting web scraping for {url}")
            
            timeout = aiohttp.ClientTimeout(total=30)
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            }
            
            async with aiohttp.ClientSession(timeout=timeout, headers=headers) as session:
                try:
                    async with session.get(url, allow_redirects=True, ssl=False) as response:
                        collected_data["status_code"] = response.status
                        collected_data["http_headers"] = dict(response.headers)
                        
                        # Get HTML content
                        html_content = await response.text()
                        collected_data["html_content"] = html_content
                        
                        # Parse HTML for technology indicators
                        soup = BeautifulSoup(html_content, 'html.parser')
                        
                        # Detect technology stack from HTML
                        tech_indicators = []
                        
                        # Check for meta tags
                        meta_generator = soup.find('meta', attrs={'name': 'generator'})
                        if meta_generator and meta_generator.get('content'):
                            tech_indicators.append(f"Generator: {meta_generator.get('content')}")
                        
                        # Check for common framework indicators
                        if soup.find('script', src=lambda x: x and 'jquery' in x.lower()):
                            tech_indicators.append("jQuery detected")
                        if soup.find('script', src=lambda x: x and 'react' in x.lower()):
                            tech_indicators.append("React detected")
                        if soup.find('script', src=lambda x: x and 'angular' in x.lower()):
                            tech_indicators.append("Angular detected")
                        if soup.find('script', src=lambda x: x and 'vue' in x.lower()):
                            tech_indicators.append("Vue.js detected")
                        
                        # Check for WordPress
                        if soup.find('link', href=lambda x: x and '/wp-content/' in x) or \
                           soup.find('script', src=lambda x: x and '/wp-content/' in x):
                            tech_indicators.append("WordPress detected")
                        
                        # Check for server header
                        server_header = collected_data["http_headers"].get('Server', '')
                        if server_header:
                            tech_indicators.append(f"Server: {server_header}")
                        
                        # Check for X-Powered-By header
                        powered_by = collected_data["http_headers"].get('X-Powered-By', '')
                        if powered_by:
                            tech_indicators.append(f"Powered By: {powered_by}")
                        
                        collected_data["technology_indicators"] = tech_indicators
                        
                        logger.info(f"SecurityExpertAgent: Web scraping completed for {url}: status={response.status}, tech_indicators={len(tech_indicators)}")
                        
                except aiohttp.ClientError as e:
                    collected_data["error"] = f"HTTP client error: {str(e)}"
                    logger.warning(f"SecurityExpertAgent: Web scraping failed for {url}: {e}")
                except Exception as e:
                    collected_data["error"] = f"Web scraping error: {str(e)}"
                    logger.error(f"SecurityExpertAgent: Web scraping error for {url}: {e}", exc_info=True)
        
        except Exception as e:
            collected_data["error"] = f"Web scraping failed: {str(e)}"
            logger.error(f"SecurityExpertAgent: Web scraping failed for {target}: {e}", exc_info=True)
        
        return collected_data
    
    async def _analyze_ssl_certificate(self, target: str) -> Dict[str, Any]:
        """Analyze SSL/TLS certificate for target"""
        ssl_data = {
            "valid": False,
            "expires": None,
            "issuer": None,
            "subject": None,
            "version": None,
            "cipher": None,
            "issues": []
        }
        
        try:
            # Extract domain from URL
            parsed = urlparse(target if target.startswith(('http://', 'https://')) else f"https://{target}")
            hostname = parsed.hostname or target.split('/')[0].split(':')[0]
            port = parsed.port or 443
            
            logger.info(f"SecurityExpertAgent: Analyzing SSL certificate for {hostname}:{port}")
            
            # Create SSL context
            context = ssl.create_default_context()
            
            # Connect and get certificate
            with socket.create_connection((hostname, port), timeout=10) as sock:
                with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                    cert = ssock.getpeercert()
                    cipher = ssock.cipher()
                    
                    ssl_data["valid"] = True
                    ssl_data["cipher"] = f"{cipher[0]} {cipher[1]}"
                    
                    # Parse certificate info
                    if cert:
                        # Get expiration date
                        not_after = cert.get('notAfter')
                        if not_after:
                            try:
                                # Parse date string (format: "Dec 31 23:59:59 2025 GMT")
                                from datetime import datetime
                                expire_date = datetime.strptime(not_after, "%b %d %H:%M:%S %Y %Z")
                                ssl_data["expires"] = expire_date.strftime("%Y-%m-%d")
                                
                                # Check if certificate is expired or expiring soon
                                days_until_expiry = (expire_date - datetime.now()).days
                                if days_until_expiry < 0:
                                    ssl_data["issues"].append("Certificate has expired")
                                elif days_until_expiry < 30:
                                    ssl_data["issues"].append(f"Certificate expires in {days_until_expiry} days")
                            except Exception as e:
                                logger.warning(f"Failed to parse certificate expiration: {e}")
                        
                        # Get issuer
                        issuer = cert.get('issuer')
                        if issuer:
                            try:
                                if isinstance(issuer, tuple):
                                    # Handle tuple of tuples: ((('CN', 'issuer'),),)
                                    issuer_dict = {}
                                    for item in issuer:
                                        if isinstance(item, tuple) and len(item) == 2:
                                            issuer_dict[item[0]] = item[1]
                                        elif isinstance(item, tuple):
                                            # Nested tuple, flatten it
                                            for sub_item in item:
                                                if isinstance(sub_item, tuple) and len(sub_item) == 2:
                                                    issuer_dict[sub_item[0]] = sub_item[1]
                                    ssl_data["issuer"] = issuer_dict.get('CN', issuer_dict.get('commonName', 'Unknown'))
                                else:
                                    ssl_data["issuer"] = str(issuer)
                            except Exception as e:
                                logger.debug(f"Failed to parse issuer: {e}")
                                ssl_data["issuer"] = str(issuer) if issuer else None
                        
                        # Get subject
                        subject = cert.get('subject')
                        if subject:
                            try:
                                if isinstance(subject, tuple):
                                    # Handle tuple of tuples: ((('CN', 'subject'),),)
                                    subject_dict = {}
                                    for item in subject:
                                        if isinstance(item, tuple) and len(item) == 2:
                                            subject_dict[item[0]] = item[1]
                                        elif isinstance(item, tuple):
                                            # Nested tuple, flatten it
                                            for sub_item in item:
                                                if isinstance(sub_item, tuple) and len(sub_item) == 2:
                                                    subject_dict[sub_item[0]] = sub_item[1]
                                    ssl_data["subject"] = subject_dict.get('CN', subject_dict.get('commonName', hostname))
                                else:
                                    ssl_data["subject"] = str(subject)
                            except Exception as e:
                                logger.debug(f"Failed to parse subject: {e}")
                                ssl_data["subject"] = str(subject) if subject else hostname
                    
                    # Get SSL version
                    ssl_data["version"] = ssock.version()
                    
                    logger.info(f"SecurityExpertAgent: SSL analysis completed for {hostname}: valid={ssl_data['valid']}, expires={ssl_data['expires']}")
        
        except socket.timeout:
            ssl_data["issues"].append("Connection timeout")
            logger.warning(f"SecurityExpertAgent: SSL analysis timeout for {target}")
        except ssl.SSLError as e:
            ssl_data["issues"].append(f"SSL error: {str(e)}")
            logger.warning(f"SecurityExpertAgent: SSL error for {target}: {e}")
        except Exception as e:
            ssl_data["issues"].append(f"Certificate analysis failed: {str(e)}")
            logger.error(f"SecurityExpertAgent: SSL analysis failed for {target}: {e}", exc_info=True)
        
        return ssl_data
    
    async def _analyze_security_headers(self, headers: Dict[str, str]) -> Dict[str, Any]:
        """Analyze security headers from HTTP response"""
        security_headers_analysis = {
            "present": [],
            "missing": [],
            "issues": []
        }
        
        # List of important security headers
        important_headers = {
            "X-Frame-Options": "Prevents clickjacking attacks",
            "Content-Security-Policy": "Prevents XSS and injection attacks",
            "Strict-Transport-Security": "Forces HTTPS (HSTS)",
            "X-Content-Type-Options": "Prevents MIME type sniffing",
            "X-XSS-Protection": "Enables XSS filtering",
            "Referrer-Policy": "Controls referrer information",
            "Permissions-Policy": "Controls browser features",
            "X-Permitted-Cross-Domain-Policies": "Controls cross-domain policies"
        }
        
        # Check for present headers
        for header_name, description in important_headers.items():
            # Check case-insensitive
            found = False
            header_value = None
            
            for key, value in headers.items():
                if key.lower() == header_name.lower():
                    found = True
                    header_value = value
                    security_headers_analysis["present"].append(header_name)
                    break
            
            if not found:
                security_headers_analysis["missing"].append(header_name)
            
            # Analyze header values for issues
            if found and header_value:
                if header_name == "X-Frame-Options" and header_value.upper() not in ["DENY", "SAMEORIGIN"]:
                    security_headers_analysis["issues"].append(f"{header_name} has invalid value: {header_value}")
                elif header_name == "Strict-Transport-Security" and "max-age" not in header_value.lower():
                    security_headers_analysis["issues"].append(f"{header_name} missing max-age directive")
                elif header_name == "Content-Security-Policy" and len(header_value) < 10:
                    security_headers_analysis["issues"].append(f"{header_name} appears to be too permissive")
        
        return security_headers_analysis
    
    async def execute(
        self,
        task_id: str,
        target: str,
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute security analysis with enhanced data collection and tools
        Overrides BaseAgent.execute to add comprehensive security analysis
        """
        execution_start = time.time()
        
        try:
            logger.info(f"SecurityExpertAgent: Starting enhanced security analysis for {target}")
            
            # STEP 1: Collect real data using tools
            tool_registry = get_tool_registry()
            web_scraper = tool_registry.get("web_scraper")
            ssl_tool = tool_registry.get("ssl_analyzer")
            
            # Use tools if available, otherwise fallback to methods
            if web_scraper:
                web_result = await web_scraper.execute({"url": target, "extract_metadata": True})
                web_data = web_result.get("result", {}) if web_result.get("success") else {}
            else:
                web_data = await self._perform_real_web_scraping(target)
            
            if ssl_tool:
                # Extract hostname for SSL check
                if "://" in target:
                    parsed = urlparse(target)
                    hostname = parsed.hostname or target.split("://")[1].split("/")[0]
                else:
                    hostname = target.split("/")[0].split(":")[0]
                ssl_result = await ssl_tool.execute({"hostname": hostname, "port": 443})
                ssl_data = ssl_result.get("result", {}) if ssl_result.get("success") else {}
            else:
                ssl_data = await self._analyze_ssl_certificate(target)
            
            security_headers = await self._analyze_security_headers(web_data.get("http_headers", {}))
            
            # STEP 2: Enhanced security checks
            # Port scanning
            port_scan_data = await self._perform_port_scan(target)
            
            # Security headers compliance
            compliance_data = await self._check_security_headers_compliance(web_data.get("http_headers", {}))
            
            # Subdomain enumeration
            if "://" in target:
                parsed = urlparse(target)
                domain = parsed.hostname or target.split("://")[1].split("/")[0]
            else:
                domain = target.split("/")[0].split(":")[0]
            subdomain_data = await self._perform_subdomain_enumeration(domain)
            
            # CVE and dependency checks (if applicable)
            cve_data = {}
            dependency_data = {}
            if parameters.get("check_cves"):
                software = parameters.get("software", target)
                version = parameters.get("version")
                cve_data = await self._check_cve_database(software, version)
            
            if parameters.get("check_dependencies"):
                dependencies = parameters.get("dependencies", {})
                dependency_data = await self._analyze_dependencies(dependencies)
            
            # Security API checks
            security_api_data = {}
            virustotal_tool = tool_registry.get("virustotal")
            shodan_tool = tool_registry.get("shodan")
            abuseipdb_tool = tool_registry.get("abuseipdb")
            
            if virustotal_tool:
                try:
                    vt_result = await virustotal_tool.execute({"resource": target, "resource_type": "url"})
                    if vt_result.get("success"):
                        security_api_data["virustotal"] = vt_result.get("result")
                except Exception as e:
                    logger.debug(f"VirusTotal check failed: {e}")
            
            # Get IP for Shodan/AbuseIPDB
            ip_address = None
            if web_data.get("dns_data", {}).get("a_records"):
                ip_address = web_data["dns_data"]["a_records"][0]
            elif "://" in target:
                try:
                    parsed = urlparse(target)
                    hostname = parsed.hostname or target.split("://")[1].split("/")[0]
                    ip_address = socket.gethostbyname(hostname)
                except Exception:
                    pass
            
            if ip_address:
                if shodan_tool:
                    try:
                        shodan_result = await shodan_tool.execute({"query": ip_address, "query_type": "host"})
                        if shodan_result.get("success"):
                            security_api_data["shodan"] = shodan_result.get("result")
                    except Exception as e:
                        logger.debug(f"Shodan check failed: {e}")
                
                if abuseipdb_tool:
                    try:
                        abuse_result = await abuseipdb_tool.execute({"ip": ip_address})
                        if abuse_result.get("success"):
                            security_api_data["abuseipdb"] = abuse_result.get("result")
                    except Exception as e:
                        logger.debug(f"AbuseIPDB check failed: {e}")
            
            # STEP 3: Prepare enhanced prompt with all collected data
            prompt = await self._prepare_prompt(
                target, parameters, web_data, ssl_data, security_headers,
                port_scan_data, compliance_data, subdomain_data, cve_data,
                dependency_data, security_api_data
            )
            
            # STEP 3: Call AI via router
            logger.info(f"SecurityExpertAgent: Calling AI with real collected data")
            
            ai_response = await self.ai_router.generate_with_fallback(
                prompt=prompt,
                model_preference=self.model_preference,
                max_tokens=4000,
                temperature=0.3,
                system_prompt=self.system_prompt,
                strategy=self.strategy
            )
            
            logger.info(f"SecurityExpertAgent: Got response from {ai_response.provider} "
                       f"({ai_response.tokens_used} tokens, ${ai_response.cost_usd:.4f})")
            
            # STEP 4: Parse response
            parsed_result = await self._parse_response(ai_response.content)
            
            # STEP 5: Merge real data with AI analysis
            if parsed_result.get("success") and parsed_result.get("data"):
                # Enhance AI results with real collected data
                ai_data = parsed_result["data"]
                
                # Merge SSL data
                if ssl_data.get("valid"):
                    if "ssl_analysis" not in ai_data:
                        ai_data["ssl_analysis"] = {}
                    ai_data["ssl_analysis"].update({
                        "valid": ssl_data["valid"],
                        "expires": ssl_data.get("expires"),
                        "issuer": ssl_data.get("issuer"),
                        "version": ssl_data.get("version"),
                        "issues": ssl_data.get("issues", [])
                    })
                
                # Merge security headers data
                if security_headers:
                    if "security_headers" not in ai_data:
                        ai_data["security_headers"] = {}
                    ai_data["security_headers"].update(security_headers)
                
                # Add technology stack from real data
                if web_data.get("technology_indicators"):
                    if "technology_stack" not in ai_data:
                        ai_data["technology_stack"] = {}
                    ai_data["technology_stack"]["detected_indicators"] = web_data["technology_indicators"]
                    if web_data.get("http_headers", {}).get("Server"):
                        ai_data["technology_stack"]["server"] = web_data["http_headers"]["Server"]
                    if web_data.get("http_headers", {}).get("X-Powered-By"):
                        ai_data["technology_stack"]["powered_by"] = web_data["http_headers"]["X-Powered-By"]
            
            execution_duration = time.time() - execution_start
            
            # Update stats
            self.executions += 1
            self.successes += 1
            self.total_duration += execution_duration
            
            # Extract summary from parsed data
            ai_data = parsed_result.get("data", {})
            summary = ai_data.get("summary", "Security analysis completed")
            
            # If summary is a markdown code block, extract the actual summary
            if isinstance(summary, str) and "```json" in summary:
                # Try to extract summary from the JSON inside
                try:
                    json_start = summary.find("{")
                    json_end = summary.rfind("}") + 1
                    if json_start != -1 and json_end > json_start:
                        json_content = summary[json_start:json_end]
                        parsed_summary = json.loads(json_content)
                        summary = parsed_summary.get("summary", summary)
                except Exception:
                    pass
            
            return {
                "success": parsed_result.get("success", True),
                "result": ai_data,
                "output": ai_data,
                "quality_score": self.expertise_score,
                "duration": execution_duration,
                "tokens_used": ai_response.tokens_used,
                "cost_usd": ai_response.cost_usd,
                "provider": ai_response.provider,
                "summary": summary
            }
        
        except Exception as e:
            execution_duration = time.time() - execution_start
            logger.error(f"SecurityExpertAgent: Execution failed: {e}", exc_info=True)
            
            self.executions += 1
            self.total_duration += execution_duration
            
            return {
                "success": False,
                "error": str(e),
                "duration": execution_duration,
                "quality_score": 0.0,
                "tokens_used": 0,
                "cost_usd": 0.0,
                "provider": "none"
            }
    
    async def _prepare_prompt(
        self,
        target: str,
        parameters: Dict[str, Any],
        web_data: Dict[str, Any] = None,
        ssl_data: Dict[str, Any] = None,
        security_headers: Dict[str, Any] = None,
        port_scan_data: Dict[str, Any] = None,
        compliance_data: Dict[str, Any] = None,
        subdomain_data: Dict[str, Any] = None,
        cve_data: Dict[str, Any] = None,
        dependency_data: Dict[str, Any] = None,
        security_api_data: Dict[str, Any] = None
    ) -> str:
        """Prepare enhanced security analysis prompt with all collected data"""
        
        depth = parameters.get("depth", "standard")
        
        # Build context from all collected data
        real_data_context = ""
        
        if web_data:
            real_data_context += f"\n\n=== WEB SCRAPING DATA ===\n"
            real_data_context += f"HTTP Status: {web_data.get('status_code', 'N/A')}\n"
            if web_data.get("technology_indicators"):
                real_data_context += f"Technology Indicators: {', '.join(web_data['technology_indicators'])}\n"
            if web_data.get("error"):
                real_data_context += f"Web Scraping Error: {web_data['error']}\n"
        
        if ssl_data:
            real_data_context += f"\n=== SSL/TLS CERTIFICATE DATA ===\n"
            real_data_context += f"Certificate Valid: {ssl_data.get('valid', False)}\n"
            if ssl_data.get("expires"):
                real_data_context += f"Certificate Expires: {ssl_data['expires']}\n"
            if ssl_data.get("issuer"):
                real_data_context += f"Issuer: {ssl_data['issuer']}\n"
            if ssl_data.get("version"):
                real_data_context += f"SSL Version: {ssl_data['version']}\n"
            if ssl_data.get("issues"):
                real_data_context += f"SSL Issues: {', '.join(ssl_data.get('issues', []))}\n"
        
        if security_headers:
            real_data_context += f"\n=== SECURITY HEADERS DATA ===\n"
            if security_headers.get("present"):
                real_data_context += f"Present Headers: {', '.join(security_headers['present'])}\n"
            if security_headers.get("missing"):
                real_data_context += f"Missing Headers: {', '.join(security_headers['missing'])}\n"
            if security_headers.get("issues"):
                real_data_context += f"Header Issues: {', '.join(security_headers['issues'])}\n"
        
        if port_scan_data:
            real_data_context += f"\n=== PORT SCAN RESULTS ===\n"
            if port_scan_data.get("open_ports"):
                open_ports = [str(p.get("port", "")) for p in port_scan_data["open_ports"]]
                real_data_context += f"Open Ports: {', '.join(open_ports)}\n"
            if port_scan_data.get("error"):
                real_data_context += f"Port Scan Error: {port_scan_data['error']}\n"
        
        if compliance_data:
            real_data_context += f"\n=== SECURITY HEADERS COMPLIANCE ===\n"
            real_data_context += f"OWASP Compliance Score: {compliance_data.get('overall_score', 0.0):.2%}\n"
            if compliance_data.get("missing_headers"):
                missing = [h.get("header", "") for h in compliance_data["missing_headers"]]
                real_data_context += f"Missing Headers: {', '.join(missing)}\n"
            if compliance_data.get("weak_headers"):
                weak = [h.get("header", "") for h in compliance_data["weak_headers"]]
                real_data_context += f"Weak Headers: {', '.join(weak)}\n"
        
        if subdomain_data:
            real_data_context += f"\n=== SUBDOMAIN ENUMERATION ===\n"
            if subdomain_data.get("subdomains_found"):
                subdomains = [s.get("subdomain", "") for s in subdomain_data["subdomains_found"]]
                real_data_context += f"Found Subdomains: {', '.join(subdomains[:10])}\n"  # Limit to 10
            if subdomain_data.get("error"):
                real_data_context += f"Subdomain Enumeration Error: {subdomain_data['error']}\n"
        
        if cve_data:
            real_data_context += f"\n=== CVE DATABASE CHECK ===\n"
            if cve_data.get("cves"):
                real_data_context += f"CVE Check Performed for: {cve_data.get('software', 'N/A')}\n"
            if cve_data.get("error"):
                real_data_context += f"CVE Check Error: {cve_data['error']}\n"
        
        if dependency_data:
            real_data_context += f"\n=== DEPENDENCY VULNERABILITY ANALYSIS ===\n"
            if dependency_data.get("vulnerable_packages"):
                vulnerable = [p.get("name", "") for p in dependency_data["vulnerable_packages"]]
                real_data_context += f"Potentially Vulnerable Packages: {', '.join(vulnerable[:10])}\n"
            if dependency_data.get("error"):
                real_data_context += f"Dependency Analysis Error: {dependency_data['error']}\n"
        
        if security_api_data:
            real_data_context += f"\n=== SECURITY API DATA ===\n"
            if security_api_data.get("virustotal"):
                real_data_context += f"VirusTotal: Check performed\n"
            if security_api_data.get("shodan"):
                real_data_context += f"Shodan: Data retrieved\n"
            if security_api_data.get("abuseipdb"):
                real_data_context += f"AbuseIPDB: Reputation checked\n"
        
        prompt = f"""Perform a comprehensive security analysis of the target: {target}

Analysis Depth: {depth}

{real_data_context}

Based on the REAL DATA collected above, please analyze:
1. SSL/TLS configuration issues (use the real certificate data provided)
2. Security headers analysis (use the real headers data provided)
3. Technology stack vulnerabilities (based on detected technologies)
4. Common vulnerabilities (OWASP Top 10) specific to this target
5. Known CVEs for the detected technology stack
6. Configuration issues based on real findings
7. Potential attack vectors specific to this target

IMPORTANT: Your analysis must be SPECIFIC to this target based on the real data provided above. 
Do not provide generic vulnerabilities - focus on issues relevant to the actual technology stack and configuration detected.

Provide results in the following JSON format:
{{
    "vulnerabilities": [
        {{
            "id": "VULN-001",
            "severity": "Critical|High|Medium|Low",
            "title": "Specific vulnerability title for this target",
            "description": "Detailed description specific to this target",
            "location": "Specific location on this target",
            "cwe": "CWE-XXX",
            "cvss_score": 9.8,
            "remediation": "Concrete fix steps for this specific target"
        }}
    ],
    "ssl_analysis": {{
        "valid": {ssl_data.get('valid', False) if ssl_data else True},
        "expires": "{ssl_data.get('expires', 'N/A') if ssl_data else 'N/A'}",
        "issues": {json.dumps(ssl_data.get('issues', [])) if ssl_data else '[]'}
    }},
    "security_headers": {{
        "present": {json.dumps(security_headers.get('present', [])) if security_headers else '[]'},
        "missing": {json.dumps(security_headers.get('missing', [])) if security_headers else '[]'},
        "issues": {json.dumps(security_headers.get('issues', [])) if security_headers else '[]'}
    }},
    "technology_stack": {{
        "server": "{web_data.get('http_headers', {}).get('Server', 'Unknown') if web_data else 'Unknown'}",
        "powered_by": "{web_data.get('http_headers', {}).get('X-Powered-By', 'Unknown') if web_data else 'Unknown'}",
        "detected_indicators": {json.dumps(web_data.get('technology_indicators', [])) if web_data else '[]'},
        "known_cves": ["CVE references for detected technologies"]
    }},
    "summary": "Overall security assessment specific to this target",
    "risk_rating": "Critical|High|Medium|Low",
    "recommendations": ["Action 1 specific to this target", "Action 2 specific to this target"]
}}"""
        
        return prompt
    
    async def _parse_response(self, response: str) -> Dict[str, Any]:
        """Parse AI response into structured format"""
        
        try:
            # Try to extract JSON from response
            # AI might wrap JSON in markdown code blocks
            json_str = None
            
            # Try different patterns to extract JSON
            if "```json" in response:
                # Extract from ```json ... ```
                parts = response.split("```json")
                if len(parts) > 1:
                    json_str = parts[1].split("```")[0].strip()
            elif "```" in response:
                # Extract from ``` ... ```
                parts = response.split("```")
                if len(parts) >= 3:
                    # Take the first code block content
                    json_str = parts[1].strip()
            else:
                json_str = response.strip()
            
            # Try to find JSON object in the string if it doesn't start with {
            if json_str and not json_str.startswith("{"):
                # Look for first { and last }
                start_idx = json_str.find("{")
                end_idx = json_str.rfind("}")
                if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
                    json_str = json_str[start_idx:end_idx+1]
            
            if json_str:
                # Fix common JSON escape issues
                import re
                # Fix invalid escape sequences (like \' or \. or \:)
                # Only allow valid JSON escape sequences: \", \\, \/, \b, \f, \n, \r, \t, \uXXXX
                # Replace invalid escapes with escaped backslash + character
                def fix_escape(match):
                    char = match.group(1)
                    # Valid escapes: n, r, t, b, f, u, ", \, /
                    if char in ['n', 'r', 't', 'b', 'f', 'u', '"', '\\', '/']:
                        return match.group(0)  # Keep valid escapes
                    # Invalid escape - escape the backslash
                    return '\\\\' + char
                
                # Fix invalid escape sequences (but preserve valid ones)
                json_str = re.sub(r'\\([^nrtbfu"\\/])', fix_escape, json_str)
                
                # Also fix unicode escapes that might be malformed
                # Try to parse, if it fails, try more aggressive fixes
                try:
                    parsed = json.loads(json_str)
                except json.JSONDecodeError as parse_err:
                    # If still fails, try to fix more aggressively
                    logger.debug(f"First parse attempt failed: {parse_err}, trying aggressive fix")
                    # Remove comments (JSON doesn't support comments)
                    json_str = re.sub(r'//.*?$', '', json_str, flags=re.MULTILINE)
                    json_str = re.sub(r'/\*.*?\*/', '', json_str, flags=re.DOTALL)
                    # Fix trailing commas
                    json_str = re.sub(r',\s*}', '}', json_str)
                    json_str = re.sub(r',\s*]', ']', json_str)
                    # Try again
                    parsed = json.loads(json_str)
                
                # Ensure parsed is a dict
                if isinstance(parsed, dict):
                    return {
                        "success": True,
                        "data": parsed,
                        "raw_response": response
                    }
                else:
                    # If parsed is not a dict, wrap it
                    return {
                        "success": True,
                        "data": {"result": parsed, "summary": str(parsed)},
                        "raw_response": response
                    }
            else:
                raise ValueError("No JSON found in response")
        
        except (json.JSONDecodeError, ValueError) as e:
            # If JSON parsing fails, try to extract structured data from text
            logger.warning(f"Failed to parse JSON response: {e}, attempting text extraction")
            
            # Try to extract key information from text response
            extracted_data = {
                "vulnerabilities": [],
                "summary": response[:500] + "..." if len(response) > 500 else response,
                "parsing_error": True,
                "raw_response": response
            }
            
            # Try to find vulnerabilities mentioned in text
            if "vulnerability" in response.lower() or "vuln" in response.lower():
                extracted_data["summary"] = "Vulnerabilities detected (see raw_response for details)"
            
            return {
                "success": True,
                "data": extracted_data,
                "raw_response": response
            }

