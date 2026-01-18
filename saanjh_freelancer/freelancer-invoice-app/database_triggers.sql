-- ======================================================
-- ADMIN LOGS TABLE
-- ======================================================
CREATE TABLE IF NOT EXISTS admin_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    table_name TEXT,
    action TEXT,
    record_id INTEGER,
    old_values TEXT,
    new_values TEXT,
    timestamp TEXT DEFAULT (datetime('now','localtime'))
);

-- ======================================================
-- CLIENTS TRIGGERS
-- ======================================================

DROP TRIGGER IF EXISTS trg_clients_insert;
CREATE TRIGGER trg_clients_insert
AFTER INSERT ON clients
BEGIN
    INSERT INTO admin_logs(table_name, action, record_id, new_values)
    VALUES('clients', 'INSERT', NEW.id,
           json_object('name', NEW.name, 'email', NEW.email, 'company', NEW.company));

    INSERT INTO admin_alerts(alert_type, message)
    VALUES('CLIENT_ADD',
           'New client added: ' || NEW.name || ' (' || NEW.email || ')');
END;

DROP TRIGGER IF EXISTS trg_clients_update;
CREATE TRIGGER trg_clients_update
AFTER UPDATE ON clients
BEGIN
    INSERT INTO admin_logs(table_name, action, record_id, old_values, new_values)
    VALUES('clients', 'UPDATE', OLD.id,
           json_object('name', OLD.name, 'email', OLD.email, 'company', OLD.company),
           json_object('name', NEW.name, 'email', NEW.email, 'company', NEW.company));

    INSERT INTO admin_alerts(alert_type, message)
    VALUES('CLIENT_UPDATE',
           'Client ID ' || OLD.id || ' was updated at ' || datetime('now','localtime'));
END;

DROP TRIGGER IF EXISTS trg_clients_delete;
CREATE TRIGGER trg_clients_delete
AFTER DELETE ON clients
BEGIN
    INSERT INTO admin_logs(table_name, action, record_id, old_values)
    VALUES('clients', 'DELETE', OLD.id,
           json_object('name', OLD.name, 'email', OLD.email, 'company', OLD.company));

    INSERT INTO admin_alerts(alert_type, message)
    VALUES('CLIENT_DELETE',
           'Client deleted: ' || OLD.name || ' (' || OLD.email || ')');
END;


-- ======================================================
-- ITEMS TRIGGERS
-- ======================================================

DROP TRIGGER IF EXISTS trg_items_insert;
CREATE TRIGGER trg_items_insert
AFTER INSERT ON items
BEGIN
    INSERT INTO admin_logs(table_name, action, record_id, new_values)
    VALUES('items', 'INSERT', NEW.id,
           json_object('description', NEW.description, 'rate', NEW.rate));

    INSERT INTO admin_alerts(alert_type, message)
    VALUES('ITEM_ADD',
           'New service/item added: "' || NEW.description || '" at rate Rs.' || NEW.rate);
END;

DROP TRIGGER IF EXISTS trg_items_update;
CREATE TRIGGER trg_items_update
AFTER UPDATE ON items
BEGIN
    INSERT INTO admin_logs(table_name, action, record_id, old_values, new_values)
    VALUES('items', 'UPDATE', OLD.id,
           json_object('description', OLD.description, 'rate', OLD.rate),
           json_object('description', NEW.description, 'rate', NEW.rate));

    INSERT INTO admin_alerts(alert_type, message)
    VALUES('ITEM_UPDATE',
           'Item "' || OLD.description || '" updated at ' || datetime('now','localtime'));
END;

DROP TRIGGER IF EXISTS trg_items_delete;
CREATE TRIGGER trg_items_delete
AFTER DELETE ON items
BEGIN
    INSERT INTO admin_logs(table_name, action, record_id, old_values)
    VALUES('items', 'DELETE', OLD.id,
           json_object('description', OLD.description, 'rate', OLD.rate));

    INSERT INTO admin_alerts(alert_type, message)
    VALUES('ITEM_DELETE',
           'Item deleted: "' || OLD.description || '"');
END;


-- ======================================================
-- INVOICES TRIGGERS
-- ======================================================

DROP TRIGGER IF EXISTS trg_invoices_insert;
CREATE TRIGGER trg_invoices_insert
AFTER INSERT ON invoices
BEGIN
    INSERT INTO admin_logs(table_name, action, record_id, new_values)
    VALUES('invoices', 'INSERT', NEW.id,
           json_object('client_id', NEW.client_id, 'date', NEW.date,
                       'due_date', NEW.due_date, 'paid', NEW.paid, 'status', NEW.status));

    INSERT INTO admin_alerts(alert_type, message)
    VALUES('INVOICE_ADD',
           'Invoice ID ' || NEW.id || ' created for Client ID ' || NEW.client_id);
END;

DROP TRIGGER IF EXISTS trg_invoices_update;
CREATE TRIGGER trg_invoices_update
AFTER UPDATE ON invoices
BEGIN
    INSERT INTO admin_logs(table_name, action, record_id, old_values, new_values)
    VALUES('invoices', 'UPDATE', OLD.id,
           json_object('client_id', OLD.client_id, 'date', OLD.date,
                       'due_date', OLD.due_date, 'paid', OLD.paid, 'status', OLD.status),
           json_object('client_id', NEW.client_id, 'date', NEW.date,
                       'due_date', NEW.due_date, 'paid', NEW.paid, 'status', NEW.status));

    INSERT INTO admin_alerts(alert_type, message)
    VALUES('INVOICE_UPDATE',
           'Invoice ID ' || OLD.id || ' was updated at ' || datetime('now','localtime'));
END;

DROP TRIGGER IF EXISTS trg_invoices_delete;
CREATE TRIGGER trg_invoices_delete
AFTER DELETE ON invoices
BEGIN
    INSERT INTO admin_logs(table_name, action, record_id, old_values)
    VALUES('invoices', 'DELETE', OLD.id,
           json_object('client_id', OLD.client_id, 'date', OLD.date,
                       'due_date', OLD.due_date, 'paid', OLD.paid, 'status', OLD.status));

    INSERT INTO admin_alerts(alert_type, message)
    VALUES('INVOICE_DELETE',
           'Invoice ID ' || OLD.id || ' deleted at ' || datetime('now','localtime'));
END;


-- ======================================================
-- INVOICE ITEMS TRIGGERS
-- ======================================================

DROP TRIGGER IF EXISTS trg_invoice_items_insert;
CREATE TRIGGER trg_invoice_items_insert
AFTER INSERT ON invoice_items
BEGIN
    INSERT INTO admin_logs(table_name, action, record_id, new_values)
    VALUES('invoice_items', 'INSERT', NEW.id,
           json_object('invoice_id', NEW.invoice_id, 'item_id', NEW.item_id, 'quantity', NEW.quantity));

    INSERT INTO admin_alerts(alert_type, message)
    VALUES('ITEM_ASSIGN',
           'Item ID ' || NEW.item_id || ' assigned to Invoice ID ' || NEW.invoice_id);
END;

DROP TRIGGER IF EXISTS trg_invoice_items_update;
CREATE TRIGGER trg_invoice_items_update
AFTER UPDATE ON invoice_items
BEGIN
    INSERT INTO admin_logs(table_name, action, record_id, old_values, new_values)
    VALUES('invoice_items', 'UPDATE', OLD.id,
           json_object('invoice_id', OLD.invoice_id, 'item_id', OLD.item_id, 'quantity', OLD.quantity),
           json_object('invoice_id', NEW.invoice_id, 'item_id', NEW.item_id, 'quantity', NEW.quantity));

    INSERT INTO admin_alerts(alert_type, message)
    VALUES('ITEM_UPDATE_INVOICE',
           'Invoice Item ID ' || OLD.id || ' quantity changed at ' || datetime('now','localtime'));
END;

DROP TRIGGER IF EXISTS trg_invoice_items_delete;
CREATE TRIGGER trg_invoice_items_delete
AFTER DELETE ON invoice_items
BEGIN
    INSERT INTO admin_logs(table_name, action, record_id, old_values)
    VALUES('invoice_items', 'DELETE', OLD.id,
           json_object('invoice_id', OLD.invoice_id, 'item_id', OLD.item_id, 'quantity', OLD.quantity));

    INSERT INTO admin_alerts(alert_type, message)
    VALUES('ITEM_REMOVE',
           'Item ID ' || OLD.item_id || ' removed from Invoice ID ' || OLD.invoice_id);
END;
