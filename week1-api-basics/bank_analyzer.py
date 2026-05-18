import os
import csv
import json
from openai import OpenAI
from dotenv import load_dotenv
from collections import defaultdict

load_dotenv()

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

def load_transactions(csv_path):
    """Load transactions from bank CSV"""
    transactions = []
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            transactions.append(row)
    return transactions

def categorize_transaction(description, amount):
    """Use AI to categorize a single transaction"""
    
    categories = """
    Categories:
    - Housing (rent, mortgage, utilities, internet, insurance)
    - Transportation (gas, car payment, insurance, maintenance, uber/lyft)
    - Groceries (groceries, Thrive Market)
    - Restaurants (restaurants, delivery, bars)
    - Healthcare (doctor, pharmacy, insurance)
    - Entertainment (streaming, movies, concerts, hobbies)
    - Shopping (clothing, electronics, home goods, amazon)
    - Subscriptions (Google One, Prime Video, HBO Max)
    - Personal (haircuts, gym, subscriptions)
    - Pet Care (canine cardio, vet appointments)
    - Other
    """
    
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": f"You categorize bank transactions. {categories}\n\nReturn ONLY the category name, nothing else."
            },
            {
                "role": "user",
                "content": f"Transaction: '{description}' Amount: ${amount}\n\nWhat category?"
            }
        ],
        max_tokens=20,
        temperature=0
    )
    
    category = response.choices[0].message.content.strip()
    return category

def analyze_statement(csv_path, process_all=True):
    """Analyze entire bank statement"""
    
    print("Loading transactions...")
    transactions = load_transactions(csv_path)
    total_transactions = len(transactions)
    print(f"Found {total_transactions} transactions\n")
    
    # Process all or just first 10
    to_process = transactions if process_all else transactions[:10]
    
    print(f"Categorizing {len(to_process)} transactions...")
    print("(This will take a few minutes for all 668)\n")
    
    total_cost = 0
    
    for i, txn in enumerate(to_process):
        description = txn.get('Description', txn.get('description', txn.get('Merchant', '')))
        amount = txn.get('Amount', txn.get('amount', '0'))
        
        category = categorize_transaction(description, amount)
        txn['category'] = category
        
        # Estimate cost (rough approximation)
        # gpt-4o-mini: $0.150/1M input tokens, $0.600/1M output tokens
        # Each call is ~100 input tokens, ~5 output tokens
        call_cost = (100 * 0.150 + 5 * 0.600) / 1_000_000
        total_cost += call_cost
        
        if i % 50 == 0:  # Progress update every 50
            print(f"Progress: {i+1}/{len(to_process)} (${total_cost:.4f} so far)")
    
    print(f"\nTotal API cost: ${total_cost:.4f}")
    
    # Save all categorized transactions
    output_file = 'all_categorized_transactions.json' if process_all else 'categorized_transactions.json'
    with open(output_file, 'w') as f:
        json.dump(to_process, f, indent=2)
    print(f"Saved to {output_file}")
    
    # Generate summary report
    if process_all:
        generate_report(to_process)

def generate_report(transactions):
    """Generate spending summary"""
    
    # Group by category and sum amounts, excluding Income
    category_totals = defaultdict(float)

    for txn in transactions:
        category = txn.get('category', 'Other')
        if category == "Income":
            continue
        amount_str = txn.get('Amount', txn.get('amount', '0'))

        try:
            amount = float(str(amount_str).replace('$', '').replace(',', ''))
            category_totals[category] += amount
        except:
            continue

    # Print report
    print("\n" + "="*60)
    print("SPENDING SUMMARY")
    print("="*60)

    sorted_categories = sorted(category_totals.items(),
                               key=lambda x: abs(x[1]),
                               reverse=True)

    total_spent = 0

    for category, amount in sorted_categories:
        total_spent += abs(amount)
        print(f"{category:20} ${abs(amount):>10,.2f}")

    print("="*60)
    print(f"{'TOTAL SPENT':20} ${total_spent:>10,.2f}")
    print("="*60)

    # Save report
    with open('spending_report.txt', 'w') as f:
        f.write("SPENDING SUMMARY\n")
        f.write("="*60 + "\n")
        for category, amount in sorted_categories:
            f.write(f"{category:20} ${abs(amount):>10,.2f}\n")
        f.write("="*60 + "\n")
        f.write(f"{'TOTAL SPENT':20} ${total_spent:>10,.2f}\n")
    
    print("\nReport saved to spending_report.txt")

if __name__ == "__main__":
    csv_file = "transactions.csv"
    
    if os.path.exists(csv_file):
        # Change to True to process all 668 transactions
        analyze_statement(csv_file, process_all=True)
    else:
        print(f"ERROR: {csv_file} not found")