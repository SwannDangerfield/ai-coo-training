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