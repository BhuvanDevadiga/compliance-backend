from app.db.session import SessionLocal
from app.models.risk_assessment import RiskAssessment

db = SessionLocal()

records = (
    db.query(RiskAssessment)
    .order_by(RiskAssessment.created_at.desc())
    .limit(10)
    .all()
)

for r in records:
    print(
        r.id,
        r.tenant_id,
        r.company_size,
        r.industry,
        r.has_gst,
        r.has_pan,
        r.risk_score,
        r.risk_level,
        r.reasons,
        r.ruleset_version,
        r.created_at,
    )
