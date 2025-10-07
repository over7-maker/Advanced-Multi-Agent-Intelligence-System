"""Database service for AMAS"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

try:
    import asyncpg
    import redis.asyncio as redis

    DATABASE_AVAILABLE = True
except ImportError:
    DATABASE_AVAILABLE = False
    logging.warning("Database drivers not available")

logger = logging.getLogger(__name__)
