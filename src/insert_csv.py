# import_csv.py
"""Import transactions from CSV file"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import csv
from src.database import SessionLocal, Transaction
from datetime import datetime
from decimal import Decimal

def import_from_csv(csv_file_path):
    """
    Import transactions from CSV file
    
    Expected CSV format:
    Date,Description,Amount
    2026-01-27,Netflix,15.99
    2026-01-26,Spotify,9.99
    """
    
    db = SessionLocal()
    
    try:
        print(f"📂 Reading CSV file: {csv_file_path}\n")
        
        transactions = []
        
        with open(csv_file_path, 'r') as file:
            csv_reader = csv.DictReader(file)
            
            for row in csv_reader:
                # Parse date (adjust format as needed)
                try:
                    # Try format: 2026-01-27
                    txn_date = datetime.strptime(row['Date'], '%Y-%m-%d').date()
                except:
                    # Try format: 01/27/2026
                    txn_date = datetime.strptime(row['Date'], '%m/%d/%Y').date()
                
                # Parse amount (remove $ and commas if present)
                amount_str = row['Amount'].replace('$', '').replace(',', '')
                amount = Decimal(amount_str)
                
                # Create transaction
                transaction = Transaction(
                    transaction_date=txn_date,
                    vendor=row['Description'].strip(),
                    amount=abs(amount)  # Make sure it's positive
                )
                
                transactions.append(transaction)
        
        # Insert all transactions
        db.add_all(transactions)
        db.commit()
        
        print(f"✅ Imported {len(transactions)} transactions from CSV\n")
        
        # Display summary
        print("📊 Imported transactions:")
        print("-" * 70)
        for txn in transactions[:10]:  # Show first 10
            print(f"{txn.transaction_date} | {txn.vendor:20s} | ${txn.amount:>8.2f}")
        
        if len(transactions) > 10:
            print(f"... and {len(transactions) - 10} more")
        print("-" * 70)
        
    except Exception as e:
        print(f"❌ Error importing CSV: {e}")
        db.rollback()
    
    finally:
        db.close()


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python import_csv.py <path_to_csv_file>")
        print("Example: python import_csv.py data/transactions.csv")
    else:
        import_from_csv(sys.argv[1])
