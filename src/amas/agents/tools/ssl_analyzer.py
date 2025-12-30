"""
SSL Analyzer Tool
Tool for analyzing SSL/TLS certificates
"""

import logging
import ssl
import socket
from typing import Any, Dict
from datetime import datetime

from . import AgentTool

logger = logging.getLogger(__name__)


class SSLAnalyzerTool(AgentTool):
    """Tool for SSL/TLS certificate analysis"""
    
    def __init__(self):
        super().__init__(
            name="ssl_analyzer",
            description="Analyze SSL/TLS certificates for validity, expiration, and security"
        )
        self.category = "data_collection"
    
    def get_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "hostname": {
                    "type": "string",
                    "description": "Hostname to analyze"
                },
                "port": {
                    "type": "integer",
                    "description": "Port number",
                    "default": 443
                }
            },
            "required": ["hostname"]
        }
    
    def validate_params(self, params: Dict[str, Any]) -> bool:
        if "hostname" not in params:
            return False
        hostname = params["hostname"]
        if not isinstance(hostname, str) or not hostname:
            return False
        # Remove protocol if present
        if "://" in hostname:
            hostname = hostname.split("://")[1]
        if "/" in hostname:
            hostname = hostname.split("/")[0]
        params["hostname"] = hostname.strip()
        return True
    
    async def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute SSL certificate analysis"""
        try:
            if not self.validate_params(params):
                return {
                    "success": False,
                    "error": "Invalid parameters: hostname is required"
                }
            
            hostname = params["hostname"]
            port = params.get("port", 443)
            
            logger.info(f"SSLAnalyzerTool: Analyzing SSL certificate for {hostname}:{port}")
            
            result = {
                "hostname": hostname,
                "port": port,
                "valid": False,
                "expires": None,
                "issuer": None,
                "subject": None,
                "version": None,
                "serial_number": None,
                "fingerprint": None,
                "issues": [],
                "error": None
            }
            
            try:
                # Create SSL context
                context = ssl.create_default_context()
                
                # Connect and get certificate
                with socket.create_connection((hostname, port), timeout=10) as sock:
                    with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                        cert = ssock.getpeercert()
                        
                        if cert:
                            result["valid"] = True
                            
                            # Extract certificate information
                            result["issuer"] = dict(x[0] for x in cert.get('issuer', []))
                            result["subject"] = dict(x[0] for x in cert.get('subject', []))
                            result["version"] = cert.get('version')
                            result["serial_number"] = cert.get('serialNumber')
                            
                            # Expiration date
                            not_after = cert.get('notAfter')
                            if not_after:
                                try:
                                    # Parse date string
                                    from datetime import datetime
                                    expires = datetime.strptime(not_after, '%b %d %H:%M:%S %Y %Z')
                                    result["expires"] = expires.isoformat()
                                    
                                    # Check if expired or expiring soon
                                    now = datetime.now()
                                    days_until_expiry = (expires - now).days
                                    
                                    if days_until_expiry < 0:
                                        result["issues"].append("Certificate has expired")
                                    elif days_until_expiry < 30:
                                        result["issues"].append(f"Certificate expires in {days_until_expiry} days")
                                    
                                except Exception as e:
                                    logger.debug(f"SSLAnalyzerTool: Failed to parse expiration date: {e}")
                                    result["expires"] = not_after
                            
                            # Certificate fingerprint
                            cert_der = ssock.getpeercert(binary_form=True)
                            if cert_der:
                                import hashlib
                                fingerprint = hashlib.sha256(cert_der).hexdigest()
                                result["fingerprint"] = fingerprint
                            
                            # Check for common issues
                            # Check certificate chain
                            try:
                                cert_chain = ssock.getpeercert_chain()
                                if not cert_chain or len(cert_chain) < 2:
                                    result["issues"].append("Certificate chain may be incomplete")
                            except Exception:
                                pass
                            
                            # Check TLS version
                            try:
                                protocol = ssock.version()
                                if protocol:
                                    result["version"] = protocol
                                    # Check for weak protocols
                                    if protocol in ['TLSv1', 'TLSv1.1']:
                                        result["issues"].append(f"Weak TLS version: {protocol}")
                            except Exception:
                                pass
                            
                            logger.info(f"SSLAnalyzerTool: Successfully analyzed certificate for {hostname}:{port}, valid={result['valid']}")
                            
                            return {
                                "success": True,
                                "result": result,
                                "metadata": {
                                    "hostname": hostname,
                                    "port": port,
                                    "certificate_valid": result["valid"]
                                }
                            }
                        else:
                            return {
                                "success": False,
                                "error": "No certificate found",
                                "result": result
                            }
            
            except socket.timeout:
                error_msg = f"Connection timeout to {hostname}:{port}"
                logger.warning(f"SSLAnalyzerTool: {error_msg}")
                result["error"] = error_msg
                return {
                    "success": False,
                    "error": error_msg,
                    "result": result
                }
            except ssl.SSLError as e:
                error_msg = f"SSL error: {str(e)}"
                logger.warning(f"SSLAnalyzerTool: {error_msg}")
                result["error"] = error_msg
                result["issues"].append(error_msg)
                return {
                    "success": False,
                    "error": error_msg,
                    "result": result
                }
            except Exception as e:
                error_msg = f"Connection error: {str(e)}"
                logger.warning(f"SSLAnalyzerTool: {error_msg}")
                result["error"] = error_msg
                return {
                    "success": False,
                    "error": error_msg,
                    "result": result
                }
        
        except Exception as e:
            logger.error(f"SSLAnalyzerTool: Failed to analyze {params.get('hostname', 'unknown')}: {e}", exc_info=True)
            return {
                "success": False,
                "error": f"SSL analysis failed: {str(e)}"
            }

