import statistics
from app.db.database import SessionLocal
from app.models.escalation_log import EscalationLog


STREAK_THRESHOLD = 3
HIGH_SIGNALS = ["stable_high", "rising_risk"]

def classify_escalation(hybrid_probability: float, trend_slope: float):

    if hybrid_probability is None:
        return {
            "escalation_signal": "insufficient_data",
            "recommended_action": "collect_more_data"
        }

    HIGH_THRESHOLD = 0.7
    MODERATE_THRESHOLD = 0.3
    VOLATILE_SLOPE = 0.05

    # Low Risk
    if hybrid_probability < MODERATE_THRESHOLD:
        return {
            "escalation_signal": "stable_low",
            "recommended_action": "normal_monitoring"
        }

    # High Risk
    if hybrid_probability >= HIGH_THRESHOLD:
        if trend_slope > VOLATILE_SLOPE:
            return {
                "escalation_signal": "rising_risk",
                "recommended_action": "prepare_mitigation"
            }
        elif trend_slope < -VOLATILE_SLOPE:
            return {
                "escalation_signal": "falling_risk",
                "recommended_action": "observe_improvement"
            }
        else:
            return {
                "escalation_signal": "stable_high",
                "recommended_action": "monitor_closely"
            }

    # Moderate Risk
    return {
        "escalation_signal": "moderate",
        "recommended_action": "periodic_review"
    }

def detect_escalation_streak(db, tenant_id: str, current_signal: str):

    COOLDOWN_CYCLES = 3
    RECOVERY_CONFIRMATION = 2

    # Get last 5 signals
    recent_logs = (
        db.query(EscalationLog)
        .filter(EscalationLog.tenant_id == tenant_id)
        .order_by(EscalationLog.timestamp.desc())
        .limit(5)
        .all()
    )

    recent_signals = [log.escalation_signal for log in recent_logs]

    if not recent_signals:
        return current_signal

    last_signal = recent_signals[0]

    # ----------------------------
    # HIGH STATE LOCK
    # ----------------------------
    if last_signal == "persistent_high_risk":
        high_count = recent_signals.count("persistent_high_risk")

        if high_count < COOLDOWN_CYCLES:
            return "persistent_high_risk"

    # ----------------------------
    # RECOVERY CONFIRMATION
    # ----------------------------
    if last_signal == "persistent_high_risk":
        low_streak = 0
        for signal in recent_signals:
            if signal in ["stable_low", "moderate"]:
                low_streak += 1
            else:
                break

        if low_streak < RECOVERY_CONFIRMATION:
            return "persistent_high_risk"

    return current_signal

def compute_severity_score(hybrid_probability: float, trend_slope: float, signal: str):
    base_score = hybrid_probability*100
    slope_boost = abs(trend_slope)*50
    signal_weight = {
        "stable_low": 0,
        "moderate": 5,
        "stable_high": 10,
        "rising_risk": 15,
        "persistent_high_risk": 25,
    }
    weight = signal_weight.get(signal,0)
    severity = base_score + slope_boost + weight
    return min(round(severity, 2), 100.0)
