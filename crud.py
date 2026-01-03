# crud.py
from sqlalchemy.orm import Session
from sqlalchemy import func
import models

def get_dashboard_summary(db: Session):
    total_txn_today = db.query(models.Transaction)\
        .filter(func.date(models.Transaction.timestamp) == func.current_date())\
        .count()

    high_risk_txn = db.query(models.AMLScore)\
        .filter(models.AMLScore.risk_label.in_(["HIGH", "CRITICAL"]))\
        .count()

    open_critical_alerts = db.query(models.AMLAlert)\
        .filter(models.AMLAlert.risk_label == "CRITICAL",
                models.AMLAlert.status == "OPEN")\
        .count()

    users_under_monitoring = db.query(models.Transaction.user_id)\
        .join(models.AMLScore)\
        .filter(models.AMLScore.risk_label.in_(["HIGH", "CRITICAL"]))\
        .distinct().count()

    return {
        "total_transactions_today": total_txn_today,
        "high_risk_transactions": high_risk_txn,
        "critical_alerts_open": open_critical_alerts,
        "users_under_monitoring": users_under_monitoring
    }
 
def get_risk_distribution(db: Session):
    results = db.query(
        models.AMLScore.risk_label,
        func.count(models.AMLScore.transaction_id)
    ).group_by(models.AMLScore.risk_label).all()
    
    return [
        {"risk_label": risk_label, "count": count}
        for risk_label, count in results
    ]

def get_transactions_by_risk(db: Session, risk: str):
    results = db.query(
        models.Transaction.transaction_id,
        models.Transaction.user_id,
        models.Transaction.transaction_amount,
        models.Transaction.timestamp,
        models.AMLScore.final_risk_score,
        models.AMLScore.risk_label,
        models.AMLAlert.status
    ).join(models.AMLScore, models.Transaction.transaction_id == models.AMLScore.transaction_id)\
     .outerjoin(models.AMLAlert, models.Transaction.transaction_id == models.AMLAlert.transaction_id)\
     .filter(models.AMLScore.risk_label == risk)\
     .all()
    
    return [
        {
            "transaction_id": tx_id,
            "user_id": user_id,
            "transaction_amount": float(amount) if amount else None,
            "timestamp": timestamp,
            "final_risk_score": float(score) if score else None,
            "risk_label": risk_label,
            "alert_status": status
        }
        for tx_id, user_id, amount, timestamp, score, risk_label, status in results
    ]

def get_transaction_detail(db: Session, tx_id: str):
    result = db.query(
        models.Transaction,
        models.AMLScore
    ).join(models.AMLScore)\
     .filter(models.Transaction.transaction_id == tx_id)\
     .first()
    
    if result is None:
        return None
    
    transaction, aml_score = result
    
    return {
        "transaction": {
            "transaction_id": transaction.transaction_id,
            "user_id": transaction.user_id,
            "timestamp": transaction.timestamp,
            "transaction_amount": float(transaction.transaction_amount) if transaction.transaction_amount else None,
            "avg_transaction_amount_30d": float(transaction.avg_transaction_amount_30d) if transaction.avg_transaction_amount_30d else None,
            "amount_deviation": float(transaction.amount_deviation) if transaction.amount_deviation else None,
            "txn_velocity": transaction.txn_velocity,
            "velocity_change": float(transaction.velocity_change) if transaction.velocity_change else None,
            "location_change_km": float(transaction.location_change_km) if transaction.location_change_km else None,
            "merchant_category": transaction.merchant_category,
            "merchant_category_risk": float(transaction.merchant_category_risk) if transaction.merchant_category_risk else None,
            "hour_of_day": transaction.hour_of_day
        },
        "aml_score": {
            "transaction_id": aml_score.transaction_id,
            "iso_score": float(aml_score.iso_score) if aml_score.iso_score else None,
            "lstm_score": float(aml_score.lstm_score) if aml_score.lstm_score else None,
            "rule_score": aml_score.rule_score,
            "final_risk_score": float(aml_score.final_risk_score) if aml_score.final_risk_score else None,
            "risk_label": aml_score.risk_label,
            "evaluated_at": aml_score.evaluated_at
        }
    }

def get_user_risk_profile(db: Session, user_id: str):
    user = db.query(models.User)\
        .filter(models.User.user_id == user_id).first()
    
    if user is None:
        return None

    alerts = db.query(models.AMLAlert)\
        .filter(models.AMLAlert.user_id == user_id).count()

    last_flagged = db.query(models.AMLScore)\
        .join(models.Transaction)\
        .filter(models.Transaction.user_id == user_id)\
        .order_by(models.AMLScore.evaluated_at.desc())\
        .first()

    return {
        "kyc_status": {
            "aadhar": user.aadhar_verified,
            "pan": user.pan_verified,
            "bank": user.bank_verified
        },
        "total_alerts": alerts,
        "last_flagged_transaction": last_flagged.transaction_id if last_flagged else None
    }

def get_all_alerts(db: Session):
    alerts = db.query(models.AMLAlert)\
        .order_by(models.AMLAlert.created_at.desc())\
        .all()
    
    return [
        {
            "alert_id": alert.alert_id,
            "transaction_id": alert.transaction_id,
            "user_id": alert.user_id,
            "risk_label": alert.risk_label,
            "reason": alert.reason,
            "status": alert.status,
            "created_at": alert.created_at
        }
        for alert in alerts
    ]

def close_alert(db: Session, alert_id: int):
    alert = db.query(models.AMLAlert)\
        .filter(models.AMLAlert.alert_id == alert_id).first()
    if alert is None:
        return None
    alert.status = "CLOSED"
    db.commit()
    return {
        "alert_id": alert.alert_id,
        "transaction_id": alert.transaction_id,
        "user_id": alert.user_id,
        "risk_label": alert.risk_label,
        "reason": alert.reason,
        "status": alert.status,
        "created_at": alert.created_at
    }
