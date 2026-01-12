from app.models.risk import RiskAssessment

def save_risk_assessment(db, data):
    assessment = RiskAssessment(**data)
    db.add(assessment)
    db.commit()
    db.refresh(assessment)
    return assessment
