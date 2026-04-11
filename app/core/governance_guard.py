import re 
from app.core.engine_config import ENGINE_VERSION

def require_engine_version(func):
    def wrapper(*args, **kwargs):

        if not ENGINE_VERSION:
            raise Exception("Governance violation: ENGINE_VERSION not set.")
        
        if not re.match(r"^\d+\.\d+\.\d+$", ENGINE_VERSION):
            raise Exception(
                f"Invaid ENGINE_VERSION format: {ENGINE_VERSION}."
                "Must follow semantic versioning X.Y.Z"

            )
        return func(*args, **kwargs)
    return wrapper
