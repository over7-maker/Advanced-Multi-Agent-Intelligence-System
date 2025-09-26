"""
LLM Service Implementation for AMAS
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional
import httpx
import json
from datetime import datetime

logger = logging.getLogger(__name__)

class LLMService:
    """LLM Service for AMAS Intelligence System"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.base_url = config.get('llm_service_url', 'http://localhost:11434')
        self.client = httpx.AsyncClient(timeout=30.0)
        self.models = []
        self.current_model = None
        
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
        max_tokens: int = 1000
    ) -> Dict[str, Any]:
        """Generate response from LLM"""
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
                    'tokens_used': data.get('eval_count', 0),
                    'timestamp': datetime.utcnow().isoformat()
                }
            else:
                return {
                    'success': False,
                    'error': f'HTTP {response.status_code}',
                    'timestamp': datetime.utcnow().isoformat()
                }
                
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return {
                'success': False,
                'error': str(e),
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