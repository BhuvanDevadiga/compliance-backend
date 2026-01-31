from datetime import datetime
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.tenant_usage_monthly import TenantUsageMonthly
from app.services.tenant_usage_query_service import (
    get_usage_today,
    get_usage_last_n_days,
)

router = APIRouter(
    prefix="/api/internal/usage",
    tags=["Internal Usage"],
)


@router.get("/today",  operation_id="internal_usage_today_v1")
def usage_today(
    tenant_id: str = Query(...),
    db: Session = Depends(get_db),
):
    return get_usage_today(db, tenant_id)


@router.get("/last-7-days")
def usage_last_7_days(
    tenant_id: str = Query(...),
    db: Session = Depends(get_db),
):
    return get_usage_last_n_days(db, tenant_id, days=7)


@router.get("/last-30-days")
def usage_last_30_days(
    tenant_id: str = Query(...),
    db: Session = Depends(get_db),
):
    return get_usage_last_n_days(db, tenant_id, days=30)

@router.get("/month")
def get_monthly_usage(
    tenant_id: str,
    db: Session = Depends(get_db),
):
    now = datetime.utcnow()

    rows = (
        db.query(TenantUsageMonthly)
        .filter_by(
            tenant_id=tenant_id,
            year=now.year,
            month=now.month,
        )
        .all()
    )

    return [
        {
            "path": r.path,
            "method": r.method,
            "request_count": r.request_count,
            "last_seen": r.last_seen,
        }
        for r in rows
    ]
