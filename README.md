# AI-Fluent Operator Training

Building AI agents that automate real operational workflows. No tutorials, no toy examples—just working systems with my actual data.

# Interview: Can you build with AI?
"I built a personal finance agent that analyzes my bank transactions. It loads Chase + Wells Fargo CSVs, filters out payments and transfers, categorizes transactions with AI, and generates budget reports. Cost: $0.01 per analysis. Here's the GitHub repo."

## What I Built

### 1. Subscription Tracker (Module 1, Task 4)
Natural language queries over my real subscription data.

**Query:** "What am I spending on entertainment?"  
**Output:** "Netflix and Spotify, totaling $26.98/month."

[Code](module1/04_tool_use.py) | Demo: Run queries in natural language, GPT decides which tools to call

**Tech:** OpenAI GPT-4o-mini, function calling, JSON data store

---

### 2. Personal Finance Agent (Module 1, Task 5)
Analyzes my actual bank transactions (Chase credit card + Wells Fargo checking).

**Features:**
- Loads multiple CSV files automatically
- Filters out payments, transfers, deposits (only real expenses)
- AI categorization of transactions
- Generates markdown budget reports

**Real Output:**
- Total spend: $201,343 across 1,260 transactions
- Average transaction: $159.80
- Top category: [Your actual top category]

[Code](module1/05_finance_agent.py) | [Sample Report](module1/budget_report_20260517.md)

**Tech:** OpenAI GPT-4o-mini, multi-CSV loading, batch AI categorization

---

### 3. Document Summarizer (Module 1, Task 1)
Takes long emails or articles, returns 3-bullet summaries.

[Code](module1/01_summarize.py)

---

### 4. Transaction Classifier (Module 1, Task 2)
Batch categorizes 20+ transactions in one API call.

[Code](module1/02_classify.py)

---

### 5. Data Extractor (Module 1, Task 3)
Messy meeting notes → structured JSON with decisions, action items, blockers.

[Code](module1/03_extract.py)

---

## Tech Stack

- **LLM:** OpenAI GPT-4o-mini (50x cheaper than Sonnet, same quality for structured tasks)
- **Language:** Python 3.11
- **Key Libraries:** `openai`, `python-dotenv`, `csv`, `json`
- **Patterns:** Function calling, multi-turn conversations, batch processing

## Cost Reality

- Subscription tracker: ~$0.0002 per query
- Finance agent full analysis: ~$0.01
- Budget report generation: ~$0.02 (categorizes 200 transactions)

**Monthly cost if I ran these weekly:** ~$0.50

## What I Learned

See [decisions.md](decisions.md) for:
- Real failure cases (with screenshots)
- Why I switched from Anthropic to OpenAI API
- CSV filtering logic for credit cards vs checking accounts
- Multi-turn tool use debugging

## How to Run

### Setup (5 min)

```bash
# Clone repo
git clone [your-repo-url]
cd ai-coo-training

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Mac/Linux
# or: .\venv\Scripts\activate  # Windows

# Install dependencies
pip install openai python-dotenv

# Add your API key
echo "OPENAI_API_KEY=your-key-here" > .env
```

### Run the Finance Agent

```bash
cd module1
python 05_finance_agent.py
```

Replace the CSV files with your own bank exports, or use the sample data.

### Run the Subscription Tracker

```bash
cd module1
python 04_tool_use.py
```

Edit `my_subscriptions.json` with your actual subscriptions.

---

## What's Next

- **Module 1:** Polish module by adding charts to budget report (matplotlib), deduplicating transactions, and adding date filtering.
- **Module 2:** Morning Brief Agent (Gmail + Google Calendar → daily summary)
- **Module 3:** Build my own MCP server
- **Module 4:** Flagship portfolio projects

---

## Repository Structure
ai-coo-training/
├── README.md
├── decisions.md           # What broke and how I fixed it
├── .env.example          # Template for API keys
├── module1/
│   ├── 01_summarize.py
│   ├── 02_classify.py
│   ├── 03_extract.py
│   ├── 04_tool_use.py           # Subscription tracker
│   ├── 05_finance_agent.py      # Finance agent
│   ├── my_subscriptions.json    # Sample data
│   └── budget_report_*.md       # Generated reports
└── module2/              # Coming soon

---

**Timeline:** Started [May 12, 2026] | Module 1 completed in ~25 hours

Built by [Kendall Almaguer] | [LinkedIn](www.linkedin.com/in/kcalmaguer) | [Email](kendalleclark@gmail.com)