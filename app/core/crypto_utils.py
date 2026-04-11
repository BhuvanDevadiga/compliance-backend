from cryptography.fernet import Fernet
from app.core.engine_config import GOVERNANCE_SIGNING_SECRET

fernet = Fernet(GOVERNANCE_SIGNING_SECRET.encode())


def encrypt_secret(secret: str) -> str:
    return fernet.encrypt(secret.encode()).decode()


def decrypt_secret(encrypted_secret: str) -> str:
    return fernet.decrypt(encrypted_secret.encode()).decode()
