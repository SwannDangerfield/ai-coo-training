# Run this once to update the agent with the new tool schema
import os
import anthropic
from dotenv import load_dotenv
load_dotenv()

client = anthropic.Anthropic()
AGENT_ID = os.environ["AGENT_ID"]

agent = client.beta.agents.update(
    agent_id=AGENT_ID,
    version=1,
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
                    "takeaways": {"type": "string", "description": "Key takeaways (2-4 sentences)"},
                    "date_published": {"type": "string", "description": "Publication date in YYYY-MM-DD format. If exact date unknown, estimate from context."},
                    "relevance": {"type": "string", "enum": ["1","2","3","4","5","6","7","8","9","10"], "description": "Relevance score 1-10 for senior operations executives leveraging Claude."}
                },
                "required": ["title", "url", "takeaways", "date_published", "relevance"]
            }
        }
    ],
    betas=["managed-agents-2026-04-01"]
)
print(f"Agent updated: {agent.id}")
