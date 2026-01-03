from pydantic import BaseModel
from datetime import datetime

class DashboardSummary(BaseModel):
    total_txns_today: int
    high_risk_txns: int
    open_alerts: int
    users_under_monitoring: int


class TransactionRow(BaseModel):
    transaction_id: str
    user_id: str
    transaction_amount: float
    timestamp: datetime
    final_risk_score: float
    risk_label: str
    alert_status: str | None
