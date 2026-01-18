from flask import Flask, render_template, request, redirect, url_for, jsonify, make_response
import sqlite3, os
from datetime import date, timedelta
from fpdf import FPDF


app = Flask(__name__)
DB = "saanjh_invoices.db"
from fpdf import FPDF

app.config['BUSINESS_NAME'] = "Saanjh Freelancer"
app.config['BUSINESS_EMAIL'] = "contact@saanjhfreelancer.in"
app.config['LOGO_PATH'] = os.path.join('static', 'logo.png')  # Adjust if needed

# ---------------------------------------------------
# DATABASE CONNECTION & INITIALIZATION
# ---------------------------------------------------
def connect():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn

# ---------------------------------------------------
# DATABASE CONNECTION & INITIALIZATION
# ---------------------------------------------------
def connect():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = connect()
    c = conn.cursor()

    # --- CLIENTS TABLE ---
    c.execute("""
        CREATE TABLE IF NOT EXISTS clients(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            email TEXT,
            company TEXT
        )
    """)

    # --- ITEMS TABLE ---
    c.execute("""
        CREATE TABLE IF NOT EXISTS items(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            description TEXT,
            rate REAL
        )
    """)

    # --- INVOICES TABLE ---
    c.execute("""
        CREATE TABLE IF NOT EXISTS invoices(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            client_id INTEGER,
            paid INTEGER DEFAULT 0,
            date TEXT,
            due_date TEXT,
            overdue_date TEXT,
            status TEXT DEFAULT 'Unpaid',
            FOREIGN KEY(client_id) REFERENCES clients(id)
        )
    """)

    # --- INVOICE ITEMS TABLE ---
    c.execute("""
        CREATE TABLE IF NOT EXISTS invoice_items(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            invoice_id INTEGER,
            item_id INTEGER,
            quantity INTEGER,
            FOREIGN KEY(invoice_id) REFERENCES invoices(id),
            FOREIGN KEY(item_id) REFERENCES items(id)
        )
    """)
    c.execute("""CREATE TABLE IF NOT EXISTS admin_alerts(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    alert_type TEXT,
    message TEXT,
    created_at TEXT DEFAULT (datetime('now','localtime'))
);""")

    # --- ADMIN LOGS TABLE (for full audit trail) ---
    c.execute("""
        CREATE TABLE IF NOT EXISTS admin_logs(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            table_name TEXT,
            action TEXT,
            record_id INTEGER,
            old_values TEXT,
            new_values TEXT,
            timestamp TEXT DEFAULT (datetime('now','localtime'))
        )
    """)

    # --- Load database triggers from external file ---
    try:
        sql_path = os.path.join(os.path.dirname(__file__), "database_triggers.sql")
        if os.path.exists(sql_path):
            with open(sql_path, "r", encoding="utf-8") as f:
                c.executescript(f.read())
            print("✅ Database triggers applied successfully.")
        else:
            print("⚠️ No trigger file found. Skipping trigger creation.")
    except Exception as e:
        print(f"⚠️ Trigger load error: {e}")

    # --- Seed data if database is empty ---
    if not c.execute("SELECT 1 FROM clients LIMIT 1").fetchone():
        print("🧩 Seeding initial data...")
        c.executemany("""
            INSERT INTO clients(name, email, company) VALUES (?, ?, ?)
        """, [
            ("Aarav Sharma", "aarav@sparkdesigns.in", "Spark Designs"),
            ("Meera Patel", "meera@growthhub.in", "GrowthHub")
        ])

        c.executemany("""
            INSERT INTO items(description, rate) VALUES (?, ?)
        """, [
            ("Website Design", 15000),
            ("App Development", 30000),
            ("SEO Optimization", 8000)
        ])

        today = date.today()
        due_date = (today + timedelta(days=10)).isoformat()

        # Create one sample invoice
        c.execute("""
            INSERT INTO invoices(client_id, paid, date, due_date)
            VALUES (?, ?, ?, ?)
        """, (1, 0, today.isoformat(), due_date))
        inv_id = c.lastrowid

        # Add sample items to that invoice
        c.executemany("""
            INSERT INTO invoice_items(invoice_id, item_id, quantity)
            VALUES (?, ?, ?)
        """, [(inv_id, 1, 1), (inv_id, 2, 1)])

    conn.commit()
    conn.close()
    print("✅ Database initialized successfully.")



# ---------------------------------------------------
# DASHBOARD
# ---------------------------------------------------

@app.route('/')
def index():
    conn = connect()
    total_clients = conn.execute("SELECT COUNT(*) FROM clients").fetchone()[0]
    total_invoices = conn.execute("SELECT COUNT(*) FROM invoices").fetchone()[0]

    paid_total = conn.execute("""
        SELECT IFNULL(SUM(it.rate * ii.quantity), 0)
        FROM invoices i
        JOIN invoice_items ii ON i.id = ii.invoice_id
        JOIN items it ON it.id = ii.item_id
        WHERE i.paid = 1
    """).fetchone()[0]

    unpaid_total = conn.execute("""
        SELECT IFNULL(SUM(it.rate * ii.quantity), 0)
        FROM invoices i
        JOIN invoice_items ii ON i.id = ii.invoice_id
        JOIN items it ON it.id = ii.item_id
        WHERE i.paid = 0
    """).fetchone()[0]

    # Provide data for charts (prevent Undefined)
    labels = ['Paid', 'Unpaid']
    values = [paid_total, unpaid_total]

    conn.close()
    return render_template("index.html",
                           total_clients=total_clients,
                           total_invoices=total_invoices,
                           unpaid=unpaid_total,
                           paid=paid_total,
                           labels=labels,
                           values=values)


# ---------------------------------------------------
# CLIENTS CRUD
# ---------------------------------------------------
@app.route('/clients')
def clients():
    conn = connect()
    rows = conn.execute("SELECT * FROM clients ORDER BY id DESC").fetchall()
    conn.close()
    return render_template("clients.html", clients=rows)

@app.route('/clients/add', methods=['GET','POST'])
def add_client():
    if request.method == 'POST':
        conn = connect()
        conn.execute("INSERT INTO clients(name,email,company) VALUES(?,?,?)",
                     (request.form['name'], request.form['email'], request.form['company']))
        conn.commit(); conn.close()
        return redirect(url_for('clients'))
    return render_template("form_generic.html", title="Add Client", fields=["name","email","company"])

@app.route('/clients/edit/<int:id>', methods=['GET','POST'])
def edit_client(id):
    conn = connect()
    if request.method == 'POST':
        conn.execute("UPDATE clients SET name=?,email=?,company=? WHERE id=?",
                     (request.form['name'], request.form['email'], request.form['company'], id))
        conn.commit(); conn.close()
        return redirect(url_for('clients'))
    data = conn.execute("SELECT * FROM clients WHERE id=?", (id,)).fetchone()
    conn.close()
    return render_template("form_generic.html", title="Edit Client", client=data, fields=["name","email","company"])

@app.route('/clients/delete/<int:id>')
def delete_client(id):
    conn = connect()
    conn.execute("DELETE FROM clients WHERE id=?", (id,))
    conn.commit(); conn.close()
    return redirect(url_for('clients'))


# ---------------------------------------------------
# ITEMS CRUD
# ---------------------------------------------------
@app.route('/items')
def items():
    conn = connect()
    rows = conn.execute("SELECT * FROM items ORDER BY id DESC").fetchall()
    conn.close()
    return render_template("items.html", items=rows)

@app.route('/items/add', methods=['GET','POST'])
def add_item():
    if request.method == 'POST':
        conn = connect()
        conn.execute("INSERT INTO items(description, rate) VALUES(?, ?)",
                     (request.form['description'], request.form['rate']))
        conn.commit(); conn.close()
        return redirect(url_for('items'))
    return render_template("form_generic.html", title="Add Item", fields=["description", "rate"])

@app.route('/items/edit/<int:id>', methods=['GET','POST'])
def edit_item(id):
    conn = connect()
    if request.method == 'POST':
        conn.execute("UPDATE items SET description=?, rate=? WHERE id=?",
                     (request.form['description'], request.form['rate'], id))
        conn.commit(); conn.close()
        return redirect(url_for('items'))
    data = conn.execute("SELECT * FROM items WHERE id=?", (id,)).fetchone()
    conn.close()
    return render_template("form_generic.html", title="Edit Item", item=data, fields=["description", "rate"])

@app.route('/items/delete/<int:id>')
def delete_item(id):
    conn = connect()
    conn.execute("DELETE FROM items WHERE id=?", (id,))
    conn.commit(); conn.close()
    return redirect(url_for('items'))


# ---------------------------------------------------
# INVOICES CRUD + PAID/UNPAID TOGGLE
# ---------------------------------------------------
from datetime import datetime, date
from flask import render_template

@app.route('/invoices')
def invoices():
    conn = connect()
    invoices = conn.execute("""
        SELECT i.*, c.name AS client
        FROM invoices i
        JOIN clients c ON c.id = i.client_id
        ORDER BY i.date DESC
    """).fetchall()

    data = []
    for inv in invoices:
        items = conn.execute("""
            SELECT it.description, it.rate, ii.quantity, (it.rate * ii.quantity) AS subtotal
            FROM invoice_items ii
            JOIN items it ON it.id = ii.item_id
            WHERE ii.invoice_id=?
        """, (inv['id'],)).fetchall()

        total = sum(i['subtotal'] for i in items)

        # ✅ Ensure dates are ISO strings ("YYYY-MM-DD")
        inv_dict = dict(inv)
        if isinstance(inv_dict['date'], date):
            inv_dict['date'] = inv_dict['date'].isoformat()
        elif isinstance(inv_dict['date'], str):
            try:
                inv_dict['date'] = datetime.strptime(inv_dict['date'], "%Y-%m-%d").date().isoformat()
            except Exception:
                pass

        if isinstance(inv_dict['due_date'], date):
            inv_dict['due_date'] = inv_dict['due_date'].isoformat()
        elif isinstance(inv_dict['due_date'], str):
            try:
                inv_dict['due_date'] = datetime.strptime(inv_dict['due_date'], "%Y-%m-%d").date().isoformat()
            except Exception:
                pass

        data.append({
            'invoice': inv_dict,
            'items': items,
            'total': total
        })

    conn.close()
    today = date.today().isoformat()  # ✅ also a string
    return render_template("invoices.html", data=data, today=today)


@app.route('/invoices/delete/<int:id>')
def delete_invoice(id):
    conn = connect()
    conn.execute("DELETE FROM invoice_items WHERE invoice_id=?", (id,))
    conn.execute("DELETE FROM invoices WHERE id=?", (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('invoices'))

@app.route('/invoices/edit/<int:id>', methods=['GET', 'POST'])
def edit_invoice(id):
    conn = connect()

    if request.method == 'POST':
        client_id = request.form['client_id']
        due_date = request.form['due_date']

        # --- Update invoice basic info ---
        conn.execute("UPDATE invoices SET client_id=?, due_date=? WHERE id=?", (client_id, due_date, id))

        # --- Update quantities ---
        item_ids = request.form.getlist('item_id')
        quantities = request.form.getlist('quantity')
        for i_id, qty in zip(item_ids, quantities):
            conn.execute("UPDATE invoice_items SET quantity=? WHERE id=?", (qty, i_id))

        conn.commit()
        conn.close()
        flash("Invoice updated successfully!", "success")
        return redirect(url_for('invoices'))

    # --- Load invoice details ---
    invoice = conn.execute("""
        SELECT i.*, c.name AS client_name, c.company
        FROM invoices i
        JOIN clients c ON c.id = i.client_id
        WHERE i.id=?
    """, (id,)).fetchone()

    clients = conn.execute("SELECT id, name, company FROM clients").fetchall()

    items = conn.execute("""
        SELECT ii.id AS ii_id, it.description, it.rate, ii.quantity, (it.rate * ii.quantity) AS subtotal
        FROM invoice_items ii
        JOIN items it ON ii.item_id = it.id
        WHERE ii.invoice_id=?
    """, (id,)).fetchall()

    all_items = conn.execute("SELECT id, description, rate FROM items").fetchall()

    conn.close()

    return render_template("invoice_edit.html",
                           invoice=invoice,
                           clients=clients,
                           items=items,
                           all_items=all_items)



@app.route('/invoices/add', methods=['GET', 'POST'])
def add_invoice():
    conn = connect()
    clients = conn.execute("SELECT * FROM clients").fetchall()
    items = conn.execute("SELECT * FROM items").fetchall()

    if request.method == 'POST':
        today = date.today()
        client_id = request.form['client_id']
        due_date = request.form['due_date']

        conn.execute(
            "INSERT INTO invoices(client_id, paid, date, due_date) VALUES (?, ?, ?, ?)",
            (client_id, 0, today.isoformat(), due_date)
        )
        invoice_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]

        # Add items for the invoice
        for item_id, qty in zip(request.form.getlist('item_id'), request.form.getlist('quantity')):
            conn.execute(
                "INSERT INTO invoice_items(invoice_id, item_id, quantity) VALUES (?, ?, ?)",
                (invoice_id, item_id, qty)
            )

        conn.commit()
        conn.close()
        return redirect(url_for('invoices'))

    conn.close()
    return render_template("invoice_add.html", clients=clients, items=items)

@app.route('/invoices/item/add/<int:invoice_id>', methods=['POST'])
def add_invoice_item(invoice_id):
    conn = connect()
    item_id = request.form['item_id']
    qty = request.form['quantity']
    conn.execute("INSERT INTO invoice_items(invoice_id, item_id, quantity) VALUES(?,?,?)",
                 (invoice_id, item_id, qty))
    conn.commit()
    conn.close()
    flash("Item added successfully!", "success")
    return redirect(url_for('edit_invoice', id=invoice_id))


@app.route('/invoices/item/delete/<int:id>/<int:invoice_id>')
def delete_invoice_item(id, invoice_id):
    conn = connect()
    conn.execute("DELETE FROM invoice_items WHERE id=?", (id,))
    conn.commit()
    conn.close()
    flash("Item removed successfully!", "info")
    return redirect(url_for('edit_invoice', id=invoice_id))

@app.route('/invoices/mark_paid/<int:id>')
def mark_paid(id):
    conn = connect()
    invoice = conn.execute("SELECT paid FROM invoices WHERE id=?", (id,)).fetchone()
    new_paid = 0 if invoice['paid'] == 1 else 1
    new_status = 'Paid' if new_paid == 1 else 'Unpaid'
    conn.execute("UPDATE invoices SET paid=?, status=? WHERE id=?", (new_paid, new_status, id))
    conn.commit()
    conn.close()
    return redirect(url_for('invoices'))



# ---------------------------------------------------
# ADMIN LOGS (TRIGGER-DRIVEN)
# ---------------------------------------------------
@app.route('/admin/alerts')
def admin_alerts():
    conn = connect()
    rows = conn.execute("SELECT * FROM admin_alerts ORDER BY id DESC").fetchall()
    alerts = [dict(r) for r in rows]
    conn.close()
    return render_template('alerts.html', alerts=alerts)

@app.route('/api/alerts')
def api_alerts():
    conn = connect()
    rows = conn.execute("SELECT * FROM admin_alerts ORDER BY id DESC LIMIT 50").fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])


from fpdf import FPDF
from flask import make_response, abort
@app.route('/invoice/pdf/<int:id>')
def invoice_pdf(id):
    conn = connect()
    inv = conn.execute("""
        SELECT i.*, c.name, c.company
        FROM invoices i
        JOIN clients c ON c.id = i.client_id
        WHERE i.id=?
    """, (id,)).fetchone()
    items = conn.execute("""
        SELECT it.description, it.rate, ii.quantity, (it.rate * ii.quantity) AS subtotal
        FROM invoice_items ii
        JOIN items it ON it.id = ii.item_id
        WHERE ii.invoice_id=?
    """, (id,)).fetchall()
    conn.close()

    inv = dict(inv)
    from fpdf import FPDF
    from flask import make_response
    import os

    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)

    logo_path = os.path.join(app.root_path, "static", "logo.png")
    if os.path.exists(logo_path):
        pdf.image(logo_path, x=10, y=8, w=25)

    pdf.set_font("Helvetica", "B", 18)
    pdf.cell(0, 10, "Saanjh Billing System", ln=True, align='C')
    pdf.ln(10)

    pdf.set_font("Helvetica", "", 11)
    pdf.cell(0, 8, f"Invoice ID: {inv['id']}", ln=True)
    pdf.cell(0, 8, f"Client: {inv['name']} ({inv['company']})", ln=True)
    pdf.cell(0, 8, f"Date: {inv['date']} | Due: {inv['due_date']}", ln=True)
    pdf.cell(0, 8, f"Status: {'Paid' if inv['paid'] else 'Unpaid'}", ln=True)
    pdf.ln(10)

    pdf.set_fill_color(124, 58, 237)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Helvetica", "B", 11)
    pdf.cell(80, 8, "Description", border=1, align='C', fill=True)
    pdf.cell(25, 8, "Qty", border=1, align='C', fill=True)
    pdf.cell(40, 8, "Rate (Rs.)", border=1, align='C', fill=True)
    pdf.cell(45, 8, "Subtotal (Rs.)", border=1, align='C', fill=True, ln=True)

    pdf.set_text_color(0, 0, 0)
    total = 0
    for it in items:
        pdf.cell(80, 8, str(it['description']), border=1)
        pdf.cell(25, 8, str(it['quantity']), border=1, align='C')
        pdf.cell(40, 8, f"{it['rate']:.2f}", border=1, align='R')
        pdf.cell(45, 8, f"{it['subtotal']:.2f}", border=1, align='R', ln=True)
        total += it['subtotal']

    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(145, 8, "Total Amount", border=1, align='R')
    pdf.cell(45, 8, f"Rs. {total:.2f}", border=1, align='R', ln=True)
    pdf.ln(10)

    pdf.set_font("Helvetica", "", 10)
    pdf.cell(0, 8, "Thank you for choosing Saanjh!", ln=True, align='C')

    response = make_response(pdf.output(dest='S').encode('latin-1'))
    response.headers["Content-Type"] = "application/pdf"
    response.headers["Content-Disposition"] = f"inline; filename=invoice_{id}.pdf"
    return response


# ---------------------------------------------------
# MAIN
# ---------------------------------------------------
if __name__ == '__main__':
    init_db()
    app.run(debug=True)
