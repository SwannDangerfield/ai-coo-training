import os
from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()

client = Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

# Check your API key is loading
print(f"API Key loaded: {os.environ.get('ANTHROPIC_API_KEY')[:20]}...")

# Try the actual latest model IDs
models_to_try = [
    "claude-3-5-sonnet-20241022",
    "claude-3-5-sonnet-latest", 
    "claude-3-5-sonnet-20240620",
    "claude-3-sonnet-20240229",
    "claude-3-opus-20240229",
    "claude-3-haiku-20240307"
]

for model in models_to_try:
    try:
        message = client.messages.create(
            model=model,
            max_tokens=50,
            messages=[{"role": "user", "content": "Test"}]
        )
        print(f"✅ {model} WORKS!")
        print(f"   Response: {message.content[0].text[:50]}")
        break  # Stop on first success
    except Exception as e:
        print(f"❌ {model} failed: {str(e)[:80]}")