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

from plaid_client import PlaidClient
from src.recurring_detector import detect_monthly_recurring
from src.subscription_agent import analyze_subscriptions as ai_analyze_subscriptions

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'dev_secret_key')

# Initialize Plaid client
plaid_client = PlaidClient()

# In-memory storage (use database in production!)
# Format: {user_id: access_token}
user_tokens = {}


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
    
    try:
        # In production, get user_id from session/auth
        user_id = request.json.get('user_id', 'demo_user')
        
        link_token = plaid_client.create_link_token(user_id)
        
        return jsonify({
            'link_token': link_token,
            'success': True
        })
        
    except Exception as e:
        return jsonify({
            'error': str(e),
            'success': False
        }), 500


@app.route('/api/exchange_public_token', methods=['POST'])
def exchange_public_token():
    """
    Step 2: Exchange public token for access token
    Called after user connects bank in Plaid Link
    """
    
    try:
        public_token = request.json['public_token']
        user_id = request.json.get('user_id', 'demo_user')
        
        # Exchange token
        result = plaid_client.exchange_public_token(public_token)
        
        # Store access token (use database in production!)
        user_tokens[user_id] = result['access_token']
        
        print(f"✅ User {user_id} connected bank successfully")
        
        return jsonify({
            'success': True,
            'message': 'Bank connected successfully!',
            'item_id': result['item_id']
        })
        
    except Exception as e:
        return jsonify({
            'error': str(e),
            'success': False
        }), 500


@app.route('/api/get_transactions', methods=['POST'])
def get_transactions():
    """
    Step 3: Fetch transactions from connected bank
    """
    
    try:
        user_id = request.json.get('user_id', 'demo_user')
        
        # Get access token from storage
        access_token = user_tokens.get(user_id)
        
        if not access_token:
            return jsonify({
                'error': 'No bank connected. Please connect your bank first.',
                'success': False
            }), 400
        
        # Fetch all transactions
        transactions = plaid_client.get_all_transactions(access_token)
        
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
        access_token = user_tokens.get(user_id)
        if not access_token:
            return jsonify({
                'error': 'No bank connected. Please connect your bank first.',
                'success': False
            }), 400
        # Fetch all transactions
        transactions = plaid_client.get_all_transactions(access_token)
        # Detect recurring subscriptions
        subscriptions = detect_monthly_recurring(transactions)
        # AI agent analysis
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
