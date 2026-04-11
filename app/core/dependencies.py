from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from app.core.security import decode_token
from jose import JWTError

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

def get_current_tenant(token: str = Depends(oauth2_scheme)):
    try:
        payload = decode_token(token)
        return payload["tenant_id"]
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    