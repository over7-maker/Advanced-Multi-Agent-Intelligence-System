"""
Performance Agent - Specialized agent for performance analysis and optimization
Implements PART_3 requirements
"""

import json
import logging
import psutil
import time
from typing import Any, Dict

from src.amas.agents.base_agent import BaseAgent
from src.amas.agents.tools import get_tool_registry
from src.amas.agents.utils.json_parser import JSONParser
from src.amas.agents.schemas import PerformanceReport

logger = logging.getLogger(__name__)


class PerformanceAgent(BaseAgent):
    """
    Performance Agent
    
    Specializes in:
    - Performance analysis
    - Bottleneck identification
    - Optimization recommendations
    - Resource usage analysis
    - Scalability assessment
    """
    
    def __init__(self):
        super().__init__(
            agent_id="performance_agent",
            name="Performance Agent",
            agent_type="performance",
            system_prompt="""You are an expert performance engineer with 15+ years of experience 
            in system optimization, performance analysis, and scalability engineering.
            
            Your expertise includes:
            • Performance profiling and bottleneck identification
            • Database query optimization
            • API response time optimization
            • Memory and CPU usage analysis
            • Caching strategy recommendations
            • Load balancing and scaling strategies
            • Network performance optimization
            • Code-level performance improvements
            • Resource utilization analysis
            • Capacity planning
            
            When analyzing performance, you:
            1. Identify specific bottlenecks with metrics
            2. Provide optimization recommendations with expected impact
            3. Suggest caching strategies where appropriate
            4. Recommend scaling approaches
            5. Prioritize optimizations by impact vs effort
            
            Always provide actionable, data-driven recommendations.""",
            model_preference=None,  # Use local models first
            strategy="quality_first"
        )
        
        # Get tool registry
        tool_registry = get_tool_registry()
        self.performance_tools = ["api_fetcher"]
    
    async def _prepare_prompt(
        self,
        target: str,
        parameters: Dict[str, Any]
    ) -> str:
        """Prepare performance analysis prompt"""
        
        task_type = parameters.get("task_type", "performance_analysis")
        metrics = parameters.get("metrics", {})
        context = parameters.get("context", {})
        
        prompt = f"""Analyze the performance of: {target}

Task Type: {task_type}

Current Metrics:
{json.dumps(metrics, indent=2) if metrics else "No metrics provided"}

Context:
{json.dumps(context, indent=2) if context else "No additional context"}

Please provide:
1. Performance bottlenecks identified
2. Root cause analysis
3. Optimization recommendations with expected impact
4. Priority ranking (High/Medium/Low)
5. Implementation effort estimate
6. Expected performance improvement percentage

Format your response as JSON with the following structure:
{{
    "bottlenecks": [
        {{
            "name": "...",
            "severity": "Critical|High|Medium|Low",
            "impact": "...",
            "location": "..."
        }}
    ],
    "optimizations": [
        {{
            "recommendation": "...",
            "impact": "High|Medium|Low",
            "effort": "High|Medium|Low",
            "expected_improvement": "X%",
            "implementation_steps": ["...", "..."]
        }}
    ],
    "summary": "...",
    "priority_actions": ["...", "..."]
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
                "analysis": result,
                "bottlenecks_count": len(result.get("bottlenecks", [])),
                "optimizations_count": len(result.get("optimizations", [])),
                "critical_issues": [
                    b for b in result.get("bottlenecks", [])
                    if b.get("severity") in ["Critical", "High"]
                ]
            }
        except json.JSONDecodeError:
            # Fallback: return raw response
            logger.warning("Failed to parse JSON response, returning raw text")
            return {
                "success": True,
                "analysis": {"raw_response": response},
                "bottlenecks_count": 0,
                "optimizations_count": 0
            }
    
    async def _collect_metrics(self, target: str, duration: int = 10) -> Dict[str, Any]:
        """
        Collect real-time performance metrics
        
        Args:
            target: Target to monitor (URL, service name, etc.)
            duration: Duration to collect metrics in seconds
        """
        metrics = {
            "target": target,
            "system_metrics": {},
            "network_metrics": {},
            "error": None
        }
        
        try:
            logger.info(f"PerformanceAgent: Collecting metrics for {target} for {duration} seconds")
            
            # System metrics
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            metrics["system_metrics"] = {
                "cpu_percent": cpu_percent,
                "memory_percent": memory.percent,
                "memory_available_gb": memory.available / (1024**3),
                "disk_percent": disk.percent,
                "disk_free_gb": disk.free / (1024**3)
            }
            
            # Network metrics (if target is a URL)
            if target.startswith(("http://", "https://")):
                import aiohttp
                start_time = time.time()
                
                async with aiohttp.ClientSession() as session:
                    try:
                        async with session.get(target, timeout=aiohttp.ClientTimeout(total=10)) as response:
                            response_time = time.time() - start_time
                            content_length = int(response.headers.get("content-length", 0))
                            
                            metrics["network_metrics"] = {
                                "response_time_ms": response_time * 1000,
                                "status_code": response.status,
                                "content_length_bytes": content_length,
                                "headers": dict(response.headers)
                            }
                    except Exception as e:
                        metrics["network_metrics"]["error"] = str(e)
            
            logger.info(f"PerformanceAgent: Metrics collected: CPU={cpu_percent}%, Memory={memory.percent}%")
        
        except Exception as e:
            metrics["error"] = f"Metrics collection failed: {str(e)}"
            logger.error(f"PerformanceAgent: Metrics collection failed: {e}", exc_info=True)
        
        return metrics
    
    async def _analyze_profiling_data(self, profiling_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze profiling data to identify bottlenecks
        """
        profiling_analysis = {
            "slow_functions": [],
            "memory_hotspots": [],
            "cpu_hotspots": [],
            "recommendations": [],
            "error": None
        }
        
        try:
            logger.info("PerformanceAgent: Analyzing profiling data")
            
            # Analyze function call times
            if profiling_data.get("function_times"):
                function_times = profiling_data["function_times"]
                sorted_functions = sorted(function_times.items(), key=lambda x: x[1], reverse=True)
                
                for func_name, call_time in sorted_functions[:10]:  # Top 10 slowest
                    profiling_analysis["slow_functions"].append({
                        "function": func_name,
                        "total_time_ms": call_time * 1000,
                        "severity": "High" if call_time > 1.0 else "Medium" if call_time > 0.5 else "Low"
                    })
            
            # Analyze memory usage
            if profiling_data.get("memory_usage"):
                memory_usage = profiling_data["memory_usage"]
                sorted_memory = sorted(memory_usage.items(), key=lambda x: x[1], reverse=True)
                
                for item, memory_mb in sorted_memory[:10]:  # Top 10 memory consumers
                    profiling_analysis["memory_hotspots"].append({
                        "item": item,
                        "memory_mb": memory_mb,
                        "severity": "High" if memory_mb > 100 else "Medium" if memory_mb > 50 else "Low"
                    })
            
            # Generate recommendations
            if profiling_analysis["slow_functions"]:
                profiling_analysis["recommendations"].append({
                    "type": "optimization",
                    "priority": "High",
                    "recommendation": "Optimize slow functions identified in profiling",
                    "functions": [f["function"] for f in profiling_analysis["slow_functions"][:5]]
                })
            
            logger.info(f"PerformanceAgent: Profiling analysis completed: "
                       f"{len(profiling_analysis['slow_functions'])} slow functions identified")
        
        except Exception as e:
            profiling_analysis["error"] = f"Profiling analysis failed: {str(e)}"
            logger.error(f"PerformanceAgent: Profiling analysis failed: {e}", exc_info=True)
        
        return profiling_analysis
    
    async def _check_database_queries(self, queries: List[str] = None) -> Dict[str, Any]:
        """
        Analyze database queries for performance issues
        """
        query_analysis = {
            "queries_analyzed": len(queries) if queries else 0,
            "slow_queries": [],
            "missing_indexes": [],
            "optimization_suggestions": [],
            "error": None
        }
        
        try:
            logger.info(f"PerformanceAgent: Analyzing {len(queries) if queries else 0} database queries")
            
            if queries:
                for i, query in enumerate(queries):
                    query_lower = query.lower()
                    
                    # Check for common performance issues
                    issues = []
                    
                    # Missing WHERE clause in SELECT
                    if query_lower.startswith("select") and "where" not in query_lower:
                        issues.append("SELECT without WHERE clause - may scan entire table")
                    
                    # LIKE with leading wildcard
                    if "like" in query_lower and query_lower.find("like") < query_lower.find("%"):
                        if query_lower[query_lower.find("like") + 4:query_lower.find("%")].strip().startswith("%"):
                            issues.append("LIKE with leading wildcard - cannot use index")
                    
                    # SELECT *
                    if "select *" in query_lower:
                        issues.append("SELECT * - fetches unnecessary columns")
                    
                    # Missing LIMIT
                    if query_lower.startswith("select") and "limit" not in query_lower and "top" not in query_lower:
                        issues.append("SELECT without LIMIT - may return large result set")
                    
                    # JOIN without indexes
                    if "join" in query_lower:
                        issues.append("JOIN query - ensure foreign keys are indexed")
                    
                    if issues:
                        query_analysis["slow_queries"].append({
                            "query_index": i,
                            "query": query[:100] + "..." if len(query) > 100 else query,
                            "issues": issues,
                            "severity": "High" if len(issues) >= 3 else "Medium" if len(issues) >= 2 else "Low"
                        })
                
                # Generate optimization suggestions
                if query_analysis["slow_queries"]:
                    query_analysis["optimization_suggestions"].append({
                        "type": "indexing",
                        "recommendation": "Add indexes on frequently queried columns",
                        "priority": "High"
                    })
                    query_analysis["optimization_suggestions"].append({
                        "type": "query_optimization",
                        "recommendation": "Optimize queries identified as slow",
                        "priority": "Medium"
                    })
            
            logger.info(f"PerformanceAgent: Query analysis completed: "
                       f"{len(query_analysis['slow_queries'])} slow queries identified")
        
        except Exception as e:
            query_analysis["error"] = f"Query analysis failed: {str(e)}"
            logger.error(f"PerformanceAgent: Query analysis failed: {e}", exc_info=True)
        
        return query_analysis
    
    async def _analyze_api_response_times(self, api_endpoints: List[str] = None) -> Dict[str, Any]:
        """
        Analyze API response times
        """
        api_analysis = {
            "endpoints_tested": len(api_endpoints) if api_endpoints else 0,
            "slow_endpoints": [],
            "average_response_time": 0.0,
            "error": None
        }
        
        try:
            logger.info(f"PerformanceAgent: Analyzing {len(api_endpoints) if api_endpoints else 0} API endpoints")
            
            if api_endpoints:
                import aiohttp
                response_times = []
                
                async with aiohttp.ClientSession() as session:
                    for endpoint in api_endpoints:
                        try:
                            start_time = time.time()
                            async with session.get(endpoint, timeout=aiohttp.ClientTimeout(total=10)) as response:
                                response_time = (time.time() - start_time) * 1000  # Convert to ms
                                response_times.append(response_time)
                                
                                if response_time > 500:  # Slow if > 500ms
                                    api_analysis["slow_endpoints"].append({
                                        "endpoint": endpoint,
                                        "response_time_ms": response_time,
                                        "status_code": response.status,
                                        "severity": "Critical" if response_time > 2000 else "High" if response_time > 1000 else "Medium"
                                    })
                        except Exception as e:
                            logger.debug(f"Failed to test endpoint {endpoint}: {e}")
                
                if response_times:
                    api_analysis["average_response_time"] = sum(response_times) / len(response_times)
            
            logger.info(f"PerformanceAgent: API analysis completed: "
                       f"{len(api_analysis['slow_endpoints'])} slow endpoints identified")
        
        except Exception as e:
            api_analysis["error"] = f"API analysis failed: {str(e)}"
            logger.error(f"PerformanceAgent: API analysis failed: {e}", exc_info=True)
        
        return api_analysis
    
    async def execute(
        self,
        task_id: str,
        target: str,
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute enhanced performance analysis with real metrics collection
        Overrides BaseAgent.execute to add comprehensive performance analysis
        """
        execution_start = time.time()
        
        try:
            logger.info(f"PerformanceAgent: Starting enhanced performance analysis for {target}")
            
            # STEP 1: Collect real-time metrics
            metrics_data = {}
            if parameters.get("collect_metrics", True):
                duration = parameters.get("metrics_duration", 10)
                metrics_data = await self._collect_metrics(target, duration)
            
            # STEP 2: Analyze profiling data (if provided)
            profiling_analysis = {}
            profiling_data = parameters.get("profiling_data")
            if profiling_data:
                profiling_analysis = await self._analyze_profiling_data(profiling_data)
            
            # STEP 3: Analyze database queries (if provided)
            query_analysis = {}
            queries = parameters.get("database_queries")
            if queries:
                query_analysis = await self._check_database_queries(queries)
            
            # STEP 4: Analyze API response times (if provided)
            api_analysis = {}
            api_endpoints = parameters.get("api_endpoints")
            if api_endpoints:
                api_analysis = await self._analyze_api_response_times(api_endpoints)
            
            # STEP 5: Prepare enhanced prompt
            prompt = await self._prepare_prompt(
                target, parameters, metrics_data, profiling_analysis, query_analysis, api_analysis
            )
            
            # STEP 6: Call AI via router
            logger.info(f"PerformanceAgent: Calling AI with performance analysis data")
            
            ai_response = await self.ai_router.generate_with_fallback(
                prompt=prompt,
                model_preference=self.model_preference,
                max_tokens=4000,
                temperature=0.3,
                system_prompt=self.system_prompt,
                strategy=self.strategy
            )
            
            logger.info(f"PerformanceAgent: Got response from {ai_response.provider} "
                       f"({ai_response.tokens_used} tokens, ${ai_response.cost_usd:.4f})")
            
            # STEP 7: Parse response
            parsed_result = await self._parse_response(ai_response.content)
            
            # STEP 8: Merge real analysis data with AI results
            if parsed_result.get("success") and parsed_result.get("analysis"):
                analysis = parsed_result["analysis"]
                
                # Merge metrics
                if metrics_data:
                    analysis["real_metrics"] = metrics_data
                
                # Merge profiling analysis
                if profiling_analysis:
                    analysis["profiling_analysis"] = profiling_analysis
                
                # Merge query analysis
                if query_analysis:
                    analysis["database_analysis"] = query_analysis
                
                # Merge API analysis
                if api_analysis:
                    analysis["api_analysis"] = api_analysis
            
            execution_duration = time.time() - execution_start
            
            # Update stats
            self.executions += 1
            self.successes += 1
            self.total_duration += execution_duration
            
            return {
                "success": parsed_result.get("success", True),
                "result": parsed_result.get("analysis", {}),
                "output": parsed_result.get("analysis", {}),
                "quality_score": 0.8,
                "duration": execution_duration,
                "tokens_used": ai_response.tokens_used,
                "cost_usd": ai_response.cost_usd,
                "provider": ai_response.provider,
                "summary": parsed_result.get("analysis", {}).get("summary", "Performance analysis completed")
            }
        
        except Exception as e:
            execution_duration = time.time() - execution_start
            logger.error(f"PerformanceAgent: Execution failed: {e}", exc_info=True)
            
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
        metrics_data: Dict[str, Any] = None,
        profiling_analysis: Dict[str, Any] = None,
        query_analysis: Dict[str, Any] = None,
        api_analysis: Dict[str, Any] = None
    ) -> str:
        """Prepare enhanced performance analysis prompt with all collected data"""
        
        task_type = parameters.get("task_type", "performance_analysis")
        metrics = parameters.get("metrics", {})
        context = parameters.get("context", {})
        
        # Build context from collected data
        analysis_context = ""
        
        if metrics_data:
            analysis_context += f"\n=== REAL-TIME METRICS ===\n"
            if metrics_data.get("system_metrics"):
                sys_metrics = metrics_data["system_metrics"]
                analysis_context += f"CPU Usage: {sys_metrics.get('cpu_percent', 0)}%\n"
                analysis_context += f"Memory Usage: {sys_metrics.get('memory_percent', 0)}%\n"
                analysis_context += f"Available Memory: {sys_metrics.get('memory_available_gb', 0):.2f} GB\n"
            if metrics_data.get("network_metrics"):
                net_metrics = metrics_data["network_metrics"]
                analysis_context += f"API Response Time: {net_metrics.get('response_time_ms', 0):.2f} ms\n"
                analysis_context += f"HTTP Status: {net_metrics.get('status_code', 'N/A')}\n"
        
        if profiling_analysis:
            analysis_context += f"\n=== PROFILING ANALYSIS ===\n"
            if profiling_analysis.get("slow_functions"):
                analysis_context += f"Slow Functions: {len(profiling_analysis['slow_functions'])}\n"
                for func in profiling_analysis["slow_functions"][:5]:
                    analysis_context += f"  - {func['function']}: {func['total_time_ms']:.2f} ms ({func['severity']})\n"
            if profiling_analysis.get("memory_hotspots"):
                analysis_context += f"Memory Hotspots: {len(profiling_analysis['memory_hotspots'])}\n"
        
        if query_analysis:
            analysis_context += f"\n=== DATABASE QUERY ANALYSIS ===\n"
            analysis_context += f"Queries Analyzed: {query_analysis.get('queries_analyzed', 0)}\n"
            analysis_context += f"Slow Queries: {len(query_analysis.get('slow_queries', []))}\n"
            if query_analysis.get("optimization_suggestions"):
                for suggestion in query_analysis["optimization_suggestions"]:
                    analysis_context += f"  - {suggestion.get('recommendation')} ({suggestion.get('priority')})\n"
        
        if api_analysis:
            analysis_context += f"\n=== API RESPONSE TIME ANALYSIS ===\n"
            analysis_context += f"Endpoints Tested: {api_analysis.get('endpoints_tested', 0)}\n"
            analysis_context += f"Average Response Time: {api_analysis.get('average_response_time', 0):.2f} ms\n"
            analysis_context += f"Slow Endpoints: {len(api_analysis.get('slow_endpoints', []))}\n"
        
        prompt = f"""Analyze the performance of: {target}

Task Type: {task_type}

{analysis_context}

Current Metrics (from parameters):
{json.dumps(metrics, indent=2) if metrics else "No additional metrics provided"}

Context:
{json.dumps(context, indent=2) if context else "No additional context"}

Based on the REAL PERFORMANCE DATA collected above, please provide:
1. Performance bottlenecks identified (use profiling and metrics data)
2. Root cause analysis (reference specific data points)
3. Optimization recommendations with expected impact
4. Priority ranking (High/Medium/Low)
5. Implementation effort estimate
6. Expected performance improvement percentage

IMPORTANT: Reference the specific findings from the analysis data above (slow functions, query issues, API response times, etc.)

Format your response as JSON with the following structure:
{{
    "bottlenecks": [
        {{
            "name": "...",
            "severity": "Critical|High|Medium|Low",
            "impact": "...",
            "location": "...",
            "evidence": "Reference to specific data point"
        }}
    ],
    "optimizations": [
        {{
            "recommendation": "...",
            "impact": "High|Medium|Low",
            "effort": "High|Medium|Low",
            "expected_improvement": "X%",
            "implementation_steps": ["...", "..."],
            "based_on": "Reference to analysis data"
        }}
    ],
    "summary": "...",
    "priority_actions": ["...", "..."]
}}"""
        
        return prompt

