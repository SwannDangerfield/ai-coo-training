import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {"role": "user", "content": "Say 'OpenAI setup successful!' and explain what an API is in one sentence."}
    ]
)

print(response.choices[0].message.content)
print(f"\nTokens: {response.usage.prompt_tokens} in, {response.usage.completion_tokens} out")