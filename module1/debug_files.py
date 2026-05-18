import os
import glob

print("Current directory:", os.getcwd())
print("\nAll files in this directory:")
for f in os.listdir("."):
    print(f"  - {f}")

print("\nAll CSV files:")
csv_files = glob.glob("*.csv")
for f in csv_files:
    print(f"  - {f}")

print("\nFiles with 'transaction' in the name:")
transaction_files = glob.glob("*transaction*.csv")
for f in transaction_files:
    print(f"  - {f}")