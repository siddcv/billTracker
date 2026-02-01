# insert_data.py
"""Insert sample data into database"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.database import SessionLocal, Transaction
from datetime import date
from decimal import Decimal

def insert_sample_data():
    """Insert some sample transactions"""
    
    db = SessionLocal()
    
    try:
        print("📝 Inserting sample transactions...\n")
        
        # Sample data (similar to what you'd get from Chase CSV)
        sample_transactions = [
            # Netflix subscriptions (recurring)
            Transaction(transaction_date=date(2026, 1, 15), vendor="Netflix", amount=Decimal("15.99")),
            Transaction(transaction_date=date(2025, 12, 15), vendor="Netflix", amount=Decimal("15.99")),
            Transaction(transaction_date=date(2025, 11, 15), vendor="Netflix", amount=Decimal("15.99")),
            
            # Spotify subscriptions (recurring)
            Transaction(transaction_date=date(2026, 1, 5), vendor="Spotify", amount=Decimal("9.99")),
            Transaction(transaction_date=date(2025, 12, 5), vendor="Spotify", amount=Decimal("9.99")),
            Transaction(transaction_date=date(2025, 11, 5), vendor="Spotify", amount=Decimal("9.99")),
            
            # Gym membership (recurring)
            Transaction(transaction_date=date(2026, 1, 1), vendor="Planet Fitness", amount=Decimal("24.99")),
            Transaction(transaction_date=date(2025, 12, 1), vendor="Planet Fitness", amount=Decimal("24.99")),
            Transaction(transaction_date=date(2025, 11, 1), vendor="Planet Fitness", amount=Decimal("24.99")),
            
            # One-time purchases (not recurring)
            Transaction(transaction_date=date(2026, 1, 27), vendor="Uber", amount=Decimal("6.33")),
            Transaction(transaction_date=date(2026, 1, 14), vendor="Uber", amount=Decimal("5.40")),
            Transaction(transaction_date=date(2026, 1, 12), vendor="United Airlines", amount=Decimal("500.00")),
            Transaction(transaction_date=date(2026, 1, 11), vendor="McDonald's", amount=Decimal("12.00")),
            Transaction(transaction_date=date(2026, 1, 11), vendor="Starbucks", amount=Decimal("4.33")),
            Transaction(transaction_date=date(2026, 1, 10), vendor="Target", amount=Decimal("89.40")),
            Transaction(transaction_date=date(2026, 1, 8), vendor="Whole Foods", amount=Decimal("67.25")),
        ]
        
        # Add all transactions
        db.add_all(sample_transactions)
        db.commit()
        
        print(f"✅ Inserted {len(sample_transactions)} transactions\n")
        
        # Query and display what was inserted
        print("📊 Current transactions in database:")
        print("-" * 70)
        
        all_txns = db.query(Transaction).order_by(Transaction.transaction_date.desc()).all()
        
        for txn in all_txns:
            print(f"ID: {txn.id:3d} | {txn.transaction_date} | {txn.vendor:20s} | ${txn.amount:>8.2f}")
        
        print("-" * 70)
        print(f"\nTotal: {len(all_txns)} transactions")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
    
    finally:
        db.close()


def clear_all_data():
    """Delete all transactions (use carefully!)"""
    
    db = SessionLocal()
    
    try:
        count = db.query(Transaction).count()
        
        if count == 0:
            print("Database is already empty")
            return
        
        response = input(f"⚠️  Delete all {count} transactions? (yes/no): ")
        
        if response.lower() == 'yes':
            db.query(Transaction).delete()
            db.commit()
            print(f"✅ Deleted {count} transactions")
        else:
            print("Cancelled")
    
    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
    
    finally:
        db.close()


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == 'clear':
        clear_all_data()
    else:
        insert_sample_data()
