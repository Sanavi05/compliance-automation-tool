from sqlalchemy import Column, String, Boolean, Integer, Numeric, Text, TIMESTAMP, ForeignKey
from database import Base
from datetime import datetime

class User(Base):
    __tablename__ = "users"

    user_id = Column(String, primary_key=True)
    full_name = Column(Text)
    aadhar_verified = Column(Boolean)
    pan_verified = Column(Boolean)
    bank_verified = Column(Boolean)
    onboarding_date = Column(TIMESTAMP)
    risk_profile = Column(Text)


class Transaction(Base):
    __tablename__ = "transactions"

    transaction_id = Column(String, primary_key=True)
    user_id = Column(String, ForeignKey("users.user_id"))
    timestamp = Column(TIMESTAMP)
    transaction_amount = Column(Numeric)
    avg_transaction_amount_30d = Column(Numeric)
    amount_deviation = Column(Numeric)
    txn_velocity = Column(Integer)
    velocity_change = Column(Numeric)
    location_change_km = Column(Numeric)
    merchant_category = Column(Text)
    merchant_category_risk = Column(Numeric)
    hour_of_day = Column(Integer)


class AMLScore(Base):
    __tablename__ = "aml_scores"

    transaction_id = Column(String, ForeignKey("transactions.transaction_id"), primary_key=True)
    iso_score = Column(Numeric)
    lstm_score = Column(Numeric)
    rule_score = Column(Integer)
    final_risk_score = Column(Numeric)
    risk_label = Column(Text)
    evaluated_at = Column(TIMESTAMP, default=datetime.utcnow)


class AMLAlert(Base):
    __tablename__ = "aml_alerts"

    alert_id = Column(Integer, primary_key=True)
    transaction_id = Column(String)
    user_id = Column(String)
    risk_label = Column(Text)
    reason = Column(Text)
    status = Column(Text, default="OPEN")
    created_at = Column(TIMESTAMP, default=datetime.utcnow)


# Import KYC models
from kyc_document import KYCDocument
from kyc_verification import KYCVerification

