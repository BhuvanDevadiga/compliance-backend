import sqlite3

conn = sqlite3.connect('app.db')
cursor = conn.cursor()

# Check all tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()
print("All tables in database:")
for t in tables:
    print(f"  - {t[0]}")

print("\nTenant Usage table structure:")
cursor.execute("PRAGMA table_info(tenant_usage);")
rows = cursor.fetchall()
if rows:
    for row in rows:
        print(row)
else:
    print("Table does not exist!")

conn.close()
