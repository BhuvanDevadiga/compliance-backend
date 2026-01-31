import sqlite3

conn = sqlite3.connect('app.db')
cursor = conn.cursor()

# Check alembic_version table
print("Checking alembic_version:")
cursor.execute("SELECT * FROM alembic_version;")
rows = cursor.fetchall()
for row in rows:
    print(row)

conn.close()
