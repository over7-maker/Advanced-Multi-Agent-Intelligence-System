import os
from typing import Optional

from openai import OpenAI


def get_client(api_key: str) -> OpenAI:
    """Returns an OpenAI client configured for OpenRouter."""
    return OpenAI(base_url="https://openrouter.ai/api/v1", api_key=api_key)


def deepseek_chat(prompt: str):
    """Call DeepSeek model."""
    api_key = os.environ.get("DEEPSEEK_API_KEY")
    if not api_key:
        raise EnvironmentError("Missing OPENROUTER_API_KEY_DEEPSEEK secret")
    client = get_client(api_key)

    completion = client.chat.completions.create(
        extra_headers={
            "HTTP-Referer": "https://github.com/over7-maker/Advanced-Multi-Agent-Intelligence-System",
            "X-Title": "AMAS Project",
        },
        extra_body={},
        model="deepseek/deepseek-chat-v3.1:free",
        messages=[{"role": "user", "content": prompt}],
    )
    content = completion.choices[0].message.content
    if content is None:
        raise ValueError("Received empty response from AI model")
    return content


def zai_glm_chat(prompt: str):
    """Call Z.AI GLM 4.5 Air model."""
    api_key = os.environ.get("GLM_API_KEY")
    if not api_key:
        raise EnvironmentError("Missing OPENROUTER_API_KEY_ZAI secret")
    client = get_client(api_key)

    completion = client.chat.completions.create(
        extra_headers={
            "HTTP-Referer": "https://github.com/over7-maker/Advanced-Multi-Agent-Intelligence-System",
            "X-Title": "AMAS Project",
        },
        extra_body={},
        model="z-ai/glm-4.5-air:free",
        messages=[{"role": "user", "content": prompt}],
    )
    content = completion.choices[0].message.content
    if content is None:
        raise ValueError("Received empty response from AI model")
    return content


def xai_grok_chat(prompt: str, image_url: Optional[str] = None):
    """Call xAI Grok 4 Fast model with optional image context."""
    api_key = os.environ.get("GROK_API_KEY")
    if not api_key:
        raise EnvironmentError("Missing OPENROUTER_API_KEY_XAI secret")
    client = get_client(api_key)

    # Build messages based on whether image_url is provided
    if image_url:
        # Multimodal message with image
        messages = [{
            "role": "user",
            "content": [
                {"type": "text", "text": prompt},
                {"type": "image_url", "image_url": {"url": image_url}},
            ]
        }]
    else:
        # Text-only message
        messages = [{"role": "user", "content": prompt}]

    completion = client.chat.completions.create(
        extra_headers={
            "HTTP-Referer": "https://github.com/over7-maker/Advanced-Multi-Agent-Intelligence-System",
            "X-Title": "AMAS Project",
        },
        extra_body={},
        model="x-ai/grok-4-fast:free",
        messages=messages,
    )
    content = completion.choices[0].message.content
    if content is None:
        raise ValueError("Received empty response from AI model")
    return content
