import os

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
    return completion.choices[0].message.content

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
    return completion.choices[0].message.content

def xai_grok_chat(prompt: str, image_url: str = None):
    """Call xAI Grok 4 Fast model with optional image context."""
    api_key = os.environ.get("GROK_API_KEY")
    if not api_key:
        raise EnvironmentError("Missing OPENROUTER_API_KEY_XAI secret")
    client = get_client(api_key)

    # For messages, handle if image_url is present or not
    if image_url:
        content = [
            {"type": "text", "text": prompt},
            {"type": "image_url", "image_url": {"url": image_url}},
        ]
    else:
        content = [{"role": "user", "content": prompt}]

    messages = (
        [{"role": "user", "content": content}]
        if image_url
        else [{"role": "user", "content": prompt}]
    )

    completion = client.chat.completions.create(
        extra_headers={
            "HTTP-Referer": "https://github.com/over7-maker/Advanced-Multi-Agent-Intelligence-System",
            "X-Title": "AMAS Project",
        },
        extra_body={},
        model="x-ai/grok-4-fast:free",
        messages=messages,
    )
    return completion.choices[0].message.content
