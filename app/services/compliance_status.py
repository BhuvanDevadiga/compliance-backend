from app.model import UserCompliance, ComplianceAuditLog

VALID_TRANSITIONS = {
    "PENDING": ["FILED", "MISSED"],
    "MISSED": ["FILED"]
}

def update_compliance_status(
    db,
    compliance_id: int,
    new_status: str,
    changed_by: str = "SYSTEM"
):
    compliance = db.query(UserCompliance).get(compliance_id)

    if not compliance:
        raise Exception("Compliance not found")

    if new_status not in VALID_TRANSITIONS.get(compliance.status, []):
        raise Exception("Invalid status transition")

    audit = ComplianceAuditLog(
        compliance_id=compliance.id,
        old_status=compliance.status,
        new_status=new_status,
        changed_by=changed_by
    )

    compliance.status = new_status
    db.add(audit)
    db.commit()

    return compliance
