import os
from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()

client = Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

# Every model string that has EVER existed
models = [
    # Latest variants
    "claude-3-5-sonnet-latest",
    "claude-4-5-haiku-latest",
    # 2024 versions
    "claude-3-5-sonnet-20241022",
    "claude-3-5-sonnet-20240620",
    # Early 2024
    "claude-3-opus-20240229",
    "claude-3-sonnet-20240229",
    "claude-3-haiku-20240307",
    # 2023 versions (legacy)
    "claude-2.1",
    "claude-2.0",
    "claude-2",
    "claude-instant-1.2",
    "claude-instant-1",
]

print("Trying EVERY model that has ever existed...\n")

for model in models:
    try:
        message = client.messages.create(
            model=model,
            max_tokens=50,
            messages=[{"role": "user", "content": "test"}]
        )
        print(f"\n✓✓✓ FOUND ONE THAT WORKS: {model}")
        print(f"Response: {message.content[0].text}\n")
        break
    except Exception as e:
        error = str(e)
        if "not_found" in error:
            print(f"✗ {model} - not found")
        else:
            print(f"✗ {model} - {error[:80]}")

print("\nIf NOTHING worked, your account has a provisioning bug.")