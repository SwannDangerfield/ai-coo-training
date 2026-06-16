import os
import json
from datetime import datetime, timedelta
from openai import OpenAI
from dotenv import load_dotenv
from get_real_data import get_credentials
from googleapiclient.discovery import build
from notion_client import Client as NotionClient

load_dotenv()
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
notion = NotionClient(auth=os.environ.get("NOTION_TOKEN"))
NOTION_DATABASE_ID = os.environ.get("NOTION_TASK_DATABASE_ID")


def get_seven_day_calendar():
    """Get calendar events for today + next 7 days across all calendars"""
    creds = get_credentials()
    service = build('calendar', 'v3', credentials=creds)
    
    now = datetime.utcnow()
    week_ahead = now + timedelta(days=7)
    
    time_min = now.isoformat() + 'Z'
    time_max = week_ahead.isoformat() + 'Z'
    
    print('📅 Fetching next 7 days of calendar events...')
    
    calendar_ids = [
        'primary',
        os.environ.get("SECONDARY_CALENDAR_ID")
    ]
    
    all_events = []
    
    for cal_id in calendar_ids:
        if not cal_id:
            continue
        try:
            events_result = service.events().list(
                calendarId=cal_id,
                timeMin=time_min,
                timeMax=time_max,
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            events = events_result.get('items', [])
            all_events.extend(events)
            print(f'  ✅ {cal_id}: {len(events)} events')
        except Exception as e:
            print(f'  ❌ {cal_id}: Failed - {e}')
    
    print(f'✅ Total: {len(all_events)} events\n')
    return all_events


def get_inbox_emails():
    """Get all emails currently in inbox (unread + read but not archived)"""
    creds = get_credentials()
    service = build('gmail', 'v1', credentials=creds)
    
    print('📧 Fetching inbox emails...')
    
    results = service.users().messages().list(
    userId='me',
    labelIds=['INBOX'],
    q='-category:promotions -category:social -category:updates',
    maxResults=20
).execute()
    
    messages = results.get('messages', [])
    
    emails = []
    for msg in messages:
        msg_data = service.users().messages().get(
            userId='me',
            id=msg['id'],
            format='metadata',
            metadataHeaders=['Subject', 'From', 'Date']
        ).execute()
        
        headers = msg_data.get('payload', {}).get('headers', [])
        subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'No Subject')
        sender = next((h['value'] for h in headers if h['name'] == 'From'), 'Unknown')
        date = next((h['value'] for h in headers if h['name'] == 'Date'), '')
        is_unread = 'UNREAD' in msg_data.get('labelIds', [])
        
        emails.append({
            'id': msg['id'],
            'subject': subject,
            'from': sender,
            'date': date,
            'unread': is_unread
        })
    
    unread = [e for e in emails if e['unread']]
    read_pending = [e for e in emails if not e['unread']]
    
    print(f'  ✅ Unread: {len(unread)}')
    print(f'  ✅ Read but pending: {len(read_pending)}')
    print(f'✅ Total inbox: {len(emails)}\n')
    
    return emails


def sync_to_notion(emails):
    """Sync inbox emails to Notion task database"""
    print('📝 Syncing inbox emails to Notion...')
    
    # Get existing Notion tasks to avoid duplicates
    existing = notion.databases.query(database_id=NOTION_DATABASE_ID)

    existing_subjects = [
        page['properties']['Name']['title'][0]['text']['content']
        for page in existing['results']
        if page['properties']['Name']['title']
    ]

    added = 0
    skipped = 0

    for email in emails:
        subject = email['subject']

        # Skip if already in Notion
        if subject in existing_subjects:
            skipped += 1
            continue

        # Add to Notion
        notion.pages.create(
            parent={"database_id": NOTION_DATABASE_ID},
            properties={
                "Name": {
                    "title": [{"text": {"content": subject}}]
                },
                "Status": {
                    "select": {"name": "To Do"}
                }
            }
        )
        added += 1
    
    print(f'  ✅ Added: {added} tasks')
    print(f'  ⏭️ Skipped (already exists): {skipped}')
    print(f'✅ Notion sync complete\n')
    
    return added


def format_calendar_by_day(events):
    """Group events by day for better readability"""
    by_day = {}
    
    for event in events:
        start = event['start'].get('dateTime', event['start'].get('date'))
        
        if 'T' in start:
            start_dt = datetime.fromisoformat(start.replace('Z', '+00:00'))
            day_key = start_dt.strftime('%A, %B %d')
            time_str = start_dt.strftime('%I:%M %p')
        else:
            day_key = datetime.fromisoformat(start).strftime('%A, %B %d')
            time_str = 'All day'
        
        if day_key not in by_day:
            by_day[day_key] = []
        
        by_day[day_key].append({
            'time': time_str,
            'title': event.get('summary', 'No title'),
            'attendees': len(event.get('attendees', []))
        })
    
    return by_day


def generate_morning_brief():
    """Generate enhanced morning brief"""
    
    print("🌅 Generating Morning Brief...\n")
    
    # Get data
    events = get_seven_day_calendar()
    emails = get_inbox_emails()
    
    # Sync to Notion
    if emails:
        sync_to_notion(emails)
    
    # Format calendar by day
    calendar_by_day = format_calendar_by_day(events)
    
    # Separate unread vs pending emails
    unread = [e for e in emails if e['unread']]
    pending = [e for e in emails if not e['unread']]
    
    # Build context for GPT
    context = f"""You are an executive assistant preparing a morning brief for a COO.

Today is {datetime.now().strftime("%A, %B %d, %Y")}.

CALENDAR - NEXT 7 DAYS:
{json.dumps(calendar_by_day, indent=2)}

UNREAD EMAILS (need attention):
{json.dumps([{'from': e['from'], 'subject': e['subject']} for e in unread], indent=2)}

INBOX EMAILS (read but not archived - pending action):
{json.dumps([{'from': e['from'], 'subject': e['subject']} for e in pending], indent=2)}

Generate a morning brief with these sections:

1. **Executive Summary** (3-4 sentences max)
   - What needs attention TODAY
   - Any upcoming deadlines or key events this week

2. **This Week's Calendar** (7-day view)
   - Highlight busy days
   - Flag any back-to-back meetings or prep needed
   - Note any conflicts or gaps

3. **Inbox Task List**
   - Unread emails needing response
   - Pending emails still requiring action
   - Prioritize by urgency if possible

Keep it under 400 words. Be direct and actionable."""

    print("🤖 Generating brief with GPT...\n")
    
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": context}]
    )
    
    brief = response.choices[0].message.content
    
    # Save to file
    filename = f"morning_brief_{datetime.now().strftime('%Y%m%d')}.md"
    
    with open(filename, "w", encoding="utf-8") as f:
        f.write(f"# Morning Brief\n")
        f.write(f"**{datetime.now().strftime('%A, %B %d, %Y')}**\n\n")
        f.write(brief)
        f.write(f"\n\n---\n")
        f.write(f"## Raw Data\n\n")
        f.write(f"**Calendar Events (7 days):** {len(events)}\n")
        f.write(f"**Unread Emails:** {len(unread)}\n")
        f.write(f"**Pending Emails:** {len(pending)}\n")
        f.write(f"\n*Generated at {datetime.now().strftime('%I:%M %p')}*\n")
    
    print(f"✅ Brief saved to {filename}\n")
    print("="*60)
    print(brief)
    print("="*60)
    print(f"\n💰 Tokens used: {response.usage.total_tokens}")
    
    return brief


if __name__ == "__main__":
    generate_morning_brief()