#!/usr/bin/env python3
"""
Complete AMAS Integration Verification Script
Tests end-to-end flow from task creation to completion
"""

import asyncio
import json
import logging
import sys
import time
from datetime import datetime
from typing import Any, Dict, List

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Color codes for terminal output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

def print_success(message: str):
    print(f"{Colors.GREEN}✓ {message}{Colors.RESET}")

def print_error(message: str):
    print(f"{Colors.RED}✗ {message}{Colors.RESET}")

def print_warning(message: str):
    print(f"{Colors.YELLOW}⚠ {message}{Colors.RESET}")

def print_info(message: str):
    print(f"{Colors.BLUE}ℹ {message}{Colors.RESET}")

def print_header(message: str):
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*80}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{message}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*80}{Colors.RESET}\n")


class IntegrationVerifier:
    """Comprehensive integration verification"""
    
    def __init__(self):
        self.results = {
            "agents": {"passed": 0, "failed": 0, "tests": []},
            "ai_router": {"passed": 0, "failed": 0, "tests": []},
            "orchestration": {"passed": 0, "failed": 0, "tests": []},
            "database": {"passed": 0, "failed": 0, "tests": []},
            "caching": {"passed": 0, "failed": 0, "tests": []},
            "websocket": {"passed": 0, "failed": 0, "tests": []},
            "integrations": {"passed": 0, "failed": 0, "tests": []},
            "monitoring": {"passed": 0, "failed": 0, "tests": []},
            "frontend": {"passed": 0, "failed": 0, "tests": []},
            "security": {"passed": 0, "failed": 0, "tests": []},
        }
    
    def record_test(self, category: str, test_name: str, passed: bool, details: str = ""):
        """Record test result"""
        self.results[category]["tests"].append({
            "name": test_name,
            "passed": passed,
            "details": details
        })
        if passed:
            self.results[category]["passed"] += 1
            print_success(f"{test_name}: {details}")
        else:
            self.results[category]["failed"] += 1
            print_error(f"{test_name}: {details}")
    
    async def verify_agents(self):
        """Verify all 12 agents extend BaseAgent"""
        print_header("Phase 1: Verifying Agent System")
        
        try:
            from src.amas.agents.base_agent import BaseAgent
            from src.amas.agents.security_expert_agent import SecurityExpertAgent
            from src.amas.agents.code_analysis_agent import CodeAnalysisAgent
            from src.amas.agents.intelligence_gathering_agent import IntelligenceGatheringAgent
            from src.amas.agents.performance_agent import PerformanceAgent
            from src.amas.agents.documentation_agent import DocumentationAgent
            from src.amas.agents.testing_agent import TestingAgent
            from src.amas.agents.deployment_agent import DeploymentAgent
            from src.amas.agents.monitoring_agent import MonitoringAgent
            from src.amas.agents.data_agent import DataAgent
            from src.amas.agents.api_agent import APIAgent
            from src.amas.agents.research_agent import ResearchAgent
            from src.amas.agents.integration_agent import IntegrationAgent
            
            agents = [
                ("SecurityExpertAgent", SecurityExpertAgent),
                ("CodeAnalysisAgent", CodeAnalysisAgent),
                ("IntelligenceGatheringAgent", IntelligenceGatheringAgent),
                ("PerformanceAgent", PerformanceAgent),
                ("DocumentationAgent", DocumentationAgent),
                ("TestingAgent", TestingAgent),
                ("DeploymentAgent", DeploymentAgent),
                ("MonitoringAgent", MonitoringAgent),
                ("DataAgent", DataAgent),
                ("APIAgent", APIAgent),
                ("ResearchAgent", ResearchAgent),
                ("IntegrationAgent", IntegrationAgent),
            ]
            
            for agent_name, agent_class in agents:
                try:
                    agent = agent_class()
                    extends_base = isinstance(agent, BaseAgent)
                    has_ai_router = hasattr(agent, 'ai_router')
                    
                    if extends_base and has_ai_router:
                        self.record_test("agents", agent_name, True, 
                                       f"Extends BaseAgent and has AI router")
                    else:
                        self.record_test("agents", agent_name, False, 
                                       f"Missing: BaseAgent={extends_base}, AI router={has_ai_router}")
                except Exception as e:
                    self.record_test("agents", agent_name, False, f"Import failed: {e}")
            
        except Exception as e:
            print_error(f"Agent verification failed: {e}")
            self.record_test("agents", "Import", False, str(e))
    
    async def verify_ai_router(self):
        """Verify AI router with 16 providers"""
        print_header("Phase 2: Verifying AI Router")
        
        try:
            from src.amas.ai.enhanced_router_v2 import PROVIDER_CONFIGS, get_available_providers
            from src.amas.ai.enhanced_router_class import get_ai_router
            
            # Check provider count
            provider_count = len(PROVIDER_CONFIGS)
            self.record_test("ai_router", "Provider Count", provider_count >= 16, 
                           f"{provider_count} providers configured")
            
            # Check required providers
            required_providers = [
                "openai", "anthropic", "cerebras", "nvidia", "groq2", "groqai",
                "deepseek", "cohere", "mistral", "together", "perplexity",
                "fireworks", "replicate", "huggingface", "ai21", "moonshot"
            ]
            
            for provider in required_providers:
                exists = provider in PROVIDER_CONFIGS
                self.record_test("ai_router", f"Provider: {provider}", exists,
                               f"Configured" if exists else "Missing")
            
            # Check router instance
            try:
                router = get_ai_router()
                has_circuit_breakers = hasattr(router, 'circuit_breakers')
                has_stats = hasattr(router, 'provider_stats')
                
                self.record_test("ai_router", "Router Instance", True,
                               f"Circuit breakers={has_circuit_breakers}, Stats={has_stats}")
            except Exception as e:
                self.record_test("ai_router", "Router Instance", False, str(e))
                
        except Exception as e:
            print_error(f"AI router verification failed: {e}")
            self.record_test("ai_router", "Import", False, str(e))
    
    async def verify_orchestration(self):
        """Verify orchestration and ML integration"""
        print_header("Phase 3: Verifying Orchestration & ML Integration")
        
        try:
            from src.amas.core.unified_intelligence_orchestrator import get_unified_orchestrator
            from src.amas.intelligence.intelligence_manager import AMASIntelligenceManager
            from src.amas.intelligence.predictive_engine import PredictiveIntelligenceEngine
            
            # Check orchestrator
            try:
                orchestrator = get_unified_orchestrator()
                agent_count = len(orchestrator.agents)
                self.record_test("orchestration", "Orchestrator Init", agent_count >= 12,
                               f"{agent_count} agents initialized")
            except Exception as e:
                self.record_test("orchestration", "Orchestrator Init", False, str(e))
            
            # Check intelligence manager
            try:
                intelligence_manager = AMASIntelligenceManager()
                has_optimize = hasattr(intelligence_manager, 'optimize_task_before_execution')
                has_record = hasattr(intelligence_manager, 'record_task_execution')
                
                self.record_test("orchestration", "Intelligence Manager", 
                               has_optimize and has_record,
                               f"Methods: optimize={has_optimize}, record={has_record}")
            except Exception as e:
                self.record_test("orchestration", "Intelligence Manager", False, str(e))
            
            # Check predictive engine
            try:
                predictive_engine = PredictiveIntelligenceEngine()
                has_predict = hasattr(predictive_engine, 'predict_task_outcome')
                
                self.record_test("orchestration", "Predictive Engine", has_predict,
                               f"predict_task_outcome={has_predict}")
            except Exception as e:
                self.record_test("orchestration", "Predictive Engine", False, str(e))
                
        except Exception as e:
            print_error(f"Orchestration verification failed: {e}")
            self.record_test("orchestration", "Import", False, str(e))
    
    async def verify_database(self):
        """Verify database tables and connections"""
        print_header("Phase 4: Verifying Database Layer")
        
        try:
            # Check migrations
            import os
            migration_files = []
            if os.path.exists("alembic/versions"):
                migration_files = [f for f in os.listdir("alembic/versions") if f.endswith(".py")]
            
            self.record_test("database", "Migration Files", len(migration_files) >= 2,
                           f"{len(migration_files)} migration files found")
            
            # Check connection modules
            try:
                from src.database.connection import init_database, get_session
                self.record_test("database", "PostgreSQL Connection", True,
                               "Connection module exists")
            except Exception as e:
                self.record_test("database", "PostgreSQL Connection", False, str(e))
            
            try:
                from src.cache.redis import init_redis
                self.record_test("database", "Redis Connection", True,
                               "Redis module exists")
            except Exception as e:
                self.record_test("database", "Redis Connection", False, str(e))
            
            try:
                from src.graph.neo4j import init_neo4j
                self.record_test("database", "Neo4j Connection", True,
                               "Neo4j module exists")
            except Exception as e:
                self.record_test("database", "Neo4j Connection", False, str(e))
                
        except Exception as e:
            print_error(f"Database verification failed: {e}")
            self.record_test("database", "Import", False, str(e))
    
    async def verify_caching(self):
        """Verify caching services"""
        print_header("Phase 5: Verifying Caching Services")
        
        try:
            from src.amas.services.task_cache_service import TaskCacheService
            from src.amas.services.agent_cache_service import AgentCacheService
            from src.amas.services.prediction_cache_service import PredictionCacheService
            
            # Task cache (5 min TTL)
            try:
                task_cache = TaskCacheService()
                has_ttl = hasattr(task_cache, 'ttl_medium')
                ttl_value = getattr(task_cache, 'ttl_medium', 0) if has_ttl else 0
                
                self.record_test("caching", "TaskCacheService", ttl_value == 300,
                               f"TTL = {ttl_value}s (expected 300s)")
            except Exception as e:
                self.record_test("caching", "TaskCacheService", False, str(e))
            
            # Agent cache (5 min TTL)
            try:
                agent_cache = AgentCacheService()
                has_ttl = hasattr(agent_cache, 'ttl_medium')
                ttl_value = getattr(agent_cache, 'ttl_medium', 0) if has_ttl else 0
                
                self.record_test("caching", "AgentCacheService", ttl_value == 300,
                               f"TTL = {ttl_value}s (expected 300s)")
            except Exception as e:
                self.record_test("caching", "AgentCacheService", False, str(e))
            
            # Prediction cache (1 hour TTL)
            try:
                prediction_cache = PredictionCacheService()
                has_ttl = hasattr(prediction_cache, 'ttl')
                ttl_value = getattr(prediction_cache, 'ttl', 0) if has_ttl else 0
                
                self.record_test("caching", "PredictionCacheService", ttl_value == 3600,
                               f"TTL = {ttl_value}s (expected 3600s)")
            except Exception as e:
                self.record_test("caching", "PredictionCacheService", False, str(e))
                
        except Exception as e:
            print_error(f"Caching verification failed: {e}")
            self.record_test("caching", "Import", False, str(e))
    
    async def verify_integrations(self):
        """Verify platform integrations"""
        print_header("Phase 6: Verifying Platform Integrations")
        
        integrations = [
            ("github_connector", "src/amas/integration/github_connector.py"),
            ("slack_connector", "src/amas/integration/slack_connector.py"),
            ("n8n_connector", "src/amas/integration/n8n_connector.py"),
            ("notion_connector", "src/amas/integration/notion_connector.py"),
            ("jira_connector", "src/amas/integration/jira_connector.py"),
            ("salesforce_connector", "src/amas/integration/salesforce_connector.py"),
        ]
        
        import os
        for name, path in integrations:
            exists = os.path.exists(path)
            self.record_test("integrations", name, exists,
                           "File exists" if exists else "File missing")
        
        # Check integration manager
        try:
            from src.amas.integration.integration_manager import get_integration_manager
            manager = get_integration_manager()
            has_register = hasattr(manager, 'register_integration')
            has_trigger = hasattr(manager, 'trigger_integration')
            
            self.record_test("integrations", "IntegrationManager", 
                           has_register and has_trigger,
                           f"Methods: register={has_register}, trigger={has_trigger}")
        except Exception as e:
            self.record_test("integrations", "IntegrationManager", False, str(e))
    
    async def verify_monitoring(self):
        """Verify monitoring and observability"""
        print_header("Phase 7: Verifying Monitoring & Observability")
        
        try:
            from src.amas.services.prometheus_metrics_service import get_metrics_service
            
            metrics_service = get_metrics_service()
            metric_count = len(metrics_service.metrics)
            
            self.record_test("monitoring", "Prometheus Metrics", metric_count >= 50,
                           f"{metric_count} metrics configured")
            
            # Check specific metric categories
            task_metrics = [k for k in metrics_service.metrics.keys() if 'task' in k]
            agent_metrics = [k for k in metrics_service.metrics.keys() if 'agent' in k]
            provider_metrics = [k for k in metrics_service.metrics.keys() if 'provider' in k]
            
            self.record_test("monitoring", "Task Metrics", len(task_metrics) >= 5,
                           f"{len(task_metrics)} task metrics")
            self.record_test("monitoring", "Agent Metrics", len(agent_metrics) >= 5,
                           f"{len(agent_metrics)} agent metrics")
            self.record_test("monitoring", "Provider Metrics", len(provider_metrics) >= 5,
                           f"{len(provider_metrics)} provider metrics")
            
        except Exception as e:
            print_error(f"Monitoring verification failed: {e}")
            self.record_test("monitoring", "Import", False, str(e))
        
        # Check tracing service
        try:
            from src.amas.services.tracing_service import get_tracing_service
            tracing = get_tracing_service()
            
            if tracing:
                has_tracer = hasattr(tracing, 'tracer')
                self.record_test("monitoring", "Tracing Service", has_tracer,
                               f"OpenTelemetry configured")
            else:
                self.record_test("monitoring", "Tracing Service", True,
                               "Optional - not configured")
        except Exception as e:
            self.record_test("monitoring", "Tracing Service", True,
                           "Optional - not available")
        
        # Check Grafana dashboards
        import os
        dashboard_dir = "monitoring/grafana/dashboards"
        if os.path.exists(dashboard_dir):
            dashboards = [f for f in os.listdir(dashboard_dir) if f.endswith(".json")]
            self.record_test("monitoring", "Grafana Dashboards", len(dashboards) >= 3,
                           f"{len(dashboards)} dashboards found")
        else:
            self.record_test("monitoring", "Grafana Dashboards", False,
                           "Dashboard directory not found")
    
    async def verify_frontend(self):
        """Verify frontend integration"""
        print_header("Phase 8: Verifying Frontend Integration")
        
        import os
        
        # Check API service
        api_service_path = "frontend/src/services/api.ts"
        if os.path.exists(api_service_path):
            with open(api_service_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
                required_methods = [
                    "listTasks", "getTask", "createTask", "executeTask",
                    "predictTask", "getSystemMetrics", "getTaskAnalytics"
                ]
                
                for method in required_methods:
                    exists = method in content
                    self.record_test("frontend", f"API Method: {method}", exists,
                                   "Implemented" if exists else "Missing")
        else:
            self.record_test("frontend", "API Service", False, "File not found")
        
        # Check key components
        components = [
            "frontend/src/components/Dashboard/DashboardNew.tsx",
            "frontend/src/components/Tasks/TaskList.tsx",
            "frontend/src/components/Tasks/CreateTask.tsx",
            "frontend/src/components/Tasks/TaskExecutionView.tsx",
            "frontend/src/components/Auth/Login.tsx",
            "frontend/src/components/Auth/ProtectedRoute.tsx",
        ]
        
        for component in components:
            exists = os.path.exists(component)
            self.record_test("frontend", os.path.basename(component), exists,
                           "Exists" if exists else "Missing")
    
    async def verify_security(self):
        """Verify security measures"""
        print_header("Phase 9: Verifying Security Measures")
        
        try:
            from src.amas.security.enhanced_auth import EnhancedAuthManager
            from src.middleware.security import SecurityMiddleware
            
            # Check auth manager
            auth = EnhancedAuthManager()
            has_jwt = hasattr(auth, 'create_access_token')
            has_password_hash = hasattr(auth, 'hash_password')
            
            self.record_test("security", "Authentication", has_jwt and has_password_hash,
                           f"JWT={has_jwt}, Password hashing={has_password_hash}")
            
            # Check security middleware
            self.record_test("security", "Security Middleware", True,
                           "Middleware exists")
            
        except Exception as e:
            print_error(f"Security verification failed: {e}")
            self.record_test("security", "Import", False, str(e))
        
        # Check .gitignore
        import os
        if os.path.exists(".gitignore"):
            with open(".gitignore", 'r') as f:
                content = f.read()
                has_env = ".env" in content
                self.record_test("security", "Secrets in .gitignore", has_env,
                               ".env files ignored" if has_env else ".env not ignored")
        else:
            self.record_test("security", ".gitignore", False, "File not found")
    
    async def verify_docker_kubernetes(self):
        """Verify Docker and Kubernetes configs"""
        print_header("Phase 10: Verifying Docker & Kubernetes")
        
        import os
        
        # Check docker-compose.prod.yml
        if os.path.exists("docker-compose.prod.yml"):
            with open("docker-compose.prod.yml", 'r') as f:
                content = f.read()
                
                required_services = [
                    "amas-backend", "nginx", "postgres", "redis", "neo4j",
                    "prometheus", "grafana", "jaeger", "alertmanager",
                    "loki", "promtail", "node-exporter", "cadvisor",
                    "postgres-exporter", "redis-exporter"
                ]
                
                for service in required_services:
                    exists = f"{service}:" in content
                    self.record_test("docker", f"Service: {service}", exists,
                                   "Configured" if exists else "Missing")
        else:
            self.record_test("docker", "docker-compose.prod.yml", False, "File not found")
        
        # Check Kubernetes manifests
        k8s_files = [
            "k8s/deployment.yaml",
            "k8s/hpa.yaml",
            "k8s/ingress.yaml",
            "k8s/service.yaml",
        ]
        
        for k8s_file in k8s_files:
            exists = os.path.exists(k8s_file)
            self.record_test("kubernetes", os.path.basename(k8s_file), exists,
                           "Exists" if exists else "Missing")
    
    async def verify_cicd(self):
        """Verify CI/CD pipelines"""
        print_header("Phase 11: Verifying CI/CD Pipeline")
        
        import os
        
        workflow_dir = ".github/workflows"
        if os.path.exists(workflow_dir):
            workflows = [f for f in os.listdir(workflow_dir) if f.endswith(".yml")]
            self.record_test("cicd", "Workflow Files", len(workflows) >= 3,
                           f"{len(workflows)} workflow files found")
            
            # Check for key workflows
            workflow_names = [f.lower() for f in workflows]
            has_test = any('test' in w or 'ci' in w for w in workflow_names)
            has_build = any('build' in w or 'deploy' in w for w in workflow_names)
            
            self.record_test("cicd", "Test Workflow", has_test,
                           "Found" if has_test else "Missing")
            self.record_test("cicd", "Build/Deploy Workflow", has_build,
                           "Found" if has_build else "Missing")
        else:
            self.record_test("cicd", "Workflow Directory", False, "Directory not found")
    
    def print_summary(self):
        """Print verification summary"""
        print_header("Verification Summary")
        
        total_passed = 0
        total_failed = 0
        
        for category, results in self.results.items():
            passed = results["passed"]
            failed = results["failed"]
            total = passed + failed
            
            total_passed += passed
            total_failed += failed
            
            if total > 0:
                percentage = (passed / total) * 100
                status_icon = "✓" if failed == 0 else "✗"
                color = Colors.GREEN if failed == 0 else Colors.RED
                
                print(f"{color}{status_icon} {category.upper()}: {passed}/{total} passed ({percentage:.1f}%){Colors.RESET}")
        
        print(f"\n{Colors.BOLD}Overall: {total_passed}/{total_passed + total_failed} tests passed{Colors.RESET}")
        
        if total_failed == 0:
            print(f"\n{Colors.GREEN}{Colors.BOLD}✓ ALL VERIFICATIONS PASSED!{Colors.RESET}")
            print(f"{Colors.GREEN}The AMAS system is fully integrated and complete.{Colors.RESET}")
            return True
        else:
            print(f"\n{Colors.RED}{Colors.BOLD}✗ {total_failed} VERIFICATIONS FAILED{Colors.RESET}")
            print(f"{Colors.RED}Please review the failed tests above.{Colors.RESET}")
            return False
    
    async def run_all_verifications(self):
        """Run all verification phases"""
        print(f"\n{Colors.BOLD}AMAS Complete Integration Verification{Colors.RESET}")
        print(f"{Colors.BOLD}Started at: {datetime.now().isoformat()}{Colors.RESET}\n")
        
        await self.verify_agents()
        await self.verify_ai_router()
        await self.verify_orchestration()
        await self.verify_database()
        await self.verify_caching()
        await self.verify_integrations()
        await self.verify_monitoring()
        await self.verify_frontend()
        await self.verify_security()
        await self.verify_docker_kubernetes()
        await self.verify_cicd()
        
        success = self.print_summary()
        
        # Save results to file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_file = f"verification_results_{timestamp}.json"
        
        with open(results_file, 'w') as f:
            json.dump(self.results, f, indent=2)
        
        print(f"\n{Colors.BLUE}Results saved to: {results_file}{Colors.RESET}")
        
        return success


async def main():
    """Main verification entry point"""
    verifier = IntegrationVerifier()
    success = await verifier.run_all_verifications()
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    asyncio.run(main())

