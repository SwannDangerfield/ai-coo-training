import os
from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()
client = Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

# Try to list models or just test a basic call
try:
    message = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=100,
        messages=[{"role": "user", "content": "Hi"}]
    )
    print("✅ claude-3-5-sonnet-20241022 works")
except Exception as e:
    print(f"❌ claude-3-5-sonnet-20241022 failed: {e}")
    
try:
    message = client.messages.create(
        model="claude-3-sonnet-20240229",
        max_tokens=100,
        messages=[{"role": "user", "content": "Hi"}]
    )
    print("✅ claude-3-sonnet-20240229 works")
except Exception as e:
    print(f"❌ claude-3-sonnet-20240229 failed: {e}")