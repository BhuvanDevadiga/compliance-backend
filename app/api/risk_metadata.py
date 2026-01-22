from fastapi import APIRouter
from app.services.risk_rules.registry import (
    list_rule_versions,
    get_rule_metadata,
)

router = APIRouter(
    prefix="/api/risk",
    tags=["Risk Metadata"]
)


@router.get("/metadata")
def list_rules():
    return list_rule_versions()


@router.get("/metadata/{version}")
def rule_metadata(version: str):
    return get_rule_metadata(version)

