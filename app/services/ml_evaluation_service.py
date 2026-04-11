from app.models.mitigation_log import MitigationLog
from sklearn.metrics import precision_score, recall_score, f1_score

def evaluate_ml_performance(db):
    logs = db.query(MitigationLog)\
             .filter(MitigationLog.ml_probability != None)\
             .all()

    if len(logs) < 5:
        return {"status": "not_enough_data", "samples": len(logs)}

    y_true = []
    y_pred = []

    for log in logs:
        y_true.append(log.actual_escalated)
        y_pred.append(1 if log.ml_probability >= 0.5 else 0)

    precision = precision_score(y_true, y_pred, zero_division=0)
    recall = recall_score(y_true, y_pred, zero_division=0)
    f1 = f1_score(y_true, y_pred, zero_division=0)

    return {
        "samples": len(logs),
        "precision": round(float(precision), 3),
        "recall": round(float(recall), 3),
        "f1_score": round(float(f1), 3),
    }