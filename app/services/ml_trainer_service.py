import joblib
import numpy as np
from sqlalchemy.orm import Session
from sklearn.linear_model import LogisticRegression
from app.models.training_snapshot import TrainingSnapshot

MODEL_PATH = "ml_escalation_model.pkl"

def train_escalation_model(db: Session):
    snapshots = db.query(TrainingSnapshot).all()
    if len(snapshots)<5:
        return {"error":"Not enough training data"}
    
    X=[]
    y=[]

    for s in snapshots:
        X.append([
            s.velocity,
            s.stability,
            s.bias,
            s.forecast_peak,
            s.forecast_accuracy,
            s.adaptive_threshold,
            s.volatility,
            s.avg_strategy_confidence,
            s.long_term_success_ratio,
            s.short_term_success_ratio
        ])
        y.append(s.escalated)

    X = np.array(X)
    y = np.array(y)

    print("DEBUG LABELS:", y)
    print("DEBUG UNIQUE:", set(y))

    if len(set(y)) < 2:
        return {"error": "Need at least 2 classes (0 and 1) to train model"}

    model = LogisticRegression()
    model.fit(X, y)

    joblib.dump(model, MODEL_PATH)

    return {
        "status": "model_trained",
        "samples_used": len(X)
    }

