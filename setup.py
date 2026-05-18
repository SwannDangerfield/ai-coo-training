# ONE-TIME SETUP — run once, save AGENT_ID to your .env (ENV_ID already saved)
import anthropic
from dotenv import load_dotenv
load_dotenv()

client = anthropic.Anthropic()

# Create agent
agent = client.beta.agents.create(
    name="AI Research",
    model="claude-sonnet-4-6",
    system=(
        "You are a research agent scouring the internet for high-quality and new "
        "(less than 2 months old) articles or videos about how to leverage Claude "
        "Cowork/Code for senior-executive level operations professionals."
    ),
    tools=[
        {
            "type": "agent_toolset_20260401"
        },
        {
            "type": "custom",
            "name": "save_to_notion",
            "description": "Save a research finding to the Notion AI Research database.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "title": {"type": "string", "description": "Article or video title"},
                    "url": {"type": "string", "description": "Link to the source"},
                    "takeaways": {"type": "string", "description": "Key takeaways (2-4 sentences)"}
                },
                "required": ["title", "url", "takeaways"]
            }
        }
    ],
    betas=["managed-agents-2026-04-01"]
)
print(f"AGENT_ID={agent.id}")