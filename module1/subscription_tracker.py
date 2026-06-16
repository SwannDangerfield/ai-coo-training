import json
import os
from datetime import datetime, timedelta
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))


def load_subscriptions():
    """Load subscriptions from JSON file"""
    with open("my_subscriptions.json", "r") as f:
        return json.load(f)


def analyze_subscriptions(subs):
    """Analyze subscriptions and flag upcoming renewals"""
    today = datetime.now().date()
    
    total_monthly = 0
    upcoming_30 = []
    upcoming_60 = []
    by_category = {}
    
    for sub in subs:
        # Monthly cost
        total_monthly += sub['monthly_cost']
        
        # Track by category
        category = sub['category']
        if category not in by_category:
            by_category[category] = 0
        by_category[category] += sub['monthly_cost']
        
        # Check renewal date
        renewal = datetime.strptime(sub['next_renewal_date'], '%Y-%m-%d').date()
        days_until = (renewal - today).days
        sub['days_until_renewal'] = days_until
        
        if days_until <= 30:
            upcoming_30.append(sub)
        elif days_until <= 60:
            upcoming_60.append(sub)
    
    return {
        'total_monthly': round(total_monthly, 2),
        'total_annual': round(total_monthly * 12, 2),
        'by_category': by_category,
        'upcoming_30': upcoming_30,
        'upcoming_60': upcoming_60,
        'total_count': len(subs)
    }


def generate_subscription_report(subs, analysis):
    """Generate AI-powered subscription report"""
    
    # Flag overdue renewals
    overdue = [s for s in subs if s['days_until_renewal'] < 0]
    
    context = f"""You are analyzing subscription spending for a COO.

SUBSCRIPTION SUMMARY:
- Total subscriptions: {analysis['total_count']}
- Total monthly cost: ${analysis['total_monthly']}
- Total annual cost: ${analysis['total_annual']}

SPENDING BY CATEGORY:
{json.dumps(analysis['by_category'], indent=2)}

RENEWING IN NEXT 30 DAYS:
{json.dumps([{
    'name': s['name'],
    'cost': s['monthly_cost'],
    'days_until': s['days_until_renewal'],
    'auto_renew': s['auto_renew'],
    'notes': s.get('notes', '')
} for s in analysis['upcoming_30']], indent=2)}

RENEWING IN 31-60 DAYS:
{json.dumps([{
    'name': s['name'],
    'cost': s['monthly_cost'],
    'days_until': s['days_until_renewal'],
    'auto_renew': s['auto_renew']
} for s in analysis['upcoming_60']], indent=2)}

OVERDUE (past renewal date):
{json.dumps([{
    'name': s['name'],
    'cost': s['monthly_cost'],
    'days_overdue': abs(s['days_until_renewal']),
    'auto_renew': s['auto_renew']
} for s in overdue], indent=2)}

ALL SUBSCRIPTIONS:
{json.dumps([{
    'name': s['name'],
    'monthly_cost': s['monthly_cost'],
    'category': s['category'],
    'days_until_renewal': s['days_until_renewal'],
    'auto_renew': s['auto_renew'],
    'notes': s.get('notes', '')
} for s in subs], indent=2)}

Generate a subscription report with:

1. **Executive Summary**
   - Total monthly/annual spend
   - Biggest expense
   - Any concerns

2. **Upcoming Renewals** (next 30 days)
   - List each with cost and days until renewal
   - Flag non-auto-renew ones (need manual action)
   - Flag any overdue

3. **Spending by Category**
   - Breakdown with percentages
   - Any category that seems high?

4. **Recommendations**
   - Any subscriptions worth reconsidering?
   - Any that overlap (e.g., multiple streaming services)?
   - Any quick wins to save money?

Keep it under 500 words. Be direct and specific with dollar amounts."""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": context}]
    )
    
    return response.choices[0].message.content, response.usage.total_tokens


def main():
    print("💳 Subscription Tracker\n")
    print("=" * 60)
    
    # Load and analyze
    subs = load_subscriptions()
    analysis = analyze_subscriptions(subs)
    
    # Print quick summary
    print(f"📊 QUICK SUMMARY:")
    print(f"  Total subscriptions: {analysis['total_count']}")
    print(f"  Monthly cost: ${analysis['total_monthly']}")
    print(f"  Annual cost: ${analysis['total_annual']}")
    print(f"  Renewing in 30 days: {len(analysis['upcoming_30'])}")
    print(f"  Renewing in 31-60 days: {len(analysis['upcoming_60'])}")
    print()
    
    # Generate report
    print("🤖 Generating report with GPT...\n")
    report, tokens = generate_subscription_report(subs, analysis)
    
    # Save report
    filename = f"subscription_report_{datetime.now().strftime('%Y%m%d')}.md"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(f"# Subscription Report\n")
        f.write(f"**Generated: {datetime.now().strftime('%B %d, %Y')}**\n\n")
        f.write(report)
        f.write(f"\n\n---\n")
        f.write(f"## All Subscriptions\n\n")
        f.write(f"| Name | Monthly Cost | Category | Next Renewal | Auto-Renew |\n")
        f.write(f"|------|-------------|----------|--------------|------------|\n")
        for sub in sorted(subs, key=lambda x: x['monthly_cost'], reverse=True):
            f.write(f"| {sub['name']} | ${sub['monthly_cost']} | {sub['category']} | {sub['next_renewal_date']} | {'✅' if sub['auto_renew'] else '❌'} |\n")
        f.write(f"\n*Generated at {datetime.now().strftime('%I:%M %p')}*\n")
    
    print("=" * 60)
    print(report)
    print("=" * 60)
    print(f"\n✅ Report saved to {filename}")
    print(f"💰 Tokens used: {tokens}")


if __name__ == "__main__":
    main()