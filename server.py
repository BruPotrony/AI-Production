import sqlite3
from pathlib import Path

from mcp.server.mcpserver import MCPServer

DB_PATH = Path(__file__).parent / "logistica.db"

server = MCPServer("logistics-mcp")

ALLOWED_ORDER_STATUSES = {"pending", "processing", "completed"}


def query(sql: str, params: tuple = ()) -> list[dict]:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        rows = conn.execute(sql, params).fetchall()
        return [dict(row) for row in rows]
    finally:
        conn.close()


def execute(sql: str, params: tuple = ()) -> int:
    conn = sqlite3.connect(DB_PATH)
    try:
        cursor = conn.execute(sql, params)
        conn.commit()
        return cursor.rowcount
    finally:
        conn.close()


@server.tool()
def list_suppliers() -> list[dict]:
    """List all suppliers."""
    return query("SELECT * FROM suppliers")


@server.tool()
def list_clients() -> list[dict]:
    """List all clients."""
    return query("SELECT * FROM clients")


@server.tool()
def list_warehouses() -> list[dict]:
    """List all warehouses."""
    return query("SELECT * FROM warehouses")


@server.tool()
def list_products(low_stock_threshold: int | None = None) -> list[dict]:
    """List products, optionally filtered to those at or below a stock threshold."""
    if low_stock_threshold is not None:
        return query("SELECT * FROM products WHERE stock <= ?", (low_stock_threshold,))
    return query("SELECT * FROM products")


@server.tool()
def list_orders(status: str | None = None) -> list[dict]:
    """List orders, optionally filtered by status (pending, processing, completed)."""
    if status is not None:
        return query("SELECT * FROM orders WHERE status = ?", (status,))
    return query("SELECT * FROM orders")


@server.tool()
def get_product_stock(product_name: str) -> list[dict]:
    """Look up stock level and warehouse for a product by name (partial match)."""
    return query(
        """
        SELECT p.id, p.name, p.stock, w.name AS warehouse, s.name AS supplier
        FROM products p
        JOIN warehouses w ON w.id = p.warehouse_id
        JOIN suppliers s ON s.id = p.supplier_id
        WHERE p.name LIKE ?
        """,
        (f"%{product_name}%",),
    )


@server.tool()
def update_stock(product_id: int, stock: int) -> dict:
    """Set the stock level for a product by id."""
    if stock < 0:
        raise ValueError("stock cannot be negative")
    rows = execute("UPDATE products SET stock = ? WHERE id = ?", (stock, product_id))
    if rows == 0:
        raise ValueError(f"no product with id {product_id}")
    return {"product_id": product_id, "stock": stock}


@server.tool()
def update_order_status(order_id: int, status: str) -> dict:
    """Update an order's status (pending, processing, or completed)."""
    if status not in ALLOWED_ORDER_STATUSES:
        raise ValueError(f"status must be one of {sorted(ALLOWED_ORDER_STATUSES)}")
    rows = execute("UPDATE orders SET status = ? WHERE id = ?", (status, order_id))
    if rows == 0:
        raise ValueError(f"no order with id {order_id}")
    return {"order_id": order_id, "status": status}


if __name__ == "__main__":
    server.run("stdio")
