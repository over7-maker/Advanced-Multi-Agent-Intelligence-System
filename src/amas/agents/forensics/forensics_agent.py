"""
Forensics Agent Implementation
"""

import asyncio
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from agents.base.intelligence_agent import AgentStatus, IntelligenceAgent

logger = logging.getLogger(__name__)


class ForensicsAgent(IntelligenceAgent):
    """Forensics Agent for AMAS Intelligence System"""

    def __init__(
        self,
        agent_id: str,
        name: str = "Forensics Agent",
        llm_service: Any = None,
        vector_service: Any = None,
        knowledge_graph: Any = None,
        security_service: Any = None,
    ):
        capabilities = [
            "evidence_acquisition",
            "file_analysis",
            "timeline_analysis",
            "metadata_extraction",
            "hash_analysis",
            "deleted_file_recovery",
        ]

        super().__init__(
            agent_id=agent_id,
            name=name,
            capabilities=capabilities,
            llm_service=llm_service,
            vector_service=vector_service,
            knowledge_graph=knowledge_graph,
            security_service=security_service,
        )

    async def execute_task(self, task_description: str, metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """Execute forensics task with real file analysis"""
        try:
            logger.info(f"Executing forensics task: {task_description}")

            # Determine task type from description
            task_type = self._classify_task(task_description)
            metadata = metadata or {}

            if task_type == "file_analysis":
                return await self._analyze_file(task_description, metadata)
            elif task_type == "hash_analysis":
                return await self._analyze_hash(task_description, metadata)
            elif task_type == "metadata_extraction":
                return await self._extract_metadata(task_description, metadata)
            elif task_type == "timeline_analysis":
                return await self._analyze_timeline(task_description, metadata)
            else:
                return await self._perform_general_forensics(task_description, metadata)

        except Exception as e:
            logger.error(f"Error executing forensics task: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat(),
            }
    async def validate_task(self, task: Dict[str, Any]) -> bool:
        """Validate if this agent can handle the task"""
        forensics_keywords = [
            "forensics",
            "evidence",
            "analysis",
            "acquisition",
            "timeline",
            "metadata",
            "hash",
            "file",
            "recovery",
        ]

        task_text = f"{task.get('type', '')} {task.get('description', '')}".lower()
        return any(keyword in task_text for keyword in forensics_keywords)


    def _classify_task(self, description: str) -> str:
        """Classify task type based on description"""
        description_lower = description.lower()
        
        if any(keyword in description_lower for keyword in ["file", "analyze", "examine"]):
            return "file_analysis"
        elif any(keyword in description_lower for keyword in ["hash", "checksum", "md5", "sha"]):
            return "hash_analysis"
        elif any(keyword in description_lower for keyword in ["metadata", "properties", "info"]):
            return "metadata_extraction"
        elif any(keyword in description_lower for keyword in ["timeline", "time", "date", "chronological"]):
            return "timeline_analysis"
        else:
            return "general_forensics"

    async def _analyze_file(self, description: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze file with real forensics techniques"""
        try:
            import os
            import hashlib
            import mimetypes
            from pathlib import Path
            
            # Extract file path from description or metadata
            file_path = metadata.get("file_path") or self._extract_file_path(description)
            if not file_path or not os.path.exists(file_path):
                return {
                    "success": False,
                    "error": "File not found or path not specified",
                    "timestamp": datetime.utcnow().isoformat(),
                }
            
            file_path = Path(file_path)
            
            # Basic file information
            stat_info = file_path.stat()
            file_info = {
                "name": file_path.name,
                "size": stat_info.st_size,
                "created": datetime.fromtimestamp(stat_info.st_ctime).isoformat(),
                "modified": datetime.fromtimestamp(stat_info.st_mtime).isoformat(),
                "accessed": datetime.fromtimestamp(stat_info.st_atime).isoformat(),
                "permissions": oct(stat_info.st_mode)[-3:],
                "mime_type": mimetypes.guess_type(str(file_path))[0] or "unknown",
            }
            
            # Calculate hashes
            hashes = await self._calculate_hashes(file_path)
            
            # File content analysis
            content_analysis = await self._analyze_file_content(file_path)
            
            # Security analysis
            security_analysis = await self._analyze_file_security(file_path)
            
            return {
                "success": True,
                "task_type": "file_analysis",
                "file_info": file_info,
                "hashes": hashes,
                "content_analysis": content_analysis,
                "security_analysis": security_analysis,
                "timestamp": datetime.utcnow().isoformat(),
            }
            
        except Exception as e:
            logger.error(f"Error in file analysis: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat(),
            }

    def _extract_file_path(self, description: str) -> Optional[str]:
        """Extract file path from description"""
        import re
        # Look for common file path patterns
        path_patterns = [
            r"[\/][\w\-\s.]+\.[\w]+",  # Unix paths
            r"[A-Za-z]:[\/][\w\-\s.]+\.[\w]+",  # Windows paths
            r"[\w\-\s.]+\.[\w]+",  # Simple filename
        ]
        
        for pattern in path_patterns:
            match = re.search(pattern, description)
            if match:
                return match.group(0)
        
        return None

    async def _calculate_hashes(self, file_path: Path) -> Dict[str, str]:
        """Calculate various hashes for file
        
        Note: MD5 and SHA1 are included for compatibility with existing systems
        and forensic tools, but SHA256 should be used for security-critical applications.
        """
        try:
            hashes = {}
            
            # Read file in chunks to handle large files
            with open(file_path, "rb") as f:
                # Include legacy hashes for forensic compatibility
                md5_hash = hashlib.md5()
                sha1_hash = hashlib.sha1()
                # Primary security hash
                sha256_hash = hashlib.sha256()
                # Additional secure hash
                sha512_hash = hashlib.sha512()
                
                while chunk := f.read(8192):
                    md5_hash.update(chunk)
                    sha1_hash.update(chunk)
                    sha256_hash.update(chunk)
                    sha512_hash.update(chunk)
                
                # Include all hashes for comprehensive analysis
                hashes["md5"] = md5_hash.hexdigest()  # Legacy compatibility
                hashes["sha1"] = sha1_hash.hexdigest()  # Legacy compatibility
                hashes["sha256"] = sha256_hash.hexdigest()  # Primary security hash
                hashes["sha512"] = sha512_hash.hexdigest()  # Additional security hash
                
                # Add security note
                hashes["_security_note"] = "Use SHA256 or SHA512 for security-critical applications"
            
            return hashes
            
        except Exception as e:
            logger.error(f"Error calculating hashes: {e}")
            return {"error": str(e)}

    async def _analyze_file_content(self, file_path: Path) -> Dict[str, Any]:
        """Analyze file content for forensics purposes"""
        try:
            import re
            
            # Read file content
            with open(file_path, "rb") as f:
                content = f.read()
            
            # Try to decode as text
            try:
                text_content = content.decode("utf-8")
                is_text = True
            except:
                try:
                    text_content = content.decode("latin-1")
                    is_text = True
                except:
                    text_content = ""
                    is_text = False
            
            analysis = {
                "is_text": is_text,
                "size_bytes": len(content),
                "null_bytes": content.count(b"\x00"),
                "printable_chars": sum(1 for c in content if 32 <= c <= 126) if is_text else 0,
            }
            
            if is_text:
                # Text analysis
                analysis.update({
                    "lines": len(text_content.splitlines()),
                    "words": len(text_content.split()),
                    "characters": len(text_content),
                    "emails": len(re.findall(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b", text_content)),
                    "urls": len(re.findall(r"http[s]?://(?:[a-zA-Z]|[0-9]|[huBHc_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+", text_content)),
                    "ip_addresses": len(re.findall(r"\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b", text_content)),
                })
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing file content: {e}")
            return {"error": str(e)}

    async def _analyze_file_security(self, file_path: Path) -> Dict[str, Any]:
        """Analyze file for security indicators"""
        try:
            import re
            
            security_flags = []
            
            # Check file extension for suspicious types
            suspicious_extensions = [".exe", ".bat", ".cmd", ".scr", ".pif", ".com", ".vbs", ".js"]
            if file_path.suffix.lower() in suspicious_extensions:
                security_flags.append(f"Suspicious file extension: {file_path.suffix}")
            
            
            # Check for embedded executables or scripts
            try:
                with open(file_path, "rb") as f:
                    content = f.read(1024)  # Read first 1KB
                    
                    # Check for PE header (Windows executables)
                    if content.startswith(b"MZ"):
                        security_flags.append("Contains PE header (executable)")
                    
                    # Check for script signatures
                    script_signatures = [
                        b"#!/bin/",  # Shell scripts
                        b"#!/usr/bin/",  # Shell scripts
                        b"<script",  # HTML/JS
                        b"<?php",  # PHP
                        b"import os",  # Python
                        b"require(",  # Node.js
                    ]
                    
                    for sig in script_signatures:
                        if sig in content:
                            security_flags.append(f"Contains script signature: {sig.decode()}")
                            break
            except:
                pass
            
            return {
                "security_flags": security_flags,
                "risk_level": "high" if len(security_flags) > 2 else "medium" if security_flags else "low",
                "analysis": f"File has {len(security_flags)} security flags"
            }
            
        except Exception as e:
            logger.error(f"Error in security analysis: {e}")
            return {"error": str(e)}

    async def _analyze_hash(self, description: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze hash value for forensics purposes"""
        try:
            import hashlib
            
            # Extract hash from description or metadata
            hash_value = metadata.get("hash") or self._extract_hash(description)
            if not hash_value:
                return {
                    "success": False,
                    "error": "No hash value found",
                    "timestamp": datetime.utcnow().isoformat(),
                }
            
            # Determine hash type
            hash_type = self._identify_hash_type(hash_value)
            
            # Check against known hash databases (mock implementation)
            database_results = await self._check_hash_databases(hash_value, hash_type)
            
            return {
                "success": True,
                "task_type": "hash_analysis",
                "hash": hash_value,
                "hash_type": hash_type,
                "database_results": database_results,
                "timestamp": datetime.utcnow().isoformat(),
            }
            
        except Exception as e:
            logger.error(f"Error in hash analysis: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat(),
            }

    def _extract_hash(self, description: str) -> Optional[str]:
        """Extract hash value from description"""
        import re
        # Look for common hash patterns
        hash_patterns = [
            r"[a-fA-F0-9]{32}",  # MD5
            r"[a-fA-F0-9]{40}",  # SHA1
            r"[a-fA-F0-9]{64}",  # SHA256
        ]
        
        for pattern in hash_patterns:
            match = re.search(pattern, description)
            if match:
                return match.group(0)
        
        return None

    def _identify_hash_type(self, hash_value: str) -> str:
        """Identify hash type based on length"""
        length = len(hash_value)
        if length == 32:
            return "MD5"
        elif length == 40:
            return "SHA1"
        elif length == 64:
            return "SHA256"
        else:
            return "Unknown"

    async def _check_hash_databases(self, hash_value: str, hash_type: str) -> Dict[str, Any]:
        """Check hash against known databases (mock implementation)"""
        # In a real implementation, this would query actual hash databases
        return {
            "virustotal": "Not checked (mock)",
            "malware_database": "Not checked (mock)",
            "known_good": "Not checked (mock)",
            "note": "Real implementation would query actual hash databases"
        }

    async def _extract_metadata(self, description: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Extract metadata from files"""
        try:
            import os
            from pathlib import Path
            
            # Extract file path
            file_path = metadata.get("file_path") or self._extract_file_path(description)
            if not file_path or not os.path.exists(file_path):
                return {
                    "success": False,
                    "error": "File not found",
                    "timestamp": datetime.utcnow().isoformat(),
                }
            
            file_path = Path(file_path)
            
            # Extract basic metadata
            stat_info = file_path.stat()
            metadata_info = {
                "file_name": file_path.name,
                "file_size": stat_info.st_size,
                "created_time": datetime.fromtimestamp(stat_info.st_ctime).isoformat(),
                "modified_time": datetime.fromtimestamp(stat_info.st_mtime).isoformat(),
                "accessed_time": datetime.fromtimestamp(stat_info.st_atime).isoformat(),
                "file_permissions": oct(stat_info.st_mode)[-3:],
                "inode": stat_info.st_ino,
                "device": stat_info.st_dev,
                "hard_links": stat_info.st_nlink,
            }
            
            return {
                "success": True,
                "task_type": "metadata_extraction",
                "metadata": metadata_info,
                "timestamp": datetime.utcnow().isoformat(),
            }
            
        except Exception as e:
            logger.error(f"Error in metadata extraction: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat(),
            }

    async def _analyze_timeline(self, description: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze file timeline for forensics"""
        try:
            import os
            from pathlib import Path
            
            # Extract directory path
            dir_path = metadata.get("directory_path") or self._extract_directory_path(description)
            if not dir_path or not os.path.exists(dir_path):
                return {
                    "success": False,
                    "error": "Directory not found",
                    "timestamp": datetime.utcnow().isoformat(),
                }
            
            dir_path = Path(dir_path)
            
            # Get all files and their timestamps
            timeline = []
            for file_path in dir_path.rglob("*"):
                if file_path.is_file():
                    stat_info = file_path.stat()
                    timeline.append({
                        "file": str(file_path),
                        "created": datetime.fromtimestamp(stat_info.st_ctime).isoformat(),
                        "modified": datetime.fromtimestamp(stat_info.st_mtime).isoformat(),
                        "accessed": datetime.fromtimestamp(stat_info.st_atime).isoformat(),
                        "size": stat_info.st_size,
                    })
            
            # Sort by creation time
            timeline.sort(key=lambda x: x["created"])
            
            return {
                "success": True,
                "task_type": "timeline_analysis",
                "timeline": timeline[:100],  # Limit to first 100 files
                "total_files": len(timeline),
                "timestamp": datetime.utcnow().isoformat(),
            }
            
        except Exception as e:
            logger.error(f"Error in timeline analysis: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat(),
            }

    def _extract_directory_path(self, description: str) -> Optional[str]:
        """Extract directory path from description"""
        import re
        # Look for directory patterns
        dir_patterns = [
            r"[\/][\w\-\s.]+[\/]?",  # Unix paths
            r"[A-Za-z]:[\/][\w\-\s.]+[\/]?",  # Windows paths
        ]
        
        for pattern in dir_patterns:
            match = re.search(pattern, description)
            if match:
                return match.group(0)
        
        return None

    async def _perform_general_forensics(self, description: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Perform general forensics analysis"""
        try:
            # Extract various data types from description
            import re
            
            # Look for file paths
            file_paths = re.findall(r"[\w\-\s.]+\.[\w]+", description)
            
            # Look for hash values
            hashes = re.findall(r"[a-fA-F0-9]{32,64}", description)
            
            analysis = {
                "file_paths_found": len(file_paths),
                "hashes_found": len(hashes),
                "extracted_data": {
                    "file_paths": file_paths[:10],  # Limit output
                    "hashes": hashes[:10],
                }
            }
            
            return {
                "success": True,
                "task_type": "general_forensics",
                "analysis": analysis,
                "timestamp": datetime.utcnow().isoformat(),
            }
            
        except Exception as e:
            logger.error(f"Error in general forensics: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat(),
            }