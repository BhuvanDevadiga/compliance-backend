import uuid
from fastapi import Request

REQUEST_ID_HEADER = "X-Request-ID"

def get_or_create_request_id(request: Request) -> str:
    rid = request.headers.get(REQUEST_ID_HEADER)
    if not rid:
        rid = str(uuid.uuid4())
    request.state.request_id = rid
    return rid
