"""
Intelligence Gathering Agent - Specialized agent for OSINT and intelligence gathering
Implements PART_3 requirements
"""

import json
import logging
import socket
import time
from typing import Any, Dict
from urllib.parse import urlparse

import aiohttp

try:
    import whois
    WHOIS_AVAILABLE = True
except ImportError:
    WHOIS_AVAILABLE = False

from src.amas.agents.base_agent import BaseAgent

logger = logging.getLogger(__name__)

if not WHOIS_AVAILABLE:
    logger.warning("python-whois not available, WHOIS lookups will be skipped")


class IntelligenceGatheringAgent(BaseAgent):
    """
    Intelligence Gathering Agent
    
    Specializes in:
    - Open Source Intelligence (OSINT) collection
    - Social media monitoring and analysis
    - Domain and IP investigation
    - Email and identity verification
    - Threat intelligence gathering
    - Dark web monitoring
    - News and information aggregation
    """
    
    def __init__(self):
        super().__init__(
            agent_id="intelligence_gathering",
            name="Intelligence Gathering Agent",
            agent_type="intelligence",
            system_prompt="""You are an elite intelligence gathering specialist with 15+ years of experience 
            in Open Source Intelligence (OSINT), threat intelligence, and information gathering.
            
            Your expertise includes:
            • OSINT collection from public sources
            • Social media monitoring and analysis
            • Domain and IP investigation (WHOIS, DNS, historical data)
            • Email and identity verification
            • Threat intelligence gathering from multiple sources
            • Dark web monitoring (when legally authorized)
            • News and information aggregation
            • Digital footprint analysis
            • Company and organization research
            • Technology stack identification
            
            When analyzing a target, you:
            1. Collect comprehensive open-source intelligence from multiple sources
            2. Analyze social media presence, activity patterns, and connections
            3. Investigate domain/IP ownership, history, and associated services
            4. Gather threat intelligence from security feeds and databases
            5. Verify email addresses and identities
            6. Identify technology stacks and infrastructure
            7. Map digital footprint and online presence
            8. Provide detailed intelligence reports with source attribution
            9. Identify potential security risks and threats
            10. Suggest actionable intelligence-based recommendations
            
            Always provide:
            - Source attribution for all information
            - Confidence levels for findings
            - Timestamps and data freshness indicators
            - Actionable recommendations based on intelligence
            
            Follow legal and ethical guidelines for intelligence gathering.""",
            tools=[],  # Tools can be added here
            model_preference="gpt-4-turbo-preview",
            strategy="quality_first"
        )
        
        self.expertise_score = 0.95  # High expertise
    
    async def _perform_dns_lookup(self, domain: str) -> Dict[str, Any]:
        """Perform real DNS lookup for domain"""
        dns_data = {
            "domain": domain,
            "a_records": [],
            "aaaa_records": [],
            "mx_records": [],
            "ns_records": [],
            "txt_records": [],
            "cname_records": [],
            "error": None
        }
        
        try:
            logger.info(f"IntelligenceGatheringAgent: Performing DNS lookup for {domain}")
            
            # A records (IPv4)
            try:
                a_records = socket.gethostbyname_ex(domain)
                if a_records:
                    dns_data["a_records"] = list(a_records[2]) if len(a_records) > 2 else []
            except socket.gaierror as e:
                logger.debug(f"DNS A record lookup failed for {domain}: {e}")
            
            # MX records
            try:
                import dns.resolver
                mx_records = dns.resolver.resolve(domain, 'MX')
                dns_data["mx_records"] = [str(mx.exchange) for mx in mx_records]
            except ImportError:
                logger.debug("dnspython not available, skipping MX records")
            except Exception as e:
                logger.debug(f"DNS MX record lookup failed for {domain}: {e}")
            
            # NS records
            try:
                import dns.resolver
                ns_records = dns.resolver.resolve(domain, 'NS')
                dns_data["ns_records"] = [str(ns) for ns in ns_records]
            except ImportError:
                logger.debug("dnspython not available, skipping NS records")
            except Exception as e:
                logger.debug(f"DNS NS record lookup failed for {domain}: {e}")
            
            # TXT records
            try:
                import dns.resolver
                txt_records = dns.resolver.resolve(domain, 'TXT')
                dns_data["txt_records"] = [str(txt).strip('"') for txt in txt_records]
            except ImportError:
                logger.debug("dnspython not available, skipping TXT records")
            except Exception as e:
                logger.debug(f"DNS TXT record lookup failed for {domain}: {e}")
            
            logger.info(f"IntelligenceGatheringAgent: DNS lookup completed for {domain}: A={len(dns_data['a_records'])}, MX={len(dns_data['mx_records'])}")
        
        except Exception as e:
            dns_data["error"] = f"DNS lookup failed: {str(e)}"
            logger.error(f"IntelligenceGatheringAgent: DNS lookup failed for {domain}: {e}", exc_info=True)
        
        return dns_data
    
    async def _perform_whois_lookup(self, domain: str) -> Dict[str, Any]:
        """Perform WHOIS lookup for domain"""
        whois_data = {
            "domain": domain,
            "registrar": None,
            "creation_date": None,
            "expiration_date": None,
            "last_updated": None,
            "name_servers": [],
            "emails": [],
            "org": None,
            "status": None,
            "error": None
        }
        
        if not WHOIS_AVAILABLE:
            whois_data["error"] = "python-whois library not available"
            return whois_data
        
        try:
            logger.info(f"IntelligenceGatheringAgent: Performing WHOIS lookup for {domain}")
            
            w = whois.whois(domain)
            
            if w:
                whois_data["registrar"] = w.registrar
                whois_data["org"] = w.org
                whois_data["status"] = w.status
                
                # Handle dates (can be list or single value)
                if w.creation_date:
                    if isinstance(w.creation_date, list):
                        whois_data["creation_date"] = str(w.creation_date[0]) if w.creation_date else None
                    else:
                        whois_data["creation_date"] = str(w.creation_date)
                
                if w.expiration_date:
                    if isinstance(w.expiration_date, list):
                        whois_data["expiration_date"] = str(w.expiration_date[0]) if w.expiration_date else None
                    else:
                        whois_data["expiration_date"] = str(w.expiration_date)
                
                if w.updated_date:
                    if isinstance(w.updated_date, list):
                        whois_data["last_updated"] = str(w.updated_date[0]) if w.updated_date else None
                    else:
                        whois_data["last_updated"] = str(w.updated_date)
                
                # Handle name servers
                if w.name_servers:
                    if isinstance(w.name_servers, list):
                        whois_data["name_servers"] = [str(ns) for ns in w.name_servers]
                    else:
                        whois_data["name_servers"] = [str(w.name_servers)]
                
                # Handle emails
                if w.emails:
                    if isinstance(w.emails, list):
                        whois_data["emails"] = [str(email) for email in w.emails]
                    else:
                        whois_data["emails"] = [str(w.emails)]
                
                logger.info(f"IntelligenceGatheringAgent: WHOIS lookup completed for {domain}: registrar={whois_data.get('registrar')}")
            else:
                whois_data["error"] = "No WHOIS data returned"
        
        except Exception as e:
            whois_data["error"] = f"WHOIS lookup failed: {str(e)}"
            logger.warning(f"IntelligenceGatheringAgent: WHOIS lookup failed for {domain}: {e}")
        
        return whois_data
    
    async def _perform_ip_geolocation(self, ip: str) -> Dict[str, Any]:
        """Perform IP geolocation lookup"""
        geo_data = {
            "ip": ip,
            "country": None,
            "city": None,
            "region": None,
            "isp": None,
            "error": None
        }
        
        try:
            logger.info(f"IntelligenceGatheringAgent: Performing IP geolocation for {ip}")
            
            # Use ipapi.co (free tier, no API key required)
            async with aiohttp.ClientSession() as session:
                try:
                    async with session.get(f"https://ipapi.co/{ip}/json/", timeout=aiohttp.ClientTimeout(total=10)) as response:
                        if response.status == 200:
                            data = await response.json()
                            geo_data.update({
                                "country": data.get("country_name"),
                                "city": data.get("city"),
                                "region": data.get("region"),
                                "isp": data.get("org"),
                                "latitude": data.get("latitude"),
                                "longitude": data.get("longitude"),
                                "timezone": data.get("timezone")
                            })
                            logger.info(f"IntelligenceGatheringAgent: IP geolocation completed for {ip}: {geo_data.get('city')}, {geo_data.get('country')}")
                        else:
                            geo_data["error"] = f"Geolocation API returned status {response.status}"
                except aiohttp.ClientError as e:
                    geo_data["error"] = f"Geolocation API error: {str(e)}"
                    logger.warning(f"IntelligenceGatheringAgent: IP geolocation failed for {ip}: {e}")
        
        except Exception as e:
            geo_data["error"] = f"IP geolocation failed: {str(e)}"
            logger.error(f"IntelligenceGatheringAgent: IP geolocation failed for {ip}: {e}", exc_info=True)
        
        return geo_data
    
    async def _extract_domain_from_target(self, target: str) -> str:
        """Extract domain from target URL or return as-is if already a domain"""
        try:
            if target.startswith(('http://', 'https://')):
                parsed = urlparse(target)
                return parsed.hostname or target
            else:
                # Assume it's already a domain
                return target.split('/')[0].split(':')[0]
        except Exception:
            return target
    
    async def execute(
        self,
        task_id: str,
        target: str,
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute intelligence gathering with real data collection
        Overrides BaseAgent.execute to add real data collection
        """
        execution_start = time.time()
        
        try:
            logger.info(f"IntelligenceGatheringAgent: Starting real data collection for {target}")
            
            # Extract domain from target
            domain = await self._extract_domain_from_target(target)
            
            # STEP 1: Collect real data
            dns_data = await self._perform_dns_lookup(domain)
            whois_data = await self._perform_whois_lookup(domain)
            
            # Get IP from DNS if available
            ip_address = None
            if dns_data.get("a_records"):
                ip_address = dns_data["a_records"][0]
            
            # Perform IP geolocation if we have an IP
            geo_data = None
            if ip_address:
                geo_data = await self._perform_ip_geolocation(ip_address)
            
            # STEP 2: Prepare prompt with real data
            prompt = await self._prepare_prompt(target, parameters, dns_data, whois_data, geo_data)
            
            # STEP 3: Call AI via router
            logger.info(f"IntelligenceGatheringAgent: Calling AI with real collected data")
            
            ai_response = await self.ai_router.generate_with_fallback(
                prompt=prompt,
                model_preference=self.model_preference,
                max_tokens=4000,
                temperature=0.3,
                system_prompt=self.system_prompt,
                strategy=self.strategy
            )
            
            logger.info(f"IntelligenceGatheringAgent: Got response from {ai_response.provider} "
                       f"({ai_response.tokens_used} tokens, ${ai_response.cost_usd:.4f})")
            
            # STEP 4: Parse response
            parsed_result = await self._parse_response(ai_response.content)
            
            # STEP 5: Merge real data with AI analysis
            if parsed_result.get("success"):
                intelligence_report = parsed_result.get("intelligence_report", {})
                
                # Add real DNS data
                if dns_data:
                    if "dns_information" not in intelligence_report:
                        intelligence_report["dns_information"] = {}
                    intelligence_report["dns_information"].update({
                        "a_records": dns_data.get("a_records", []),
                        "mx_records": dns_data.get("mx_records", []),
                        "ns_records": dns_data.get("ns_records", []),
                        "txt_records": dns_data.get("txt_records", [])
                    })
                
                # Add real WHOIS data
                if whois_data and not whois_data.get("error"):
                    if "whois_information" not in intelligence_report:
                        intelligence_report["whois_information"] = {}
                    intelligence_report["whois_information"].update({
                        "registrar": whois_data.get("registrar"),
                        "creation_date": whois_data.get("creation_date"),
                        "expiration_date": whois_data.get("expiration_date"),
                        "last_updated": whois_data.get("last_updated"),
                        "name_servers": whois_data.get("name_servers", []),
                        "org": whois_data.get("org"),
                        "status": whois_data.get("status")
                    })
                
                # Add real geolocation data
                if geo_data:
                    if "geolocation" not in intelligence_report:
                        intelligence_report["geolocation"] = {}
                    intelligence_report["geolocation"].update({
                        "country": geo_data.get("country"),
                        "city": geo_data.get("city"),
                        "region": geo_data.get("region"),
                        "isp": geo_data.get("isp"),
                        "ip": geo_data.get("ip")
                    })
            
            execution_duration = time.time() - execution_start
            
            # Update stats
            self.executions += 1
            self.successes += 1
            self.total_duration += execution_duration
            
            return {
                "success": parsed_result.get("success", True),
                "result": parsed_result.get("intelligence_report", {}),
                "output": parsed_result.get("intelligence_report", {}),
                "quality_score": self.expertise_score,
                "duration": execution_duration,
                "tokens_used": ai_response.tokens_used,
                "cost_usd": ai_response.cost_usd,
                "provider": ai_response.provider,
                "summary": parsed_result.get("summary", "Intelligence gathering completed")
            }
        
        except Exception as e:
            execution_duration = time.time() - execution_start
            logger.error(f"IntelligenceGatheringAgent: Execution failed: {e}", exc_info=True)
            
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
        dns_data: Dict[str, Any] = None,
        whois_data: Dict[str, Any] = None,
        geo_data: Dict[str, Any] = None
    ) -> str:
        """Prepare intelligence gathering prompt with real collected data"""
        
        depth = parameters.get("depth", "standard")
        focus_areas = parameters.get("focus_areas", [])
        
        # Build context from real collected data
        real_data_context = ""
        
        if dns_data:
            real_data_context += f"\n\n=== REAL DNS DATA ===\n"
            real_data_context += f"Domain: {dns_data.get('domain', target)}\n"
            if dns_data.get("a_records"):
                real_data_context += f"IP Addresses (A records): {', '.join(dns_data['a_records'])}\n"
            if dns_data.get("mx_records"):
                real_data_context += f"Mail Servers (MX): {', '.join(dns_data['mx_records'])}\n"
            if dns_data.get("ns_records"):
                real_data_context += f"Name Servers (NS): {', '.join(dns_data['ns_records'])}\n"
            if dns_data.get("txt_records"):
                real_data_context += f"TXT Records: {', '.join(dns_data['txt_records'][:3])}...\n"
            if dns_data.get("error"):
                real_data_context += f"DNS Error: {dns_data['error']}\n"
        
        if whois_data and not whois_data.get("error"):
            real_data_context += f"\n=== REAL WHOIS DATA ===\n"
            real_data_context += f"Domain: {whois_data.get('domain', target)}\n"
            if whois_data.get("registrar"):
                real_data_context += f"Registrar: {whois_data['registrar']}\n"
            if whois_data.get("creation_date"):
                real_data_context += f"Creation Date: {whois_data['creation_date']}\n"
            if whois_data.get("expiration_date"):
                real_data_context += f"Expiration Date: {whois_data['expiration_date']}\n"
            if whois_data.get("last_updated"):
                real_data_context += f"Last Updated: {whois_data['last_updated']}\n"
            if whois_data.get("org"):
                real_data_context += f"Organization: {whois_data['org']}\n"
            if whois_data.get("name_servers"):
                real_data_context += f"Name Servers: {', '.join(whois_data['name_servers'][:5])}\n"
            if whois_data.get("status"):
                real_data_context += f"Status: {whois_data['status']}\n"
        
        if geo_data:
            real_data_context += f"\n=== REAL IP GEOLOCATION DATA ===\n"
            real_data_context += f"IP Address: {geo_data.get('ip', 'N/A')}\n"
            if geo_data.get("country"):
                real_data_context += f"Country: {geo_data['country']}\n"
            if geo_data.get("city"):
                real_data_context += f"City: {geo_data['city']}\n"
            if geo_data.get("region"):
                real_data_context += f"Region: {geo_data['region']}\n"
            if geo_data.get("isp"):
                real_data_context += f"ISP: {geo_data['isp']}\n"
            if geo_data.get("error"):
                real_data_context += f"Geolocation Error: {geo_data['error']}\n"
        
        prompt = f"""Perform comprehensive intelligence gathering on the target: {target}

Analysis Depth: {depth}

Focus Areas: {', '.join(focus_areas) if focus_areas else 'Comprehensive analysis'}

{real_data_context}

Based on the REAL DATA collected above, please gather intelligence on:
1. Domain/IP Information:
   - Use the real DNS records provided above
   - Analyze the IP geolocation data provided
   - Investigate associated domains and services based on real DNS data
   - Identify subdomains and related infrastructure

2. Social Media Presence:
   - Platform presence (Twitter, LinkedIn, Facebook, etc.)
   - Activity patterns and posting frequency
   - Connections and network analysis
   - Public posts and content analysis

3. Digital Footprint:
   - Email addresses and verification
   - Online accounts and profiles
   - Technology stack identification
   - Public code repositories (GitHub, GitLab, etc.)

4. Threat Intelligence:
   - Known security incidents or breaches
   - Malware associations
   - Phishing and scam reports
   - Security reputation scores

5. Company/Organization Intelligence:
   - Business registration and legal status
   - Key personnel and leadership
   - Financial information (if public)
   - Partnerships and relationships

6. News and Media Coverage:
   - Recent news articles
   - Press releases
   - Media mentions
   - Industry reports

IMPORTANT: Your analysis must be SPECIFIC to this target based on the real DNS, WHOIS, and geolocation data provided above.
Use the actual IP addresses, mail servers, registrar information, domain registration dates, and location information to provide accurate intelligence.

Provide a comprehensive intelligence report with:
- All findings with source attribution
- Confidence levels for each finding
- Timestamps and data freshness
- Identified risks and threats
- Actionable recommendations
- Next steps for deeper investigation if needed

Format the response as structured JSON with clear sections."""

        return prompt
    
    async def _parse_response(self, response: str) -> Dict[str, Any]:
        """Parse intelligence gathering response"""
        
        try:
            # Try to parse as JSON first
            if response.strip().startswith('{'):
                parsed = json.loads(response)
                return {
                    "success": True,
                    "intelligence_report": parsed,
                    "summary": parsed.get("summary", "Intelligence gathering completed"),
                    "findings": parsed.get("findings", []),
                    "threats": parsed.get("threats", []),
                    "recommendations": parsed.get("recommendations", [])
                }
        except json.JSONDecodeError:
            pass
        
        # If not JSON, parse as structured text
        return {
            "success": True,
            "intelligence_report": {
                "raw_response": response,
                "summary": response[:500] + "..." if len(response) > 500 else response
            },
            "summary": "Intelligence gathering completed",
            "findings": [],
            "threats": [],
            "recommendations": []
        }


