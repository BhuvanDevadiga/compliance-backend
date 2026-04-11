import joblib
import numpy as np
from app.ml.features import build_feature_vector

MODEL_PATH ="ml_escalation_model.pkl"
_model = None

def load_model():
    global _model
    if _model is None:
        _model = joblib.load(MODEL_PATH)
    return _model

def predict_escalation_probability(feature_vector: dict):
    model = load_model()

    X = np.array([[
        feature_vector["velocity"],
        feature_vector["stability"],
        feature_vector["bias"],
        feature_vector["forecast_peak"],
        feature_vector["forecast_accuracy"],
        feature_vector["adaptive_threshold"],
        feature_vector["volatility"],
        feature_vector["avg_strategy_confidence"],
        feature_vector["long_term_success_ratio"],
        feature_vector["short_term_success_ratio"]
    ]])

    prob = model.predict_proba(X)[0][1]  # probability of class 1
    return float(prob)


def compute_ml_score(db, tenant_id: str) -> float:
    feature_vector = build_feature_vector(db, tenant_id)

    if not feature_vector:
        return 0.2

    return round(predict_escalation_probability(feature_vector), 3)
    
