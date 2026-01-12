def calculate_trend(history):
    if len(history) < 2:
        return "insufficient_data"

    latest = history[0].risk_score
    previous = history[1].risk_score

    if latest < previous:
        return "improving"
    elif latest > previous:
        return "worsening"
    return "stable"
