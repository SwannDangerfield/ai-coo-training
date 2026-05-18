# Create: full_analysis.py
import json
from collections import Counter

with open('all_categorized_transactions.json', 'r') as f:
    transactions = json.load(f)

print(f"\n=== PROCESSED {len(transactions)} TRANSACTIONS ===\n")

# What's in the $14,270 "Other" bucket?
other_txns = [t for t in transactions if t.get('category') == 'Other']
print(f"'Other' category: {len(other_txns)} transactions = ${sum(float(t['Amount']) for t in other_txns):,.2f}\n")

print("First 20 'Other' transactions:")
for txn in other_txns[:20]:
    print(f"  {txn['Description'][:45]:45} ${float(txn['Amount']):>10,.2f}")

# Category breakdo