import os
import requests
import anthropic
from dotenv import load_dotenv
load_dotenv()

client = anthropic.Anthropic()

AGENT_ID          = os.environ["AGENT_ID"]
ENV_ID            = os.environ["ENV_ID"]
NOTION_TOKEN      = os.environ["NOTION_TOKEN"]
NOTION_DATABASE_ID = os.environ["NOTION_DATABASE_ID"]

KICKOFF = (
    "Research the latest articles and videos (published in the last 2 months) "
    "about how to leverage Claude Cowork/Code for senior-executive level "
    "operations professionals. Find at least 5 high-quality sources and save "
    "each one to Notion using the save_to_notion tool."
)


NOTION_HEADERS = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Notion-Version": "2022-06-28",
    "Content-Type": "application/json",
}

def url_already_saved(url: str) -> bool:
    """Check if a URL already exists in the Notion database."""
    resp = requests.post(
        f"https://api.notion.com/v1/databases/{NOTION_DATABASE_ID}/query",
        headers=NOTION_HEADERS,
        json={"filter": {"property": "URL", "url": {"equals": url}}},
    )
    if resp.ok:
        return len(resp.json().get("results", [])) > 0
    return False

def save_to_notion(title: str, url: str, takeaways: str, date_published: str, relevance: str) -> str:
    if url_already_saved(url):
        return f"Skipped (already saved): {title}"

    resp = requests.post(
        "https://api.notion.com/v1/pages",
        headers=NOTION_HEADERS,
        json={
            "parent": {"database_id": NOTION_DATABASE_ID},
            "properties": {
                "Article Title": {
                    "title": [{"text": {"content": title}}]
                },
                "URL": {
                    "url": url
                },
                "Takeaways": {
                    "rich_text": [{"text": {"content": takeaways}}]
                },
                "Date Published": {
                    "date": {"start": date_published}
                },
                "Relevance": {
                    "select": {"name": relevance}
                },
            },
        },
    )
    if resp.ok:
        return f"Saved: {title}"
    return f"Notion error {resp.status_code}: {resp.text}"


# Create session
session = client.beta.sessions.create(
    agent=AGENT_ID,
    environment_id=ENV_ID,
)
print(f"Session: {session.id}\n")

# Stream-first, then send kickoff
with client.beta.sessions.events.stream(session_id=session.id) as stream:
    client.beta.sessions.events.send(
        session_id=session.id,
        events=[{
            "type": "user.message",
            "content": [{"type": "text", "text": KICKOFF}],
        }],
    )

    for event in stream:
        if event.type == "agent.message":
            for block in event.content:
                if block.type == "text":
                    print(block.text, end="", flush=True)

        elif event.type == "agent.custom_tool_use" and event.name == "save_to_notion":
            print(f"\n→ Saving: {event.input.get('title')}")
            result = save_to_notion(
                title=event.input["title"],
                url=event.input["url"],
                takeaways=event.input["takeaways"],
                date_published=event.input["date_published"],
                relevance=event.input["relevance"],
            )
            print(f"  {result}")
            client.beta.sessions.events.send(
                session_id=session.id,
                events=[{
                    "type": "user.custom_tool_result",
                    "custom_tool_use_id": event.id,
                    "content": [{"type": "text", "text": result}],
                }],
            )

        elif event.type == "session.status_idle":
            if event.stop_reason.type != "requires_action":
                break

        elif event.type == "session.status_terminated":
            break

print("\n\nDone.")