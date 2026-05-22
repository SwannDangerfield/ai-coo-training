# AI-Fluent Operator Training - Decisions Log

## Week 1: Transaction Categorizer (May 8-10, 2026)

### What I Built
`bank_analyzer.py` - Automated expense categorizer for credit card transactions

**Input:** 668 transactions from Chase credit card CSV export  
**Output:** 
- `all_categorized_transactions.json` - Full categorized dataset
- `spending_report.txt` - Summary by category

### Tech Stack
- OpenAI API (switched from Anthropic due to API key activation bug)
- Python 3.11.7
- CSV → JSON processing

### Results
**Processed:** 668 transactions  
**Categories created:** 11 (Restaurants, Shopping, Groceries, Pet Care, etc.)  
**Runtime:** ~3-5 minutes  
**Cost:** $0.02 (via OpenAI)

**Top spending categories:**
- Restaurants: $8,823.64 (165 transactions)
- Shopping: $8,011.59
- Pet Care: $5,430.03

### What Worked
- Model correctly categorized ~83% of transactions (554/668)
- Clean JSON output with original data preserved
- Fast processing - under 5 minutes for full dataset
- Extremely cheap at scale ($0.02 for 668 = ~$0.30 per 10K transactions)

### Edge Cases / What Broke
**"Other" category: 114 transactions ($14,270.69)**

Main failure modes:
1. **Credit card payments** - `Payment Thank You-Mobile $9,186.43` was categorized as "Other" instead of being filtered out (it's a payment TO the card, not an expense)
2. **Obscure local merchants** - `ALEXANDRIA CLEANERS`, `COMPOST CREW`, `TST* PORT CITY` had no obvious category
3. **Political donations** - `ACTBLUE*` went to "Other"
4. **Tobacco purchases** - `PMUSA` (Philip Morris) unclear category
5. **Small refunds/adjustments** - `JAY HOTEL ROOMS $0.48` (should probably be ignored)

### What I'd Do Differently

**Immediate fixes:**
- Filter out positive amounts (credits/payments) before categorization
- Add "Donations" category for political/charitable giving
- Add "Services" category for dry cleaning, lawn care, etc.
- Set minimum threshold (ignore transactions under $1)

**For production:**
- Add human review flag for "Other" transactions over $100
- Batch API calls instead of one-per-transaction (faster, cheaper)
- Track categorization confidence scores
- Build feedback loop to improve categories over time

### Cost at Scale
- 668 transactions = $0.02
- 10,000 transactions/month = ~$0.30
- 100,000 transactions/month = ~$3.00

**Operator insight:** At this cost, the bottleneck isn't API fees - it's human review time for the ~17% that land in "Other."

### Technical Blocker
**Anthropic API key issue:** Encountered activation bug preventing Claude API usage. Switched to OpenAI to maintain momentum. Need to debug Anthropic setup for Week 2 MCP work.

### Interview Answer
"I built a transaction categorizer that processed 668 real credit card transactions. It correctly categorized 83% automatically, but struggled with three edge cases: credit card payments (which aren't expenses), obscure local merchants without clear categories, and small refunds under $1. The interesting failure mode was that $9K credit card payment getting lumped into 'Other' - in production, you'd filter credits before categorization. Cost was $0.02 for 668 transactions, which scales to about $3 per 100K transactions. At that price, the constraint isn't API cost - it's human review capacity for edge cases."

---

## Next Steps
- [ ] Fix Anthropic API key issue
- [ ] Add expense filtering (remove credits/payments)
- [ ] Re-run with Claude to compare quality vs. OpenAI
- [ ] Document model comparison in decisions.md

## Module 1, Task 4: Tool Use + Real Data

**What worked:**
- Built multi-turn tool use (GPT chains tools together)
- Connected to my actual subscription data (JSON file)
- Can query in natural language: "What am I spending on entertainment?"

**What broke:**
- JSON syntax error (missing comma) - learned to validate with jsonlint.com
- Switched from Anthropic to OpenAI API (gpt-4o-mini is 50x cheaper anyway)

**Cost:**
- ~$0.0002 per query with 4 tools available
- Could run 5,000 queries for $1

**Next:**
- Module 1 Task 5: Personal Finance Agent (same pattern, but with bank transactions)

## Module 1, Task 5: Personal Finance Agent

**What worked:**
- Multi-CSV loading (Chase credit card + Wells Fargo checking)
- Smart filtering (payments, transfers, deposits excluded)
- AI categorization of transactions
- Budget report generator (markdown output)

**What broke:**
- Had to debug Wells Fargo filters (deposits, Zelle, check cashing)
- Chase payment descriptions varied ("Payment Thank You-Mobile")
- Categorize function had wrong API attribute initially

**Real output:**
- [Your total spending]
- [Number of transactions]
- Generated `budget_report_YYYYMMDD.md` with full breakdown

**Cost:**
- Full analysis run: ~$0.01
- Could run this weekly for $0.50/year

**Time saved:**
- Used to spend 1-2 hours manually categorizing in Mint
- Now: 30 seconds to run script + 5 min to review report

**Next:** Module 2 - Morning Brief Agent

## Module 2: Morning Brief Agent

**What worked:**
- Google Calendar API + Gmail API direct integration (skipped MCP complexity)
- OAuth 2.0 flow for Calendar + Gmail read-only access
- Real-time synthesis: pulls actual calendar events + unread/important emails from last 24h
- Windows Task Scheduler automation (runs daily at 7am)
- Switched from Anthropic to OpenAI API (gpt-4o-mini) - Anthropic key had no model access

**What broke:**
- MCP SDK from Python was flaky and protocol versions incompatible
  - Spent 2 hours debugging MCP connections before switching to direct Google APIs
  - Lesson: When the abstraction layer is broken, drop down to the underlying API
- Anthropic API returned 404 for all models despite valid key
  - Switched to OpenAI which was already working from Module 1
- GitHub push protection blocked commits with OAuth tokens/credentials in history
  - Had to nuke Git history and start fresh with proper .gitignore
  - Lesson: Set up .gitignore BEFORE first commit, always

**Real output:**
- Morning brief generated from my actual Google Calendar + Gmail
- Synthesizes 4+ calendar events + 10+ emails into 300-word actionable brief
- Identifies connections (e.g., "Sarah's email about AWS costs relates to your 4pm vendor renewal meeting")
- Saved as markdown file: `morning_brief_YYYYMMDD.md`

**Cost:**
- ~$0.01 per brief (150-300 tokens)
- Running daily = $3.65/year
- 50x cheaper than any "executive briefing" SaaS tool

**Time saved:**
- Before: 15-20 minutes every morning checking calendar, scanning email, mental synthesis
- After: 2 minutes reading the brief
- ROI: Saves ~90 hours/year

**Technical wins:**
- Learned OAuth 2.0 flow end-to-end (Google Cloud Console, scopes, token refresh)
- Handled multiple data sources (Calendar API, Gmail API) with single credential flow
- Built automated scheduling with Windows Task Scheduler + batch file
- Proper secrets management (.gitignore, never commit tokens/credentials)

**What I'd do differently at scale:**
- Add error notifications (email/Slack if brief generation fails)
- Add task integration (Notion API, Asana API, or local task file)
- Cache calendar/email data to reduce API calls if run multiple times per day
- Add "prep needed" detection (flag meetings without agenda or with many attendees)
- Implement retry logic if Google APIs are rate-limited

**Next steps:**
- Could add real task integration (currently removed mock tasks)
- Could add voice/SMS delivery option (Twilio integration)
- Could expand to pull Slack mentions, GitHub PRs, etc.
- Module 3: Build custom MCP server (turn one of my agents into a reusable MCP)

---

**Module 1 + 2 Summary:**
- Total agents built: 7 (5 in Module 1, 2 in Module 2)
- Total time: ~10 hours
- Plan estimate: 30+ hours
- All using real data (bank transactions, Google Calendar, Gmail)
- Total monthly cost if running everything: <$1

## Module 2, Task 3: Productivity Dashboard

**What worked:**
- Multi-calendar support: pulls from both "Kendall Almaguer" (primary) and "Almaguer Calendar" (secondary)
- Smart event categorization using attendees + keywords:
  - Meetings: Events with other attendees
  - Focus Time: Solo work blocks (coding, deep work, etc.)
  - Personal: Appointments, therapy, errands (matched by keywords: dr, krav, therapy, telehealth, etc.)
- Weekly retrospective analysis: backward-looking vs. Morning Brief's forward-looking approach
- Clean category breakdown output shows real time allocation before GPT synthesis
- Cost: ~$0.02 per weekly report (867 tokens)

**What broke:**
- Python bytecode caching nightmare
  - Edited file but Python kept running old cached version from `__pycache__/`
  - Spent 30+ minutes debugging "why isn't my code running?"
  - Fix: `Remove-Item __pycache__ -Recurse -Force`
  - Lesson: When code changes don't take effect, delete __pycache__ first
- Duplicate function definitions in same file
  - Had TWO `generate_dashboard()` functions - old version and new version
  - Python was running the first one (old), ignoring the second (new)
  - VS Code showed warnings but didn't make it obvious
  - Fix: Search for function name, found it twice, deleted old version
- Virtual environment deactivation
  - venv got deactivated mid-session (probably when switching directories)
  - Led to "ModuleNotFoundError: No module named 'openai'"
  - Fix: Always check `(venv)` shows in prompt before running scripts
- Case-sensitive keyword matching
  - Added personal keywords like 'Dr', 'Krav' but was checking against `summary.lower()`
  - Events with "Dr. Smith" weren't matching because 'Dr' ≠ 'dr'
  - Fix: lowercase ALL keywords in the list

**Real output:**
- Weekly dashboard analyzing last 7 days across 13 calendar events
- Example breakdown from actual data:
  - Meetings: 2 hours (8%)
  - Focus Time: 24 hours (87%)
  - Personal: 6.5 hours (5%)
- GPT identifies patterns: "Meeting-heavy Tuesdays", "Low Friday productivity"
- Actionable recommendations: redistribute meetings, block more focus time, set fixed email hours
- Raw data section shows breakdown by category (not hidden like debug output)

**Technical wins:**
- Learned Google Calendar API supports multiple calendar IDs in single script
- Used `defaultdict(lambda: dict)` for clean nested data structures
- Clean function separation: `categorize_event()` does one thing well
- Proper error handling when pulling from multiple calendars (try/except per calendar)

**Cost:**
- ~$0.02 per weekly report
- Running monthly (4 reports) = $0.08/month
- 50x cheaper than any "productivity analytics" SaaS

**Time saved:**
- Before: No systematic weekly review, relied on memory
- After: 3-5 minutes reviewing synthesized insights
- Identifies patterns I wouldn't catch manually (e.g., "Wednesdays have 10 hours of focus time")

**What I'd do differently at scale:**
- Add week-over-week comparison ("Meeting time up 30% from last week")
- Flag anomalies automatically ("You spent 15 hours in meetings - highest ever")
- Add task completion tracking from Notion/Asana
- Visual charts (time breakdown by day as bar chart)
- Email it automatically every Sunday night

**Categorization logic decisions:**
- Default solo events to Focus Time (not Personal) - assumes calendar blocking = intentional work time
- This might miscategorize "forgot to add attendees" meetings as Focus Time
- Could improve: check event description for meeting URLs (Zoom, Meet) → reclassify as Meeting
- Trade-off: Simple rules work 90% of the time; edge cases require human review

**Integration with Morning Brief:**
- Morning Brief: Daily, forward-looking ("what's today?")
- Productivity Dashboard: Weekly, backward-looking ("how was last week?")
- Together they create a complete productivity feedback loop

**Next steps:**
- Could schedule this to run automatically every Sunday at 8pm (Task Scheduler)
- Could add Slack integration (post dashboard to #personal channel)
- Could expand to pull from Notion for task completion rates

---

**Module 2 Complete:**
- Morning Brief: Daily synthesis (calendar + email) ✅
- Productivity Dashboard: Weekly retrospective ✅
- Total time: ~14 hours vs. 25+ hour estimate
- Both using real Google Calendar + Gmail data
- Total monthly cost if running both: <$1