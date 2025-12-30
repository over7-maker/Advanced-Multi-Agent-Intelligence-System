"""
DNS Lookup Tool
Tool for performing DNS lookups (A, MX, NS, TXT records)
"""

import logging
import socket
from typing import Any, Dict, List

from . import AgentTool

logger = logging.getLogger(__name__)

# Try to import dnspython for advanced DNS queries
try:
    import dns.resolver
    DNS_PYTHON_AVAILABLE = True
except ImportError:
    DNS_PYTHON_AVAILABLE = False
    logger.warning("dnspython not available, some DNS record types will be skipped")


class DNSLookupTool(AgentTool):
    """Tool for DNS lookups"""
    
    def __init__(self):
        super().__init__(
            name="dns_lookup",
            description="Perform DNS lookups for A, MX, NS, TXT, and other record types"
        )
        self.category = "data_collection"
    
    def get_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "domain": {
                    "type": "string",
                    "description": "Domain name to lookup"
                },
                "record_types": {
                    "type": "array",
                    "items": {
                        "type": "string",
                        "enum": ["A", "AAAA", "MX", "NS", "TXT", "CNAME", "SOA"]
                    },
                    "description": "DNS record types to query",
                    "default": ["A", "MX"]
                }
            },
            "required": ["domain"]
        }
    
    def validate_params(self, params: Dict[str, Any]) -> bool:
        if "domain" not in params:
            return False
        domain = params["domain"]
        if not isinstance(domain, str) or not domain:
            return False
        # Remove protocol if present
        if "://" in domain:
            domain = domain.split("://")[1]
        if "/" in domain:
            domain = domain.split("/")[0]
        params["domain"] = domain.strip()
        return True
    
    async def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute DNS lookup"""
        try:
            if not self.validate_params(params):
                return {
                    "success": False,
                    "error": "Invalid parameters: domain is required"
                }
            
            domain = params["domain"]
            record_types = params.get("record_types", ["A", "MX"])
            
            logger.info(f"DNSLookupTool: Looking up {domain} for records: {record_types}")
            
            result = {
                "domain": domain,
                "a_records": [],
                "aaaa_records": [],
                "mx_records": [],
                "ns_records": [],
                "txt_records": [],
                "cname_records": [],
                "soa_records": [],
                "error": None
            }
            
            # A records (IPv4) - using socket
            if "A" in record_types:
                try:
                    a_records = socket.gethostbyname_ex(domain)
                    if a_records and len(a_records) > 2:
                        result["a_records"] = list(a_records[2])
                except socket.gaierror as e:
                    logger.debug(f"DNSLookupTool: A record lookup failed for {domain}: {e}")
                    result["error"] = f"A record lookup failed: {str(e)}"
            
            # Advanced record types require dnspython
            if DNS_PYTHON_AVAILABLE:
                # MX records
                if "MX" in record_types:
                    try:
                        mx_records = dns.resolver.resolve(domain, 'MX')
                        result["mx_records"] = [
                            {
                                "priority": mx.preference,
                                "exchange": str(mx.exchange)
                            }
                            for mx in mx_records
                        ]
                    except Exception as e:
                        logger.debug(f"DNSLookupTool: MX record lookup failed for {domain}: {e}")
                
                # NS records
                if "NS" in record_types:
                    try:
                        ns_records = dns.resolver.resolve(domain, 'NS')
                        result["ns_records"] = [str(ns) for ns in ns_records]
                    except Exception as e:
                        logger.debug(f"DNSLookupTool: NS record lookup failed for {domain}: {e}")
                
                # TXT records
                if "TXT" in record_types:
                    try:
                        txt_records = dns.resolver.resolve(domain, 'TXT')
                        result["txt_records"] = [
                            str(txt).strip('"') for txt in txt_records
                        ]
                    except Exception as e:
                        logger.debug(f"DNSLookupTool: TXT record lookup failed for {domain}: {e}")
                
                # CNAME records
                if "CNAME" in record_types:
                    try:
                        cname_records = dns.resolver.resolve(domain, 'CNAME')
                        result["cname_records"] = [str(cname) for cname in cname_records]
                    except Exception as e:
                        logger.debug(f"DNSLookupTool: CNAME record lookup failed for {domain}: {e}")
                
                # SOA records
                if "SOA" in record_types:
                    try:
                        soa_records = dns.resolver.resolve(domain, 'SOA')
                        result["soa_records"] = [
                            {
                                "mname": str(soa.mname),
                                "rname": str(soa.rname),
                                "serial": soa.serial,
                                "refresh": soa.refresh,
                                "retry": soa.retry,
                                "expire": soa.expire,
                                "minimum": soa.minimum
                            }
                            for soa in soa_records
                        ]
                    except Exception as e:
                        logger.debug(f"DNSLookupTool: SOA record lookup failed for {domain}: {e}")
            else:
                logger.warning(f"DNSLookupTool: dnspython not available, skipping advanced record types for {domain}")
            
            logger.info(f"DNSLookupTool: DNS lookup completed for {domain}: "
                       f"A={len(result['a_records'])}, MX={len(result['mx_records'])}, "
                       f"NS={len(result['ns_records'])}, TXT={len(result['txt_records'])}")
            
            return {
                "success": True,
                "result": result,
                "metadata": {
                    "domain": domain,
                    "record_types_queried": record_types,
                    "dnspython_available": DNS_PYTHON_AVAILABLE
                }
            }
        
        except Exception as e:
            logger.error(f"DNSLookupTool: Failed to lookup {params.get('domain', 'unknown')}: {e}", exc_info=True)
            return {
                "success": False,
                "error": f"DNS lookup failed: {str(e)}"
            }

