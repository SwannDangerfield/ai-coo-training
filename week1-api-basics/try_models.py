import os
from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()

client = Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

# Try each of these in order
models_to_try = [
    "claude-sonnet-4-20250514",
    "claude-3-5-sonnet-20241022",
    "claude-3-5-sonnet-latest",
    "claude-sonnet-latest",
]

for model in models_to_try:
    try:
        print(f"Trying {model}...")
        message = client.messages.create(
            model=model,
            max_tokens=100,
            messages=[{"role": "user", "content": "Say 'This model works!'"}]
        )
        print(f"\n✓✓✓ SUCCESS WITH: {model}")
        print(f"Response: {message.content[0].text}\n")
        break
    except Exception as e:
        print(f"Failed: {str(e)[:80]}\n")