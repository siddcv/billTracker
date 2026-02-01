# test_setup.py
"""
Quick test to verify all dependencies are installed correctly
"""

def test_imports():
    """Test that all critical packages can be imported"""
    
    print("Testing imports...")
    
    try:
        import flask
        print("✅ Flask imported")
        
        import plaid
        print("✅ Plaid imported")
        
        import langchain
        print("✅ LangChain imported")
        
        from langchain_openai import ChatOpenAI
        print("✅ LangChain-OpenAI imported")
        
        import pandas as pd
        print("✅ Pandas imported")
        
        import numpy as np
        print("✅ NumPy imported")
        
        from dotenv import load_dotenv
        print("✅ python-dotenv imported")
        
        import os
        load_dotenv()
        print("✅ .env file loading works")
        
        print("\n🎉 All dependencies installed successfully!")
        print("\nNext steps:")
        print("1. Get Plaid API keys: https://dashboard.plaid.com/signup")
        print("2. Get OpenAI API key: https://platform.openai.com/api-keys")
        print("3. Add keys to .env file")
        print("4. Run: python app.py")
        
        return True
        
    except ImportError as e:
        print(f"\n❌ Import error: {e}")
        print("Run: pip install -r requirements.txt")
        return False

if __name__ == "__main__":
    test_imports()
