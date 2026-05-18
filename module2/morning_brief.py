import os
import json
from datetime import datetime
from openai import OpenAI
from dotenv import load_dotenv
from get_real_data import get_all_data

load_dotenv()
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

def load_data():
    """Load real calendar + emails, mock tasks"""
    
    print("📊 Loading real data from Google...\n")
    
    # Real data from Google
    google_data = get_all_data()
    calendar = google_data['calendar']
    emails = google_data['emails']
    
    # Mock tasks for now (add real task integration later)
    with open("mock_tasks.json", "r") as f:
        tasks = json.load(f)
    
    return calendar, emails, tasks

def generate_morning_brief():
    """Generate a morning brief from real calendar/email + mock tasks"""
    
    calendar, emails, tasks = load_data()
    
    # Build context for GPT
    context = f"""You are an executive assistant preparing a morning brief for a COO.

Today is {datetime.now().strftime("%A, %B %d, %Y")}.

CALENDAR (today's events - REAL DATA):
{json.dumps(calendar, indent=2)}

EMAILS (unread/important from last 24h - REAL DATA):
{json.dumps(emails, indent=2)}

TASKS (active/upcoming):
{json.dumps(tasks, indent=2)}

Generate a concise morning brief with:
1. Executive Summary (2-3 sentences - what needs attention TODAY)
2. Today's Schedule (highlight any back-to-back meetings or prep needs)
3. Critical Action Items (flag anything due today or blocking others)
4. Heads Up (email threads needing response, deadline conflicts, prep gaps)

**Look for connections:** If an email relates to a meeting today, mention it. If a task is due but not scheduled, flag it.

Keep it under 400 words. Be direct and actionable."""

    print("🤖 Generating brief with GPT...\n")
    
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "user",
                "content": context
            }
        ]
    )
    
    brief = response.choices[0].message.content
    
    # Save to file
    filename = f"morning_brief_{datetime.now().strftime('%Y%m%d')}.md"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(f"# Morning Brief - {datetime.now().strftime('%B %d, %Y')}\n\n")
        f.write(brief)
        f.write("\n\n---\n")
        f.write(f"*Generated at {datetime.now().strftime('%I:%M %p')} using real Google Calendar + Gmail data*\n")
    
    print(f"✅ Brief saved to {filename}\n")
    print("="*60)
    print(brief)
    print("="*60)
    print(f"\n💰 Tokens used: {response.usage.total_tokens}")
    
    return brief

if __name__ == "__main__":
    generate_morning_brief()