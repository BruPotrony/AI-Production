import sqlite3

conn = sqlite3.connect("logistic.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS suppliers (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS clients (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    email TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS warehouses (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    location TEXT NOT NULL
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    stock INTEGER NOT NULL DEFAULT 0,
    supplier_id INTEGER NOT NULL,
    warehouse_id INTEGER NOT NULL,
    FOREIGN KEY (supplier_id) REFERENCES suppliers(id),
    FOREIGN KEY (warehouse_id) REFERENCES warehouses(id)

)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS orders (
    id INTEGER PRIMARY KEY,
    product_id INTEGER NOT NULL,
    client_id INTEGER NOT NULL,
    qty INTEGER NOT NULL,
    status TEXT NOT NULL DEFAULT 'pending',
    from_warehouse INTEGER,

    to_warehouse INTEGER,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (from_warehouse) REFERENCES warehouses(id),
    FOREIGN KEY (product_id) REFERENCES products(id),
    FOREIGN KEY (client_id) REFERENCES clients(id)
)
""")

# --- Sample data ---

cursor.executemany(
    "INSERT INTO suppliers (name) VALUES (?)",
    [
        ("Acme Packaging Co",),
        ("Global Pallets Ltd",),
        ("EcoWrap Supplies",),
    ]
)

cursor.executemany(
    "INSERT INTO clients (name, email) VALUES (?, ?)",
    [
        ("Nordic Threads", "orders@nordicthreads.com"),
        ("Urban Roast Coffee", "supply@urbanroast.com"),
        ("Bright Toys Inc", "procurement@brighttoys.com"),
        ("Vela Skincare", "ops@velaskincare.com"),
    ]
)

cursor.executemany(
    "INSERT INTO warehouses (name, location) VALUES (?, ?)",
    [
        ("Barcelona Hub", "Barcelona, ES"),
        ("Madrid Central", "Madrid, ES"),
        ("Newark Fulfillment", "Newark, US"),
    ]
)

cursor.executemany(
    "INSERT INTO products (name, stock, supplier_id, warehouse_id) VALUES (?, ?, ?, ?)",
    [
        ("Cardboard box A4", 120, 1, 1),
        ("Shipping labels", 8, 1, 1),
        ("Standard pallet", 45, 2, 2),
        ("Plastic wrap film", 3, 3, 1),
        ("Bubble mailer bag", 200, 3, 3),
        ("Packing tape roll", 60, 1, 2),
        ("Fragile stickers", 15, 3, 1),
    ]
)

cursor.executemany(
    "INSERT INTO orders (product_id, client_id, qty, status, from_warehouse) VALUES (?, ?, ?, ?, ?)",
    [
        (1, 1, 20, "completed", 1),
        (2, 2, 5, "pending", 1),
        (3, 3, 10, "processing", 2),
        (4, 1, 2, "pending", 1),
        (5, 4, 50, "completed", 3),
        (6, 2, 8, "processing", 2),
        (7, 3, 4, "pending", 1),
        (1, 4, 15, "completed", 1),
    ]
)

conn.commit()
conn.close()