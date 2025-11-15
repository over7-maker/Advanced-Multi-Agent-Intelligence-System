import asyncio
import ipaddress
import json
import logging
import socket
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timezone, timedelta
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Any, Set, Type, Union
from urllib.parse import urljoin, urlparse
import aiohttp

logger = logging.getLogger(__name__)

BLOCKED_IP_RANGES = [
    ipaddress.IPv4Network('127.0.0.0/8'),
    ipaddress.IPv4Network('10.0.0.0/8'),
    ipaddress.IPv4Network('172.16.0.0/12'),
    ipaddress.IPv4Network('192.168.0.0/16'),
    ipaddress.IPv4Network('169.254.0.0/16'),
]

class IntegrationType(str, Enum):
    """Enumeration of supported external integration platforms.\n\n    Used to standardize integration types across the ecosystem manager.\n    Values are lowercase strings matching configuration keys and service identifiers.\n    """
    # Workflow & Automation Platforms
    N8N = "n8n"
    ZAPIER = "zapier"
    MAKE = "make"
    POWER_AUTOMATE = "power_automate"
    # Communication Platforms
    SLACK = "slack"
    DISCORD = "discord"
    TEAMS = "teams"
    TELEGRAM = "telegram"
    # Cloud Services
    AWS = "aws"
    GOOGLE_CLOUD = "google_cloud"
    AZURE = "azure"
    # Business Applications
    SALESFORCE = "salesforce"
    HUBSPOT = "hubspot"
    NOTION = "notion"
    AIRTABLE = "airtable"
    # Development Tools
    GITHUB = "github"
    GITLAB = "gitlab"
    JIRA = "jira"
    JENKINS = "jenkins"
    # Data Platforms
    SNOWFLAKE = "snowflake"
    BIGQUERY = "bigquery"
    DATABRICKS = "databricks"
    MONGODB = "mongodb"
    POSTGRESQL = "postgresql"
    # AI Services
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    HUGGINGFACE = "huggingface"
    COHERE = "cohere"
    GOOGLE_SHEETS = "google_sheets"

@dataclass
class IntegrationConfig:
    integration_id: str
    integration_type: IntegrationType
    name: str
    base_url: Optional[str] = None
    api_key: Optional[str] = field(default=None, repr=False)

    # ... (other fields remain the same for brevity)

    def __post_init__(self):
        if not self.integration_id:
            raise ValueError("integration_id is required")
        if not isinstance(self.integration_type, IntegrationType):
            raise TypeError("integration_type must be IntegrationType")
        if not self.name:
            raise ValueError("name is required")
        if self.base_url and not _validate_url(self.base_url):
            raise ValueError(f"Invalid base_url format: {self.base_url}")


def _validate_url(url: str) -> bool:
    if not isinstance(url, str):
        logger.warning(f"Non-string value passed to _validate_url: {type(url)}")
        return False
    try:
        parsed = urlparse(url)
        if parsed.scheme not in ("http", "https") or not parsed.netloc:
            return False
        try:
            ip_str = socket.gethostbyname(parsed.hostname)
            ip = ipaddress.IPv4Address(ip_str)
            for blocked in BLOCKED_IP_RANGES:
                if ip in blocked:
                    logger.warning(f"Blocked SSRF attempt to internal IP: {ip}")
                    return False
        except socket.gaierror:
            pass  # Let request fail later if DNS unresolved
        return True
    except (AttributeError, TypeError) as e:
        logger.debug(f"Invalid URL structure: {url}, error: {e}")
        return False
