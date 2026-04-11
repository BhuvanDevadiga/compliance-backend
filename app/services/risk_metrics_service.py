from datetime import datetime, timedelta
from app.models.decision_snapshot import DecisionSnapshot


def get_regret_risk_index(db):
   

    # 🔹 You likely already store regret in decision logs
    # Replace this with your actual model/table
    logs = db.query(DecisionSnapshot).order_by(
        DecisionSnapshot.created_at.desc()
    ).limit(50).all()

    if not logs:
        return {
            "rolling_average_regret": 0,
            "max_allowed_regret": 0.15,
            "regret_risk_index": 0,
            "risk_level": "LOW",
            "trend": "stable",
            "trend_slope": 0,
            "strict_actions": 0,
            "effective_exploration_rate": 0.4
        }

    regrets = [log.regret for log in logs if log.regret is not None]

    if not regrets:
        regrets = [0]

    # 🔹 Rolling average
    avg_regret = sum(regrets) / len(regrets)

    # 🔹 Simple trend (last - first)
    trend_slope = regrets[0] - regrets[-1]

    if trend_slope > 0.02:
        trend = "increasing"
    elif trend_slope < -0.02:
        trend = "decreasing"
    else:
        trend = "stable"

    # 🔹 Risk index (normalized)
    MAX_ALLOWED_REGRET = 0.15
    regret_risk_index = min(avg_regret / MAX_ALLOWED_REGRET, 1.0)

    # 🔹 Risk level
    if regret_risk_index > 0.8:
        risk_level = "HIGH"
    elif regret_risk_index > 0.5:
        risk_level = "MEDIUM"
    else:
        risk_level = "LOW"

    # 🔹 Strict actions count (you already track this)
    strict_actions = sum(1 for log in logs if getattr(log, "action", None) == "strict")

    return {
        "rolling_average_regret": round(avg_regret, 4),
        "max_allowed_regret": MAX_ALLOWED_REGRET,
        "regret_risk_index": round(regret_risk_index, 4),
        "risk_level": risk_level,
        "trend": trend,
        "trend_slope": round(trend_slope, 4),
        "strict_actions": strict_actions,
        "effective_exploration_rate": 0.4,  # default base
        "evaluated_at": datetime.utcnow().isoformat()
    }
