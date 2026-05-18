import os
from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()

client = Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

models = [
    "claude-3-5-sonnet-20241022",
    "claude-3-5-sonnet-20240620",
    "claude-3-opus-20240229",
    "claude-3-sonnet-20240229",
    "claude-3-haiku-20240307",
]

print("Testing models...\n")

for model in models:
    try:
        message = client.messages.create(
            model=model,
            max_tokens=50,
            messages=[{"role": "user", "content": "hi"}]
        )
        print(f"SUCCESS: {model} works!")
        print(f"Response: {message.content[0].text}\n")
        break
    except Exception as e:
        print(f"Failed: {model}")
        print(f"  Error: {str(e)[:100]}\n")