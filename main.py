# main.py
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import crud
from database import get_db
from kyc_routes import kyc_bp
from auth_routes import auth_router

app = FastAPI(title="Compliance Automation Tool", version="1.0.0")

# Add CORS middleware for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve static files
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

static_dir = os.path.join(os.path.dirname(__file__), "static")
if os.path.exists(static_dir):
    # Mount static files - this must be done before other routes
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

@app.get("/")
async def read_root():
    """Serve the main frontend page"""
    static_file = os.path.join(static_dir, "index.html")
    if os.path.exists(static_file):
        return FileResponse(static_file)
    return {"message": "Frontend not found. Please check static/index.html"}

# Register routers
app.include_router(auth_router)
app.include_router(kyc_bp)

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
