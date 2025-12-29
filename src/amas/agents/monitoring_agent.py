"""
Monitoring Agent - Specialized agent for system monitoring and observability
Implements PART_3 requirements
"""

import json
import logging
import time
from typing import Any, Dict, List

from src.amas.agents.base_agent import BaseAgent
from src.amas.agents.tools import get_tool_registry
from src.amas.agents.utils.json_parser import JSONParser
from src.amas.agents.schemas import MonitoringConfig

logger = logging.getLogger(__name__)


class MonitoringAgent(BaseAgent):
    """
    Monitoring Agent
    
    Specializes in:
    - System monitoring setup
    - Metrics collection
    - Alert configuration
    - Logging strategies
    - Observability best practices
    """
    
    def __init__(self):
        super().__init__(
            agent_id="monitoring_agent",
            name="Monitoring Agent",
            agent_type="monitoring",
            system_prompt="""You are an expert SRE/DevOps engineer with 15+ years of experience 
            in system monitoring, observability, and reliability engineering.
            
            Your expertise includes:
            • Prometheus metrics design
            • Grafana dashboard creation
            • Alert rule configuration
            • Distributed tracing (OpenTelemetry, Jaeger)
            • Log aggregation (ELK, Loki)
            • APM (Application Performance Monitoring)
            • SLI/SLO definition
            • Error tracking and analysis
            • Performance monitoring
            • Capacity planning
            
            When setting up monitoring, you:
            1. Define comprehensive metrics (RED: Rate, Errors, Duration)
            2. Create meaningful dashboards
            3. Configure actionable alerts
            4. Set up proper logging
            5. Implement distributed tracing
            
            Always produce production-ready monitoring configurations.""",
            model_preference=None,  # Use local models first
            strategy="quality_first"
        )
        
        # Get tool registry
        tool_registry = get_tool_registry()
        self.monitoring_tools = []
    
    async def _prepare_prompt(
        self,
        target: str,
        parameters: Dict[str, Any]
    ) -> str:
        """Prepare monitoring setup prompt"""
        
        monitoring_type = parameters.get("monitoring_type", "application")
        tools = parameters.get("tools", ["prometheus", "grafana"])
        app_info = parameters.get("app_info", {})
        
        prompt = f"""Design monitoring setup for: {target}

Monitoring Type: {monitoring_type}
Tools: {', '.join(tools)}

Application Information:
{json.dumps(app_info, indent=2) if app_info else "No app info provided"}

Please provide comprehensive monitoring configuration including:
1. Key metrics to track (RED metrics: Rate, Errors, Duration)
2. Prometheus metric definitions
3. Grafana dashboard JSON
4. Alert rules configuration
5. Logging strategy
6. Distributed tracing setup
7. SLI/SLO definitions

Format your response as JSON with the following structure:
{{
    "metrics": [
        {{
            "name": "...",
            "type": "counter|gauge|histogram",
            "description": "...",
            "labels": ["...", "..."]
        }}
    ],
    "dashboards": [
        {{
            "name": "...",
            "panels": [...]
        }}
    ],
    "alerts": [
        {{
            "name": "...",
            "condition": "...",
            "severity": "critical|warning|info"
        }}
    ],
    "logging_strategy": "...",
    "tracing_config": "...",
    "sli_slo": {{
        "sli": "...",
        "slo": "..."
    }}
}}"""
        
        return prompt
    
    async def _parse_response(self, response: str) -> Dict[str, Any]:
        """Parse AI response into structured format"""
        
        try:
            # Try to extract JSON from response
            if "```json" in response:
                json_start = response.find("```json") + 7
                json_end = response.find("```", json_start)
                response = response[json_start:json_end].strip()
            elif "```" in response:
                json_start = response.find("```") + 3
                json_end = response.find("```", json_start)
                response = response[json_start:json_end].strip()
            
            result = json.loads(response)
            
            return {
                "success": True,
                "monitoring_config": result,
                "metrics_count": len(result.get("metrics", [])),
                "dashboards_count": len(result.get("dashboards", [])),
                "alerts_count": len(result.get("alerts", []))
            }
        except json.JSONDecodeError:
            # Fallback: return raw response
            logger.warning("Failed to parse JSON response, returning raw text")
            return {
                "success": True,
                "monitoring_config": {
                    "raw_response": response,
                    "metrics": []
                },
                "metrics_count": 0,
                "dashboards_count": 0,
                "alerts_count": 0
            }
    
    async def _generate_prometheus_metrics(self, app_info: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Generate Prometheus metric definitions
        """
        metrics = []
        
        try:
            logger.info("MonitoringAgent: Generating Prometheus metrics")
            
            app_name = app_info.get("name", "app")
            
            # RED metrics (Rate, Errors, Duration)
            metrics.extend([
                {
                    "name": f"{app_name}_http_requests_total",
                    "type": "counter",
                    "description": "Total number of HTTP requests",
                    "labels": ["method", "endpoint", "status_code"],
                    "example": f'{app_name}_http_requests_total{{method="GET", endpoint="/api/v1/tasks", status_code="200"}} 1234'
                },
                {
                    "name": f"{app_name}_http_request_duration_seconds",
                    "type": "histogram",
                    "description": "HTTP request duration in seconds",
                    "labels": ["method", "endpoint"],
                    "buckets": [0.1, 0.5, 1.0, 2.5, 5.0, 10.0],
                    "example": f'{app_name}_http_request_duration_seconds_bucket{{method="GET", endpoint="/api/v1/tasks", le="0.5"}} 1000'
                },
                {
                    "name": f"{app_name}_http_errors_total",
                    "type": "counter",
                    "description": "Total number of HTTP errors",
                    "labels": ["method", "endpoint", "error_type"],
                    "example": f'{app_name}_http_errors_total{{method="POST", endpoint="/api/v1/tasks", error_type="validation"}} 5'
                }
            ])
            
            # Application-specific metrics
            metrics.extend([
                {
                    "name": f"{app_name}_tasks_processed_total",
                    "type": "counter",
                    "description": "Total number of tasks processed",
                    "labels": ["task_type", "status"],
                    "example": f'{app_name}_tasks_processed_total{{task_type="security_scan", status="success"}} 500'
                },
                {
                    "name": f"{app_name}_task_duration_seconds",
                    "type": "histogram",
                    "description": "Task execution duration",
                    "labels": ["task_type"],
                    "buckets": [1.0, 5.0, 10.0, 30.0, 60.0, 300.0],
                    "example": f'{app_name}_task_duration_seconds_bucket{{task_type="security_scan", le="30.0"}} 450'
                },
                {
                    "name": f"{app_name}_active_tasks",
                    "type": "gauge",
                    "description": "Number of currently active tasks",
                    "labels": ["task_type"],
                    "example": f'{app_name}_active_tasks{{task_type="security_scan"}} 10'
                },
                {
                    "name": f"{app_name}_agent_executions_total",
                    "type": "counter",
                    "description": "Total agent executions",
                    "labels": ["agent_id", "status"],
                    "example": f'{app_name}_agent_executions_total{{agent_id="security_expert", status="success"}} 1000'
                },
                {
                    "name": f"{app_name}_ai_provider_calls_total",
                    "type": "counter",
                    "description": "Total AI provider API calls",
                    "labels": ["provider", "model", "status"],
                    "example": f'{app_name}_ai_provider_calls_total{{provider="openai", model="gpt-4", status="success"}} 5000'
                },
                {
                    "name": f"{app_name}_ai_tokens_used_total",
                    "type": "counter",
                    "description": "Total AI tokens used",
                    "labels": ["provider", "model"],
                    "example": f'{app_name}_ai_tokens_used_total{{provider="openai", model="gpt-4"}} 1000000'
                },
                {
                    "name": f"{app_name}_database_queries_total",
                    "type": "counter",
                    "description": "Total database queries",
                    "labels": ["operation", "table", "status"],
                    "example": f'{app_name}_database_queries_total{{operation="select", table="tasks", status="success"}} 50000'
                },
                {
                    "name": f"{app_name}_database_query_duration_seconds",
                    "type": "histogram",
                    "description": "Database query duration",
                    "labels": ["operation", "table"],
                    "buckets": [0.01, 0.05, 0.1, 0.5, 1.0, 5.0],
                    "example": f'{app_name}_database_query_duration_seconds_bucket{{operation="select", table="tasks", le="0.1"}} 48000'
                },
                {
                    "name": f"{app_name}_cache_hits_total",
                    "type": "counter",
                    "description": "Total cache hits",
                    "labels": ["cache_type"],
                    "example": f'{app_name}_cache_hits_total{{cache_type="redis"}} 100000'
                },
                {
                    "name": f"{app_name}_cache_misses_total",
                    "type": "counter",
                    "description": "Total cache misses",
                    "labels": ["cache_type"],
                    "example": f'{app_name}_cache_misses_total{{cache_type="redis"}} 5000'
                }
            ])
            
            logger.info(f"MonitoringAgent: Generated {len(metrics)} Prometheus metrics")
        
        except Exception as e:
            logger.error(f"MonitoringAgent: Prometheus metrics generation failed: {e}", exc_info=True)
        
        return metrics
    
    async def _generate_grafana_dashboards(self, app_info: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Generate Grafana dashboard JSON configurations
        """
        dashboards = []
        
        try:
            logger.info("MonitoringAgent: Generating Grafana dashboards")
            
            app_name = app_info.get("name", "app")
            
            # System Overview Dashboard
            system_dashboard = {
                "dashboard": {
                    "title": f"{app_name} - System Overview",
                    "tags": ["system", "overview"],
                    "timezone": "browser",
                    "panels": [
                        {
                            "id": 1,
                            "title": "HTTP Request Rate",
                            "type": "graph",
                            "targets": [
                                {
                                    "expr": f"rate({app_name}_http_requests_total[5m])",
                                    "legendFormat": "{{method}} {{endpoint}}"
                                }
                            ]
                        },
                        {
                            "id": 2,
                            "title": "HTTP Error Rate",
                            "type": "graph",
                            "targets": [
                                {
                                    "expr": f"rate({app_name}_http_errors_total[5m])",
                                    "legendFormat": "{{error_type}}"
                                }
                            ]
                        },
                        {
                            "id": 3,
                            "title": "HTTP Request Duration (p95)",
                            "type": "graph",
                            "targets": [
                                {
                                    "expr": f"histogram_quantile(0.95, rate({app_name}_http_request_duration_seconds_bucket[5m]))",
                                    "legendFormat": "p95"
                                }
                            ]
                        },
                        {
                            "id": 4,
                            "title": "Active Tasks",
                            "type": "stat",
                            "targets": [
                                {
                                    "expr": f"sum({app_name}_active_tasks)",
                                    "legendFormat": "Active Tasks"
                                }
                            ]
                        }
                    ],
                    "refresh": "10s",
                    "time": {
                        "from": "now-1h",
                        "to": "now"
                    }
                }
            }
            dashboards.append(system_dashboard)
            
            # Task Analytics Dashboard
            task_dashboard = {
                "dashboard": {
                    "title": f"{app_name} - Task Analytics",
                    "tags": ["tasks", "analytics"],
                    "panels": [
                        {
                            "id": 1,
                            "title": "Tasks Processed",
                            "type": "graph",
                            "targets": [
                                {
                                    "expr": f"rate({app_name}_tasks_processed_total[5m])",
                                    "legendFormat": "{{task_type}} - {{status}}"
                                }
                            ]
                        },
                        {
                            "id": 2,
                            "title": "Task Duration",
                            "type": "graph",
                            "targets": [
                                {
                                    "expr": f"histogram_quantile(0.95, rate({app_name}_task_duration_seconds_bucket[5m]))",
                                    "legendFormat": "p95 - {{task_type}}"
                                }
                            ]
                        }
                    ]
                }
            }
            dashboards.append(task_dashboard)
            
            # Agent Performance Dashboard
            agent_dashboard = {
                "dashboard": {
                    "title": f"{app_name} - Agent Performance",
                    "tags": ["agents", "performance"],
                    "panels": [
                        {
                            "id": 1,
                            "title": "Agent Executions",
                            "type": "graph",
                            "targets": [
                                {
                                    "expr": f"rate({app_name}_agent_executions_total[5m])",
                                    "legendFormat": "{{agent_id}} - {{status}}"
                                }
                            ]
                        }
                    ]
                }
            }
            dashboards.append(agent_dashboard)
            
            logger.info(f"MonitoringAgent: Generated {len(dashboards)} Grafana dashboards")
        
        except Exception as e:
            logger.error(f"MonitoringAgent: Grafana dashboard generation failed: {e}", exc_info=True)
        
        return dashboards
    
    async def _generate_alert_rules(self, app_info: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Generate Prometheus alert rules
        """
        alert_rules = []
        
        try:
            logger.info("MonitoringAgent: Generating alert rules")
            
            app_name = app_info.get("name", "app")
            
            # Critical alerts
            alert_rules.extend([
                {
                    "alert": f"{app_name}_HighErrorRate",
                    "expr": f"rate({app_name}_http_errors_total[5m]) > 0.1",
                    "for": "5m",
                    "labels": {
                        "severity": "critical"
                    },
                    "annotations": {
                        "summary": f"{app_name} has high error rate",
                        "description": "Error rate is above 0.1 errors/second for 5 minutes"
                    }
                },
                {
                    "alert": f"{app_name}_HighResponseTime",
                    "expr": f"histogram_quantile(0.95, rate({app_name}_http_request_duration_seconds_bucket[5m])) > 2.0",
                    "for": "5m",
                    "labels": {
                        "severity": "critical"
                    },
                    "annotations": {
                        "summary": f"{app_name} has high response time",
                        "description": "95th percentile response time is above 2 seconds"
                    }
                },
                {
                    "alert": f"{app_name}_TaskFailureRate",
                    "expr": f"rate({app_name}_tasks_processed_total{{status=\"failed\"}}[5m]) / rate({app_name}_tasks_processed_total[5m]) > 0.1",
                    "for": "10m",
                    "labels": {
                        "severity": "warning"
                    },
                    "annotations": {
                        "summary": f"{app_name} has high task failure rate",
                        "description": "Task failure rate is above 10%"
                    }
                },
                {
                    "alert": f"{app_name}_DatabaseSlowQueries",
                    "expr": f"histogram_quantile(0.95, rate({app_name}_database_query_duration_seconds_bucket[5m])) > 1.0",
                    "for": "5m",
                    "labels": {
                        "severity": "warning"
                    },
                    "annotations": {
                        "summary": f"{app_name} has slow database queries",
                        "description": "95th percentile database query time is above 1 second"
                    }
                },
                {
                    "alert": f"{app_name}_LowCacheHitRate",
                    "expr": f"rate({app_name}_cache_hits_total[5m]) / (rate({app_name}_cache_hits_total[5m]) + rate({app_name}_cache_misses_total[5m])) < 0.7",
                    "for": "10m",
                    "labels": {
                        "severity": "warning"
                    },
                    "annotations": {
                        "summary": f"{app_name} has low cache hit rate",
                        "description": "Cache hit rate is below 70%"
                    }
                },
                {
                    "alert": f"{app_name}_AIProviderFailures",
                    "expr": f"rate({app_name}_ai_provider_calls_total{{status=\"failed\"}}[5m]) > 0.05",
                    "for": "5m",
                    "labels": {
                        "severity": "critical"
                    },
                    "annotations": {
                        "summary": f"{app_name} AI provider failures",
                        "description": "AI provider failure rate is above 0.05 failures/second"
                    }
                }
            ])
            
            logger.info(f"MonitoringAgent: Generated {len(alert_rules)} alert rules")
        
        except Exception as e:
            logger.error(f"MonitoringAgent: Alert rules generation failed: {e}", exc_info=True)
        
        return alert_rules
    
    async def _define_sli_slo(self, app_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        Define SLI/SLO (Service Level Indicators/Objectives)
        """
        sli_slo = {
            "slis": [],
            "slos": [],
            "error_budget": {},
            "error": None
        }
        
        try:
            logger.info("MonitoringAgent: Defining SLI/SLO")
            
            app_name = app_info.get("name", "app")
            
            # Define SLIs
            sli_slo["slis"] = [
                {
                    "name": "Availability",
                    "description": "Percentage of successful HTTP requests",
                    "metric": f"sum(rate({app_name}_http_requests_total{{status_code!~\"5..\"}}[5m])) / sum(rate({app_name}_http_requests_total[5m]))",
                    "target": 0.999  # 99.9% availability
                },
                {
                    "name": "Latency",
                    "description": "Percentage of requests under 500ms",
                    "metric": f"sum(rate({app_name}_http_request_duration_seconds_bucket{{le=\"0.5\"}}[5m])) / sum(rate({app_name}_http_request_duration_seconds_bucket[5m]))",
                    "target": 0.95  # 95% of requests under 500ms
                },
                {
                    "name": "Error Rate",
                    "description": "Percentage of requests that are errors",
                    "metric": f"sum(rate({app_name}_http_errors_total[5m])) / sum(rate({app_name}_http_requests_total[5m]))",
                    "target": 0.001  # 0.1% error rate
                }
            ]
            
            # Define SLOs
            sli_slo["slos"] = [
                {
                    "name": "Availability SLO",
                    "sli": "Availability",
                    "target": "99.9%",
                    "window": "30 days",
                    "description": "99.9% of requests should be successful"
                },
                {
                    "name": "Latency SLO",
                    "sli": "Latency",
                    "target": "95%",
                    "window": "30 days",
                    "description": "95% of requests should complete in under 500ms"
                },
                {
                    "name": "Error Rate SLO",
                    "sli": "Error Rate",
                    "target": "< 0.1%",
                    "window": "30 days",
                    "description": "Error rate should be below 0.1%"
                }
            ]
            
            # Calculate error budget
            sli_slo["error_budget"] = {
                "availability": {
                    "target": 0.999,
                    "window_days": 30,
                    "allowed_downtime_minutes": 43.2,  # 0.1% of 30 days
                    "current_usage": "0%"
                },
                "latency": {
                    "target": 0.95,
                    "window_days": 30,
                    "allowed_slow_requests_percent": 5.0,
                    "current_usage": "0%"
                }
            }
            
            logger.info(f"MonitoringAgent: Defined {len(sli_slo['slis'])} SLIs and {len(sli_slo['slos'])} SLOs")
        
        except Exception as e:
            sli_slo["error"] = f"SLI/SLO definition failed: {str(e)}"
            logger.error(f"MonitoringAgent: SLI/SLO definition failed: {e}", exc_info=True)
        
        return sli_slo
    
    async def _recommend_observability_stack(self, app_info: Dict[str, Any]) -> List[str]:
        """
        Recommend observability tools stack
        """
        stack = []
        
        try:
            logger.info("MonitoringAgent: Recommending observability stack")
            
            # Core stack
            stack.extend([
                "Prometheus - Metrics collection and storage",
                "Grafana - Visualization and dashboards",
                "Alertmanager - Alert routing and management"
            ])
            
            # Logging stack
            stack.extend([
                "Loki - Log aggregation",
                "Promtail - Log shipping"
            ])
            
            # Tracing stack
            stack.extend([
                "Jaeger - Distributed tracing",
                "OpenTelemetry - Instrumentation"
            ])
            
            # Additional tools
            stack.extend([
                "cAdvisor - Container metrics",
                "Node Exporter - System metrics"
            ])
            
            logger.info(f"MonitoringAgent: Recommended {len(stack)} observability tools")
        
        except Exception as e:
            logger.error(f"MonitoringAgent: Observability stack recommendation failed: {e}", exc_info=True)
        
        return stack
    
    async def execute(
        self,
        task_id: str,
        target: str,
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute enhanced monitoring setup with config generation
        Overrides BaseAgent.execute to add comprehensive monitoring capabilities
        """
        execution_start = time.time()
        
        try:
            logger.info(f"MonitoringAgent: Starting enhanced monitoring setup for {target}")
            
            app_info = parameters.get("app_info", {})
            
            # STEP 1: Generate Prometheus metrics
            prometheus_metrics = []
            if parameters.get("generate_metrics", True):
                prometheus_metrics = await self._generate_prometheus_metrics(app_info)
            
            # STEP 2: Generate Grafana dashboards
            grafana_dashboards = []
            if parameters.get("generate_dashboards", True):
                grafana_dashboards = await self._generate_grafana_dashboards(app_info)
            
            # STEP 3: Generate alert rules
            alert_rules = []
            if parameters.get("generate_alerts", True):
                alert_rules = await self._generate_alert_rules(app_info)
            
            # STEP 4: Define SLI/SLO
            sli_slo = {}
            if parameters.get("define_sli_slo", True):
                sli_slo = await self._define_sli_slo(app_info)
            
            # STEP 5: Recommend observability stack
            observability_stack = []
            if parameters.get("recommend_stack", True):
                observability_stack = await self._recommend_observability_stack(app_info)
            
            # STEP 6: Prepare enhanced prompt
            prompt = await self._prepare_prompt(
                target, parameters, prometheus_metrics, grafana_dashboards, alert_rules, sli_slo, observability_stack
            )
            
            # STEP 7: Call AI via router
            logger.info(f"MonitoringAgent: Calling AI with monitoring configuration data")
            
            ai_response = await self.ai_router.generate_with_fallback(
                prompt=prompt,
                model_preference=self.model_preference,
                max_tokens=4000,
                temperature=0.3,
                system_prompt=self.system_prompt,
                strategy=self.strategy
            )
            
            logger.info(f"MonitoringAgent: Got response from {ai_response.provider} "
                       f"({ai_response.tokens_used} tokens, ${ai_response.cost_usd:.4f})")
            
            # STEP 8: Parse response
            parsed_result = await self._parse_response(ai_response.content)
            
            # STEP 9: Merge generated configs with AI results
            if parsed_result.get("success") and parsed_result.get("monitoring_config"):
                monitoring_config = parsed_result["monitoring_config"]
                
                # Merge Prometheus metrics
                if prometheus_metrics:
                    monitoring_config["prometheus_metrics"] = prometheus_metrics
                
                # Merge Grafana dashboards
                if grafana_dashboards:
                    monitoring_config["grafana_dashboards"] = grafana_dashboards
                
                # Merge alert rules
                if alert_rules:
                    monitoring_config["alert_rules"] = alert_rules
                
                # Merge SLI/SLO
                if sli_slo:
                    monitoring_config["sli_slo"] = sli_slo
                
                # Merge observability stack
                if observability_stack:
                    monitoring_config["observability_stack"] = observability_stack
            
            execution_duration = time.time() - execution_start
            
            # Update stats
            self.executions += 1
            self.successes += 1
            self.total_duration += execution_duration
            
            return {
                "success": parsed_result.get("success", True),
                "result": parsed_result.get("monitoring_config", {}),
                "output": parsed_result.get("monitoring_config", {}),
                "quality_score": 0.8,
                "duration": execution_duration,
                "tokens_used": ai_response.tokens_used,
                "cost_usd": ai_response.cost_usd,
                "provider": ai_response.provider,
                "summary": f"Generated monitoring config with {len(prometheus_metrics)} metrics, {len(grafana_dashboards)} dashboards, {len(alert_rules)} alerts"
            }
        
        except Exception as e:
            execution_duration = time.time() - execution_start
            logger.error(f"MonitoringAgent: Execution failed: {e}", exc_info=True)
            
            self.executions += 1
            self.total_duration += execution_duration
            
            return {
                "success": False,
                "error": str(e),
                "duration": execution_duration,
                "quality_score": 0.0
            }
    
    async def _prepare_prompt(
        self,
        target: str,
        parameters: Dict[str, Any],
        prometheus_metrics: List[Dict[str, Any]] = None,
        grafana_dashboards: List[Dict[str, Any]] = None,
        alert_rules: List[Dict[str, Any]] = None,
        sli_slo: Dict[str, Any] = None,
        observability_stack: List[str] = None
    ) -> str:
        """Prepare enhanced monitoring prompt with all generated configs"""
        
        monitoring_type = parameters.get("monitoring_type", "application")
        tools = parameters.get("tools", ["prometheus", "grafana"])
        app_info = parameters.get("app_info", {})
        
        # Build context from generated configs
        monitoring_context = ""
        
        if prometheus_metrics:
            monitoring_context += f"\n=== GENERATED PROMETHEUS METRICS ===\n"
            monitoring_context += f"Metrics Defined: {len(prometheus_metrics)}\n"
            for metric in prometheus_metrics[:5]:
                monitoring_context += f"  - {metric.get('name')} ({metric.get('type')}): {metric.get('description', '')}\n"
        
        if grafana_dashboards:
            monitoring_context += f"\n=== GENERATED GRAFANA DASHBOARDS ===\n"
            monitoring_context += f"Dashboards: {len(grafana_dashboards)}\n"
            for dashboard in grafana_dashboards:
                dashboard_data = dashboard.get("dashboard", {})
                monitoring_context += f"  - {dashboard_data.get('title', 'Dashboard')}: {len(dashboard_data.get('panels', []))} panels\n"
        
        if alert_rules:
            monitoring_context += f"\n=== GENERATED ALERT RULES ===\n"
            monitoring_context += f"Alert Rules: {len(alert_rules)}\n"
            for alert in alert_rules[:5]:
                monitoring_context += f"  - {alert.get('alert')}: {alert.get('annotations', {}).get('summary', '')}\n"
        
        if sli_slo:
            monitoring_context += f"\n=== SLI/SLO DEFINITIONS ===\n"
            monitoring_context += f"SLIs: {len(sli_slo.get('slis', []))}\n"
            monitoring_context += f"SLOs: {len(sli_slo.get('slos', []))}\n"
            if sli_slo.get("error_budget"):
                monitoring_context += f"Error Budget: Defined\n"
        
        if observability_stack:
            monitoring_context += f"\n=== RECOMMENDED OBSERVABILITY STACK ===\n"
            monitoring_context += f"Tools: {len(observability_stack)}\n"
            for tool in observability_stack[:5]:
                monitoring_context += f"  - {tool}\n"
        
        prompt = f"""Design comprehensive monitoring setup for: {target}

Monitoring Type: {monitoring_type}
Tools: {', '.join(tools)}

{monitoring_context}

Application Information:
{json.dumps(app_info, indent=2) if app_info else "No app info provided"}

Based on the GENERATED MONITORING CONFIGURATION above (Prometheus metrics, Grafana dashboards, alert rules, SLI/SLO), please provide:
1. Complete monitoring strategy (reference generated metrics and dashboards)
2. Metric collection best practices (use generated Prometheus metrics)
3. Dashboard design recommendations (enhance generated dashboards)
4. Alert strategy (review generated alert rules)
5. SLI/SLO implementation (use defined SLI/SLO)
6. Logging strategy
7. Distributed tracing setup
8. Production monitoring checklist

IMPORTANT: 
- Reference the generated Prometheus metrics, Grafana dashboards, and alert rules
- Use the defined SLI/SLO for service level objectives
- Ensure all configurations are production-ready

Format your response as JSON with the following structure:
{{
    "metrics": {json.dumps(prometheus_metrics) if prometheus_metrics else []},
    "dashboards": {json.dumps(grafana_dashboards) if grafana_dashboards else []},
    "alerts": {json.dumps(alert_rules) if alert_rules else []},
    "logging_strategy": "...",
    "tracing_config": "...",
    "sli_slo": {json.dumps(sli_slo) if sli_slo else {}},
    "observability_stack": {json.dumps(observability_stack) if observability_stack else []}
}}"""
        
        return prompt

