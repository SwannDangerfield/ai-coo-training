import os
from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()

client = Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

models = [
    "claude-3-5-sonnet-latest",
    "claude-4-5-haiku-latest",
]

print("Testing current models...\n")

for model in models:
    try:
        message = client.messages.create(
            model=model,
            max_tokens=100,
            messages=[{"role": "user", "content": "Say 'Setup successful!' and explain what an API is in one sentence."}]
        )
        print(f"✓✓✓ {model} WORKS!\n")
        print(message.content[0].text)
        print(f"\nTokens: {message.usage.input_tokens} in, {message.usage.output_tokens} out")
        print(f"\n--- USE THIS MODEL: {model} ---\n")
        break
    except Exception as e:
        print(f"✗ {model} failed: {str(e)[:100]}\n")