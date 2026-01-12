REGULATION_WEIGHTS = {
    "SOC2": {
        "Access Control": 1.2,
        "Data Encryption": 1.5,
        "Audit Logs": 1.3
    },
    "ISO27001": {
        "Access Control": 1.1,
        "Data Encryption": 1.4,
        "Audit Logs": 1.2
    },
    "GDPR": {
        "Access Control": 1.0,
        "Data Encryption": 1.6,
        "Audit Logs": 1.1
    }
}

def get_weight_multiplier(regulation: str, control_name: str) -> float:
    return REGULATION_WEIGHTS.get(regulation, {}).get(control_name, 1.0)
