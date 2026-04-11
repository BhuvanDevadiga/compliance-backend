from app.ml.features import build_feature_vector

def predict_probability(db, tenant_id : str)-> float:
    features= build_feature_vector(db, tenant_id)

    if not features:
        return 0.2
    
    global_score = (
        0.35*max(0, features["velocity"])+
        0.25 * (1 - features["stability"]) +
        0.15 * features["forecast_peak"] +
        0.10 * features["volatility"] +
        0.15 * (1 - features["long_term_success_ratio"])
                 
    )

    tenant_adjustment = (
        0.5 * (1 - features["short_term_success_ratio"]) +
        0.5 * (1 - features["avg_strategy_confidence"])
    )

    final_probability = (
        0.7 * global_score +
        0.3 * tenant_adjustment
    )

    return round(min(1.0, max(0.0, final_probability)), 3)    
