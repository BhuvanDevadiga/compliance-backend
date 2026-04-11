import asyncio
from app.db.database import SessionLocal
from app.services.anchor_service import anchor_chain_head

ANCHOR_INTERVAL_SECONDS = 300

async def anchor_loop():
    while True:
        try:
            db = SessionLocal()
            result = anchor_chain_head(db)
            if result:
                print(f"[ANCHOR] New anchor created: {result}")
            else:
                print("[ANCHOR] No change — skipped.")
            db.close()

        except Exception as e:
            print("[ANCHOR ERROR]", str(e))
        await asyncio.sleep(ANCHOR_INTERVAL_SECONDS)        