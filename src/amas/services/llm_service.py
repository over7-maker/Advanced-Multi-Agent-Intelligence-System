"""
Enhanced LLM Service Implementation for AMAS with Multiple API Support
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional
import httpx
import json
from datetime import datetime
import os

logger = logging.getLogger(__name__)

class LLMService:
    """Enhanced LLM Service for AMAS Intelligence System with Multiple API Support"""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.base_url = config.get('llm_service_url', 'http://localhost:11434')
        self.client = httpx.AsyncClient(timeout=30.0)
        self.models = []
        self.current_model = None

        # API Keys for external services
        self.deepseek_api_key = config.get('deepseek_api_key', os.getenv('DEEPSEEK_API_KEY'))
        self.glm_api_key = config.get('glm_api_key', os.getenv('GLM_API_KEY'))
        self.grok_api_key = config.get('grok_api_key', os.getenv('GROK_API_KEY'))

        # API endpoints
        self.api_endpoints = {
            'deepseek': 'https://api.deepseek.com/v1/chat/completions',
            'glm': 'https://open.bigmodel.cn/api/paas/v4/chat/completions',
            'grok': 'https://api.x.ai/v1/chat/completions'
        }

    async def initialize(self):
        """Initialize the LLM service"""
        try:
            # Check service health
            await self.health_check()

            # Get available models
            await self._load_models()

            # Set default model
            if self.models:
                self.current_model = self.models[0]
                logger.info(f"LLM service initialized with model: {self.current_model}")
            else:
                logger.warning("No models available in LLM service")

        except Exception as e:
            logger.error(f"Failed to initialize LLM service: {e}")
            raise

    async def health_check(self) -> Dict[str, Any]:
        """Check LLM service health"""
        try:
            response = await self.client.get(f"{self.base_url}/api/tags")
            if response.status_code == 200:
                return {
                    'status': 'healthy',
                    'timestamp': datetime.utcnow().isoformat(),
                    'service': 'llm'
                }
            else:
                return {
                    'status': 'unhealthy',
                    'error': f'HTTP {response.status_code}',
                    'timestamp': datetime.utcnow().isoformat(),
                    'service': 'llm'
                }
        except Exception as e:
            return {
                'status': 'unhealthy',
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat(),
                'service': 'llm'
            }

    async def _load_models(self):
        """Load available models"""
        try:
            response = await self.client.get(f"{self.base_url}/api/tags")
            if response.status_code == 200:
                data = response.json()
                self.models = [model['name'] for model in data.get('models', [])]
                logger.info(f"Loaded {len(self.models)} models: {self.models}")
            else:
                logger.error(f"Failed to load models: HTTP {response.status_code}")
        except Exception as e:
            logger.error(f"Error loading models: {e}")

    async def generate_response(
        self,
        prompt: str,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1000,
        provider: str = 'ollama'
    ) -> Dict[str, Any]:
        """Generate response from LLM with multiple provider support"""
        try:
            if provider == 'ollama':
                return await self._generate_ollama_response(prompt, model, temperature, max_tokens)
            elif provider == 'deepseek':
                return await self._generate_deepseek_response(prompt, model, temperature, max_tokens)
            elif provider == 'glm':
                return await self._generate_glm_response(prompt, model, temperature, max_tokens)
            elif provider == 'grok':
                return await self._generate_grok_response(prompt, model, temperature, max_tokens)
            else:
                raise ValueError(f"Unsupported provider: {provider}")

        except Exception as e:
            logger.error(f"Error generating response with {provider}: {e}")
            return {
                'success': False,
                'error': str(e),
                'provider': provider,
                'timestamp': datetime.utcnow().isoformat()
            }

    async def _generate_ollama_response(self, prompt: str, model: Optional[str] = None, temperature: float = 0.7, max_tokens: int = 1000) -> Dict[str, Any]:
        """Generate response using Ollama"""
        try:
            model_name = model or self.current_model
            if not model_name:
                raise ValueError("No model available")

            payload = {
                "model": model_name,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": temperature,
                    "num_predict": max_tokens
                }
            }

            response = await self.client.post(
                f"{self.base_url}/api/generate",
                json=payload
            )

            if response.status_code == 200:
                data = response.json()
                return {
                    'success': True,
                    'response': data.get('response', ''),
                    'model': model_name,
                    'provider': 'ollama',
                    'tokens_used': data.get('eval_count', 0),
                    'timestamp': datetime.utcnow().isoformat()
                }
            else:
                return {
                    'success': False,
                    'error': f'HTTP {response.status_code}',
                    'provider': 'ollama',
                    'timestamp': datetime.utcnow().isoformat()
                }

        except Exception as e:
            logger.error(f"Error generating Ollama response: {e}")
            return {
                'success': False,
                'error': str(e),
                'provider': 'ollama',
                'timestamp': datetime.utcnow().isoformat()
            }

    async def _generate_deepseek_response(self, prompt: str, model: Optional[str] = None, temperature: float = 0.7, max_tokens: int = 1000) -> Dict[str, Any]:
        """Generate response using DeepSeek API"""
        try:
            if not self.deepseek_api_key:
                raise ValueError("DeepSeek API key not configured")

            model_name = model or "deepseek-chat"
            headers = {
                "Authorization": f"Bearer {self.deepseek_api_key}",
                "Content-Type": "application/json"
            }

            payload = {
                "model": model_name,
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": max_tokens,
                "temperature": temperature
            }

            response = await self.client.post(
                self.api_endpoints['deepseek'],
                headers=headers,
                json=payload
            )

            if response.status_code == 200:
                result = response.json()
                return {
                    'success': True,
                    'response': result['choices'][0]['message']['content'],
                    'model': model_name,
                    'provider': 'deepseek',
                    'usage': result.get('usage', {}),
                    'timestamp': datetime.utcnow().isoformat()
                }
            else:
                return {
                    'success': False,
                    'error': f"HTTP {response.status_code}: {response.text}",
                    'provider': 'deepseek',
                    'timestamp': datetime.utcnow().isoformat()
                }

        except Exception as e:
            logger.error(f"Error generating DeepSeek response: {e}")
            return {
                'success': False,
                'error': str(e),
                'provider': 'deepseek',
                'timestamp': datetime.utcnow().isoformat()
            }

    async def _generate_glm_response(self, prompt: str, model: Optional[str] = None, temperature: float = 0.7, max_tokens: int = 1000) -> Dict[str, Any]:
        """Generate response using GLM API"""
        try:
            if not self.glm_api_key:
                raise ValueError("GLM API key not configured")

            model_name = model or "glm-4"
            headers = {
                "Authorization": f"Bearer {self.glm_api_key}",
                "Content-Type": "application/json"
            }

            payload = {
                "model": model_name,
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": max_tokens,
                "temperature": temperature
            }

            response = await self.client.post(
                self.api_endpoints['glm'],
                headers=headers,
                json=payload
            )

            if response.status_code == 200:
                result = response.json()
                return {
                    'success': True,
                    'response': result['choices'][0]['message']['content'],
                    'model': model_name,
                    'provider': 'glm',
                    'usage': result.get('usage', {}),
                    'timestamp': datetime.utcnow().isoformat()
                }
            else:
                return {
                    'success': False,
                    'error': f"HTTP {response.status_code}: {response.text}",
                    'provider': 'glm',
                    'timestamp': datetime.utcnow().isoformat()
                }

        except Exception as e:
            logger.error(f"Error generating GLM response: {e}")
            return {
                'success': False,
                'error': str(e),
                'provider': 'glm',
                'timestamp': datetime.utcnow().isoformat()
            }

    async def _generate_grok_response(self, prompt: str, model: Optional[str] = None, temperature: float = 0.7, max_tokens: int = 1000) -> Dict[str, Any]:
        """Generate response using Grok API"""
        try:
            if not self.grok_api_key:
                raise ValueError("Grok API key not configured")

            model_name = model or "grok-beta"
            headers = {
                "Authorization": f"Bearer {self.grok_api_key}",
                "Content-Type": "application/json"
            }

            payload = {
                "model": model_name,
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": max_tokens,
                "temperature": temperature
            }

            response = await self.client.post(
                self.api_endpoints['grok'],
                headers=headers,
                json=payload
            )

            if response.status_code == 200:
                result = response.json()
                return {
                    'success': True,
                    'response': result['choices'][0]['message']['content'],
                    'model': model_name,
                    'provider': 'grok',
                    'usage': result.get('usage', {}),
                    'timestamp': datetime.utcnow().isoformat()
                }
            else:
                return {
                    'success': False,
                    'error': f"HTTP {response.status_code}: {response.text}",
                    'provider': 'grok',
                    'timestamp': datetime.utcnow().isoformat()
                }

        except Exception as e:
            logger.error(f"Error generating Grok response: {e}")
            return {
                'success': False,
                'error': str(e),
                'provider': 'grok',
                'timestamp': datetime.utcnow().isoformat()
            }

    async def generate_embedding(self, text: str, model: Optional[str] = None) -> Dict[str, Any]:
        """Generate embedding for text"""
        try:
            model_name = model or self.current_model
            if not model_name:
                raise ValueError("No model available")

            payload = {
                "model": model_name,
                "prompt": text
            }

            response = await self.client.post(
                f"{self.base_url}/api/embeddings",
                json=payload
            )

            if response.status_code == 200:
                data = response.json()
                return {
                    'success': True,
                    'embedding': data.get('embedding', []),
                    'model': model_name,
                    'timestamp': datetime.utcnow().isoformat()
                }
            else:
                return {
                    'success': False,
                    'error': f'HTTP {response.status_code}',
                    'timestamp': datetime.utcnow().isoformat()
                }

        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            return {
                'success': False,
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }

    async def close(self):
        """Close the service"""
        await self.client.aclose()
