from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from sqlalchemy.orm import Session
from datetime import date, timedelta
from app.database import get_db
from app.core.security import decode_token
from app.services.dashboard_service import (
    generate_dashboard_insights,
    get_dashboard_summary,
    get_tenant_risk_history,
)
from app.schemas.dashboard import DashboardSummaryResponse
from app.services.dashboard_service import get_controls_for_tenant
from fastapi.responses import FileResponse
from app.services.report_service import generate_compliance_report

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])
api_router = APIRouter(tags=["Dashboard API"])
dashboard_oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login", auto_error=False)


def resolve_dashboard_tenant(
    tenant_id: str | None = Query(default=None),
    token: str | None = Depends(dashboard_oauth2_scheme),
) -> str:
    if tenant_id:
        return tenant_id

    if not token:
        raise HTTPException(
            status_code=401,
            detail="Missing tenant_id query parameter or bearer token",
        )

    try:
        payload = decode_token(token)
    except JWTError as exc:
        raise HTTPException(status_code=401, detail="Invalid token") from exc

    resolved_tenant_id = payload.get("tenant_id")
    if not resolved_tenant_id:
        raise HTTPException(status_code=401, detail="Token missing tenant_id")

    return resolved_tenant_id


def _get_user_compliance_model():
    from app.model import UserCompliance

    return UserCompliance


def _require_dashboard_summary(db: Session, tenant_id: str):
    result = get_dashboard_summary(db, tenant_id)
    if not result:
        raise HTTPException(
            status_code=404,
            detail="Tenant not found or no controls available",
        )
    return result

@router.get("/{user_id}/summary")
def compliance_summary(user_id: int, db: Session = Depends(get_db)):
    UserCompliance = _get_user_compliance_model()
    total = db.query(UserCompliance).filter(
        UserCompliance.user_id == user_id
    ).count()

    pending = db.query(UserCompliance).filter(
        UserCompliance.user_id == user_id,
        UserCompliance.status == "PENDING"
    ).count()

    filed = db.query(UserCompliance).filter(
        UserCompliance.user_id == user_id,
        UserCompliance.status == "FILED"
    ).count()

    missed = db.query(UserCompliance).filter(
        UserCompliance.user_id == user_id,
        UserCompliance.status == "MISSED"
    ).count()

    return {
        "total": total,
        "pending": pending,
        "filed": filed,
        "missed": missed
    }

@router.get("/{user_id}/upcoming")
def upcoming_compliances(user_id: int, db: Session = Depends(get_db)):
    UserCompliance = _get_user_compliance_model()
    today = date.today()
    next_week = today + timedelta(days=7)

    compliances = db.query(UserCompliance).filter(
        UserCompliance.user_id == user_id,
        UserCompliance.status == "PENDING",
        UserCompliance.due_date.between(today, next_week)
    ).order_by(UserCompliance.due_date).all()

    return compliances

@router.get("/{user_id}/missed")
def missed_compliances(user_id: int, db: Session = Depends(get_db)):
    UserCompliance = _get_user_compliance_model()
    compliances = db.query(UserCompliance).filter(
        UserCompliance.user_id == user_id,
        UserCompliance.status == "MISSED"
    ).order_by(UserCompliance.due_date.desc()).all()

    return compliances

@router.get("", response_model=DashboardSummaryResponse)
def dashboard_overview(
    tenant_id: str = Depends(resolve_dashboard_tenant),
    db: Session = Depends(get_db),
):
    return _require_dashboard_summary(db, tenant_id)


@router.get("/summary", response_model=DashboardSummaryResponse)
def dashboard_summary(
    tenant_id: str = Depends(resolve_dashboard_tenant),
    db: Session = Depends(get_db),
):
    return _require_dashboard_summary(db, tenant_id)


@router.get("/distribution")
def dashboard_distribution(
    tenant_id: str = Depends(resolve_dashboard_tenant),
    db: Session = Depends(get_db),
):
    summary = _require_dashboard_summary(db, tenant_id)
    return {
        "tenant_id": tenant_id,
        "distribution": summary["distribution"],
    }

@router.get("/controls")
def dashboard_controls(
    tenant_id: str = Depends(resolve_dashboard_tenant),
    db: Session = Depends(get_db),
):
    return get_controls_for_tenant(db, tenant_id)


@router.get("/risk-trend")
def dashboard_risk_trend(
    tenant_id: str = Depends(resolve_dashboard_tenant),
    db: Session = Depends(get_db),
):
    return get_tenant_risk_history(db, tenant_id)


@router.get("/trend")
def dashboard_trend(
    tenant_id: str = Depends(resolve_dashboard_tenant),
    db: Session = Depends(get_db),
):
    return get_tenant_risk_history(db, tenant_id)


@router.get("/insights")
def dashboard_insights(
    tenant_id: str = Depends(resolve_dashboard_tenant),
    db: Session = Depends(get_db),
):
    return generate_dashboard_insights(db, tenant_id)


@router.get("/export-report")
def export_report(
    tenant_id: str = Depends(resolve_dashboard_tenant),
    db: Session = Depends(get_db),
):
    file_path = f"compliance_report_{tenant_id}.pdf"
    generate_compliance_report(db, tenant_id, file_path)

    return FileResponse(
        path=file_path,
        filename=file_path,
        media_type="application/pdf"
    )


@api_router.get("/controls")
def controls_api(
    tenant_id: str = Depends(resolve_dashboard_tenant),
    db: Session = Depends(get_db),
):
    return get_controls_for_tenant(db, tenant_id)


@api_router.get("/insights")
def insights_api(
    tenant_id: str = Depends(resolve_dashboard_tenant),
    db: Session = Depends(get_db),
):
    return {
        "tenant_id": tenant_id,
        "items": generate_dashboard_insights(db, tenant_id),
    }


@api_router.get("/report/pdf")
def report_pdf_api(
    tenant_id: str = Depends(resolve_dashboard_tenant),
    db: Session = Depends(get_db),
):
    file_path = f"compliance_report_{tenant_id}.pdf"
    generate_compliance_report(db, tenant_id, file_path)
    return {
        "tenant_id": tenant_id,
        "status": "ready",
        "format": "pdf",
        "filename": file_path,
        "download_path": "/dashboard/export-report",
    }
