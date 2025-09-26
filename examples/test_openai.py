import os
from agents.openrouter_clients import deepseek_chat, zai_glm_chat, xai_grok_chat

def main():
    print("Testing DeepSeek model:")
    response1 = deepseek_chat("What is the meaning of life?")
    print(response1)
    print("\n---\n")

    print("Testing Z.AI GLM 4.5 Air model:")
    response2 = zai_glm_chat("What is the meaning of life?")
    print(response2)
    print("\n---\n")

    print("Testing xAI Grok 4 Fast model with image:")
    img_url = "https://upload.wikimedia.org/wikipedia/commons/thumb/d/dd/Gfp-wisconsin-madison-the-nature-boardwalk.jpg/2560px-Gfp-wisconsin-madison-the-nature-boardwalk.jpg"
    response3 = xai_grok_chat("What is in this image?", image_url=img_url)
    print(response3)

if __name__ == "__main__":
    main()
