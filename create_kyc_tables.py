"""
Database migration script for KYC tables
Run this script to create KYC tables in the database
"""
from database import engine, Base
from kyc_document import KYCDocument
from kyc_verification import KYCVerification
import models  # Import existing models to ensure all tables are created

def create_kyc_tables():
    """Create KYC tables in the database"""
    try:
        # Create all tables defined in Base metadata
        Base.metadata.create_all(bind=engine)
        print("✓ KYC tables created successfully!")
        print("  - kyc_documents")
        print("  - kyc_verifications")
    except Exception as e:
        print(f"✗ Error creating KYC tables: {e}")

if __name__ == "__main__":
    print("Creating KYC tables...")
    create_kyc_tables()
