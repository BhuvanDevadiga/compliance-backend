def compute_dynamic_thresholds(
        forecast_reliability: float,
        escalation_rate: float,
):
    base_watch = 0.4
    base_critical= 0.75

    if forecast_reliability >= 0.85:
        base_watch = -0.05
        base_critical = -0.5

    elif forecast_reliability < 0.6:
        base_watch =+0.05
        base_critical =+0.05

    if escalation_rate > 0.3:
        base_watch =-0.05
        base_critical =-0.05

    base_watch = max(0.2, min(base_watch, 0.6))
    base_critical = max(0.6, min(base_critical, 0.9))

    return round(base_watch, 3), round(base_critical, 3)


        
    