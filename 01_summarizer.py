import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

# Read a long document
with open("long_document.txt", "r", encoding="utf-8") as f:
    content = f.read()

# Ask GPT to summarize
response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {
            "role": "user",
            "content": f"Summarize this in exactly 3 bullet points:\n\n{content}"
        }
    ],
    max_tokens=500
)

summary = response.choices[0].message.content
print(summary)

# Save the summary
with open("summary.txt", "w", encoding="utf-8") as f:
    f.write(summary)

print(f"\nCost: ${(response.usage.prompt_tokens * 0.00015 + response.usage.completion_tokens * 0.0006) / 1000:.4f}")