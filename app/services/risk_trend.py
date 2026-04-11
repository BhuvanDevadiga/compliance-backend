def analyze_trend(events):
    event_signal = {
        "risk_escalated": 2.0,
        "tenant_quarantined": 3.0,
        "alert_health_critical": 2.0,
        "alert_risk_high": 2.0,
        "alert_tenant_isolated": 3.0,
        "tenant_recovered": -3.0,
    }

    if not events:
        return {
            "trend": "unknown",
            "volatility": "none",
            "interpretation": "No data available",
        }

    scores = []
    for e in events:
        if not e.payload or "risk_score" not in e.payload:
            continue
        try:
            scores.append(float(e.payload["risk_score"]))
        except (TypeError, ValueError):
            continue

    if len(scores) < 2:
        pressure = []
        level = 0.0
        for e in events:
            step = event_signal.get(getattr(e, "event_type", None))
            if step is None:
                continue
            level += step
            pressure.append(level)

        if len(pressure) >= 2:
            delta = pressure[-1] - pressure[0]
            if delta > 2:
                trend = "escalating"
            elif delta < -2:
                trend = "recovering"
            else:
                trend = "stable"

            volatility = "high" if max(pressure) - min(pressure) > 4 else "moderate"
            return {
                "trend": trend,
                "volatility": volatility,
                "interpretation": (
                    f"Trend inferred from event flow ({len(pressure)} signals) "
                    "because risk_score history is missing."
                ),
            }

        return {
            "trend": "stable",
            "volatility": "low",
            "interpretation": "Insufficient history",
        }

    delta = scores[-1] - scores[0]

    if delta > 10:
        trend = "escalating"
    elif delta < -10:
        trend = "recovering"
    else:
        trend = "stable"

    volatility = "high" if max(scores) - min(scores) > 20 else "moderate"

    return {
        "trend": trend,
        "volatility": volatility,
        "interpretation": f"Tenant risk is {trend} with {volatility} variability.",
    }
