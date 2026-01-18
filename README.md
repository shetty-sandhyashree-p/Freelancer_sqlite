Saanjh Freelancer – Invoice Management System

A simple, clean, and functional Flask + SQLite based invoice management system designed for freelancers and small businesses.

This project allows you to manage:
- Clients
- Services / Items
- Invoices
- Invoice items
- Payment status
- Admin alerts (via database triggers)
- PDF invoice generation

 Features

- Client CRUD (Add / Edit / Delete)
- Item & Service Management
- Invoice creation with multiple items
- Edit invoices (client, due date, status, quantities)
- Mark invoices as Paid / Unpaid
- Automatic invoice total calculation
- PDF invoice generation
- Admin alerts & audit logs (trigger-based)
- Dashboard with payment summary chart
- SQLite database (no setup required)

---

## 🛠 Tech Stack

- Backend:Python (Flask)
- Database: SQLite3
- **Frontend:** HTML, Bootstrap 5, Jinja2
- **PDF:** FPDF
- **Charts:** Chart.js

---

## 📂 Project Structure

```
freelancer-invoice-app/
│
├── app.py
├── saanjh_invoices.db
├── database_triggers.sql
├── README.md
│
├── templates/
│   ├── base.html
│   ├── index.html
│   ├── invoices.html
│   ├── invoice_edit.html
│   ├── invoice_add.html
│   ├── clients.html
│   ├── items.html
│   └── alerts.html
│
├── static/
│   └── logo.png
