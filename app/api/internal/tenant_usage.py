from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from datetime import date
from typing import Optional

from app.db.database import get_db
from app.models.tenant_usage import TenantUsage

router = APIRouter(
prefix="/api/internal/usage",
tags=["Internal Usage"],
)

#@router.get("/today")
def usage_today(
    tenant_id: str = Query(...),
    usage_date: Optional[str] = Query(None, description="Date in YYYY-MM-DD format, defaults to today"),
    db: Session = Depends(get_db),
):
    if usage_date:
        query_date = date.fromisoformat(usage_date)
    else:
        query_date = date.today()

    rows = (
        db.query(TenantUsage)
        .filter(
            TenantUsage.tenant_id == tenant_id,
            TenantUsage.usage_date == query_date,
        )
        .all()
    )

    return [
        {
            "path": r.path,
            "method": r.method,
            "request_count": r.request_count,
            "last_seen": r.updated_at,
        }
        for r in rows
    ]
