#!/usr/bin/env python3
"""
Intelligent AI Router System
Routes tasks to the most appropriate AI agents and models
"""

import os
import json
import asyncio
from datetime import datetime
from typing import Dict, List, Any, Optional
from openai import OpenAI
import logging


class IntelligentAIRouter:
    def __init__(self):
        # Initialize all 9 API keys
        self.api_keys = {
            "deepseek": os.environ.get("DEEPSEEK_API_KEY"),
            "claude": os.environ.get("CLAUDE_API_KEY"),
            "gpt4": os.environ.get("GPT4_API_KEY"),
            "glm": os.environ.get("GLM_API_KEY"),
            "grok": os.environ.get("GROK_API_KEY"),
            "kimi": os.environ.get("KIMI_API_KEY"),
            "qwen": os.environ.get("QWEN_API_KEY"),
            "gemini": os.environ.get("GEMINI_API_KEY"),
            "gptoss": os.environ.get("GPTOSS_API_KEY"),
        }

        # Initialize AI clients
        self.ai_clients = self._initialize_ai_clients()

        # Task routing rules
        self.routing_rules = {
            "code_analysis": {
                "primary_models": ["deepseek", "claude", "gpt4"],
                "secondary_models": ["glm", "grok"],
                "fallback_models": ["kimi", "qwen", "gemini", "gptoss"],
            },
            "security_analysis": {
                "primary_models": ["claude", "gpt4", "deepseek"],
                "secondary_models": ["glm", "grok"],
                "fallback_models": ["kimi", "qwen", "gemini", "gptoss"],
            },
            "intelligence_gathering": {
                "primary_models": ["grok", "glm", "kimi"],
                "secondary_models": ["claude", "gpt4"],
                "fallback_models": ["deepseek", "qwen", "gemini", "gptoss"],
            },
            "incident_response": {
                "primary_models": ["claude", "deepseek", "gpt4"],
                "secondary_models": ["glm", "grok"],
                "fallback_models": ["kimi", "qwen", "gemini", "gptoss"],
            },
            "documentation": {
                "primary_models": ["claude", "gpt4", "glm"],
                "secondary_models": ["deepseek", "grok"],
                "fallback_models": ["kimi", "qwen", "gemini", "gptoss"],
            },
            "performance_optimization": {
                "primary_models": ["deepseek", "gpt4", "claude"],
                "secondary_models": ["glm", "grok"],
                "fallback_models": ["kimi", "qwen", "gemini", "gptoss"],
            },
            "quality_assurance": {
                "primary_models": ["claude", "deepseek", "gpt4"],
                "secondary_models": ["glm", "grok"],
                "fallback_models": ["kimi", "qwen", "gemini", "gptoss"],
            },
        }

        # Model performance tracking
        self.performance_metrics = {
            "success_rate": {},
            "response_time": {},
            "quality_score": {},
            "cost_efficiency": {},
        }

        # Initialize logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

    def _initialize_ai_clients(self):
        """Initialize AI clients with intelligent routing"""
        clients = []

        client_configs = [
            {
                "name": "DeepSeek",
                "key": self.api_keys["deepseek"],
                "base_url": "https://api.deepseek.com/v1",
                "model": "deepseek-chat",
                "priority": 1,
                "specialization": "code_analysis",
            },
            {
                "name": "Claude",
                "key": self.api_keys["claude"],
                "base_url": "https://openrouter.ai/api/v1",
                "model": "anthropic/claude-3.5-sonnet",
                "priority": 2,
                "specialization": "security_analysis",
            },
            {
                "name": "GPT-4",
                "key": self.api_keys["gpt4"],
                "base_url": "https://openrouter.ai/api/v1",
                "model": "openai/gpt-4o",
                "priority": 3,
                "specialization": "general_analysis",
            },
            {
                "name": "GLM",
                "key": self.api_keys["glm"],
                "base_url": "https://openrouter.ai/api/v1",
                "model": "z-ai/glm-4.5-air:free",
                "priority": 4,
                "specialization": "intelligence_gathering",
            },
            {
                "name": "Grok",
                "key": self.api_keys["grok"],
                "base_url": "https://openrouter.ai/api/v1",
                "model": "x-ai/grok-4-fast:free",
                "priority": 5,
                "specialization": "intelligence_gathering",
            },
            {
                "name": "Kimi",
                "key": self.api_keys["kimi"],
                "base_url": "https://openrouter.ai/api/v1",
                "model": "moonshot/moonshot-v1-8k:free",
                "priority": 6,
                "specialization": "documentation",
            },
            {
                "name": "Qwen",
                "key": self.api_keys["qwen"],
                "base_url": "https://openrouter.ai/api/v1",
                "model": "qwen/qwen-2.5-7b-instruct:free",
                "priority": 7,
                "specialization": "performance_optimization",
            },
            {
                "name": "Gemini",
                "key": self.api_keys["gemini"],
                "base_url": "https://openrouter.ai/api/v1",
                "model": "google/gemini-pro-1.5",
                "priority": 8,
                "specialization": "quality_assurance",
            },
            {
                "name": "GPTOSS",
                "key": self.api_keys["gptoss"],
                "base_url": "https://openrouter.ai/api/v1",
                "model": "openai/gpt-3.5-turbo:free",
                "priority": 9,
                "specialization": "fallback",
            },
        ]

        for config in client_configs:
            if config["key"]:
                try:
                    client = OpenAI(base_url=config["base_url"], api_key=config["key"])
                    clients.append(
                        {
                            "name": config["name"],
                            "client": client,
                            "model": config["model"],
                            "priority": config["priority"],
                            "specialization": config["specialization"],
                        }
                    )
                except Exception as e:
                    self.logger.warning(f"Failed to initialize {config['name']}: {e}")

        clients.sort(key=lambda x: x["priority"])
        return clients

    def route_task(
        self, task_type: str, task_description: str, context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Route task to the most appropriate AI agent"""
        self.logger.info(f"🎯 Routing task: {task_type}")

        # Get routing rules for this task type
        routing_rule = self.routing_rules.get(
            task_type, self.routing_rules["code_analysis"]
        )

        # Find the best available model
        best_model = self._find_best_model(routing_rule, task_type)

        if not best_model:
            return {"error": "No suitable AI model available"}

        # Execute task with selected model
        result = self._execute_task(best_model, task_description, context)

        # Update performance metrics
        self._update_performance_metrics(best_model["name"], result)

        return {
            "task_type": task_type,
            "model_used": best_model["name"],
            "specialization": best_model["specialization"],
            "result": result,
            "timestamp": datetime.now().isoformat(),
        }

    def _find_best_model(
        self, routing_rule: Dict[str, List[str]], task_type: str
    ) -> Optional[Dict[str, Any]]:
        """Find the best available model for the task"""
        # Try primary models first
        for model_name in routing_rule["primary_models"]:
            model = self._get_model_by_name(model_name)
            if model and self._is_model_available(model):
                return model

        # Try secondary models
        for model_name in routing_rule["secondary_models"]:
            model = self._get_model_by_name(model_name)
            if model and self._is_model_available(model):
                return model

        # Try fallback models
        for model_name in routing_rule["fallback_models"]:
            model = self._get_model_by_name(model_name)
            if model and self._is_model_available(model):
                return model

        return None

    def _get_model_by_name(self, model_name: str) -> Optional[Dict[str, Any]]:
        """Get model by name"""
        for client in self.ai_clients:
            if client["name"].lower() == model_name:
                return client
        return None

    def _is_model_available(self, model: Dict[str, Any]) -> bool:
        """Check if model is available"""
        # Check if model has been performing well recently
        model_name = model["name"]
        success_rate = self.performance_metrics["success_rate"].get(model_name, 1.0)
        return success_rate > 0.5  # 50% success rate threshold

    def _execute_task(
        self,
        model: Dict[str, Any],
        task_description: str,
        context: Dict[str, Any] = None,
    ) -> Dict[str, Any]:
        """Execute task with selected model"""
        try:
            # Create specialized prompt
            prompt = self._create_task_prompt(
                task_description, context, model["specialization"]
            )

            response = model["client"].chat.completions.create(
                model=model["model"],
                messages=[
                    {
                        "role": "system",
                        "content": f"You are a specialized AI agent focused on {model['specialization']}",
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=0.7,
                max_tokens=4000,
            )

            return {
                "success": True,
                "response": response.choices[0].message.content,
                "model_used": model["name"],
                "specialization": model["specialization"],
            }

        except Exception as e:
            self.logger.error(f"Error executing task with {model['name']}: {e}")
            return {"success": False, "error": str(e), "model_used": model["name"]}

    def _create_task_prompt(
        self, task_description: str, context: Dict[str, Any], specialization: str
    ) -> str:
        """Create specialized prompt for the task"""
        base_prompt = f"""
        Task: {task_description}
        
        Context: {context or 'No additional context provided'}
        
        Specialization: {specialization}
        
        Please provide:
        1. Detailed analysis and recommendations
        2. Specific actionable steps
        3. Priority level for implementation
        4. Potential risks and mitigation strategies
        5. Success metrics and KPIs
        
        Format your response as a structured analysis with clear sections.
        """

        return base_prompt

    def _update_performance_metrics(self, model_name: str, result: Dict[str, Any]):
        """Update performance metrics for the model"""
        if model_name not in self.performance_metrics["success_rate"]:
            self.performance_metrics["success_rate"][model_name] = 0.0
            self.performance_metrics["response_time"][model_name] = 0.0
            self.performance_metrics["quality_score"][model_name] = 0.0
            self.performance_metrics["cost_efficiency"][model_name] = 0.0

        # Update success rate
        if result.get("success", False):
            self.performance_metrics["success_rate"][model_name] = min(
                1.0, self.performance_metrics["success_rate"][model_name] + 0.1
            )
        else:
            self.performance_metrics["success_rate"][model_name] = max(
                0.0, self.performance_metrics["success_rate"][model_name] - 0.1
            )

        # Update other metrics (simplified for now)
        self.performance_metrics["response_time"][model_name] = 1.0  # Placeholder
        self.performance_metrics["quality_score"][model_name] = 0.8  # Placeholder
        self.performance_metrics["cost_efficiency"][model_name] = 0.9  # Placeholder

    def get_routing_statistics(self) -> Dict[str, Any]:
        """Get routing statistics and performance metrics"""
        return {
            "total_models": len(self.ai_clients),
            "available_models": len(
                [c for c in self.ai_clients if self._is_model_available(c)]
            ),
            "performance_metrics": self.performance_metrics,
            "routing_rules": self.routing_rules,
            "timestamp": datetime.now().isoformat(),
        }

    def optimize_routing(self) -> Dict[str, Any]:
        """Optimize routing based on performance metrics"""
        self.logger.info("🔧 Optimizing AI routing...")

        # Analyze performance metrics
        best_models = {}
        for task_type in self.routing_rules:
            best_models[task_type] = self._find_best_performing_model(task_type)

        # Update routing rules based on performance
        for task_type, best_model in best_models.items():
            if best_model:
                # Move best performing model to primary position
                current_rule = self.routing_rules[task_type]
                if best_model not in current_rule["primary_models"]:
                    current_rule["primary_models"].insert(0, best_model)
                    # Remove from other categories if present
                    for category in ["secondary_models", "fallback_models"]:
                        if best_model in current_rule[category]:
                            current_rule[category].remove(best_model)

        return {
            "optimization_complete": True,
            "best_models": best_models,
            "updated_routing_rules": self.routing_rules,
            "timestamp": datetime.now().isoformat(),
        }

    def _find_best_performing_model(self, task_type: str) -> Optional[str]:
        """Find the best performing model for a task type"""
        best_model = None
        best_score = 0.0

        for model_name, success_rate in self.performance_metrics[
            "success_rate"
        ].items():
            if success_rate > best_score:
                best_score = success_rate
                best_model = model_name

        return best_model


def main():
    """Main execution function"""
    router = IntelligentAIRouter()

    # Test routing for different task types
    task_types = [
        "code_analysis",
        "security_analysis",
        "intelligence_gathering",
        "incident_response",
        "documentation",
        "performance_optimization",
        "quality_assurance",
    ]

    print("🎯 Testing Intelligent AI Routing System...")

    for task_type in task_types:
        result = router.route_task(
            task_type,
            f"Analyze and provide recommendations for {task_type}",
            {"focus": task_type},
        )

        print(f"✅ {task_type}: {result.get('model_used', 'No model available')}")

    # Get routing statistics
    stats = router.get_routing_statistics()
    print(f"\n📊 Routing Statistics:")
    print(f"Total Models: {stats['total_models']}")
    print(f"Available Models: {stats['available_models']}")

    # Optimize routing
    optimization = router.optimize_routing()
    print(f"\n🔧 Routing Optimization: {optimization['optimization_complete']}")

    print("\n🎉 Intelligent AI Routing System Test Complete!")


if __name__ == "__main__":
    main()
