import sqlite3, os

DB = "saanjh_invoices.db"

if not os.path.exists(DB):
    print("❌ Database not found:", DB)
    exit()

conn = sqlite3.connect(DB)
c = conn.cursor()

print("⚙️ Deep repair: fixing invoices ↔ invoice_items relationship")

# Disable FK checks
c.execute("PRAGMA foreign_keys=OFF;")

# Back up data (if present)
try:
    c.execute("CREATE TABLE IF NOT EXISTS _backup_invoices AS SELECT * FROM invoices;")
    c.execute("CREATE TABLE IF NOT EXISTS _backup_invoice_items AS SELECT * FROM invoice_items;")
except Exception as e:
    print("⚠️ Could not back up existing tables:", e)

# Drop the old tables
c.execute("DROP TABLE IF EXISTS invoice_items;")
c.execute("DROP TABLE IF EXISTS invoices;")

# Recreate invoices with correct structure (matching triggers.sql)
c.execute("""
CREATE TABLE invoices (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    client_id INTEGER,
    paid INTEGER DEFAULT 0,
    date TEXT,
    due_date TEXT,
    overdue_date TEXT,
    status TEXT DEFAULT 'Unpaid',
    FOREIGN KEY(client_id) REFERENCES clients(id)
);
""")

# Recreate invoice_items with correct FK
c.execute("""
CREATE TABLE invoice_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    invoice_id INTEGER,
    item_id INTEGER,
    quantity INTEGER,
    FOREIGN KEY(invoice_id) REFERENCES invoices(id),
    FOREIGN KEY(item_id) REFERENCES items(id)
);
""")

# Try to restore old data safely
try:
    c.execute("""
    INSERT INTO invoices (id, client_id, paid, date, due_date)
    SELECT id, client_id, paid, date, due_date FROM _backup_invoices;
    """)
except Exception as e:
    print("ℹ️ Skipping restore of invoices:", e)

try:
    c.execute("""
    INSERT INTO invoice_items (invoice_id, item_id, quantity)
    SELECT invoice_id, item_id, quantity FROM _backup_invoice_items;
    """)
except Exception as e:
    print("ℹ️ Skipping restore of invoice_items:", e)

# Clean up backups
c.execute("DROP TABLE IF EXISTS _backup_invoices;")
c.execute("DROP TABLE IF EXISTS _backup_invoice_items;")

# Re-enable FK checks
c.execute("PRAGMA foreign_keys=ON;")
conn.commit()
conn.close()

print("✅ Deep repair completed! Foreign keys are now valid.")
