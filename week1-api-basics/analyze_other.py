import json

# Load the transactions
with open('categorized_transactions.json', 'r') as f:
    transactions = json.load(f)

# Filter for "Other" category
other_txns = [t for t in transactions if t.get('category') == 'Other']

print(f"\n=== FOUND {len(other_txns)} 'Other' TRANSACTIONS ===\n")

# Show first 15 descriptions and amounts
for txn in other_txns[:15]:
    print(f"{txn['Description'][:50]:50} ${txn['Amount']:>10}")

# Save to separate file
with open('other_transactions.json', 'w') as f:
    json.dump(other_txns, f, indent=2)

print(f"\nFull list saved to other_transactions.json")