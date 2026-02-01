# src/plaid_client.py
"""
Plaid API Client - Handles bank connections and transaction fetching
"""

import os
import plaid
from plaid.api import plaid_api
from plaid.model.link_token_create_request import LinkTokenCreateRequest
from plaid.model.link_token_create_request_user import LinkTokenCreateRequestUser
from plaid.model.products import Products
from plaid.model.country_code import CountryCode
from plaid.model.item_public_token_exchange_request import ItemPublicTokenExchangeRequest
from plaid.model.transactions_sync_request import TransactionsSyncRequest
from datetime import datetime, timedelta


class PlaidClient:
    """Wrapper for Plaid API operations"""
    
    def __init__(self):
        """Initialize Plaid client with credentials from environment"""
        
        client_id = os.getenv('PLAID_CLIENT_ID')
        secret = os.getenv('PLAID_SECRET')
        env = os.getenv('PLAID_ENV', 'sandbox')
        
        if not client_id or not secret:
            raise ValueError("Missing Plaid credentials in environment variables")
        
        # Set environment
        if env == 'sandbox':
            host = plaid.Environment.Sandbox
        elif env == 'development':
            host = plaid.Environment.Development
        else:
            host = plaid.Environment.Production
        
        # Configure client
        configuration = plaid.Configuration(
            host=host,
            api_key={
                'clientId': client_id,
                'secret': secret,
            }
        )
        
        api_client = plaid.ApiClient(configuration)
        self.client = plaid_api.PlaidApi(api_client)
        
        print(f"✅ Plaid client initialized (environment: {env})")
    
    def create_link_token(self, user_id):
        """
        Create a Link token for Plaid Link (frontend)
        
        Args:
            user_id: Your internal user identifier
            
        Returns:
            str: Link token to be used by frontend
        """
        
        try:
            request = LinkTokenCreateRequest(
                user=LinkTokenCreateRequestUser(
                    client_user_id=str(user_id)
                ),
                client_name="Bill & Subscription Tracker",
                products=[Products("transactions")],
                country_codes=[CountryCode('US')],
                language='en',
            )
            
            response = self.client.link_token_create(request)
            link_token = response['link_token']
            
            print(f"✅ Link token created for user: {user_id}")
            return link_token
            
        except plaid.ApiException as e:
            print(f"❌ Error creating link token: {e}")
            raise
    
    def exchange_public_token(self, public_token):
        """
        Exchange public token for access token
        
        After user connects their bank, Plaid gives you a public_token.
        Exchange it for a permanent access_token to fetch data.
        
        Args:
            public_token: Token received from Plaid Link
            
        Returns:
            dict: Contains access_token and item_id
        """
        
        try:
            exchange_request = ItemPublicTokenExchangeRequest(
                public_token=public_token
            )
            
            exchange_response = self.client.item_public_token_exchange(exchange_request)
            
            access_token = exchange_response['access_token']
            item_id = exchange_response['item_id']
            
            print(f"✅ Token exchanged successfully. Item ID: {item_id}")
            
            return {
                'access_token': access_token,
                'item_id': item_id
            }
            
        except plaid.ApiException as e:
            print(f"❌ Error exchanging token: {e}")
            raise
    
    def get_transactions(self, access_token, cursor=None):
        """
        Fetch transactions using /transactions/sync endpoint
        
        This is the modern way to get transactions (replaces old /transactions/get)
        
        Args:
            access_token: User's access token from exchange step
            cursor: Pagination cursor (None for first call)
            
        Returns:
            dict: Contains transactions list and next cursor
        """
        
        try:
            # Build request - only include cursor if it's not None
            if cursor:
                request = TransactionsSyncRequest(
                    access_token=access_token,
                    cursor=cursor
                )
            else:
                request = TransactionsSyncRequest(
                    access_token=access_token
                )
            
            response = self.client.transactions_sync(request)
            
            # Process transactions
            transactions = []
            for txn in response['added']:
                # Plaid provides cleaned merchant names
                merchant_name = txn.get('merchant_name') or txn.get('name', 'Unknown')
                
                transactions.append({
                    'transaction_id': txn['transaction_id'],
                    'date': txn['date'],
                    'merchant': merchant_name,
                    'amount': abs(txn['amount']),  # Make positive for easier display
                    'category': txn.get('category', []),
                    'pending': txn.get('pending', False),
                    'account_id': txn['account_id'],
                })
            
            print(f"✅ Fetched {len(transactions)} transactions")
            
            return {
                'transactions': transactions,
                'cursor': response['next_cursor'],
                'has_more': response['has_more']
            }
            
        except plaid.ApiException as e:
            print(f"❌ Error fetching transactions: {e}")
            raise

    
    def get_all_transactions(self, access_token):
        """
        Fetch ALL transactions (handles pagination automatically)
        
        Args:
            access_token: User's access token
            
        Returns:
            list: All transactions
        """
        
        all_transactions = []
        cursor = None
        has_more = True
        
        print("📡 Fetching all transactions...")
        
        while has_more:
            result = self.get_transactions(access_token, cursor)
            all_transactions.extend(result['transactions'])
            cursor = result['cursor']
            has_more = result['has_more']
        
        print(f"✅ Total transactions fetched: {len(all_transactions)}")
        return all_transactions


# Test function
def test_plaid_client():
    """Quick test of PlaidClient class"""
    
    from dotenv import load_dotenv
    load_dotenv()
    
    try:
        # Initialize client
        client = PlaidClient()
        
        # Test creating link token
        link_token = client.create_link_token(user_id='test_user_123')
        print(f"\n🎉 Link token: {link_token[:30]}...")
        
        print("\n✅ PlaidClient is working!")
        print("Next: Build Flask app to test full flow")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")


if __name__ == "__main__":
    test_plaid_client()
