import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# test_simple_db.py
"""Test simplified single-user database"""

from src.database import SessionLocal, Transaction, Subscription
from datetime import date
from decimal import Decimal

def test_transactions():
    """Test adding and querying transactions"""
    
    print("🔍 Testing database operations...\n")
    
    db = SessionLocal()
    
    try:
        # Add some test transactions
        print("1. Adding transactions...")
        transactions = [
            Transaction(
                transaction_date=date(2026, 1, 27),
                vendor="Uber",
                amount=Decimal("6.33")
            ),
            Transaction(
                transaction_date=date(2026, 1, 14),
                vendor="Uber",
                amount=Decimal("5.40")
            ),
            Transaction(
                transaction_date=date(2026, 1, 12),
                vendor="United Airlines",
                amount=Decimal("500.00")
            ),
            Transaction(
                transaction_date=date(2026, 1, 11),
                vendor="McDonald's",
                amount=Decimal("12.00")
            ),
            Transaction(
                transaction_date=date(2026, 1, 11),
                vendor="Starbucks",
                amount=Decimal("4.33")
            )
        ]
        
        db.add_all(transactions)
        db.commit()
        print(f"✅ Added {len(transactions)} transactions\n")
        
        # Query all transactions
        print("2. Querying all transactions...")
        all_txns = db.query(Transaction).order_by(Transaction.transaction_date.desc()).all()
        
        print(f"\nFound {len(all_txns)} transactions:")
        print("-" * 60)
        for txn in all_txns:
            print(f"ID: {txn.id:3d} | {txn.transaction_date} | {txn.vendor:20s} | ${txn.amount:>7.2f}")
        print("-" * 60)
        
        # Query by vendor
        print("\n3. Finding Uber transactions...")
        uber_txns = db.query(Transaction).filter(Transaction.vendor == "Uber").all()
        print(f"Found {len(uber_txns)} Uber transactions:")
        for txn in uber_txns:
            print(f"  {txn.transaction_date}: ${txn.amount}")
        
        print("\n✅ All tests passed!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
    
    finally:
        db.close()


if __name__ == "__main__":
    test_transactions()
