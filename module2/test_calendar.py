import os
import json
import asyncio
from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()

# Switch to Anthropic API (MCP works better with Claude)
client = Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

def test_calendar():
    """Test pulling calendar events via Claude + MCP"""
    
    print("Testing Calendar MCP access...\n")
    
    # Call Claude with a calendar query
    # Claude will use the MCP server you just authorized
    message = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=2048,
        messages=[
            {
                "role": "user",
                "content": "What events do I have on my calendar today? List them with times."
            }
        ]
    )
    
    print("📅 Calendar Events:")
    print(message.content[0].text)
    print(f"\n💰 Tokens used: {message.usage.input_tokens + message.usage.output_tokens}")

if __name__ == "__main__":
    test_calendar()