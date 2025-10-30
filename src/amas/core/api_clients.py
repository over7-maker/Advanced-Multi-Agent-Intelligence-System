from standalone_universal_ai_manager import get_api_key
#!/usr/bin/env python3
"""
AMAS API Clients - Specialized Adapters for Each AI Provider

This module provides specialized client adapters for each AI provider,
handling their unique requirements, authentication, and response formats.
"""

import asyncio
import json
import os
import time
from dataclasses import dataclass
from typing import Any, AsyncGenerator, Dict, List, Optional

import aiohttp
import cohere
import httpx
from openai import AsyncOpenAI
from tenacity import retry, stop_after_attempt, wait_exponential


@dataclass
class APIResponse:
    """Standardized API response format"""

    content: str
    model: str
    usage: Optional[Dict] = None
    metadata: Optional[Dict] = None
    api_name: str = ""
    response_time: float = 0.0


class BaseAPIClient:
    """Base class for all API clients"""

    def __init__(self, api_key: str, base_url: str, model: str):
        self.api_key = api_key
        self.base_url = base_url
        self.model = model
        self.session: Optional[aiohttp.ClientSession] = None
        self.http_client: Optional[httpx.AsyncClient] = None

    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        self.http_client = httpx.AsyncClient(timeout=30.0)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
        if self.http_client:
            await self.http_client.aclose()

    async def generate(self, messages: List[Dict], **kwargs) -> APIResponse:
        """Generate response - to be implemented by subclasses"""
        raise NotImplementedError

    async def generate_streaming(
        self, messages: List[Dict], **kwargs
    ) -> AsyncGenerator[APIResponse, None]:
        """Generate streaming response - to be implemented by subclasses"""
        raise NotImplementedError


class OpenAICompatibleClient(BaseAPIClient):
    """Client for OpenAI-compatible APIs"""

    async def generate(self, messages: List[Dict], **kwargs) -> APIResponse:
        """Generate response using OpenAI-compatible API"""
        start_time = time.time()

        client = AsyncOpenAI(base_url=self.base_url, api_key=self.api_key)

        response = await client.chat.completions.create(
            model=self.model,
            messages=messages,
            max_tokens=kwargs.get("max_tokens", 4000),
            temperature=kwargs.get("temperature", 0.7),
            timeout=kwargs.get("timeout", 30),
        )

        return APIResponse(
            content=response.choices[0].message.content,
            model=response.model,
            usage=response.usage.dict() if response.usage else None,
            api_name=self.__class__.__name__,
            response_time=time.time() - start_time,
        )

    async def generate_streaming(
        self, messages: List[Dict], **kwargs
    ) -> AsyncGenerator[APIResponse, None]:
        """Generate streaming response"""
        client = AsyncOpenAI(base_url=self.base_url, api_key=self.api_key)

        stream = await client.chat.completions.create(
            model=self.model,
            messages=messages,
            max_tokens=kwargs.get("max_tokens", 4000),
            temperature=kwargs.get("temperature", 0.7),
            stream=True,
            timeout=kwargs.get("timeout", 30),
        )

        content = ""
        async for chunk in stream:
            if chunk.choices[0].delta.content:
                content += chunk.choices[0].delta.content
                yield APIResponse(
                    content=chunk.choices[0].delta.content,
                    model=self.model,
                    api_name=self.__class__.__name__,
                )


class CerebrasClient(BaseAPIClient):
    """Specialized client for Cerebras API"""

    async def generate(self, messages: List[Dict], **kwargs) -> APIResponse:
        """Generate response using Cerebras API"""
        start_time = time.time()

        # Convert messages to Cerebras format
        system_content = ""
        user_content = ""

        for msg in messages:
            if msg["role"] == "system":
                system_content = msg["content"]
            elif msg["role"] == "user":
                user_content = msg["content"]

        payload = {
            "messages": [{"role": "user", "content": user_content}],
            "model": self.model,
            "stream": False,
            "max_completion_tokens": kwargs.get("max_tokens", 4000),
            "temperature": kwargs.get("temperature", 0.7),
        }

        if system_content:
            payload["messages"].insert(0, {"role": "system", "content": system_content})

        async with self.http_client.post(
            f"{self.base_url}/chat/completions",
            headers={"Authorization": f"Bearer {self.api_key}"},
            json=payload,
        ) as response:
            result = await response.json()

            return APIResponse(
                content=result["choices"][0]["message"]["content"],
                model=result["model"],
                usage=result.get("usage"),
                api_name="Cerebras",
                response_time=time.time() - start_time,
            )


class CohereClient(BaseAPIClient):
    """Specialized client for Cohere API"""

    def __init__(self, api_key: str, base_url: str, model: str):
        super().__init__(api_key, base_url, model)
        self.cohere_client = cohere.AsyncClient(api_key)

    async def generate(self, messages: List[Dict], **kwargs) -> APIResponse:
        """Generate response using Cohere API"""
        start_time = time.time()

        # Convert messages to Cohere format
        user_content = ""
        for msg in messages:
            if msg["role"] == "user":
                user_content = msg["content"]
                break

        response = await self.cohere_client.chat(
            model=self.model,
            message=user_content,
            max_tokens=kwargs.get("max_tokens", 4000),
            temperature=kwargs.get("temperature", 0.7),
        )

        return APIResponse(
            content=response.text,
            model=self.model,
            usage=response.meta,
            api_name="Cohere",
            response_time=time.time() - start_time,
        )


class ChutesClient(BaseAPIClient):
    """Specialized client for Chutes API"""

    async def generate(self, messages: List[Dict], **kwargs) -> APIResponse:
        """Generate response using Chutes API"""
        start_time = time.time()

        payload = {
            "model": self.model,
            "messages": messages,
            "stream": False,
            "max_tokens": kwargs.get("max_tokens", 4000),
            "temperature": kwargs.get("temperature", 0.7),
        }

        async with self.http_client.post(
            f"{self.base_url}/chat/completions",
            headers={"Authorization": f"Bearer {self.api_key}"},
            json=payload,
        ) as response:
            result = await response.json()

            return APIResponse(
                content=result["choices"][0]["message"]["content"],
                model=result["model"],
                usage=result.get("usage"),
                api_name="Chutes",
                response_time=time.time() - start_time,
            )

    async def generate_streaming(
        self, messages: List[Dict], **kwargs
    ) -> AsyncGenerator[APIResponse, None]:
        """Generate streaming response using Chutes API"""
        payload = {
            "model": self.model,
            "messages": messages,
            "stream": True,
            "max_tokens": kwargs.get("max_tokens", 4000),
            "temperature": kwargs.get("temperature", 0.7),
        }

        async with self.http_client.stream(
            "POST",
            f"{self.base_url}/chat/completions",
            headers={"Authorization": f"Bearer {self.api_key}"},
            json=payload,
        ) as response:
            async for line in response.aiter_lines():
                if line.startswith("data: "):
                    data = line[6:]
                    if data == "[DONE]":
                        break
                    try:
                        chunk = json.loads(data.strip())
                        if chunk and "choices" in chunk:
                            content = (
                                chunk["choices"][0].get("delta", {}).get("content", "")
                            )
                            if content:
                                yield APIResponse(
                                    content=content, model=self.model, api_name="Chutes"
                                )
                    except json.JSONDecodeError:
                        continue


class GeminiClient(BaseAPIClient):
    """Specialized client for Gemini API"""

    async def generate(self, messages: List[Dict], **kwargs) -> APIResponse:
        """Generate response using Gemini API"""
        start_time = time.time()

        # Convert messages to Gemini format
        user_content = ""
        for msg in messages:
            if msg["role"] == "user":
                user_content = msg["content"]
                break

        payload = {
            "contents": [{"parts": [{"text": user_content}]}],
            "generationConfig": {
                "maxOutputTokens": kwargs.get("max_tokens", 4000),
                "temperature": kwargs.get("temperature", 0.7),
            },
        }

        async with self.http_client.post(
            f"{self.base_url}/models/{self.model}:generateContent",
            headers={"X-goog-api-key": self.api_key},
            json=payload,
        ) as response:
            result = await response.json()

            return APIResponse(
                content=result["candidates"][0]["content"]["parts"][0]["text"],
                model=self.model,
                usage=result.get("usageMetadata"),
                api_name="Gemini",
                response_time=time.time() - start_time,
            )


class NVIDIAClient(BaseAPIClient):
    """Specialized client for NVIDIA API"""

    async def generate(self, messages: List[Dict], **kwargs) -> APIResponse:
        """Generate response using NVIDIA API"""
        start_time = time.time()

        client = AsyncOpenAI(base_url=self.base_url, api_key=self.api_key)

        response = await client.chat.completions.create(
            model=self.model,
            messages=messages,
            max_tokens=kwargs.get("max_tokens", 4000),
            temperature=kwargs.get("temperature", 0.7),
            timeout=kwargs.get("timeout", 30),
        )

        return APIResponse(
            content=response.choices[0].message.content,
            model=response.model,
            usage=response.usage.dict() if response.usage else None,
            api_name="NVIDIA",
            response_time=time.time() - start_time,
        )


class APIClientFactory:
    """Factory for creating appropriate API clients"""

    @staticmethod
    def create_client(
        api_name: str, api_key: str, base_url: str, model: str
    ) -> BaseAPIClient:
        """Create appropriate client based on API name"""

        client_map = {
            "cerebras": CerebrasClient,
            "codestral": OpenAICompatibleClient,
            "deepseek": OpenAICompatibleClient,
            "glm": OpenAICompatibleClient,
            "gptoss": OpenAICompatibleClient,
            "grok": OpenAICompatibleClient,
            "groqai": OpenAICompatibleClient,
            "groq2": OpenAICompatibleClient,
            "kimi": OpenAICompatibleClient,
            "nvidia": NVIDIAClient,
            "nvidia2": NVIDIAClient,
            "qwen": OpenAICompatibleClient,
            "gemini": GeminiClient,
            "gemini2": GeminiClient,
            "cohere": CohereClient,
            "chutes": ChutesClient,
        }

        client_class = client_map.get(api_name, OpenAICompatibleClient)
        return client_class(api_key, base_url, model)


# Convenience functions for easy usage
async def get_client(
    api_name: str, api_key: str, base_url: str, model: str
) -> BaseAPIClient:
    """Get an API client instance"""
    return APIClientFactory.create_client(api_name, api_key, base_url, model)


async def test_api_client(
    api_name: str, api_key: str, base_url: str, model: str
) -> bool:
    """Test if an API client is working"""
    try:
        async with get_client(api_name, api_key, base_url, model) as client:
            response = await client.generate(
                [
                    {
                        "role": "user",
                        "content": "Hello, this is a test. Please respond with 'OK'.",
                    }
                ],
                max_tokens=10,
                temperature=0.1,
            )
            return response.content is not None
    except Exception as e:
        print(f"API {api_name} test failed: {e}")
        return False


# Example usage
async def main():
    """Example usage of API clients"""
    print("🚀 AMAS API Clients - Testing Individual Clients")
    print("=" * 50)

    # Test configurations
    test_configs = [
        {
            "name": "codestral",
            "key": get_api_key("CODESTRAL_API_KEY"),
            "url": "https://codestral.mistral.ai/v1",
            "model": "codestral-latest",
        },
        {
            "name": "deepseek",
            "key": get_api_key("DEEPSEEK_API_KEY"),
            "url": "https://api.deepseek.com/v1",
            "model": "deepseek-chat",
        },
    ]

    for config in test_configs:
        if not config["key"]:
            print(f"❌ {config['name']}: No API key found")
            continue

        print(f"\n🧪 Testing {config['name']}...")

        try:
            async with get_client(
                config["name"], config["key"], config["url"], config["model"]
            ) as client:
                response = await client.generate(
                    [{"role": "user", "content": "Explain AI in one sentence."}],
                    max_tokens=50,
                )

                print(f"✅ {config['name']}: Success")
                print(f"   Response: {response.content[:100]}...")
                print(f"   Model: {response.model}")
                print(f"   Response Time: {response.response_time:.2f}s")

        except Exception as e:
            print(f"❌ {config['name']}: Failed - {e}")


if __name__ == "__main__":
    asyncio.run(main())
