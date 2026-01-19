from fastapi import APIRouter
from app.services.risk_rules.registry import (
    list_rule_versions,
    get_rule_metadata,
)

router = APIRouter(prefix="/risk/versions", tags=["Risk Rules"])

@router.get("/")
def get_versions():
    return list_rule_versions()

@router.get("/{version}")
def get_version(version: str):
    return get_rule_metadata(version)
