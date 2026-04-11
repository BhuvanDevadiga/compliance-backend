from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.mitigation_strategy_performance import MitigationStrategyPerformance
from app.services.escalation_probability_engine import compute_escalation_probability

router = APIRouter(prefix = "/admin/intelligence", tags = ["Mitigation Intelligence"])

@router.get("/{tenant_id}")
def get_mitigation_intelligence(tenant_id : str, db : Session = Depends(get_db)):
    risk = compute_escalation_probability(db, tenant_id)

    records= (
        db.query(MitigationStrategyPerformance)
        .filter(MitigationStrategyPerformance.tenant_id==tenant_id)
        .all()
    )
    if not records:
        return  {"message": "No mitigation data found for tenant"}
    ranked = sorted(records, key = lambda r: r.confidence, reverse= True)
    best = ranked[0]
    worst = ranked[-1]

    return {
        "tenant": tenant_id,
        "current_risk_probability": risk["probability"],
        "strategy_ranking":[
            {
                "strategy": r.strategy,
                "confidence": r.confidence,
                "success": r.success_score,
            }
            for r in ranked
        ],
        "top_strategy":best.strategy,
        "weakest_strategy": worst.strategy,

    }


