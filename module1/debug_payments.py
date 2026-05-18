import csv

print("=== CHASE PAYMENTS ===")
with open("ChaseYTD.CSV", "r", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for i, row in enumerate(reader):
        category = row.get("Category", "")
        description = row.get("Description", "")
        
        # Show rows with "payment" in description
        if "payment" in description.lower():
            print(f"\nRow {i}:")
            print(f"  Category: '{category}'")
            print(f"  Description: '{description}'")
            print(f"  Amount: {row.get('Amount')}")
            
            if i >= 5:  # Show first 5
                break

print("\n\n=== WELLS FARGO - ALL TRANSACTIONS (first 10) ===")
with open("WellsFargoYTD.csv", "r", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    print("Columns:", reader.fieldnames)
    print()
    
    for i, row in enumerate(reader):
        if i >= 10:
            break
        print(f"Row {i}: {row}")