# main.py
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
import crud
from database import get_db

app = FastAPI()

@app.get("/health")
def health():
    return {"status": "healthy"}

@app.get("/dashboard/summary")
def summary(db: Session = Depends(get_db)):
    return crud.get_dashboard_summary(db)

@app.get("/dashboard/risk-distribution")
def risk_distribution(db: Session = Depends(get_db)):
    return crud.get_risk_distribution(db)

@app.get("/dashboard/transactions")
def transactions(risk: str, db: Session = Depends(get_db)):
    """
    Get transactions filtered by risk level.
    
    Valid risk values: LOW, MEDIUM, HIGH, CRITICAL
    
    Example: /dashboard/transactions?risk=HIGH
    """
    valid_risks = ["LOW", "MEDIUM", "HIGH", "CRITICAL"]
    if risk.upper() not in valid_risks:
        raise HTTPException(
            status_code=400, 
            detail=f"Invalid risk value. Must be one of: {', '.join(valid_risks)}"
        )
    return crud.get_transactions_by_risk(db, risk.upper())

@app.get("/transaction/{tx_id}")
def transaction_detail(tx_id: str, db: Session = Depends(get_db)):
    result = crud.get_transaction_detail(db, tx_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return result

@app.get("/user/{user_id}/risk-profile")
def user_risk_profile(user_id: str, db: Session = Depends(get_db)):
    result = crud.get_user_risk_profile(db, user_id)
    if result is None:
        raise HTTPException(status_code=404, detail="User not found")
    return result

@app.get("/alerts")
def all_alerts(db: Session = Depends(get_db)):
    return crud.get_all_alerts(db)

@app.put("/alerts/{alert_id}/close")
def close_alert(alert_id: int, db: Session = Depends(get_db)):
    result = crud.close_alert(db, alert_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Alert not found")
    return result
