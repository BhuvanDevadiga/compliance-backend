def generate_risk_insight(state):

    if state.risk_level == "critical":
        message = "Tenant is in critical risk. Isolation recommended."
        action = "Immediate audit + freeze high-risk operations."

    elif state.risk_level == "high":
        message = "High behavioral risk detected."
        action = "Monitor closely and apply throttling."

    elif state.risk_level == "medium":
        message = "Elevated tenant activity."
        action = "Observe for escalation patterns."

    else:
        message = "Tenant operating normally."
        action = "No intervention required."

    return {
        "tenant_id": state.tenant_id,
        "risk_score": state.risk_score,
        "risk_level": state.risk_level,
        "quarantined": state.quarantined,
        "last_reason": state.last_escalation_reason,
        "insight": message,
        "recommended_action": action,
    }
