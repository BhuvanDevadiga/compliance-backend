import json
import sqlite3
import urllib.request
import urllib.error

API_URL = "http://127.0.0.1:8000/api/public/risk/score"
DB_PATH = "compliance.db"

API_KEY = "d088822466dbdc4c56472837a3863a88"
TENANT_ID = "1"   # MUST exist in tenants table


def call_api():
    payload = {
        "company_size": "small",
        "industry": "finance",
        "has_gst": True,
        "has_pan": False
    }

    data = json.dumps(payload).encode("utf-8")

    req = urllib.request.Request(
        API_URL,
        data=data,
        method="POST",
        headers={
            "Content-Type": "application/json",
            "X-API-Key": API_KEY,
            "X-Tenant-ID": TENANT_ID,
        }
    )

    try:
        with urllib.request.urlopen(req) as resp:
            body = resp.read().decode()
            print("\n✅ Request successful!")
            print("Status:", resp.status)
            print("Response JSON:", body)
    except urllib.error.HTTPError as e:
        print("\n❌ Request failed")
        print("Status:", e.code)
        print(e.read().decode())


def show_audit_logs():
    print("\n📜 Last 5 audit logs:")

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            id,
            tenant_id,
            method,
            path,
            status_code,
            latency_ms,
            created_at
        FROM request_audit_logs
        ORDER BY id DESC
        LIMIT 5;
    """)

    rows = cursor.fetchall()
    conn.close()

    if not rows:
        print("⚠️ No audit logs found")
        return

    for r in rows:
        print(r)


if __name__ == "__main__":
    call_api()
    show_audit_logs()
