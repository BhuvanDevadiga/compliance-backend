from dataclasses import dataclass


@dataclass
class SimulationInput:
    base_risk: int
    escalation_events: int
    mitigation_strength: int


def simulate_risk(input: SimulationInput):

    projected_risk = input.base_risk

    # escalation pressure
    projected_risk += input.escalation_events * 10

    # mitigation effect
    projected_risk -= input.mitigation_strength * 5

    # clamp
    projected_risk = max(0, min(projected_risk, 100))

    # interpret result
    if projected_risk >= 80:
        state = "critical"
    elif projected_risk >= 50:
        state = "elevated"
    else:
        state = "stable"

    anomaly_probability = min(
        1.0,
        (input.escalation_events / 10),
    )

    return {
        "projected_risk": projected_risk,
        "state": state,
        "anomaly_probability": round(anomaly_probability, 2),
        "explanation": "Simulation based on escalation pressure vs mitigation strength",
    }
