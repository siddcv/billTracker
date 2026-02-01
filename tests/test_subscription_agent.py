import unittest
from src.subscription_agent import analyze_subscriptions

class TestSubscriptionAgent(unittest.TestCase):
    def test_analyze_subscriptions(self):
        subscriptions = [
            {'merchant': 'Spotify', 'amount': 9.99, 'frequency': 'monthly', 'annual_cost': 119.88},
            {'merchant': 'Netflix', 'amount': 15.99, 'frequency': 'monthly', 'annual_cost': 191.88}
        ]
        analysis = analyze_subscriptions(subscriptions)
        self.assertIn('summary', analysis)
        self.assertIn('savings_opportunities', analysis)
        self.assertIn('cancel_instructions', analysis)
        self.assertGreaterEqual(analysis['total_potential_savings'], 0)
        # Check for expected savings suggestions
        suggestions = [s['merchant'] for s in analysis['savings_opportunities']]
        self.assertIn('Netflix', suggestions)
        self.assertIn('Spotify', suggestions)
        # Check for cancellation instructions
        merchants = [c['merchant'] for c in analysis['cancel_instructions']]
        self.assertIn('Netflix', merchants)
        self.assertIn('Spotify', merchants)

if __name__ == '__main__':
    unittest.main()
