"""
Deployment Agent - Specialized agent for deployment automation and DevOps
Implements PART_3 requirements
"""

import json
import logging
import os
from typing import Any, Dict, List

from src.amas.agents.base_agent import BaseAgent
from src.amas.agents.tools import get_tool_registry
from src.amas.agents.utils.json_parser import JSONParser
from src.amas.agents.schemas import DeploymentPlan

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
            model_preference=None,  # Use local models first
            strategy="quality_first"
        )
        
        # Get tool registry
        tool_registry = get_tool_registry()
        self.deployment_tools = ["github_api"]
    
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
    
    async def _generate_dockerfile(self, app_info: Dict[str, Any]) -> str:
        """
        Generate Dockerfile based on application information
        """
        try:
            logger.info("DeploymentAgent: Generating Dockerfile")
            
            language = app_info.get("language", "python")
            framework = app_info.get("framework", "fastapi")
            dependencies = app_info.get("dependencies", [])
            port = app_info.get("port", 8000)
            
            dockerfile = f"""# Multi-stage build for {language} application
FROM {language}:3.11-slim as builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y \\
    gcc \\
    g++ \\
    && rm -rf /var/lib/apt/lists/*

# Copy dependency files
"""
            
            if language == "python":
                dockerfile += """COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

"""
            elif language == "node":
                dockerfile += """COPY package*.json .
RUN npm ci --only=production

"""
            
            dockerfile += f"""# Production stage
FROM {language}:3.11-slim

WORKDIR /app

# Install runtime dependencies only
RUN apt-get update && apt-get install -y \\
    && rm -rf /var/lib/apt/lists/*

# Copy from builder
"""
            
            if language == "python":
                dockerfile += """COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin
"""
            elif language == "node":
                dockerfile += """COPY --from=builder /app/node_modules ./node_modules
"""
            
            dockerfile += f"""
# Copy application code
COPY . .

# Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE {port}

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \\
    CMD curl -f http://localhost:{port}/health || exit 1

# Run application
"""
            
            if framework == "fastapi":
                dockerfile += """CMD ["uvicorn", "src.amas.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
"""
            elif framework == "flask":
                dockerfile += f"""CMD ["python", "-m", "flask", "run", "--host=0.0.0.0", "--port={port}"]
"""
            else:
                dockerfile += f"""CMD ["python", "app.py"]
"""
            
            logger.info("DeploymentAgent: Dockerfile generated")
            return dockerfile
        
        except Exception as e:
            logger.error(f"DeploymentAgent: Dockerfile generation failed: {e}", exc_info=True)
            return f"# Error generating Dockerfile: {str(e)}\n"
    
    async def _generate_kubernetes_manifests(self, app_info: Dict[str, Any]) -> Dict[str, str]:
        """
        Generate Kubernetes manifests (Deployment, Service, Ingress)
        """
        manifests = {}
        
        try:
            logger.info("DeploymentAgent: Generating Kubernetes manifests")
            
            app_name = app_info.get("name", "app")
            image = app_info.get("image", f"{app_name}:latest")
            port = app_info.get("port", 8000)
            replicas = app_info.get("replicas", 3)
            
            # Deployment manifest
            deployment_manifest = f"""apiVersion: apps/v1
kind: Deployment
metadata:
  name: {app_name}
  labels:
    app: {app_name}
spec:
  replicas: {replicas}
  selector:
    matchLabels:
      app: {app_name}
  template:
    metadata:
      labels:
        app: {app_name}
    spec:
      containers:
      - name: {app_name}
        image: {image}
        ports:
        - containerPort: {port}
        env:
        - name: ENVIRONMENT
          value: "production"
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: {port}
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health/ready
            port: {port}
          initialDelaySeconds: 5
          periodSeconds: 5
"""
            manifests["deployment.yaml"] = deployment_manifest
            
            # Service manifest
            service_manifest = f"""apiVersion: v1
kind: Service
metadata:
  name: {app_name}-service
  labels:
    app: {app_name}
spec:
  type: ClusterIP
  ports:
  - port: 80
    targetPort: {port}
    protocol: TCP
  selector:
    app: {app_name}
"""
            manifests["service.yaml"] = service_manifest
            
            # Ingress manifest (optional)
            if app_info.get("ingress_enabled", True):
                ingress_manifest = f"""apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: {app_name}-ingress
  annotations:
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
spec:
  ingressClassName: nginx
  rules:
  - host: {app_info.get('domain', app_name + '.example.com')}
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: {app_name}-service
            port:
              number: 80
"""
                manifests["ingress.yaml"] = ingress_manifest
            
            logger.info(f"DeploymentAgent: Generated {len(manifests)} Kubernetes manifests")
        
        except Exception as e:
            logger.error(f"DeploymentAgent: Kubernetes manifest generation failed: {e}", exc_info=True)
            manifests["error"] = str(e)
        
        return manifests
    
    async def _generate_cicd_pipeline(self, app_info: Dict[str, Any], platform: str = "github") -> Dict[str, Any]:
        """
        Generate CI/CD pipeline configuration
        """
        pipeline_config = {
            "platform": platform,
            "config": "",
            "stages": [],
            "error": None
        }
        
        try:
            logger.info(f"DeploymentAgent: Generating {platform} CI/CD pipeline")
            
            app_name = app_info.get("name", "app")
            language = app_info.get("language", "python")
            
            if platform == "github":
                # GitHub Actions workflow
                workflow = f"""name: CI/CD Pipeline

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install pytest pytest-cov
    
    - name: Run tests
      run: |
        pytest --cov=src --cov-report=xml
    
    - name: Upload coverage
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml

  build:
    needs: test
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Docker Buildx
      uses: docker/setup-buildx-action@v2
    
    - name: Login to Docker Hub
      uses: docker/login-action@v2
      with:
        username: ${{{{ secrets.DOCKER_USERNAME }}}}
        password: ${{{{ secrets.DOCKER_PASSWORD }}}}
    
    - name: Build and push
      uses: docker/build-push-action@v4
      with:
        context: .
        push: true
        tags: ${{{{ secrets.DOCKER_USERNAME }}}}/{app_name}:${{{{ github.sha }}}}

  deploy:
    needs: build
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    steps:
    - uses: actions/checkout@v3
    
    - name: Deploy to Kubernetes
      uses: azure/k8s-deploy@v4
      with:
        manifests: |
          k8s/deployment.yaml
          k8s/service.yaml
        images: ${{{{ secrets.DOCKER_USERNAME }}}}/{app_name}:${{{{ github.sha }}}}
"""
                pipeline_config["config"] = workflow
                pipeline_config["stages"] = ["test", "build", "deploy"]
            
            elif platform == "gitlab":
                # GitLab CI configuration
                gitlab_ci = f""".stages:
  - test
  - build
  - deploy

test:
  stage: test
  image: python:3.11
  script:
    - pip install -r requirements.txt
    - pip install pytest pytest-cov
    - pytest --cov=src --cov-report=xml
  coverage: '/TOTAL.*\\s+(\\d+%)$/'

build:
  stage: build
  image: docker:latest
  services:
    - docker:dind
  script:
    - docker build -t $CI_REGISTRY_IMAGE:$CI_COMMIT_SHA .
    - docker push $CI_REGISTRY_IMAGE:$CI_COMMIT_SHA

deploy:
  stage: deploy
  image: bitnami/kubectl:latest
  script:
    - kubectl apply -f k8s/
  only:
    - main
"""
                pipeline_config["config"] = gitlab_ci
                pipeline_config["stages"] = ["test", "build", "deploy"]
            
            logger.info(f"DeploymentAgent: Generated {platform} CI/CD pipeline")
        
        except Exception as e:
            pipeline_config["error"] = f"CI/CD pipeline generation failed: {str(e)}"
            logger.error(f"DeploymentAgent: CI/CD pipeline generation failed: {e}", exc_info=True)
        
        return pipeline_config
    
    async def _generate_infrastructure_code(self, app_info: Dict[str, Any], iac_tool: str = "terraform") -> Dict[str, str]:
        """
        Generate Infrastructure as Code (Terraform, Ansible)
        """
        iac_code = {}
        
        try:
            logger.info(f"DeploymentAgent: Generating {iac_tool} infrastructure code")
            
            app_name = app_info.get("name", "app")
            
            if iac_tool == "terraform":
                # Terraform configuration
                main_tf = f"""terraform {{
  required_version = ">= 1.0"
  
  required_providers {{
    kubernetes = {{
      source  = "hashicorp/kubernetes"
      version = "~> 2.0"
    }}
  }}
}}

provider "kubernetes" {{
  config_path = "~/.kube/config"
}}

resource "kubernetes_deployment" "{app_name}" {{
  metadata {{
    name = "{app_name}"
    labels = {{
      app = "{app_name}"
    }}
  }}

  spec {{
    replicas = 3

    selector {{
      match_labels = {{
        app = "{app_name}"
      }}
    }}

    template {{
      metadata {{
        labels = {{
          app = "{app_name}"
        }}
      }}

      spec {{
        container {{
          image = "{app_info.get('image', app_name + ':latest')}"
          name  = "{app_name}"

          resources {{
            requests = {{
              cpu    = "250m"
              memory = "256Mi"
            }}
            limits = {{
              cpu    = "500m"
              memory = "512Mi"
            }}
          }}

          liveness_probe {{
            http_get {{
              path = "/health"
              port = {app_info.get('port', 8000)}
            }}
            initial_delay_seconds = 30
            period_seconds        = 10
          }}
        }}
      }}
    }}
  }}
}}

resource "kubernetes_service" "{app_name}" {{
  metadata {{
    name = "{app_name}-service"
  }}
  spec {{
    selector = {{
      app = kubernetes_deployment.{app_name}.metadata[0].labels.app
    }}
    port {{
      port        = 80
      target_port = {app_info.get('port', 8000)}
    }}
    type = "ClusterIP"
  }}
}}
"""
                iac_code["main.tf"] = main_tf
                
                # Variables file
                variables_tf = f"""variable "app_name" {{
  description = "Application name"
  type        = string
  default     = "{app_name}"
}}

variable "image" {{
  description = "Container image"
  type        = string
  default     = "{app_info.get('image', app_name + ':latest')}"
}}

variable "replicas" {{
  description = "Number of replicas"
  type        = number
  default     = 3
}}
"""
                iac_code["variables.tf"] = variables_tf
                
                # Outputs file
                outputs_tf = f"""output "deployment_name" {{
  value = kubernetes_deployment.{app_name}.metadata[0].name
}}

output "service_name" {{
  value = kubernetes_service.{app_name}.metadata[0].name
}}
"""
                iac_code["outputs.tf"] = outputs_tf
            
            elif iac_tool == "ansible":
                # Ansible playbook
                playbook = f"""---
- name: Deploy {app_name}
  hosts: k8s_cluster
  become: yes
  tasks:
    - name: Create namespace
      kubernetes.core.k8s:
        name: {app_name}
        api_version: v1
        kind: Namespace
        state: present

    - name: Deploy application
      kubernetes.core.k8s:
        state: present
        definition:
          apiVersion: apps/v1
          kind: Deployment
          metadata:
            name: {app_name}
            namespace: {app_name}
          spec:
            replicas: 3
            selector:
              matchLabels:
                app: {app_name}
            template:
              metadata:
                labels:
                  app: {app_name}
              spec:
                containers:
                - name: {app_name}
                  image: {app_info.get('image', app_name + ':latest')}
                  ports:
                  - containerPort: {app_info.get('port', 8000)}
"""
                iac_code["deploy.yml"] = playbook
            
            logger.info(f"DeploymentAgent: Generated {iac_tool} infrastructure code")
        
        except Exception as e:
            logger.error(f"DeploymentAgent: Infrastructure code generation failed: {e}", exc_info=True)
            iac_code["error"] = str(e)
        
        return iac_code
    
    async def _recommend_deployment_strategy(self, app_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        Recommend deployment strategy based on application characteristics
        """
        strategy_recommendation = {
            "recommended_strategy": "rolling",
            "alternatives": [],
            "rationale": "",
            "risk_assessment": {}
        }
        
        try:
            logger.info("DeploymentAgent: Recommending deployment strategy")
            
            # Analyze application characteristics
            is_critical = app_info.get("critical", False)
            has_state = app_info.get("stateful", False)
            traffic_volume = app_info.get("traffic_volume", "medium")
            
            if is_critical and traffic_volume == "high":
                strategy_recommendation["recommended_strategy"] = "blue-green"
                strategy_recommendation["rationale"] = "Blue-green deployment provides zero-downtime for critical high-traffic applications"
                strategy_recommendation["alternatives"] = ["canary", "rolling"]
            elif has_state:
                strategy_recommendation["recommended_strategy"] = "rolling"
                strategy_recommendation["rationale"] = "Rolling deployment is suitable for stateful applications"
                strategy_recommendation["alternatives"] = ["recreate"]
            else:
                strategy_recommendation["recommended_strategy"] = "canary"
                strategy_recommendation["rationale"] = "Canary deployment allows gradual rollout with risk mitigation"
                strategy_recommendation["alternatives"] = ["rolling", "blue-green"]
            
            # Risk assessment
            strategy_recommendation["risk_assessment"] = {
                "downtime_risk": "Low" if strategy_recommendation["recommended_strategy"] in ["blue-green", "canary"] else "Medium",
                "rollback_complexity": "Low" if strategy_recommendation["recommended_strategy"] == "blue-green" else "Medium",
                "resource_usage": "High" if strategy_recommendation["recommended_strategy"] == "blue-green" else "Medium"
            }
            
            logger.info(f"DeploymentAgent: Recommended strategy: {strategy_recommendation['recommended_strategy']}")
        
        except Exception as e:
            logger.error(f"DeploymentAgent: Strategy recommendation failed: {e}", exc_info=True)
            strategy_recommendation["error"] = str(e)
        
        return strategy_recommendation
    
    async def execute(
        self,
        task_id: str,
        target: str,
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute enhanced deployment planning with code generation
        Overrides BaseAgent.execute to add comprehensive deployment capabilities
        """
        execution_start = time.time()
        
        try:
            logger.info(f"DeploymentAgent: Starting enhanced deployment planning for {target}")
            
            app_info = parameters.get("app_info", {})
            deployment_type = parameters.get("deployment_type", "container")
            platform = parameters.get("platform", "kubernetes")
            
            # STEP 1: Generate Dockerfile
            dockerfile = ""
            if parameters.get("generate_dockerfile", True) and deployment_type == "container":
                dockerfile = await self._generate_dockerfile(app_info)
            
            # STEP 2: Generate Kubernetes manifests
            k8s_manifests = {}
            if parameters.get("generate_kubernetes", True) and platform == "kubernetes":
                k8s_manifests = await self._generate_kubernetes_manifests(app_info)
            
            # STEP 3: Generate CI/CD pipeline
            cicd_pipeline = {}
            cicd_platform = parameters.get("cicd_platform", "github")
            if parameters.get("generate_cicd", True):
                cicd_pipeline = await self._generate_cicd_pipeline(app_info, cicd_platform)
            
            # STEP 4: Generate Infrastructure as Code
            iac_code = {}
            iac_tool = parameters.get("iac_tool", "terraform")
            if parameters.get("generate_iac", True):
                iac_code = await self._generate_infrastructure_code(app_info, iac_tool)
            
            # STEP 5: Recommend deployment strategy
            strategy_recommendation = await self._recommend_deployment_strategy(app_info)
            
            # STEP 6: Prepare enhanced prompt
            prompt = await self._prepare_prompt(
                target, parameters, dockerfile, k8s_manifests, cicd_pipeline, iac_code, strategy_recommendation
            )
            
            # STEP 7: Call AI via router
            logger.info(f"DeploymentAgent: Calling AI with deployment configuration data")
            
            ai_response = await self.ai_router.generate_with_fallback(
                prompt=prompt,
                model_preference=self.model_preference,
                max_tokens=4000,
                temperature=0.3,
                system_prompt=self.system_prompt,
                strategy=self.strategy
            )
            
            logger.info(f"DeploymentAgent: Got response from {ai_response.provider} "
                       f"({ai_response.tokens_used} tokens, ${ai_response.cost_usd:.4f})")
            
            # STEP 8: Parse response
            parsed_result = await self._parse_response(ai_response.content)
            
            # STEP 9: Merge generated code with AI results
            if parsed_result.get("success") and parsed_result.get("deployment_plan"):
                deployment_plan = parsed_result["deployment_plan"]
                
                # Merge Dockerfile
                if dockerfile:
                    deployment_plan["dockerfile"] = dockerfile
                
                # Merge Kubernetes manifests
                if k8s_manifests:
                    deployment_plan["kubernetes_manifests"] = k8s_manifests
                
                # Merge CI/CD pipeline
                if cicd_pipeline:
                    deployment_plan["cicd_pipeline"] = cicd_pipeline
                
                # Merge Infrastructure as Code
                if iac_code:
                    deployment_plan["infrastructure_code"] = iac_code
                
                # Merge strategy recommendation
                deployment_plan["deployment_strategy"] = strategy_recommendation.get("recommended_strategy", "rolling")
                deployment_plan["strategy_recommendation"] = strategy_recommendation
            
            execution_duration = time.time() - execution_start
            
            # Update stats
            self.executions += 1
            self.successes += 1
            self.total_duration += execution_duration
            
            return {
                "success": parsed_result.get("success", True),
                "result": parsed_result.get("deployment_plan", {}),
                "output": parsed_result.get("deployment_plan", {}),
                "quality_score": 0.8,
                "duration": execution_duration,
                "tokens_used": ai_response.tokens_used,
                "cost_usd": ai_response.cost_usd,
                "provider": ai_response.provider,
                "summary": f"Generated deployment plan with {len(k8s_manifests)} K8s manifests and CI/CD pipeline"
            }
        
        except Exception as e:
            execution_duration = time.time() - execution_start
            logger.error(f"DeploymentAgent: Execution failed: {e}", exc_info=True)
            
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
        dockerfile: str = None,
        k8s_manifests: Dict[str, str] = None,
        cicd_pipeline: Dict[str, Any] = None,
        iac_code: Dict[str, str] = None,
        strategy_recommendation: Dict[str, Any] = None
    ) -> str:
        """Prepare enhanced deployment prompt with all generated code"""
        
        deployment_type = parameters.get("deployment_type", "container")
        platform = parameters.get("platform", "kubernetes")
        environment = parameters.get("environment", "production")
        app_info = parameters.get("app_info", {})
        
        # Build context from generated code
        deployment_context = ""
        
        if dockerfile:
            deployment_context += f"\n=== GENERATED DOCKERFILE ===\n"
            deployment_context += f"{dockerfile[:1000]}...\n"
        
        if k8s_manifests:
            deployment_context += f"\n=== GENERATED KUBERNETES MANIFESTS ===\n"
            deployment_context += f"Manifests Generated: {', '.join(k8s_manifests.keys())}\n"
            for name, content in list(k8s_manifests.items())[:2]:
                deployment_context += f"\n{name}:\n{content[:500]}...\n"
        
        if cicd_pipeline:
            deployment_context += f"\n=== GENERATED CI/CD PIPELINE ===\n"
            deployment_context += f"Platform: {cicd_pipeline.get('platform', 'unknown')}\n"
            deployment_context += f"Stages: {', '.join(cicd_pipeline.get('stages', []))}\n"
            if cicd_pipeline.get("config"):
                deployment_context += f"Pipeline Config: {len(cicd_pipeline['config'])} characters\n"
        
        if iac_code:
            deployment_context += f"\n=== GENERATED INFRASTRUCTURE CODE ===\n"
            deployment_context += f"Files Generated: {', '.join(iac_code.keys())}\n"
        
        if strategy_recommendation:
            deployment_context += f"\n=== DEPLOYMENT STRATEGY RECOMMENDATION ===\n"
            deployment_context += f"Recommended: {strategy_recommendation.get('recommended_strategy', 'rolling')}\n"
            deployment_context += f"Rationale: {strategy_recommendation.get('rationale', '')}\n"
        
        prompt = f"""Plan comprehensive deployment for: {target}

Deployment Type: {deployment_type}
Platform: {platform}
Environment: {environment}

{deployment_context}

Application Information:
{json.dumps(app_info, indent=2) if app_info else "No app info provided"}

Based on the GENERATED DEPLOYMENT CODE above (Dockerfile, Kubernetes manifests, CI/CD pipeline, IaC), please provide:
1. Deployment strategy analysis (use strategy recommendation)
2. Complete deployment plan (reference generated manifests)
3. CI/CD pipeline review (use generated pipeline config)
4. Infrastructure requirements (use generated IaC)
5. Rollback procedures (specific to recommended strategy)
6. Health checks and monitoring setup
7. Security considerations for deployment
8. Production readiness checklist

IMPORTANT: 
- Reference the generated Dockerfile, K8s manifests, and CI/CD pipeline
- Use the recommended deployment strategy
- Ensure all generated code is production-ready
- Provide specific rollback procedures

Format your response as JSON with the following structure:
{{
    "deployment_strategy": "{strategy_recommendation.get('recommended_strategy', 'rolling') if strategy_recommendation else 'rolling'}",
    "pipeline_config": {json.dumps(cicd_pipeline.get('config', '')) if cicd_pipeline else '""'},
    "infrastructure": {{
        "resources": {{...}},
        "scaling": {{...}},
        "terraform_code": {json.dumps(iac_code) if iac_code else {}}
    }},
    "container_config": {json.dumps(dockerfile) if dockerfile else '""'},
    "kubernetes_manifests": {json.dumps(k8s_manifests) if k8s_manifests else {}},
    "rollback_procedure": "...",
    "health_checks": ["...", "..."],
    "security_measures": ["...", "..."]
}}"""
        
        return prompt

