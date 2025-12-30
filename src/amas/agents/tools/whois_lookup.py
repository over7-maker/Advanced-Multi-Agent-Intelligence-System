"""
WHOIS Lookup Tool
Tool for performing WHOIS lookups
"""

import logging
from typing import Any, Dict
from datetime import datetime

from . import AgentTool

logger = logging.getLogger(__name__)

# Try to import python-whois
try:
    import whois
    WHOIS_AVAILABLE = True
except ImportError:
    WHOIS_AVAILABLE = False
    logger.warning("python-whois not available, WHOIS lookups will be skipped")


class WHOISLookupTool(AgentTool):
    """Tool for WHOIS lookups"""
    
    def __init__(self):
        super().__init__(
            name="whois_lookup",
            description="Perform WHOIS lookups for domain registration information"
        )
        self.category = "data_collection"
    
    def get_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "domain": {
                    "type": "string",
                    "description": "Domain name to lookup"
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
        """Execute WHOIS lookup"""
        try:
            if not self.validate_params(params):
                return {
                    "success": False,
                    "error": "Invalid parameters: domain is required"
                }
            
            domain = params["domain"]
            
            logger.info(f"WHOISLookupTool: Looking up {domain}")
            
            result = {
                "domain": domain,
                "registrar": None,
                "creation_date": None,
                "expiration_date": None,
                "last_updated": None,
                "name_servers": [],
                "org": None,
                "status": None,
                "error": None
            }
            
            if not WHOIS_AVAILABLE:
                return {
                    "success": False,
                    "error": "python-whois library not available",
                    "result": result
                }
            
            try:
                # Perform WHOIS lookup
                w = whois.whois(domain)
                
                if w:
                    result["registrar"] = w.registrar
                    
                    # Handle dates (can be list or single value)
                    if w.creation_date:
                        if isinstance(w.creation_date, list):
                            result["creation_date"] = w.creation_date[0].isoformat() if w.creation_date else None
                        else:
                            result["creation_date"] = w.creation_date.isoformat() if hasattr(w.creation_date, 'isoformat') else str(w.creation_date)
                    
                    if w.expiration_date:
                        if isinstance(w.expiration_date, list):
                            result["expiration_date"] = w.expiration_date[0].isoformat() if w.expiration_date else None
                        else:
                            result["expiration_date"] = w.expiration_date.isoformat() if hasattr(w.expiration_date, 'isoformat') else str(w.expiration_date)
                    
                    if w.updated_date:
                        if isinstance(w.updated_date, list):
                            result["last_updated"] = w.updated_date[0].isoformat() if w.updated_date else None
                        else:
                            result["last_updated"] = w.updated_date.isoformat() if hasattr(w.updated_date, 'isoformat') else str(w.updated_date)
                    
                    # Name servers
                    if w.name_servers:
                        if isinstance(w.name_servers, list):
                            result["name_servers"] = [str(ns).lower() for ns in w.name_servers]
                        else:
                            result["name_servers"] = [str(w.name_servers).lower()]
                    
                    result["org"] = w.org
                    result["status"] = w.status
                    
                    logger.info(f"WHOISLookupTool: Successfully looked up {domain}")
                    
                    return {
                        "success": True,
                        "result": result,
                        "metadata": {
                            "domain": domain,
                            "has_registration_data": bool(w.registrar)
                        }
                    }
                else:
                    return {
                        "success": False,
                        "error": "No WHOIS data found",
                        "result": result
                    }
            
            except Exception as e:
                logger.warning(f"WHOISLookupTool: WHOIS lookup failed for {domain}: {e}")
                result["error"] = str(e)
                return {
                    "success": False,
                    "error": f"WHOIS lookup failed: {str(e)}",
                    "result": result
                }
        
        except Exception as e:
            logger.error(f"WHOISLookupTool: Failed to lookup {params.get('domain', 'unknown')}: {e}", exc_info=True)
            return {
                "success": False,
                "error": f"WHOIS lookup failed: {str(e)}"
            }

