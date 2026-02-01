# src/subscription_agent.py
"""
Subscription AI Agent: Analyzes detected subscriptions with OpenAI
"""
import os
from typing import List, Dict, Any
from dotenv import load_dotenv

load_dotenv()

# Try to import OpenAI, fallback to static analysis if not available
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False


# Static plan data for fallback
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
    },
    'Planet Fitness': {
        'cheaper_plan': {'name': 'Basic', 'amount': 10.00, 'savings_per_month': 14.99, 'savings_per_year': 179.88},
        'cancel_steps': [
            'Visit your home club in person',
            'Fill out cancellation form',
            'Or send certified letter'
        ]
    }
}


def analyze_subscriptions_with_ai(subscriptions: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Analyze subscriptions using OpenAI GPT-4 for intelligent insights.
    Falls back to static analysis if OpenAI not available.
    """
    if not OPENAI_AVAILABLE or not os.getenv('OPENAI_API_KEY'):
        print("⚠️  OpenAI not available, using static analysis")
        return analyze_subscriptions(subscriptions)
    
    try:
        client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        
        # Calculate totals
        total_monthly = sum(sub['amount'] for sub in subscriptions)
        total_annual = sum(sub['annual_cost'] for sub in subscriptions)
        
        # Format subscriptions for AI
        sub_list = "\n".join([
            f"- {sub['merchant']}: ${sub['amount']:.2f}/month (${sub['annual_cost']:.2f}/year, {sub['occurrences']} charges detected)"
            for sub in subscriptions
        ])
        
        # AI prompt
        prompt = f"""You are a personal finance advisor analyzing subscription spending.

User's Subscriptions:
{sub_list}

Total: ${total_monthly:.2f}/month (${total_annual:.2f}/year)

Please provide:
1. Summary of spending patterns
2. Specific money-saving recommendations for each subscription
3. Which subscriptions to keep vs cancel
4. Total potential savings

Be concise, actionable, and friendly."""

        # Call OpenAI
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a helpful personal finance advisor specializing in subscription management."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=800
        )
        
        ai_analysis = response.choices[0].message.content
        
        # Also get cancellation instructions from static data
        cancel_instructions = []
        for sub in subscriptions:
            merchant = sub['merchant']
            plan = default_plan_suggestions.get(merchant)
            if plan and 'cancel_steps' in plan:
                cancel_instructions.append({
                    'merchant': merchant,
                    'steps': plan['cancel_steps'],
                    'url': plan.get('cancel_url', 'N/A')
                })
        
        return {
            'summary': f"{len(subscriptions)} subscriptions totaling ${total_monthly:.2f}/month (${total_annual:.2f}/year)",
            'ai_analysis': ai_analysis,
            'cancel_instructions': cancel_instructions
        }
        
    except Exception as e:
        print(f"⚠️  Error with OpenAI, falling back to static analysis: {e}")
        return analyze_subscriptions(subscriptions)


def analyze_subscriptions(subscriptions: List[Dict[str, Any]], plan_suggestions=default_plan_suggestions) -> Dict[str, Any]:
    """
    Static analysis (fallback when OpenAI not available).
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
            if 'cancel_steps' in plan:
                cancel_instructions.append({
                    'merchant': merchant,
                    'steps': plan['cancel_steps'],
                    'url': plan.get('cancel_url', 'N/A')
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
    
    # Format analysis text
    analysis_text = f"""
📊 Subscription Analysis

{summary}

💰 Savings Opportunities:
"""
    for s in savings:
        analysis_text += f"\n• {s['merchant']}: {s['suggestion']}"
    
    analysis_text += f"\n\n💵 Total Potential Savings: ${total_savings:.2f}/year"
    
    return {
        'summary': summary,
        'ai_analysis': analysis_text,
        'savings_opportunities': savings,
        'total_potential_savings': total_savings,
        'cancel_instructions': cancel_instructions
    }


# Test function
if __name__ == "__main__":
    # Sample subscriptions for testing
    test_subs = [
        {'merchant': 'Netflix', 'amount': 15.99, 'annual_cost': 191.88, 'occurrences': 3},
        {'merchant': 'Spotify', 'amount': 9.99, 'annual_cost': 119.88, 'occurrences': 3},
        {'merchant': 'Planet Fitness', 'amount': 24.99, 'annual_cost': 299.88, 'occurrences': 3}
    ]
    
    print("🤖 Testing AI Agent...\n")
    analysis = analyze_subscriptions_with_ai(test_subs)
    
    print(analysis['summary'])
    print("\n" + "="*70)
    print(analysis['ai_analysis'])
    print("="*70)
