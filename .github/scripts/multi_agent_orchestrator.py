import os
from openai import OpenAI

def get_openrouter_client(api_key_env, model_name):
    api_key = os.environ.get(api_key_env)
    if not api_key:
        raise ValueError(f"Environment variable {api_key_env} is not set")
    return OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=api_key
    ), model_name

async def call_model(client, model, prompt):
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
        max_tokens=1000
    )
    return response.choices[0].message.content

async def main():
    import asyncio

    # Define each AI agent client and model
    deepseek_client, deepseek_model = get_openrouter_client("DEEPSEEK_API_KEY", "deepseek/deepseek-chat-v3.1:free")
    glm_client, glm_model = get_openrouter_client("GLM_API_KEY", "z-ai/glm-4.5-air:free")
    grok_client, grok_model = get_openrouter_client("GROK_API_KEY", "x-ai/grok-4-fast:free")

    # Multi-agent prompts
    initial_prompt = "Gather initial open source intelligence on the recent cyber attacks targeting financial institutions."
    
    # 1. DeepSeek collects initial intelligence
    deepseek_result = await call_model(deepseek_client, deepseek_model, initial_prompt)
    print("DeepSeek result:", deepseek_result)

    # 2. GLM for deeper contextual analysis based on DeepSeek’s output
    glm_prompt = f"Analyze this intelligence and extract potential threat actors and their tactics:\n\n{deepseek_result}"
    glm_result = await call_model(glm_client, glm_model, glm_prompt)
    print("GLM result:", glm_result)

    # 3. Grok summarizes and delivers actionable recommendations
    grok_prompt = f"Summarize the analysis and provide actionable cybersecurity recommendations:\n\n{glm_result}"
    grok_result = await call_model(grok_client, grok_model, grok_prompt)
    print("Grok result:", grok_result)

    # Final aggregated report
    full_report = (
        "### Multi-Agent Intelligence Report\n\n"
        f"**Step 1: OSINT by DeepSeek**\n{deepseek_result}\n\n"
        f"**Step 2: Threat Analysis by GLM**\n{glm_result}\n\n"
        f"**Step 3: Recommendations by Grok**\n{grok_result}\n"
    )

    # Save report to file
    with open("artifacts/multi_agent_report.md", "w", encoding="utf-8") as f:
        f.write(full_report)

    print("\nFull report saved to artifacts/multi_agent_report.md")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
    print("DEEPSEEK_API_KEY:", bool(os.getenv("DEEPSEEK_API_KEY")))
    print("GLM_API_KEY:", bool(os.getenv("GLM_API_KEY")))
    print("GROK_API_KEY:", bool(os.getenv("GROK_API_KEY")))
