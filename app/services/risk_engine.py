STATUS_FACTOR = {
    "implemented": 0,
    "partial": 0.5,
    "missing": 1
}

EVIDENCE_PENALTY = 0.3


def calculate_risk_score(controls, answers):
    total_risk = 0
    breakdown = []

    for control in controls:
        answer = answers.get(control["id"])

        if not answer:
            # No response = worst case
            risk = control["weight"] * 1.2
        else:
            status_factor = STATUS_FACTOR[answer["status"]]
            risk = control["weight"] * status_factor

            if not answer["evidence_uploaded"]:
                risk += control["weight"] * EVIDENCE_PENALTY

        breakdown.append({
            "control": control["name"],
            "risk": round(risk, 2)
        })

        total_risk += risk

    normalized = min(100, round(total_risk, 2))
    return normalized, breakdown

from app.services.regulation_config import get_weight_multiplier

def calculate_risk_score(controls, answers, regulation: str):
    total_risk = 0
    breakdown = []

    for control in controls:
        multiplier = get_weight_multiplier(regulation, control["name"])
        weight = control["weight"] * multiplier

        answer = answers.get(control["id"])
        if not answer:
            risk = weight * 1.2
        else:
            status_factor = STATUS_FACTOR[answer["status"]]
            risk = weight * status_factor
            if not answer["evidence_uploaded"]:
                risk += weight * EVIDENCE_PENALTY

        breakdown.append({
            "control": control["name"],
            "risk": round(risk, 2)
        })
        total_risk += risk

    return min(100, round(total_risk, 2)), breakdown

