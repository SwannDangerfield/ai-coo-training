import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.environ.get("ANTHROPIC_API_KEY")

if api_key:
    print(f"API key loaded successfully!")
    print(f"Key starts with: {api_key[:15]}...")
    print(f"Key ends with: ...{api_key[-6:]}")
    print(f"Key length: {len(api_key)} characters")
else:
    print("ERROR: API key not found in .env file")
    print("\nMake sure your .env file exists and looks like:")
    print("ANTHROPIC_API_KEY=sk-ant-api03-your-key-here")