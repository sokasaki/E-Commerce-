import sqlite3
import os

db_path = os.path.join('instance', 'mydb.db')

if not os.path.exists(db_path):
    print(f"❌ Database not found at: {db_path}")
    exit(1)

print(f"✅ Database found at: {db_path}")
print(f"   Size: {os.path.getsize(db_path) / 1024:.2f} KB\n")

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Get all tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
tables = cursor.fetchall()

print("=" * 60)
print("DATABASE TABLES")
print("=" * 60)
for table in tables:
    print(f"• {table[0]}")

# Get structure and counts for each table
for table in tables:
    table_name = table[0]
    print(f"\n{'=' * 60}")
    print(f"TABLE: {table_name}")
    print("=" * 60)
    
    # Get table structure
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = cursor.fetchall()
    print("\nColumns:")
    for col in columns:
        col_id, name, type_, notnull, default, pk = col
        pk_str = " [PRIMARY KEY]" if pk else ""
        notnull_str = " NOT NULL" if notnull else ""
        default_str = f" DEFAULT {default}" if default else ""
        print(f"  • {name} ({type_}){pk_str}{notnull_str}{default_str}")
    
    # Get row count
    cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
    count = cursor.fetchone()[0]
    print(f"\nRow count: {count}")
    
    # Show sample data if available
    if count > 0 and count <= 10:
        cursor.execute(f"SELECT * FROM {table_name} LIMIT 5")
        rows = cursor.fetchall()
        print("\nSample data:")
        for row in rows:
            print(f"  {row}")

# Check for foreign keys
print(f"\n{'=' * 60}")
print("FOREIGN KEY RELATIONSHIPS")
print("=" * 60)
for table in tables:
    table_name = table[0]
    cursor.execute(f"PRAGMA foreign_key_list({table_name})")
    fks = cursor.fetchall()
    if fks:
        for fk in fks:
            print(f"• {table_name}.{fk[3]} → {fk[2]}.{fk[4]}")

conn.close()
print("\n✅ Database check complete!")
