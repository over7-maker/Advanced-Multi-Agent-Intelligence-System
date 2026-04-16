"""
Network Scanner Tools
Implementations for network scanning: Nmap, Masscan, Rustscan
"""

import logging
import subprocess
from typing import Any, Dict
import xml.etree.ElementTree as ET

from . import AgentTool

logger = logging.getLogger(__name__)


class NmapTool(AgentTool):
    """Nmap network port scanner"""
    
    def __init__(self):
        super().__init__(
            name="nmap",
            description="Network port scanner and service detection"
        )
        self.category = "network_analysis"
    
    def get_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "target": {"type": "string", "description": "IP address, hostname, or CIDR"},
                "ports": {"type": "string", "description": "Port range (e.g., '80,443' or '1-1000')", "default": "1-1000"},
                "scan_type": {"type": "string", "enum": ["syn", "tcp", "udp", "ping"], "default": "syn"}
            },
            "required": ["target"]
        }
    
    async def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute Nmap scan"""
        try:
            target = params.get("target")
            ports = params.get("ports", "1-1000")
            scan_type = params.get("scan_type", "syn")
            
            # Check if nmap is installed
            try:
                subprocess.run(["nmap", "--version"], capture_output=True, check=True)
            except (subprocess.CalledProcessError, FileNotFoundError):
                return {"success": False, "error": "Nmap not installed. Install nmap package."}
            
            # Build nmap command
            cmd = ["nmap", "-p", ports, "-oX", "-"]
            
            if scan_type == "syn":
                cmd.append("-sS")
            elif scan_type == "tcp":
                cmd.append("-sT")
            elif scan_type == "udp":
                cmd.append("-sU")
            elif scan_type == "ping":
                cmd.append("-sn")
            
            cmd.append(target)
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
            
            if result.returncode == 0:
                # Parse XML output
                try:
                    root = ET.fromstring(result.stdout)
                    hosts = []
                    
                    for host in root.findall("host"):
                        host_data = {
                            "address": host.find("address").get("addr") if host.find("address") is not None else None,
                            "status": host.find("status").get("state") if host.find("status") is not None else None,
                            "ports": []
                        }
                        
                        for port in host.findall(".//port"):
                            port_data = {
                                "port": port.get("portid"),
                                "protocol": port.get("protocol"),
                                "state": port.find("state").get("state") if port.find("state") is not None else None,
                                "service": port.find("service").get("name") if port.find("service") is not None else None
                            }
                            host_data["ports"].append(port_data)
                        
                        hosts.append(host_data)
                    
                    return {
                        "success": True,
                        "result": {
                            "target": target,
                            "hosts": hosts,
                            "count": len(hosts)
                        }
                    }
                except ET.ParseError:
                    return {"success": False, "error": "Failed to parse Nmap XML output"}
            
            return {"success": False, "error": f"Nmap failed: {result.stderr}"}
        except subprocess.TimeoutExpired:
            return {"success": False, "error": "Nmap scan timed out"}
        except Exception as e:
            logger.error(f"Nmap scan failed: {e}")
            return {"success": False, "error": str(e)}


class MasscanTool(AgentTool):
    """Masscan fast port scanner"""
    
    def __init__(self):
        super().__init__(
            name="masscan",
            description="Fast port scanner for large networks"
        )
        self.category = "network_analysis"
    
    def get_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "target": {"type": "string", "description": "IP address or CIDR"},
                "ports": {"type": "string", "description": "Port range (e.g., '80,443' or '1-1000')", "default": "1-1000"},
                "rate": {"type": "integer", "description": "Packets per second", "default": 1000}
            },
            "required": ["target"]
        }
    
    async def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute Masscan scan"""
        try:
            target = params.get("target")
            ports = params.get("ports", "1-1000")
            rate = params.get("rate", 1000)
            
            # Check if masscan is installed
            try:
                subprocess.run(["masscan", "--version"], capture_output=True, check=True)
            except (subprocess.CalledProcessError, FileNotFoundError):
                return {"success": False, "error": "Masscan not installed. See: https://github.com/robertdavidgraham/masscan"}
            
            # Run masscan
            cmd = ["masscan", target, "-p", ports, "--rate", str(rate), "-oJ", "-"]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                import json
                try:
                    # Masscan outputs JSON lines
                    results = []
                    for line in result.stdout.strip().split('\n'):
                        if line.strip():
                            try:
                                results.append(json.loads(line))
                            except json.JSONDecodeError:
                                continue
                    
                    return {
                        "success": True,
                        "result": {
                            "target": target,
                            "ports": results,
                            "count": len(results)
                        }
                    }
                except Exception as e:
                    return {"success": False, "error": f"Failed to parse Masscan output: {e}"}
            
            return {"success": False, "error": f"Masscan failed: {result.stderr}"}
        except subprocess.TimeoutExpired:
            return {"success": False, "error": "Masscan scan timed out"}
        except Exception as e:
            logger.error(f"Masscan scan failed: {e}")
            return {"success": False, "error": str(e)}


class RustscanTool(AgentTool):
    """Rustscan fast port scanner"""
    
    def __init__(self):
        super().__init__(
            name="rustscan",
            description="Fast port scanner written in Rust"
        )
        self.category = "network_analysis"
    
    def get_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "target": {"type": "string", "description": "IP address or hostname"},
                "ports": {"type": "string", "description": "Port range (e.g., '1-1000')", "default": "1-1000"},
                "ulimit": {"type": "integer", "description": "Ulimit value", "default": 5000}
            },
            "required": ["target"]
        }
    
    async def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute Rustscan"""
        try:
            target = params.get("target")
            ports = params.get("ports", "1-1000")
            ulimit = params.get("ulimit", 5000)
            
            # Check if rustscan is installed
            try:
                subprocess.run(["rustscan", "--version"], capture_output=True, check=True)
            except (subprocess.CalledProcessError, FileNotFoundError):
                return {"success": False, "error": "Rustscan not installed. See: https://github.com/RustScan/RustScan"}
            
            # Run rustscan
            cmd = ["rustscan", "-a", target, "-p", ports, "--ulimit", str(ulimit), "--", "-sV"]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                # Parse rustscan output (similar to nmap)
                ports_found = []
                for line in result.stdout.split('\n'):
                    if '/tcp' in line or '/udp' in line:
                        parts = line.split()
                        if len(parts) >= 3:
                            port_proto = parts[0]
                            state = parts[1]
                            service = parts[2] if len(parts) > 2 else "unknown"
                            ports_found.append({
                                "port": port_proto,
                                "state": state,
                                "service": service
                            })
                
                return {
                    "success": True,
                    "result": {
                        "target": target,
                        "ports": ports_found,
                        "count": len(ports_found),
                        "raw_output": result.stdout
                    }
                }
            
            return {"success": False, "error": f"Rustscan failed: {result.stderr}"}
        except subprocess.TimeoutExpired:
            return {"success": False, "error": "Rustscan timed out"}
        except Exception as e:
            logger.error(f"Rustscan failed: {e}")
            return {"success": False, "error": str(e)}

