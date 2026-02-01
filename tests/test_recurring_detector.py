import unittest
from src.recurring_detector import detect_monthly_recurring

class TestRecurringDetector(unittest.TestCase):
    def test_detect_monthly_recurring(self):
        transactions = [
            {'merchant': 'Spotify', 'amount': 9.99, 'date': '2026-01-05'},
            {'merchant': 'Spotify', 'amount': 9.99, 'date': '2025-12-05'},
            {'merchant': 'Spotify', 'amount': 9.99, 'date': '2025-11-05'},
            {'merchant': 'Netflix', 'amount': 15.99, 'date': '2026-01-10'},
            {'merchant': 'Netflix', 'amount': 15.99, 'date': '2025-12-10'},
            {'merchant': 'Uber', 'amount': 6.33, 'date': '2026-01-01'},
        ]
        result = detect_monthly_recurring(transactions)
        merchants = {sub['merchant'] for sub in result}
        self.assertIn('Spotify', merchants)
        self.assertIn('Netflix', merchants)
        for sub in result:
            if sub['merchant'] == 'Spotify':
                self.assertEqual(sub['amount'], 9.99)
                self.assertEqual(sub['frequency'], 'monthly')
                self.assertEqual(sub['occurrences'], 3)
                self.assertAlmostEqual(sub['annual_cost'], 119.88, places=2)
            if sub['merchant'] == 'Netflix':
                self.assertEqual(sub['amount'], 15.99)
                self.assertEqual(sub['frequency'], 'monthly')
                self.assertEqual(sub['occurrences'], 2)
                self.assertAlmostEqual(sub['annual_cost'], 191.88, places=2)

if __name__ == '__main__':
    unittest.main()
