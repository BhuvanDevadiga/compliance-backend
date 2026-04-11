from sqlalchemy.orm import Session
from sqlalchemy import desc
from statistics import mean
from datetime import datetime
from app.models.decision_snapshot import DecisionSnapshot
from app.models.system_state import GlobalSystemState
from app.core.engine_config import MAX_ALLOWED_REGRET

ROLLING_WINDOW = 20

def compute_regret_risk_index(db: Session, tenant_id: str):

    
    snapshots = (
        db.query(DecisionSnapshot)
        .filter(DecisionSnapshot.tenant_id==tenant_id)
        .order_by(desc(DecisionSnapshot.created_at))
        .limit(ROLLING_WINDOW)
        .all()
    )

    if not snapshots:
        return {
            "regret_risk_index": 0.0,
            "risk_level": "LOW",
            "trend": "stable",
        }

    regrets = [s.regret for s in snapshots if s.regret is not None]

    if not regrets:
        return {
            "regret_risk_index": 0.0,
            "risk_level": "LOW",
            "trend": "stable",
        }

    rolling_avg = mean(regrets)

    
    trend = "stable"
    if len(regrets) >= 2:
        if regrets[0] > regrets[-1]:
            trend = "increasing"
        elif regrets[0] < regrets[-1]:
            trend = "decreasing"

   
    threshold_ratio = rolling_avg / MAX_ALLOWED_REGRET

  
    risk_score = min(threshold_ratio, 1.0)

    
    if trend == "increasing":
        risk_score = min(risk_score + 0.15, 1.0)

    
    state = db.query(GlobalSystemState).first()
    if state and state.adaptive_engine_frozen:
        risk_score = 1.0

    
    if risk_score >= 0.8:
        risk_level = "HIGH"
    elif risk_score >= 0.5:
        risk_level = "MEDIUM"
    else:
        risk_level = "LOW"

    return {
        "rolling_average_regret": round(rolling_avg, 5),
        "max_allowed_regret": MAX_ALLOWED_REGRET,
        "regret_risk_index": round(risk_score, 3),
        "risk_level": risk_level,
        "trend": trend,
        "evaluated_at": datetime.utcnow(),
    }

def get_exploration_multiplier(db:Session, tenant_id:str)-> float:
    health = compute_regret_risk_index(db, tenant_id)

    risk_level = health["risk_level"]
    if risk_level=="HIGH":
        return 0.4
    elif risk_level=="MEDIUM":
        return 0.75
    elif risk_level=="LOW":
        return 1.0

    return 1.0 