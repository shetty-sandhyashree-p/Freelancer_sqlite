import sqlite3

DB = "saanjh_invoices.db"
conn = sqlite3.connect(DB)
c = conn.cursor()

print("\n=== TABLES PRESENT ===")
for row in c.execute("SELECT name FROM sqlite_master WHERE type='table';"):
    print("-", row[0])

print("\n=== FOREIGN KEYS of invoice_items ===")
for row in c.execute("PRAGMA foreign_key_list(invoice_items);"):
    print(row)

print("\n=== FOREIGN KEYS of invoices ===")
for row in c.execute("PRAGMA foreign_key_list(invoices);"):
    print(row)

print("\n=== INVOICE_ITEMS SCHEMA ===")
for row in c.execute("SELECT sql FROM sqlite_master WHERE name='invoice_items';"):
    print(row[0])

print("\n=== INVOICES SCHEMA ===")
for row in c.execute("SELECT sql FROM sqlite_master WHERE name='invoices';"):
    print(row[0])

conn.close()
