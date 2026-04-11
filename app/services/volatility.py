from sqlalchemy import desc
from app.models.decision_audit import DecisionAudit

def compute_volatility(db, tenant_id, window=20):
    rows=(
        db.query(DecisionAudit)
        .filter(DecisionAudit.tenant_id == tenant_id)
        .order_by(desc(DecisionAudit.created_at))
        .limit(window)
        .all()
    )

    if len(rows)<2 :
        return 0.0
    
    scores = [r.hybrid_score for r in rows]
    mean = sum(scores) / len(scores)
    variance = sum((s - mean) ** 2 for s in scores) / len(scores)
    volatility = variance ** 0.5
    return min(volatility, 1.0)
        