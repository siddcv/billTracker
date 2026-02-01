"""
Subscription AI Agent: Analyzes detected subscriptions and suggests savings.
"""
from typing import List, Dict, Any

# Example static plan data for savings suggestions
default_plan_suggestions = {
    'Netflix': {
        'cheaper_plan': {'name': 'Standard', 'amount': 12.99, 'savings_per_month': 3.00, 'savings_per_year': 36.00},
        'cancel_url': 'https://netflix.com/account',
        'cancel_steps': [
            'Go to netflix.com/account',
            'Click "Cancel Membership"',
            'Confirm cancellation'
        ]
    },
    'Spotify': {
        'annual_discount': {'percent': 15, 'savings_per_year': 18.00},
        'cancel_url': 'https://spotify.com/account',
        'cancel_steps': [
            'Go to spotify.com/account',
            'Click "Manage Subscription"',
            'Select "Cancel" and follow prompts'
        ]
    }
    # Add more merchants as needed
}

def analyze_subscriptions(subscriptions: List[Dict[str, Any]], plan_suggestions=default_plan_suggestions) -> Dict[str, Any]:
    """
    Analyze subscriptions, calculate totals, suggest savings, and provide cancellation help.
    """
    total_monthly = sum(sub['amount'] for sub in subscriptions)
    total_annual = sum(sub['annual_cost'] for sub in subscriptions)
    savings = []
    cancel_instructions = []

    for sub in subscriptions:
        merchant = sub['merchant']
        plan = plan_suggestions.get(merchant)
        if plan:
            if 'cheaper_plan' in plan:
                diff = sub['amount'] - plan['cheaper_plan']['amount']
                if diff > 0:
                    savings.append({
                        'merchant': merchant,
                        'suggestion': f"Downgrade to {plan['cheaper_plan']['name']} (${plan['cheaper_plan']['amount']}/mo) - Save ${plan['cheaper_plan']['savings_per_year']}/year"
                    })
            if 'annual_discount' in plan:
                savings.append({
                    'merchant': merchant,
                    'suggestion': f"Pay annually for {plan['annual_discount']['percent']}% discount - Save ${plan['annual_discount']['savings_per_year']}/year"
                })
            cancel_instructions.append({
                'merchant': merchant,
                'steps': plan['cancel_steps'],
                'url': plan['cancel_url']
            })

    total_savings = 0.0
    for sub in subscriptions:
        merchant = sub['merchant']
        plan = plan_suggestions.get(merchant)
        if plan:
            if 'cheaper_plan' in plan:
                diff = sub['amount'] - plan['cheaper_plan']['amount']
                if diff > 0:
                    total_savings += plan['cheaper_plan']['savings_per_year']
            if 'annual_discount' in plan:
                total_savings += plan['annual_discount']['savings_per_year']

    summary = f"{len(subscriptions)} subscriptions totaling ${total_monthly:.2f}/month (${total_annual:.2f}/year)"
    analysis = {
        'summary': summary,
        'savings_opportunities': savings,
        'total_potential_savings': total_savings,
        'cancel_instructions': cancel_instructions
    }
    return analysis
