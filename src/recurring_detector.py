"""
Recurring subscription detector for monthly patterns.
"""
from datetime import datetime, timedelta
from collections import defaultdict, Counter
from typing import List, Dict, Any


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
