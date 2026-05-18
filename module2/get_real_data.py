import os
import json
from datetime import datetime, timedelta
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# Scopes - Calendar + Gmail read-only
SCOPES = [
    'https://www.googleapis.com/auth/calendar.readonly',
    'https://www.googleapis.com/auth/gmail.readonly'
]

def get_credentials():
    """Handle OAuth flow and return credentials"""
    creds = None
    token_path = 'token_google.json'
    
    # Load existing token if it exists
    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)
    
    # If no valid creds, do OAuth flow
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            print("🔄 Refreshing expired token...")
            creds.refresh(Request())
        else:
            print("🔐 Starting OAuth flow...")
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        
        # Save the token for next time
        with open(token_path, 'w') as token:
            token.write(creds.to_json())
        print("✅ Token saved\n")
    
    return creds

def get_calendar_events():
    """Fetch today's calendar events"""
    creds = get_credentials()
    service = build('calendar', 'v3', credentials=creds)
    
    # Get today's events
    now = datetime.utcnow()
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0).isoformat() + 'Z'
    today_end = (now + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0).isoformat() + 'Z'
    
    print('📅 Fetching calendar events for today...')
    
    events_result = service.events().list(
        calendarId='primary',
        timeMin=today_start,
        timeMax=today_end,
        singleEvents=True,
        orderBy='startTime'
    ).execute()
    
    events = events_result.get('items', [])
    
    # Format events
    formatted_events = []
    for event in events:
        start = event['start'].get('dateTime', event['start'].get('date'))
        end = event['end'].get('dateTime', event['end'].get('date'))
        
        formatted_events.append({
            'summary': event.get('summary', 'No title'),
            'start': start,
            'end': end,
            'attendees': [a.get('email', '') for a in event.get('attendees', [])]
        })
    
    print(f'✅ Found {len(formatted_events)} events\n')
    return formatted_events

def get_recent_emails(max_results=10):
    """Fetch recent unread + important emails from last 24 hours"""
    creds = get_credentials()
    service = build('gmail', 'v1', credentials=creds)
    
    print('📧 Fetching recent emails...')
    
    # Query: unread OR important, from last 24 hours
    yesterday = datetime.now() - timedelta(days=1)
    query = f'after:{yesterday.strftime("%Y/%m/%d")} (is:unread OR is:important)'
    
    results = service.users().messages().list(
        userId='me',
        q=query,
        maxResults=max_results
    ).execute()
    
    messages = results.get('messages', [])
    
    formatted_emails = []
    
    for msg in messages:
        # Get full message details
        message = service.users().messages().get(userId='me', id=msg['id']).execute()
        
        # Extract headers
        headers = message['payload']['headers']
        subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'No subject')
        from_email = next((h['value'] for h in headers if h['name'] == 'From'), 'Unknown')
        date_str = next((h['value'] for h in headers if h['name'] == 'Date'), '')
        
        # Get snippet (preview text)
        snippet = message.get('snippet', '')
        
        # Check if unread
        unread = 'UNREAD' in message.get('labelIds', [])
        
        formatted_emails.append({
            'from': from_email,
            'subject': subject,
            'snippet': snippet,
            'date': date_str,
            'unread': unread
        })
    
    print(f'✅ Found {len(formatted_emails)} emails\n')
    return formatted_emails

def get_all_data():
    """Fetch calendar + emails in one call"""
    calendar = get_calendar_events()
    emails = get_recent_emails()
    
    return {
        'calendar': calendar,
        'emails': emails
    }

if __name__ == "__main__":
    print("Fetching real Google data...\n")
    data = get_all_data()
    
    print("\n" + "="*60)
    print("CALENDAR:")
    print(json.dumps(data['calendar'], indent=2))
    
    print("\n" + "="*60)
    print("EMAILS:")
    print(json.dumps(data['emails'], indent=2))