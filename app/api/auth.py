from contextlib import suppress
from urllib.parse import parse_qsl

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy import text
from sqlalchemy.orm import Session
from app.database import get_db
from app.core.security import verify_password,hash_password,create_access_token

router = APIRouter(prefix="/auth", tags=["Auth"])


async def _extract_request_data(request: Request) -> dict[str, str]:
    payload: dict[str, str] = dict(request.query_params)
    content_type = request.headers.get("content-type", "")

    if "application/json" in content_type:
        with suppress(Exception):
            json_payload = await request.json()
            if isinstance(json_payload, dict):
                payload.update(
                    {
                        str(key): str(value)
                        for key, value in json_payload.items()
                        if value is not None
                    }
                )
        return payload

    if "application/x-www-form-urlencoded" in content_type:
        form_payload = parse_qsl((await request.body()).decode("utf-8"), keep_blank_values=True)
        payload.update(
            {
                str(key): str(value)
                for key, value in form_payload
                if value is not None
            }
        )

    return payload


@router.post("/register")
async def register(request: Request, db: Session = Depends(get_db)):
    payload = await _extract_request_data(request)
    email = payload.get("email")
    password = payload.get("password")
    tenant_id = payload.get("tenant_id")
    username = payload.get("username") or email

    if not email or not password or not tenant_id:
        raise HTTPException(
            status_code=422,
            detail="email, password, and tenant_id are required",
        )

    existing_user = db.execute(
        text(
            """
            SELECT id, username, hashed_password, tenant_id
            FROM users
            WHERE username = :username
            LIMIT 1
            """
        ),
        {"username": username},
    ).mappings().first()
    if existing_user:
        raise HTTPException(status_code=400, detail="User already exists")

    db.execute(
        text(
            """
            INSERT INTO users (username, hashed_password, tenant_id, is_active, is_admin)
            VALUES (:username, :hashed_password, :tenant_id, :is_active, :is_admin)
            """
        ),
        {
            "username": username,
            "hashed_password": hash_password(password),
            "tenant_id": tenant_id,
            "is_active": True,
            "is_admin": False,
        },
    )
    db.commit()
    return {"message": "User created", "username": username, "tenant_id": tenant_id}

@router.post("/login")
async def login(request: Request, db: Session = Depends(get_db)):
    payload = await _extract_request_data(request)
    identity = payload.get("username") or payload.get("email")
    password = payload.get("password")

    if not identity or not password:
        raise HTTPException(
            status_code=422,
            detail="username/email and password are required",
        )

    user = db.execute(
        text(
            """
            SELECT id, username, hashed_password, tenant_id
            FROM users
            WHERE username = :username
            LIMIT 1
            """
        ),
        {"username": identity},
    ).mappings().first()

    if not user or not verify_password(password, user["hashed_password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token({
        "user_id": user["id"],
        "tenant_id": user["tenant_id"],
    })

    return {"access_token": token, "token_type": "bearer"}
