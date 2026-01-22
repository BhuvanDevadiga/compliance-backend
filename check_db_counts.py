from app.db.database import SessionLocal
from app.models.risk_assessment import RiskAssessment


db = SessionLocal()

count = db.query(RiskAssessment).count()
print("Total risk assessments:", count)

latest = (
    db.query(RiskAssessment)
    .order_by(RiskAssessment.created_at.desc())
    .limit(5)
    .all()
)

print("\nLast 5 records:")
for r in latest:
    print(r.id, r.risk_score, r.risk_level, r.created_at)

db.close()
