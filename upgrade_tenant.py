from app.db.database import SessionLocal
from app.models.tenant import Tenant

db = SessionLocal()
tenant = db.query(Tenant).filter(Tenant.tenant_id == 'demo').first()
if tenant:
    tenant.plan = 'enterprise'
    db.commit()
    print('✅ Demo tenant upgraded to enterprise (1000 req/sec)')
else:
    print('❌ Tenant not found')
db.close()
