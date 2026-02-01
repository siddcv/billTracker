# app.py
"""
Flask app for Bill & Subscription Tracker
"""

from flask import Flask, request, jsonify, render_template
from dotenv import load_dotenv
import os
import sys

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# from plaid_client import PlaidClient  # Plaid code commented out
from src.recurring_detector import detect_monthly_recurring
from src.subscription_agent import analyze_subscriptions as ai_analyze_subscriptions
from src.database import get_transactions_for_user  # Assume this function will fetch from DB

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'dev_secret_key')

# Initialize Plaid client
# plaid_client = PlaidClient()  # Plaid code commented out

# In-memory storage (use database in production!)
# Format: {user_id: access_token}
# user_tokens = {}  # Plaid code commented out


@app.route('/')
def index():
    """Serve the main page"""
    return render_template('index.html')


@app.route('/api/create_link_token', methods=['POST'])
def create_link_token():
    """
    Step 1: Create Link token for frontend
    Frontend calls this first to initialize Plaid Link
    """
    
    # Plaid code commented out
    return jsonify({'error': 'Plaid integration disabled', 'success': False}), 501


@app.route('/api/exchange_public_token', methods=['POST'])
def exchange_public_token():
    """
    Step 2: Exchange public token for access token
    Called after user connects bank in Plaid Link
    """
    
    # Plaid code commented out
    return jsonify({'error': 'Plaid integration disabled', 'success': False}), 501


@app.route('/api/get_transactions', methods=['POST'])
def get_transactions():
    """
    Step 3: Fetch transactions from connected bank
    """
    
    try:
        user_id = request.json.get('user_id', 'demo_user')
        # Fetch transactions from database
        transactions = get_transactions_for_user(user_id)
        return jsonify({
            'success': True,
            'transactions': transactions,
            'count': len(transactions)
        })
    except Exception as e:
        return jsonify({
            'error': str(e),
            'success': False
        }), 500


@app.route('/api/analyze_subscriptions', methods=['POST'])
def analyze_subscriptions():
    """
    Analyze subscriptions: detect recurring, return details and AI analysis
    """
    try:
        user_id = request.json.get('user_id', 'demo_user')
        # Fetch transactions from database
        transactions = get_transactions_for_user(user_id)
        subscriptions = detect_monthly_recurring(transactions)
        ai_analysis = ai_analyze_subscriptions(subscriptions)
        return jsonify({
            'success': True,
            'subscriptions': subscriptions,
            'count': len(subscriptions),
            'analysis': ai_analysis
        })
    except Exception as e:
        return jsonify({
            'error': str(e),
            'success': False
        }), 500


@app.route('/api/status', methods=['GET'])
def status():
    """Check if app is running and configured"""
    return jsonify({
        'status': 'running',
        'environment': os.getenv('PLAID_ENV', 'sandbox'),
        'plaid_configured': bool(os.getenv('PLAID_CLIENT_ID'))
    })


if __name__ == '__main__':
    print("\n" + "="*50)
    print("🚀 Starting Bill & Subscription Tracker")
    print("="*50)
    print(f"Environment: {os.getenv('PLAID_ENV', 'sandbox')}")
    print(f"Plaid configured: {bool(os.getenv('PLAID_CLIENT_ID'))}")
    print("\n📱 Open in browser: http://localhost:5000")
    print("="*50 + "\n")
    
    app.run(debug=True, port=5000)
