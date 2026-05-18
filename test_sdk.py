import os
from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()

client = Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

# Try the "latest" alias first
try:
    message = client.messages.create(
        model="claude-3-5-sonnet-latest",
        max_tokens=100,
        messages=[{"role": "user", "content": "Hi"}]
    )
    print("✅ claude-3-5-sonnet-latest works!")
    print(message.content[0].text)
except Exception as e:
    print(f"❌ claude-3-5-sonnet-latest failed: {e}")

# Try the specific version
try:
    message = client.messages.create(
        model="claude-3-5-sonnet-20240620",
        max_tokens=100,
        messages=[{"role": "user", "content": "Hi"}]
    )
    print("✅ claude-3-5-sonnet-20240620 works!")
    print(message.content[0].text)
except Exception as e:
    print(f"❌ claude-3-5-sonnet-20240620 failed: {e}")