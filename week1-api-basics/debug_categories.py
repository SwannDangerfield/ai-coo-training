# Create: debug_categories.py
import json

with open('categorized_transactions.json', 'r') as f:
    transactions = json.load(f)

# Count transactions by category
from collections import Counter

categories = [t.get('category', 'MISSING') for t in transactions]
category_counts = Counter(categories)

print("\n=== CATEGORY COUNTS ===")
for cat, count in sorted(category_counts.items()):
    print(f"{cat:20} {count:4} transactions")

# Also sum amounts by category
category_totals = {}
for t in transactions:
    cat = t.get('category', 'MISSING')
    amount = float(t['Amount'])
    category_totals[cat] = category_totals.get(cat, 0) + amount

print("\n=== CATEGORY TOTALS ===")
for cat, total in sorted(category_totals.items(), key=lambda x: x[1]):
    print(f"{cat:20} ${total:>12,.2f}")