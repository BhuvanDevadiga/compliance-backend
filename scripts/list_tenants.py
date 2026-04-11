try:
    from scripts._bootstrap import add_project_root
except ModuleNotFoundError:
    from _bootstrap import add_project_root

add_project_root()

from app.db.database import SessionLocal
from app.models.tenant import Tenant

db = SessionLocal()
tenants = db.query(Tenant).all()

for t in tenants:
    print(t.id, t.tenant_id, t.api_key_hash, t.is_active)

db.close()
