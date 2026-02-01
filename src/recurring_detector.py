# src/recurring_detector.py
"""
Recurring subscription detector for monthly patterns - PostgreSQL version
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from datetime import datetime, timedelta
from collections import defaultdict
from typing import List, Dict, Any
from src.database import Transaction, SessionLocal


def detect_monthly_recurring_from_db() -> List[Dict[str, Any]]:
    """
    Fetch transactions from PostgreSQL and detect recurring patterns.
    Returns list of detected subscriptions.
    """
    db = SessionLocal()
    
    try:
        # Fetch all transactions from database
        transactions = db.query(Transaction).all()
        
        if not transactions:
            print("⚠️  No transactions in database")
            return []
        
        print(f"📊 Analyzing {len(transactions)} transactions...")
        
        # Convert to dict format for processing
        txn_dicts = []
        for txn in transactions:
            txn_dicts.append({
                'merchant': txn.vendor,
                'amount': float(txn.amount),
                'date': txn.transaction_date.strftime('%Y-%m-%d')
            })
        
        # Use existing detection logic
        recurring = detect_monthly_recurring(txn_dicts)
        
        print(f"✅ Found {len(recurring)} recurring subscriptions")
        
        return recurring
        
    finally:
        db.close()


def detect_monthly_recurring(transactions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Detects monthly recurring transactions from a list of transactions.
    Each transaction is a dict with keys: merchant, amount, date (YYYY-MM-DD).
    Returns a list of detected subscriptions with details.
    """
    # Group by (merchant, amount)
    groups = defaultdict(list)
    for tx in transactions:
        key = (tx['merchant'], round(float(tx['amount']), 2))
        groups[key].append(tx)

    recurring = []
    for (merchant, amount), txs in groups.items():
        if len(txs) < 2:
            continue  # Need at least 2 to consider recurring
        
        # Sort by date descending
        txs_sorted = sorted(txs, key=lambda x: x['date'], reverse=True)
        
        # Check if dates are roughly monthly (within 5 days of 1 month apart)
        intervals = []
        for i in range(1, len(txs_sorted)):
            d1_raw = txs_sorted[i-1]['date']
            d2_raw = txs_sorted[i]['date']
            
            # Support both string and datetime.date
            if isinstance(d1_raw, str):
                d1 = datetime.strptime(d1_raw, '%Y-%m-%d')
            else:
                d1 = datetime.combine(d1_raw, datetime.min.time())
            if isinstance(d2_raw, str):
                d2 = datetime.strptime(d2_raw, '%Y-%m-%d')
            else:
                d2 = datetime.combine(d2_raw, datetime.min.time())
            
            delta = abs((d1 - d2).days)
            intervals.append(delta)
        
        if not intervals:
            continue
        
        avg_interval = sum(intervals) / len(intervals)
        
        # Monthly = 28-31 days
        if 28 <= avg_interval <= 31:
            # Estimate next charge date
            last_date_raw = txs_sorted[0]['date']
            if isinstance(last_date_raw, str):
                last_date = datetime.strptime(last_date_raw, '%Y-%m-%d')
            else:
                last_date = datetime.combine(last_date_raw, datetime.min.time())
            
            next_charge = last_date + timedelta(days=round(avg_interval))
            
            recurring.append({
                'merchant': merchant,
                'amount': amount,
                'frequency': 'monthly',
                'next_charge_date': next_charge.strftime('%Y-%m-%d'),
                'confidence': min(1.0, 0.7 + 0.1 * (len(txs_sorted)-2)),
                'occurrences': len(txs_sorted),
                'annual_cost': round(amount * 12, 2)
            })
    
    return recurring


def save_subscriptions_to_db(subscriptions: List[Dict[str, Any]]):
    """Save detected subscriptions to database"""
    from src.database import Subscription
    from decimal import Decimal
    
    db = SessionLocal()
    
    try:
        # Clear existing subscriptions
        db.query(Subscription).delete()
        
        # Add new ones
        for sub in subscriptions:
            db_sub = Subscription(
                vendor=sub['merchant'],
                amount=Decimal(str(sub['amount'])),
                frequency=sub['frequency'],
                next_charge_date=datetime.strptime(sub['next_charge_date'], '%Y-%m-%d').date(),
                confidence=Decimal(str(sub['confidence'])),
                occurrences=sub['occurrences'],
                annual_cost=Decimal(str(sub['annual_cost']))
            )
            db.add(db_sub)
        
        db.commit()
        print(f"💾 Saved {len(subscriptions)} subscriptions to database")
        
    except Exception as e:
        print(f"❌ Error saving subscriptions: {e}")
        db.rollback()
    finally:
        db.close()


# Test function
if __name__ == "__main__":
    print("🔍 Running pattern detector...\n")
    
    # Detect subscriptions
    subscriptions = detect_monthly_recurring_from_db()
    
    if subscriptions:
        print("\n💳 Detected Subscriptions:")
        print("=" * 70)
        for sub in subscriptions:
            print(f"{sub['merchant']:20s} | ${sub['amount']:>7.2f}/month | Next: {sub['next_charge_date']}")
        print("=" * 70)
        
        total_monthly = sum(sub['amount'] for sub in subscriptions)
        total_annual = sum(sub['annual_cost'] for sub in subscriptions)
        print(f"\nTotal: ${total_monthly:.2f}/month (${total_annual:.2f}/year)")
        
        # Save to database
        save_subscriptions_to_db(subscriptions)
    else:
        print("\n⚠️  No recurring subscriptions found.")
        print("Make sure you have at least 2 occurrences of the same merchant with the same amount.")
