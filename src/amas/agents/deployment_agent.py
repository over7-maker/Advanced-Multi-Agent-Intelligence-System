"""
Deployment Agent - Specialized agent for deployment automation and DevOps
Implements PART_3 requirements
"""

import json
import logging
from typing import Any, Dict

from src.amas.agents.base_agent import BaseAgent

logger = logging.getLogger(__name__)


class DeploymentAgent(BaseAgent):
    """
    Deployment Agent
    
    Specializes in:
    - Deployment automation
    - CI/CD pipeline configuration
    - Infrastructure as Code
    - Container orchestration
    - Rollback strategies
    """
    
    def __init__(self):
        super().__init__(
            agent_id="deployment_agent",
            name="Deployment Agent",
            agent_type="deployment",
            system_prompt="""You are an expert DevOps engineer with 15+ years of experience 
            in deployment automation, CI/CD pipelines, and infrastructure management.
            
            Your expertise includes:
            • Docker and containerization
            • Kubernetes orchestration
            • CI/CD pipeline design (GitHub Actions, GitLab CI, Jenkins)
            • Infrastructure as Code (Terraform, Ansible)
            • Blue-green deployments
            • Canary releases
            • Rollback strategies
            • Environment management
            • Monitoring and alerting setup
            • Security best practices for deployments
            
            When planning deployments, you:
            1. Design safe, automated deployment pipelines
            2. Include proper testing stages
            3. Plan rollback procedures
            4. Ensure zero-downtime deployments
            5. Follow security best practices
            
            Always produce production-ready deployment configurations.""",
            model_preference="gpt-4-turbo-preview",
            strategy="quality_first"
        )
    
    async def _prepare_prompt(
        self,
        target: str,
        parameters: Dict[str, Any]
    ) -> str:
        """Prepare deployment planning prompt"""
        
        deployment_type = parameters.get("deployment_type", "container")
        platform = parameters.get("platform", "kubernetes")
        environment = parameters.get("environment", "production")
        app_info = parameters.get("app_info", {})
        
        prompt = f"""Plan deployment for: {target}

Deployment Type: {deployment_type}
Platform: {platform}
Environment: {environment}

Application Information:
{json.dumps(app_info, indent=2) if app_info else "No app info provided"}

Please provide comprehensive deployment plan including:
1. Deployment strategy (blue-green, canary, rolling)
2. CI/CD pipeline configuration
3. Infrastructure requirements
4. Container/Docker configuration
5. Kubernetes manifests (if applicable)
6. Rollback procedures
7. Health checks and monitoring
8. Security considerations

Format your response as JSON with the following structure:
{{
    "deployment_strategy": "...",
    "pipeline_config": "...",
    "infrastructure": {{
        "resources": {{...}},
        "scaling": {{...}}
    }},
    "container_config": "...",
    "kubernetes_manifests": "...",
    "rollback_procedure": "...",
    "health_checks": ["...", "..."],
    "security_measures": ["...", "..."]
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
                "deployment_plan": result,
                "has_pipeline_config": bool(result.get("pipeline_config")),
                "has_kubernetes_manifests": bool(result.get("kubernetes_manifests")),
                "has_rollback_procedure": bool(result.get("rollback_procedure"))
            }
        except json.JSONDecodeError:
            # Fallback: return raw response
            logger.warning("Failed to parse JSON response, returning raw text")
            return {
                "success": True,
                "deployment_plan": {
                    "raw_response": response,
                    "deployment_strategy": "rolling"
                },
                "has_pipeline_config": False,
                "has_kubernetes_manifests": False,
                "has_rollback_procedure": False
            }

