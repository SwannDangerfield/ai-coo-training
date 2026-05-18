import os
import json
import csv
from datetime import datetime
from collections import defaultdict
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

def load_transactions(filenames=None):
    """Load transactions from one or more bank CSVs"""
    if filenames is None:
        import glob
        filenames = glob.glob("*.csv") + glob.glob("*.CSV")
        
        if not filenames:
            print("⚠️  No CSV files found")
            return []
    
    if isinstance(filenames, str):
        filenames = [filenames]
    
    all_transactions = []
    skipped_count = 0
    
    for filename in filenames:
        if filename in ["my_subscriptions.json", "debug_files.py"]:
            continue
            
        try:
            with open(filename, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                
                for row in reader:
                    # Handle different column naming conventions
                    description = (row.get("Description") or row.get("DESCRIPTION") or 
                                 row.get("Merchant") or "")
                    
                    category = row.get("Category") or row.get("CATEGORY") or ""
                    
                    # Get amount (handle different column names)
                    amount = (row.get("Amount") or row.get("AMOUNT") or 
                            row.get("Debit") or row.get("Credit"))
                    
                    # FILTER 1: Chase - Skip payment transactions
                    if "payment thank you" in description.lower():
                        skipped_count += 1
                        continue
                    
                    # FILTER 2: Wells Fargo - Skip multiple patterns
                    if "wellsfargo" in filename.lower():
                        # Skip Chase credit card payments
                        if "chase credit" in description.lower():
                            skipped_count += 1
                            continue
                        
                        # Skip internal transfers
                        if "transfer to" in description.lower() or "transfer from" in description.lower():
                            skipped_count += 1
                            continue
                        
                        # Skip checks deposited (income)
                        if "deposited or cashed check" in description.lower():
                            skipped_count += 1
                            continue
                        
                        # Skip Zelle transfers (personal transfers, not expenses)
                        if "zelle to" in description.lower() or "zelle from" in description.lower():
                            skipped_count += 1
                            continue
                        
                        # Skip deposits/income (positive amounts)
                        try:
                            amount_float = float(str(amount).replace("$", "").replace(",", ""))
                            if amount_float > 0:
                                skipped_count += 1
                                continue
                        except:
                            pass
                    
                    # Skip if amount is None or empty
                    if not amount or str(amount).strip() == "":
                        continue
                    
                    # Get date (handle different column names)
                    date = row.get("Transaction Date") or row.get("DATE") or row.get("Date")
                    
                    all_transactions.append({
                        "date": date,
                        "description": description,
                        "amount": amount,
                        "category": category if category else "Uncategorized",  # <-- Keep Chase categories
                        "source_file": filename
                    })
            
            print(f"✅ Loaded transactions from {filename}")
        
        except FileNotFoundError:
            print(f"⚠️  {filename} not found, skipping")
        except Exception as e:
            print(f"❌ Error loading {filename}: {e}")
    
    print(f"📊 Total: {len(all_transactions)} transactions ({skipped_count} filtered out)\n")
    return all_transactions

def generate_budget_report():
    """Generate a markdown budget report"""
    
    # Get the data
    total_data = get_total_spending()
    
    # Categorize first 200 transactions (AI categorization in batches)
    print("📝 Categorizing transactions for report...")
    categorize_transactions()
    
    category_data = get_spending_by_category()
    largest = find_largest_transactions(10)
    
    # Build the report
    report = f"""# Personal Finance Report
Generated: {datetime.now().strftime("%Y-%m-%d %H:%M")}

## Summary
- **Total Spent:** ${total_data['total_spent']:,.2f}
- **Total Transactions:** {total_data['transaction_count']}
- **Average Transaction:** ${total_data['average_transaction']:.2f}

## Spending by Category

"""
    
    for category, amount in category_data['categories'].items():
        # Handle blank/empty categories
        if not category or category.strip() == "":
            display_category = "Uncategorized"
        else:
            display_category = category
        
        percentage = (amount / total_data['total_spent']) * 100
        report += f"- **{display_category.title()}:** ${amount:,.2f} ({percentage:.1f}%)\n"
    
    report += f"\n## Top 10 Largest Expenses\n\n"
    
    for i, txn in enumerate(largest['largest_transactions'], 1):
        report += f"{i}. **{txn['date']}** - {txn['description'][:50]} - ${txn['amount']:,.2f}\n"
    
    report += f"\n---\n*Report generated from {len(TRANSACTIONS)} transactions*\n"
    
    # Save to file
    filename = f"budget_report_{datetime.now().strftime('%Y%m%d')}.md"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(report)
    
    print(f"\n✅ Report saved to {filename}")
    
    return {
        "filename": filename,
        "total_spent": total_data['total_spent'],
        "top_category": category_data['top_category']
    }

TRANSACTIONS = load_transactions()

# Tools for GPT
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_total_spending",
            "description": "Get total spending for a date range",
            "parameters": {
                "type": "object",
                "properties": {
                    "start_date": {
                        "type": "string",
                        "description": "Start date (YYYY-MM-DD) or 'all'"
                    },
                    "end_date": {
                        "type": "string",
                        "description": "End date (YYYY-MM-DD) or 'all'"
                    }
                }
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "categorize_transactions",
            "description": "Categorize all transactions using AI",
            "parameters": {
                "type": "object",
                "properties": {}
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_spending_by_category",
            "description": "Get spending breakdown by category",
            "parameters": {
                "type": "object",
                "properties": {}
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "find_largest_transactions",
            "description": "Find the N largest transactions",
            "parameters": {
                "type": "object",
                "properties": {
                    "count": {
                        "type": "integer",
                        "description": "Number of transactions to return (default 10)"
                    }
                }
            }
        }
    },
{
        "type": "function",
        "function": {
            "name": "generate_budget_report",
            "description": "Generate a detailed budget report and save as markdown",
            "parameters": {
                "type": "object",
                "properties": {}
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search_transactions",
            "description": "Search for transactions by merchant/description",
            "parameters": {
                "type": "object",
                "properties": {
                    "keyword": {
                        "type": "string",
                        "description": "Keyword to search for (e.g., 'Starbucks', 'Amazon')"
                    }
                }
            }
        }
    }
]

# Function implementations
def get_total_spending(start_date="all", end_date="all"):
    """Calculate total spending"""
    total = 0
    count = 0
    
    for t in TRANSACTIONS:
        # Convert amount to float (handle negative numbers, strip $, etc.)
        amount_str = str(t["amount"]).replace("$", "").replace(",", "")
        try:
            amount = abs(float(amount_str))  # abs() for negative amounts
            total += amount
            count += 1
        except:
            continue
    
    return {
        "total_spent": round(total, 2),
        "transaction_count": count,
        "average_transaction": round(total / count, 2) if count > 0 else 0
    }

def categorize_transactions():
    """Use GPT to categorize transactions in batches"""
    
    # Categorize in batches of 50 (balance speed vs cost)
    batch_size = 50
    total_categorized = 0
    
    for i in range(0, min(len(TRANSACTIONS), 200), batch_size):  # Cap at 200 transactions
        batch = TRANSACTIONS[i:i+batch_size]
        descriptions = [t["description"] for t in batch]
        
        prompt = f"""Categorize these transactions into standard budget categories.
Return ONLY a JSON array with one category per transaction.

Categories: pet care, dining, groceries, entertainment, shopping, transportation, utilities, healthcare, travel, subscriptions, housing, other

Transactions:
{json.dumps(descriptions, indent=2)}

Return format: ["dining", "groceries", "entertainment", ...]
"""
        
        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0
            )
            
            categories_text = response.choices[0].message.content
            categories_text = categories_text.replace("```json", "").replace("```", "").strip()
            categories = json.loads(categories_text)
            
            # Update transactions
            for j, category in enumerate(categories):
                if i + j < len(TRANSACTIONS):
                    TRANSACTIONS[i + j]["category"] = category
                    total_categorized += 1
            
            print(f"  ✓ Categorized batch {i//batch_size + 1} ({len(categories)} transactions)")
        
        except Exception as e:
            print(f"  ✗ Batch {i//batch_size + 1} failed: {e}")
    
    return {
        "message": f"Categorized {total_categorized} transactions in batches",
        "total": total_categorized
    }

def get_spending_by_category():
    """Break down spending by category"""
    by_category = defaultdict(float)
    
    for t in TRANSACTIONS:
        category = t.get("category", "Uncategorized")
        amount_str = str(t["amount"]).replace("$", "").replace(",", "")
        try:
            amount = abs(float(amount_str))
            by_category[category] += amount
        except:
            continue
    
    # Sort by amount
    sorted_categories = sorted(by_category.items(), key=lambda x: x[1], reverse=True)
    
    return {
        "categories": {cat: round(amt, 2) for cat, amt in sorted_categories},
        "top_category": sorted_categories[0][0] if sorted_categories else "None",
        "top_amount": round(sorted_categories[0][1], 2) if sorted_categories else 0
    }

def find_largest_transactions(count=10):
    """Find largest transactions"""
    # Sort by amount
    sorted_txns = []
    for t in TRANSACTIONS:
        amount_str = str(t["amount"]).replace("$", "").replace(",", "")
        try:
            amount = abs(float(amount_str))
            sorted_txns.append({
                "date": t["date"],
                "description": t["description"],
                "amount": amount
            })
        except:
            continue
    
    sorted_txns.sort(key=lambda x: x["amount"], reverse=True)
    
    return {
        "largest_transactions": sorted_txns[:count]
    }

def search_transactions(keyword):
    """Search for transactions by keyword"""
    matches = []
    
    for t in TRANSACTIONS:
        if keyword.lower() in t["description"].lower():
            amount_str = str(t["amount"]).replace("$", "").replace(",", "")
            try:
                amount = abs(float(amount_str))
                matches.append({
                    "date": t["date"],
                    "description": t["description"],
                    "amount": amount
                })
            except:
                continue
    
    total = sum(m["amount"] for m in matches)
    
    return {
        "keyword": keyword,
        "match_count": len(matches),
        "total_spent": round(total, 2),
        "transactions": matches[:10]  # First 10 matches
    }

def run_agent(user_message):
    """Run the finance agent"""
    print(f"\n{'='*60}")
    print(f"USER: {user_message}")
    print(f"{'='*60}\n")
    
    messages = [{"role": "user", "content": user_message}]
    
    max_iterations = 5
    iteration = 0
    
    while iteration < max_iterations:
        iteration += 1
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            tools=tools,
            tool_choice="auto"
        )
        
        response_message = response.choices[0].message
        
        if response_message.tool_calls:
            messages.append(response_message)
            
            for tool_call in response_message.tool_calls:
                print(f"\n🔧 GPT called: {tool_call.function.name}")
                print(f"   With input: {tool_call.function.arguments}")
                
                function_args = json.loads(tool_call.function.arguments)
                function_name = tool_call.function.name
                
                # Execute function
                if function_name == "get_total_spending":
                    tool_result = get_total_spending(
                        function_args.get("start_date", "all"),
                        function_args.get("end_date", "all")
                    )
                elif function_name == "categorize_transactions":
                    tool_result = categorize_transactions()
                elif function_name == "get_spending_by_category":
                    tool_result = get_spending_by_category()
                elif function_name == "find_largest_transactions":
                    tool_result = find_largest_transactions(function_args.get("count", 10))
                elif function_name == "search_transactions":
                    tool_result = search_transactions(function_args.get("keyword", ""))
                elif function_name == "generate_budget_report":
                    tool_result = generate_budget_report()
                else:
                    tool_result = {"error": "Unknown function"}
                
                print(f"\n📊 Function returned: {json.dumps(tool_result, indent=2)}")
                
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "name": function_name,
                    "content": json.dumps(tool_result)
                })
            
            continue
        
        else:
            print(f"\n💬 GPT: {response_message.content}\n")
            print(f"💰 Tokens: {response.usage.total_tokens}")
            return response_message.content
    
    print(f"\n⚠️  Hit max iterations")
    return "Too many tool calls"

# Test it
if __name__ == "__main__":
    if not TRANSACTIONS:
        print("\n❌ No transactions loaded. Add transactions.csv first.\n")
    else:
        run_agent("How much have I spent in total?")
        run_agent("What are my top 5 biggest expenses?")
        run_agent("Categorize my transactions and show me spending by category")
        run_agent("How much did I spend on groceries?")
        run_agent("Generate a budget report for me")

# At the very end of your script, add:
print("\n=== AVAILABLE TOOLS ===")
for tool in tools:
    print(f"- {tool['function']['name']}")