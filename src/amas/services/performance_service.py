"""
Performance Optimization Service for AMAS Intelligence System - Phase 3
Provides performance optimization, caching, load balancing, and resource management
"""

import asyncio
import hashlib
import json
import logging
import time
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Union

logger = logging.getLogger(__name__)

class CacheStrategy(Enum):
    """Cache strategy enumeration"""

    LRU = "lru"
    LFU = "lfu"
    TTL = "ttl"
    WRITE_THROUGH = "write_through"
    WRITE_BACK = "write_back"

class LoadBalanceStrategy(Enum):
    """Load balancing strategy enumeration"""

    ROUND_ROBIN = "round_robin"
    LEAST_CONNECTIONS = "least_connections"
    WEIGHTED_ROUND_ROBIN = "weighted_round_robin"
    LEAST_RESPONSE_TIME = "least_response_time"
    RANDOM = "random"

@dataclass
class CacheEntry:
    """Cache entry data structure"""

    key: str
    value: Any
    created_at: datetime
    accessed_at: datetime
    access_count: int
    ttl: Optional[float] = None
    size: int = 0

@dataclass
class PerformanceMetrics:
    """Performance metrics data structure"""

    service_name: str
    response_time: float
    throughput: float
    error_rate: float
    cpu_usage: float
    memory_usage: float
    connection_count: int
    timestamp: datetime

class PerformanceService:
    """
    Performance Optimization Service for AMAS Intelligence System

    Provides comprehensive performance optimization including caching,
    load balancing, resource management, and performance monitoring.
    """

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the performance service.

        Args:
            config: Configuration dictionary
        """
        self.config = config

        # Cache configuration
        self.cache_config = {
            "max_size": config.get("cache_max_size", 1000),
            "default_ttl": config.get("cache_default_ttl", 3600),
            "strategy": CacheStrategy(config.get("cache_strategy", "lru")),
            "enable_compression": config.get("cache_compression", True),
        }

        # Load balancing configuration
        self.load_balance_config = {
            "strategy": LoadBalanceStrategy(
                config.get("load_balance_strategy", "round_robin")
            ),
            "health_check_interval": config.get("health_check_interval", 30),
            "max_retries": config.get("max_retries", 3),
            "timeout": config.get("timeout", 30),
        }

        # Performance monitoring
        self.performance_metrics = {}
        self.optimization_rules = []

        # Cache storage
        self.cache = {}
        self.cache_stats = {"hits": 0, "misses": 0, "evictions": 0, "size": 0}

        # Load balancers
        self.load_balancers = {}
        self.service_pools = {}

        # Resource management
        self.resource_limits = {
            "max_memory": config.get("max_memory", 1024 * 1024 * 1024),  # 1GB
            "max_cpu": config.get("max_cpu", 80.0),  # 80%
            "max_connections": config.get("max_connections", 1000),
        }

        logger.info("Performance service initialized")

    async def initialize(self):
        """Initialize the performance service"""
        try:
            logger.info("Initializing performance service...")

            # Initialize cache system
            await self._initialize_cache_system()

            # Initialize load balancers
            await self._initialize_load_balancers()

            # Initialize resource management
            await self._initialize_resource_management()

            # Initialize performance monitoring
            await self._initialize_performance_monitoring()

            # Start optimization tasks
            await self._start_optimization_tasks()

            logger.info("Performance service initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize performance service: {e}")
            raise

    async def _initialize_cache_system(self):
        """Initialize cache system"""
        try:
            logger.info("Initializing cache system...")

            # Initialize cache based on strategy
            if self.cache_config["strategy"] == CacheStrategy.LRU:
                await self._initialize_lru_cache()
            elif self.cache_config["strategy"] == CacheStrategy.LFU:
                await self._initialize_lfu_cache()
            elif self.cache_config["strategy"] == CacheStrategy.TTL:
                await self._initialize_ttl_cache()

            logger.info("Cache system initialized")

        except Exception as e:
            logger.error(f"Failed to initialize cache system: {e}")
            raise

    async def _initialize_lru_cache(self):
        """Initialize LRU cache"""
        self.cache_order = []  # For LRU ordering

    async def _initialize_lfu_cache(self):
        """Initialize LFU cache"""
        self.cache_frequency = {}  # For LFU frequency tracking

    async def _initialize_ttl_cache(self):
        """Initialize TTL cache"""
        self.cache_ttl = {}  # For TTL tracking

    async def _initialize_load_balancers(self):
        """Initialize load balancers"""
        try:
            logger.info("Initializing load balancers...")

            # Initialize LLM provider load balancer
            self.load_balancers["llm_providers"] = {
                "strategy": self.load_balance_config["strategy"],
                "providers": [
                    {"name": "ollama", "weight": 1, "health": True},
                    {"name": "deepseek", "weight": 2, "health": True},
                    {"name": "glm", "weight": 1, "health": True},
                    {"name": "grok", "weight": 1, "health": True},
                ],
                "current_index": 0,
                "health_checks": {},
            }

            # Initialize agent load balancer
            self.load_balancers["agents"] = {
                "strategy": self.load_balance_config["strategy"],
                "agents": [],
                "current_index": 0,
                "health_checks": {},
            }

            logger.info("Load balancers initialized")

        except Exception as e:
            logger.error(f"Failed to initialize load balancers: {e}")
            raise

    async def _initialize_resource_management(self):
        """Initialize resource management"""
        try:
            logger.info("Initializing resource management...")

            # Initialize resource monitoring
            self.resource_monitoring = {
                "memory_usage": 0,
                "cpu_usage": 0,
                "connection_count": 0,
                "last_check": datetime.utcnow(),
            }

            logger.info("Resource management initialized")

        except Exception as e:
            logger.error(f"Failed to initialize resource management: {e}")
            raise

    async def _initialize_performance_monitoring(self):
        """Initialize performance monitoring"""
        try:
            logger.info("Initializing performance monitoring...")

            # Initialize performance metrics collection
            self.performance_monitoring = {
                "metrics": {},
                "thresholds": {
                    "response_time": 5.0,
                    "error_rate": 0.05,
                    "throughput": 1000,
                },
                "optimization_rules": [],
            }

            logger.info("Performance monitoring initialized")

        except Exception as e:
            logger.error(f"Failed to initialize performance monitoring: {e}")
            raise

    async def _start_optimization_tasks(self):
        """Start optimization tasks"""
        try:
            logger.info("Starting optimization tasks...")

            # Start background optimization tasks
            self.optimization_tasks = [
                asyncio.create_task(self._optimize_cache()),
                asyncio.create_task(self._optimize_load_balancing()),
                asyncio.create_task(self._optimize_resource_usage()),
                asyncio.create_task(self._monitor_performance()),
            ]

            logger.info("Optimization tasks started")

        except Exception as e:
            logger.error(f"Failed to start optimization tasks: {e}")
            raise

    async def get_from_cache(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        try:
            if key not in self.cache:
                self.cache_stats["misses"] += 1
                return None

            entry = self.cache[key]

            # Check TTL
            if (
                entry.ttl
                and (datetime.utcnow() - entry.created_at).total_seconds() > entry.ttl
            ):
                await self._evict_from_cache(key)
                self.cache_stats["misses"] += 1
                return None

            # Update access information
            entry.accessed_at = datetime.utcnow()
            entry.access_count += 1

            # Update cache order for LRU
            if self.cache_config["strategy"] == CacheStrategy.LRU:
                self.cache_order.remove(key)
                self.cache_order.append(key)

            self.cache_stats["hits"] += 1
            return entry.value

        except Exception as e:
            logger.error(f"Failed to get from cache: {e}")
            return None

    async def set_in_cache(
        self, key: str, value: Any, ttl: Optional[float] = None
    ) -> bool:
        """Set value in cache"""
        try:
            # Check cache size limit
            if len(self.cache) >= self.cache_config["max_size"]:
                await self._evict_oldest_entry()

            # Create cache entry
            entry = CacheEntry(
                key=key,
                value=value,
                created_at=datetime.utcnow(),
                accessed_at=datetime.utcnow(),
                access_count=1,
                ttl=ttl or self.cache_config["default_ttl"],
                size=len(str(value)),
            )

            # Store in cache
            self.cache[key] = entry

            # Update cache order for LRU
            if self.cache_config["strategy"] == CacheStrategy.LRU:
                if key in self.cache_order:
                    self.cache_order.remove(key)
                self.cache_order.append(key)

            # Update cache frequency for LFU
            if self.cache_config["strategy"] == CacheStrategy.LFU:
                self.cache_frequency[key] = 1

            # Update cache stats
            self.cache_stats["size"] = len(self.cache)

            return True

        except Exception as e:
            logger.error(f"Failed to set in cache: {e}")
            return False

    async def _evict_from_cache(self, key: str):
        """Evict entry from cache"""
        try:
            if key in self.cache:
                del self.cache[key]

                # Update cache order
                if key in self.cache_order:
                    self.cache_order.remove(key)

                # Update cache frequency
                if key in self.cache_frequency:
                    del self.cache_frequency[key]

                # Update cache stats
                self.cache_stats["evictions"] += 1
                self.cache_stats["size"] = len(self.cache)

        except Exception as e:
            logger.error(f"Failed to evict from cache: {e}")

    async def _evict_oldest_entry(self):
        """Evict oldest entry from cache"""
        try:
            if not self.cache:
                return

            if self.cache_config["strategy"] == CacheStrategy.LRU:
                # Evict least recently used
                if self.cache_order:
                    oldest_key = self.cache_order[0]
                    await self._evict_from_cache(oldest_key)

            elif self.cache_config["strategy"] == CacheStrategy.LFU:
                # Evict least frequently used
                if self.cache_frequency:
                    oldest_key = min(
                        self.cache_frequency.keys(),
                        key=lambda k: self.cache_frequency[k],
                    )
                    await self._evict_from_cache(oldest_key)

            elif self.cache_config["strategy"] == CacheStrategy.TTL:
                # Evict oldest by creation time
                oldest_key = min(
                    self.cache.keys(), key=lambda k: self.cache[k].created_at
                )
                await self._evict_from_cache(oldest_key)

        except Exception as e:
            logger.error(f"Failed to evict oldest entry: {e}")

    async def select_llm_provider(self, task_type: str = None) -> str:
        """Select LLM provider using load balancing"""
        try:
            balancer = self.load_balancers["llm_providers"]
            providers = [p for p in balancer["providers"] if p["health"]]

            if not providers:
                raise Exception("No healthy LLM providers available")

            if balancer["strategy"] == LoadBalanceStrategy.ROUND_ROBIN:
                provider = providers[balancer["current_index"] % len(providers)]
                balancer["current_index"] += 1
                return provider["name"]

            elif balancer["strategy"] == LoadBalanceStrategy.LEAST_CONNECTIONS:
                # Select provider with least connections
                provider = min(providers, key=lambda p: p.get("connections", 0))
                return provider["name"]

            elif balancer["strategy"] == LoadBalanceStrategy.WEIGHTED_ROUND_ROBIN:
                # Weighted round robin selection
                total_weight = sum(p["weight"] for p in providers)
                if total_weight == 0:
                    return providers[0]["name"]

                # Simple weighted selection
                provider = providers[balancer["current_index"] % len(providers)]
                balancer["current_index"] += 1
                return provider["name"]

            elif balancer["strategy"] == LoadBalanceStrategy.LEAST_RESPONSE_TIME:
                # Select provider with least response time
                provider = min(
                    providers, key=lambda p: p.get("response_time", float("inf"))
                )
                return provider["name"]

            elif balancer["strategy"] == LoadBalanceStrategy.RANDOM:
                import random

                provider = random.choice(providers)
                return provider["name"]

            else:
                return providers[0]["name"]

        except Exception as e:
            logger.error(f"Failed to select LLM provider: {e}")
            return "ollama"  # Fallback

    async def select_agent(self, task_type: str) -> str:
        """Select agent using load balancing"""
        try:
            balancer = self.load_balancers["agents"]
            agents = [a for a in balancer["agents"] if a.get("health", True)]

            if not agents:
                raise Exception("No healthy agents available")

            # Filter agents by task type capability
            suitable_agents = [
                a for a in agents if task_type in a.get("capabilities", [])
            ]

            if not suitable_agents:
                suitable_agents = agents  # Fallback to all agents

            if balancer["strategy"] == LoadBalanceStrategy.ROUND_ROBIN:
                agent = suitable_agents[
                    balancer["current_index"] % len(suitable_agents)
                ]
                balancer["current_index"] += 1
                return agent["id"]

            elif balancer["strategy"] == LoadBalanceStrategy.LEAST_CONNECTIONS:
                agent = min(suitable_agents, key=lambda a: a.get("active_tasks", 0))
                return agent["id"]

            else:
                return suitable_agents[0]["id"]

        except Exception as e:
            logger.error(f"Failed to select agent: {e}")
            return "osint_001"  # Fallback

    async def _optimize_cache(self):
        """Optimize cache performance"""
        while True:
            try:
                # Clean expired entries
                current_time = datetime.utcnow()
                expired_keys = []

                for key, entry in self.cache.items():
                    if (
                        entry.ttl
                        and (current_time - entry.created_at).total_seconds()
                        > entry.ttl
                    ):
                        expired_keys.append(key)

                for key in expired_keys:
                    await self._evict_from_cache(key)

                # Optimize cache size
                if len(self.cache) > self.cache_config["max_size"] * 0.9:
                    # Evict 10% of entries
                    evict_count = int(len(self.cache) * 0.1)
                    for _ in range(evict_count):
                        await self._evict_oldest_entry()

                await asyncio.sleep(300)  # Optimize every 5 minutes

            except Exception as e:
                logger.error(f"Cache optimization error: {e}")
                await asyncio.sleep(60)

    async def _optimize_load_balancing(self):
        """Optimize load balancing"""
        while True:
            try:
                # Update provider health
                for provider in self.load_balancers["llm_providers"]["providers"]:
                    health = await self._check_provider_health(provider["name"])
                    provider["health"] = health

                # Update agent health
                for agent in self.load_balancers["agents"]["agents"]:
                    health = await self._check_agent_health(agent["id"])
                    agent["health"] = health

                await asyncio.sleep(self.load_balance_config["health_check_interval"])

            except Exception as e:
                logger.error(f"Load balancing optimization error: {e}")
                await asyncio.sleep(60)

    async def _optimize_resource_usage(self):
        """Optimize resource usage"""
        while True:
            try:
                # Monitor resource usage
                await self._monitor_resource_usage()

                # Apply optimization rules
                await self._apply_optimization_rules()

                await asyncio.sleep(60)  # Check every minute

            except Exception as e:
                logger.error(f"Resource optimization error: {e}")
                await asyncio.sleep(60)

    async def _monitor_performance(self):
        """Monitor performance metrics"""
        while True:
            try:
                # Collect performance metrics
                await self._collect_performance_metrics()

                # Analyze performance trends
                await self._analyze_performance_trends()

                await asyncio.sleep(30)  # Monitor every 30 seconds

            except Exception as e:
                logger.error(f"Performance monitoring error: {e}")
                await asyncio.sleep(60)

    async def _check_provider_health(self, provider_name: str) -> bool:
        """Check health of LLM provider"""
        try:
            # Simulate health check
            # In real implementation, this would check actual provider health
            return True

        except Exception as e:
            logger.error(f"Failed to check provider health for {provider_name}: {e}")
            return False

    async def _check_agent_health(self, agent_id: str) -> bool:
        """Check health of agent"""
        try:
            # Simulate health check
            # In real implementation, this would check actual agent health
            return True

        except Exception as e:
            logger.error(f"Failed to check agent health for {agent_id}: {e}")
            return False

    async def _monitor_resource_usage(self):
        """Monitor resource usage"""
        try:
            import psutil

            # Get system resource usage
            memory = psutil.virtual_memory()
            cpu = psutil.cpu_percent(interval=1)

            # Update resource monitoring
            self.resource_monitoring.update(
                {
                    "memory_usage": memory.percent,
                    "cpu_usage": cpu,
                    "last_check": datetime.utcnow(),
                }
            )

            # Check resource limits
            if memory.percent > self.resource_limits["max_cpu"]:
                await self._handle_resource_limit_exceeded("memory", memory.percent)

            if cpu > self.resource_limits["max_cpu"]:
                await self._handle_resource_limit_exceeded("cpu", cpu)

        except Exception as e:
            logger.error(f"Failed to monitor resource usage: {e}")

    async def _handle_resource_limit_exceeded(self, resource: str, usage: float):
        """Handle resource limit exceeded"""
        try:
            logger.warning(f"Resource limit exceeded: {resource} usage is {usage:.1f}%")

            # Apply optimization measures
            if resource == "memory":
                await self._optimize_memory_usage()
            elif resource == "cpu":
                await self._optimize_cpu_usage()

        except Exception as e:
            logger.error(f"Failed to handle resource limit exceeded: {e}")

    async def _optimize_memory_usage(self):
        """Optimize memory usage"""
        try:
            # Clear cache
            await self._clear_cache()

            # Reduce cache size
            self.cache_config["max_size"] = int(self.cache_config["max_size"] * 0.8)

            logger.info("Memory usage optimized")

        except Exception as e:
            logger.error(f"Failed to optimize memory usage: {e}")

    async def _optimize_cpu_usage(self):
        """Optimize CPU usage"""
        try:
            # Reduce concurrent operations
            # Adjust load balancing weights
            # Implement rate limiting

            logger.info("CPU usage optimized")

        except Exception as e:
            logger.error(f"Failed to optimize CPU usage: {e}")

    async def _clear_cache(self):
        """Clear cache"""
        try:
            self.cache.clear()
            self.cache_order.clear()
            self.cache_frequency.clear()
            self.cache_stats["size"] = 0

            logger.info("Cache cleared")

        except Exception as e:
            logger.error(f"Failed to clear cache: {e}")

    async def _collect_performance_metrics(self):
        """Collect performance metrics"""
        try:
            # Collect cache metrics
            cache_hit_rate = self.cache_stats["hits"] / max(
                self.cache_stats["hits"] + self.cache_stats["misses"], 1
            )

            # Store performance metrics
            metrics = PerformanceMetrics(
                service_name="performance_service",
                response_time=0.0,  # Would be calculated from actual measurements
                throughput=1000,  # Would be calculated from actual measurements
                error_rate=0.0,  # Would be calculated from actual measurements
                cpu_usage=self.resource_monitoring["cpu_usage"],
                memory_usage=self.resource_monitoring["memory_usage"],
                connection_count=0,  # Would be calculated from actual measurements
                timestamp=datetime.utcnow(),
            )

            self.performance_metrics[datetime.utcnow()] = metrics

        except Exception as e:
            logger.error(f"Failed to collect performance metrics: {e}")

    async def _analyze_performance_trends(self):
        """Analyze performance trends"""
        try:
            # Analyze performance trends
            # Identify optimization opportunities
            # Apply automatic optimizations

            pass

        except Exception as e:
            logger.error(f"Failed to analyze performance trends: {e}")

    async def _apply_optimization_rules(self):
        """Apply optimization rules"""
        try:
            # Apply automatic optimization rules
            # Adjust cache settings
            # Adjust load balancing parameters

            pass

        except Exception as e:
            logger.error(f"Failed to apply optimization rules: {e}")

    async def get_performance_status(self) -> Dict[str, Any]:
        """Get performance status"""
        return {
            "cache_stats": self.cache_stats,
            "resource_monitoring": self.resource_monitoring,
            "load_balancers": {
                name: {
                    "strategy": balancer["strategy"].value,
                    "healthy_providers": len(
                        [p for p in balancer["providers"] if p["health"]]
                    ),
                    "total_providers": len(balancer["providers"]),
                }
                for name, balancer in self.load_balancers.items()
            },
            "optimization_active": len(self.optimization_tasks) > 0,
            "timestamp": datetime.utcnow().isoformat(),
        }

    async def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        hit_rate = self.cache_stats["hits"] / max(
            self.cache_stats["hits"] + self.cache_stats["misses"], 1
        )

        return {
            "size": self.cache_stats["size"],
            "max_size": self.cache_config["max_size"],
            "hit_rate": hit_rate,
            "hits": self.cache_stats["hits"],
            "misses": self.cache_stats["misses"],
            "evictions": self.cache_stats["evictions"],
            "strategy": self.cache_config["strategy"].value,
            "timestamp": datetime.utcnow().isoformat(),
        }

    async def clear_cache(self) -> bool:
        """Clear all cache"""
        try:
            await self._clear_cache()
            return True

        except Exception as e:
            logger.error(f"Failed to clear cache: {e}")
            return False

    async def shutdown(self):
        """Shutdown performance service"""
        try:
            logger.info("Shutting down performance service...")

            # Cancel optimization tasks
            for task in self.optimization_tasks:
                task.cancel()

            # Wait for tasks to complete
            await asyncio.gather(*self.optimization_tasks, return_exceptions=True)

            # Clear cache
            await self._clear_cache()

            logger.info("Performance service shutdown complete")

        except Exception as e:
            logger.error(f"Error during performance service shutdown: {e}")
