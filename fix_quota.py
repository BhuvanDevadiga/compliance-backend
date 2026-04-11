from app.db.database import SessionLocal
from app.models.tenant_quota import TenantQuota
from app.models.tenant_usage_daily import TenantUsageDaily
from datetime import date
from sqlalchemy import func

db = SessionLocal()

# Check current quota
quota = db.query(TenantQuota).filter(TenantQuota.tenant_id == 'demo').first()
used = db.query(func.coalesce(func.sum(TenantUsageDaily.request_count), 0)).filter(
    TenantUsageDaily.tenant_id == 'demo',
    TenantUsageDaily.usage_date == date.today(),
).scalar()

print(f"Current daily limit: {quota.daily_limit if quota else 'No quota record'}")
print(f"Used today: {used}")

# Set very high daily limit for demo (10 million requests per day)
if quota:
    quota.daily_limit = 10000000
    db.commit()
    print("✅ Updated daily limit to 10 million for demo tenant")
else:
    print("❌ No quota record found - creating one")
    new_quota = TenantQuota(
        tenant_id='demo',
        plan='enterprise',
        daily_limit=10000000,
        monthly_limit=300000000,
        enforce_hard_limit=False
    )
    db.add(new_quota)
    db.commit()
    print("✅ Created enterprise quota (10M daily) for demo tenant")

# Also clear daily usage to start fresh
db.query(TenantUsageDaily).filter(
    TenantUsageDaily.tenant_id == 'demo',
    TenantUsageDaily.usage_date == date.today()
).delete()
db.commit()
print("✅ Cleared today's usage record")

db.close()
