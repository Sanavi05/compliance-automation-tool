"""
ML PIPELINE:
SQL → ML → SQL
"""

import numpy as np
from sqlalchemy.orm import Session
from database import SessionLocal
from models import Transaction, AMLScore, AMLAlert

def rule_engine(txn: Transaction):
    score = 0
    reasons = []

    if txn.amount_deviation > 2:
        score += 30
        reasons.append("High amount deviation")

    if txn.txn_velocity > 5:
        score += 25
        reasons.append("High transaction velocity")

    if txn.location_change_km > 500:
        score += 20
        reasons.append("Sudden location change")

    if txn.merchant_category_risk > 0.7:
        score += 25
        reasons.append("High-risk merchant")

    return score, reasons


def ml_models(txn: Transaction):
    iso_score = np.random.uniform(0, 1)
    lstm_score = np.random.uniform(0, 1)
    return iso_score, lstm_score


def risk_label(score):
    if score >= 80:
        return "CRITICAL"
    elif score >= 60:
        return "HIGH"
    elif score >= 40:
        return "MEDIUM"
    return "LOW"


def run_pipeline():
    db: Session = SessionLocal()

    transactions = db.query(Transaction).all()

    for txn in transactions:
        # Skip already evaluated txns
        exists = db.query(AMLScore).filter_by(transaction_id=txn.transaction_id).first()
        if exists:
            continue

        rule_score, reasons = rule_engine(txn)
        iso, lstm = ml_models(txn)

        final_score = rule_score + (iso + lstm) * 20
        label = risk_label(final_score)

        aml = AMLScore(
            transaction_id=txn.transaction_id,
            iso_score=iso,
            lstm_score=lstm,
            rule_score=rule_score,
            final_risk_score=final_score,
            risk_label=label
        )

        db.add(aml)

        if label in ["HIGH", "CRITICAL"]:
            alert = AMLAlert(
                transaction_id=txn.transaction_id,
                user_id=txn.user_id,
                risk_label=label,
                reason=", ".join(reasons)
            )
            db.add(alert)

    db.commit()
    db.close()


if __name__ == "__main__":
    run_pipeline()
