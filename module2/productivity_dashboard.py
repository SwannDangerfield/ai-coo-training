import os
import json
from datetime import datetime, timedelta
from collections import defaultdict
from openai import OpenAI
from dotenv import load_dotenv
from get_real_data import get_credentials
from googleapiclient.discovery import build

load_dotenv()
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))


def get_week_calendar():
    """Get last week's calendar events from multiple calendars"""
    creds = get_credentials()
    service = build('calendar', 'v3', credentials=creds)
    
    now = datetime.utcnow()
    week_ago = now - timedelta(days=7)
    
    week_start = week_ago.replace(hour=0, minute=0, second=0, microsecond=0).isoformat() + 'Z'
    week_end = now.isoformat() + 'Z'
    
    print('📅 Fetching calendar events from last 7 days...')
    
    # Calendar IDs to pull from
    calendar_ids = [
        'primary',  # Almaguer Family (your primary calendar)
        'ro85evq28963apm4bt1hd0qqhg@group.calendar.google.com'  # Replace with your full ID
    ]
    
    all_events = []
    
    for cal_id in calendar_ids:
        try:
            events_result = service.events().list(
                calendarId=cal_id,
                timeMin=week_start,
                timeMax=week_end,
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

def get_week_emails():
    """Get email count from last 7 days"""
    creds = get_credentials()
    service = build('gmail', 'v1', credentials=creds)
    
    print('📧 Fetching emails from last 7 days...')
    
    week_ago = datetime.now() - timedelta(days=7)
    query = f'after:{week_ago.strftime("%Y/%m/%d")}'
    
    results = service.users().messages().list(
        userId='me',
        q=query,
        maxResults=100
    ).execute()
    
    messages = results.get('messages', [])
    print(f'✅ Found {len(messages)} emails\n')
    
    return len(messages)


def categorize_event(event):
    """
    Categorize event into: Meeting, Focus Time, or Personal
    
    Logic:
    - Meeting: Has other attendees
    - Focus Time: Solo event with focus-related keywords
    - Personal: Solo event with personal keywords
    - Other: Everything else (defaults to Focus Time)
    """
    summary = event.get('summary', 'No title').lower()
    attendees = event.get('attendees', [])
    
    # Has other people = Meeting
    if len(attendees) > 0:
        return 'Meetings'
    
    # Solo events - check keywords
    focus_keywords = ['focus', 'deep work', 'coding', 'writing', 'block', 'heads down']
    personal_keywords = ['dentist', 'gym', 'workout', 'personal', 'appointment', 
                         'lunch', 'dinner', 'coffee', 'errands', 'break', 
                         'dr', 'krav', 'therapy', 'telehealth', 'laser', 
                         'zivah', 'remy', 'pina', 'ryan']
    
    if any(keyword in summary for keyword in focus_keywords):
        return 'Focus Time'
    elif any(keyword in summary for keyword in personal_keywords):
        return 'Personal'
    else:
        # Default: solo calendar blocks without clear keywords = Focus Time
        return 'Focus Time'


def analyze_time_breakdown(events):
    """Analyze how time was spent across categories and days"""
    
    by_day = defaultdict(lambda: {
        'Meetings': 0,
        'Focus Time': 0,
        'Personal': 0,
        'event_count': 0
    })
    
    by_category = defaultdict(float)
    total_hours = 0
    
    for event in events:
        start = event['start'].get('dateTime', event['start'].get('date'))
        end = event['end'].get('dateTime', event['end'].get('date'))
        
        # Skip all-day events (no 'T' in timestamp)
        if 'T' not in start:
            continue
        
        # Calculate duration
        start_dt = datetime.fromisoformat(start.replace('Z', '+00:00'))
        end_dt = datetime.fromisoformat(end.replace('Z', '+00:00'))
        duration_hours = (end_dt - start_dt).total_seconds() / 3600
        
        # Categorize
        category = categorize_event(event)
        
        # Track by day
        day_name = start_dt.strftime('%A')
        by_day[day_name][category] += duration_hours
        by_day[day_name]['event_count'] += 1
        
        # Track by category
        by_category[category] += duration_hours
        total_hours += duration_hours
    
    return {
        'by_day': dict(by_day),
        'by_category': dict(by_category),
        'total_hours': round(total_hours, 1)
    }


def generate_dashboard():
    """Generate weekly productivity dashboard"""
    
    print("📊 Analyzing your week...\n")
    
    # Get data
    events = get_week_calendar()
    email_count = get_week_emails()
    
    # Analyze
    analysis = analyze_time_breakdown(events)
    
    # Category breakdown
    print("\n🔍 Category Breakdown:")
    print(f"  Meetings: {analysis['by_category'].get('Meetings', 0)} hours")
    print(f"  Focus Time: {analysis['by_category'].get('Focus Time', 0)} hours")
    print(f"  Personal: {analysis['by_category'].get('Personal', 0)} hours")
    print(f"  Total: {analysis['total_hours']} hours")
    print()
    
    meeting_hours = analysis['by_category'].get('Meetings', 0)
    focus_hours = analysis['by_category'].get('Focus Time', 0)
    personal_hours = analysis['by_category'].get('Personal', 0)
    
    # Build context for GPT
    context = f"""You are analyzing a week of productivity data for a COO.

TIME BREAKDOWN (last 7 days):
- Meetings (with attendees): {meeting_hours} hours
- Focus Time (solo work blocks): {focus_hours} hours
- Personal (appointments, errands): {personal_hours} hours
- Email volume: {email_count} emails

BREAKDOWN BY DAY:
{json.dumps(analysis['by_day'], indent=2)}

Generate a weekly productivity dashboard with:

1. **Executive Summary** (2-3 sentences)
   - Overall assessment of the week
   - Key insight or concern

2. **Time Analysis**
   - Meeting vs. focus vs. personal time breakdown
   - Most/least busy days
   - Quality of time allocation (enough focus time?)

3. **Insights & Recommendations**
   - Patterns you notice (e.g., "Meeting-heavy Tuesdays")
   - Suggestions for next week (e.g., "Block more focus time on Mondays")
   - Email management observations

Keep it under 400 words. Be direct and actionable."""

    print("🤖 Generating dashboard with GPT...\n")
    
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": context}]
    )
    
    dashboard = response.choices[0].message.content
    
    # Save to file
    filename = f"productivity_dashboard_{datetime.now().strftime('%Y%m%d')}.md"
    
    with open(filename, "w", encoding="utf-8") as f:
        f.write(f"# Weekly Productivity Dashboard\n")
        f.write(f"**Week of {(datetime.now() - timedelta(days=7)).strftime('%B %d')} - {datetime.now().strftime('%B %d, %Y')}**\n\n")
        f.write(dashboard)
        f.write(f"\n\n---\n")
        f.write(f"## Raw Data\n\n")
        f.write(f"**Total Events:** {len(events)}\n\n")
        f.write(f"**Time Breakdown:**\n")
        f.write(f"- Meetings: {meeting_hours} hours\n")
        f.write(f"- Focus Time: {focus_hours} hours\n")
        f.write(f"- Personal: {personal_hours} hours\n")
        f.write(f"- Total: {analysis['total_hours']} hours\n\n")
        f.write(f"**Emails:** {email_count}\n")
        f.write(f"\n*Generated at {datetime.now().strftime('%I:%M %p')}*\n")
    
    print(f"✅ Dashboard saved to {filename}\n")
    print("="*60)
    print(dashboard)
    print("="*60)
    print(f"\n💰 Tokens used: {response.usage.total_tokens}")
    
    return dashboard


if __name__ == "__main__":
    generate_dashboard()