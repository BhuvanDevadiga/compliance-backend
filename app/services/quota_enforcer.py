from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.services.quota_service import get_quota_snapshot


def enforce_daily_quota(db: Session, tenant_id: str):
    quota = get_quota_snapshot(db, tenant_id)

    if quota["daily_limit"] is not None and quota["used"] >= quota["daily_limit"]:
        raise HTTPException(
            status_code=429,
            detail={
                "message": "Daily API quota exceeded",
                "limit": quota["daily_limit"],
                "used": quota["used"],
                "plan": quota["plan"],
            },
        )
