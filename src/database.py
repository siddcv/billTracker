# src/database.py
"""
Simplified database for single user
"""

import os
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, Date, DateTime, DECIMAL
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

load_dotenv()

# Database connection
DATABASE_URL = f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"

engine = create_engine(DATABASE_URL, echo=False)  # Set echo=True for debugging
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class Transaction(Base):
    """Transaction model - your exact schema!"""
    __tablename__ = "transactions"
    
    id = Column(Integer, primary_key=True, index=True)
    transaction_date = Column(Date, nullable=False)
    vendor = Column(String(255), nullable=False)
    amount = Column(DECIMAL(10, 2), nullable=False)
    category = Column(String(100), nullable=True)
    uploaded_at = Column(DateTime, default=datetime.utcnow)


class Subscription(Base):
    """Detected recurring subscription"""
    __tablename__ = "subscriptions"
    
    id = Column(Integer, primary_key=True, index=True)
    vendor = Column(String(255), nullable=False)
    amount = Column(DECIMAL(10, 2), nullable=False)
    frequency = Column(String(50), nullable=False)
    next_charge_date = Column(Date, nullable=True)
    confidence = Column(DECIMAL(3, 2), nullable=True)
    occurrences = Column(Integer, default=0)
    annual_cost = Column(DECIMAL(10, 2), nullable=True)
    first_detected = Column(DateTime, default=datetime.utcnow)
    last_updated = Column(DateTime, default=datetime.utcnow)


def get_db():
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def test_connection():
    """Test database connection"""
    try:
        db = SessionLocal()
        db.execute("SELECT 1")
        db.close()
        print("✅ Database connection successful!")
        return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False


def get_transactions_for_user(user_id=None):
    """
    Fetch all transactions for the user (single user version).
    Returns a list of dicts: {merchant, amount, date}
    """
    db = SessionLocal()
    try:
        transactions = db.query(Transaction).order_by(Transaction.transaction_date.desc()).all()
        # Convert to list of dicts for frontend compatibility
        result = []
        for t in transactions:
            result.append({
                'merchant': t.vendor,
                'amount': float(t.amount),
                'date': t.transaction_date.strftime('%Y-%m-%d')
            })
        return result
    finally:
        db.close()


if __name__ == "__main__":
    test_connection()
