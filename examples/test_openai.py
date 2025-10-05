import os
from agents.openrouter_clients import deepseek_chat, zai_glm_chat, xai_grok_chat


def main():
    # Create output file path
    output_file = os.path.join(os.path.dirname(__file__), "test_output.txt")

    with open(output_file, "w") as f:
        f.write("Testing OpenRouter APIs\n")
        f.write("=" * 50 + "\n\n")

        f.write("Testing DeepSeek model:\n")
        response1 = deepseek_chat("What is the meaning of life?")
        f.write(response1 + "\n\n")
        f.write("-" * 30 + "\n\n")

        f.write("Testing Z.AI GLM 4.5 Air model:\n")
        response2 = zai_glm_chat("What is the meaning of life?")
        f.write(response2 + "\n\n")
        f.write("-" * 30 + "\n\n")

        f.write("Testing xAI Grok 4 Fast model with image:\n")
        img_url = "https://upload.wikimedia.org/wikipedia/commons/thumb/d/dd/Gfp-wisconsin-madison-the-nature-boardwalk.jpg/2560px-Gfp-wisconsin-madison-the-nature-boardwalk.jpg"
        response3 = xai_grok_chat("What is in this image?", image_url=img_url)
        f.write(response3 + "\n")

    print(f"✅ Output saved to: {output_file}")


if __name__ == "__main__":
    main()
