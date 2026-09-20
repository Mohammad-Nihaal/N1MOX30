import sqlite3

connection = sqlite3.connect("n1mox30.db")
cursor = connection.cursor()

tables = cursor.execute(
    """
    SELECT name
    FROM sqlite_master
    WHERE type='table'
    ORDER BY name
    """
).fetchall()

print("\n========== DATABASE TABLES ==========\n")

for table in tables:
    print(table[0])

print("\n========== AUTOMATION_WORKFLOWS ==========\n")

for row in cursor.execute(
    "PRAGMA table_info(automation_workflows)"
).fetchall():
    print(row)

print("\n========== AUTOMATION_STEPS ==========\n")

for row in cursor.execute(
    "PRAGMA table_info(automation_steps)"
).fetchall():
    print(row)

connection.close()
