from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.autonomous_decision_log import AutonomousDecisionLog
from app.models.strategy_performance import StrategyPerformance


def get_decisions(db: Session, tenant_id: str, limit: int = 50):
    return (
        db.query(AutonomousDecisionLog)
        .filter(AutonomousDecisionLog.tenant_id == tenant_id)
        .order_by(AutonomousDecisionLog.created_at.desc())
        .limit(limit)
        .all()
    )
def get_forecast_accuracy(db: Session, tenant_id: str):
    result = (
        db.query(
            func.avg(AutonomousDecisionLog.forecast_accuracy).label("avg_accuracy"),
            func.count().label("total_cycles")
        )
        .filter(AutonomousDecisionLog.tenant_id == tenant_id)
        .first()
    )

    return {
        "average_accuracy": round(result.avg_accuracy or 0, 3),
        "total_cycles": result.total_cycles
    }
def get_strategy_performance(db: Session, tenant_id: str):
    strategies = (
        db.query(StrategyPerformance)
        .filter(StrategyPerformance.tenant_id == tenant_id)
        .all()
    )

    return [
        {
            "strategy_name": s.strategy_name,
            "success_score": s.success_score,
            "failure_score": s.failure_score,
            "net_score": s.success_score - s.failure_score
        }
        for s in strategies
    ]