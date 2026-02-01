# test_plaid.py
"""
Test Plaid API connection - verifies your credentials work
"""

import os
from dotenv import load_dotenv
import plaid
from plaid.api import plaid_api
from plaid.model.link_token_create_request import LinkTokenCreateRequest
from plaid.model.link_token_create_request_user import LinkTokenCreateRequestUser
from plaid.model.products import Products
from plaid.model.country_code import CountryCode

# Load environment variables
load_dotenv()

def test_plaid_connection():
    """Test that Plaid API credentials are valid"""
    
    print("🔍 Testing Plaid API connection...\n")
    
    # Step 1: Check environment variables
    client_id = os.getenv('PLAID_CLIENT_ID')
    secret = os.getenv('PLAID_SECRET')
    env = os.getenv('PLAID_ENV', 'sandbox')
    
    if not client_id or not secret:
        print("❌ Error: Plaid credentials not found in .env file")
        print("Please add PLAID_CLIENT_ID and PLAID_SECRET to .env")
        return False
    
    print(f"✅ Found credentials in .env")
    print(f"   Client ID: {client_id[:10]}...")
    print(f"   Environment: {env}\n")
    
    # Step 2: Configure Plaid client
    try:
        if env == 'sandbox':
            host = plaid.Environment.Sandbox
        elif env == 'development':
            host = plaid.Environment.Development
        else:
            host = plaid.Environment.Production
        
        configuration = plaid.Configuration(
            host=host,
            api_key={
                'clientId': client_id,
                'secret': secret,
            }
        )
        
        api_client = plaid.ApiClient(configuration)
        client = plaid_api.PlaidApi(api_client)
        
        print("✅ Plaid client configured successfully\n")
        
    except Exception as e:
        print(f"❌ Error configuring Plaid client: {e}")
        return False
    
    # Step 3: Test API by creating a Link token
    try:
        print("📡 Testing API by creating Link token...")
        
        request = LinkTokenCreateRequest(
            user=LinkTokenCreateRequestUser(
                client_user_id='test_user_123'
            ),
            client_name="Subscription Tracker Test",
            products=[Products("transactions")],
            country_codes=[CountryCode('US')],
            language='en',
        )
        
        response = client.link_token_create(request)
        link_token = response['link_token']
        
        print(f"✅ Link token created successfully!")
        print(f"   Token: {link_token[:20]}...\n")
        
        print("🎉 SUCCESS! Plaid API connection is working!\n")
        print("Next steps:")
        print("1. You can now connect to Chase (and other banks)")
        print("2. Run the full app to test bank connection")
        print("3. In Sandbox, use these test credentials:")
        print("   Username: user_good")
        print("   Password: pass_good")
        
        return True
        
    except plaid.ApiException as e:
        print(f"❌ API Error: {e}")
        print("\nPossible issues:")
        print("- Check that your client_id and secret are correct")
        print("- Make sure you copied them from the 'sandbox' section")
        print("- Verify no extra spaces in .env file")
        return False
    
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

if __name__ == "__main__":
    success = test_plaid_connection()
    
    if success:
        print("\n✨ Your Plaid setup is ready to go!")
    else:
        print("\n⚠️  Please fix the errors above and try again")