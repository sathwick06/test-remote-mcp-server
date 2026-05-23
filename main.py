from fastmcp import FastMCP
import os
import sqlite3

DB_PATH = os.path.join(os.path.dirname(__file__), "expenses.db")

CATEGORY_PATH = os.path.join(os.path.dirname(__file__), "category.json")

mcp = FastMCP("ExpenseTracker")

def init_db():
    with sqlite3.connect(DB_PATH) as c:
        c.execute("""
            CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                amount REAL NOT NULL,
                category TEXT NOT NULL,
                subcategory TEXT DEFAULT '',
                note TEXT Default ''
            )
        """)

init_db()

@mcp.tool()
def add_expenses(date, amount, category, subcategory="", note=""):
    """Add a new expense entry to the database."""
    category = category.lower().strip()        
    subcategory = subcategory.lower().strip()
    with sqlite3.connect(DB_PATH) as c:
        cur = c.execute(
            "INSERT INTO expenses(date, amount, category, subcategory, note) VALUES (?, ?, ?, ?, ?)",
            (date, amount, category, subcategory, note)
        )
        return{"status": "ok", "id": cur.lastrowid}
    
@mcp.tool()
def list_expenses(start_date,end_date):
    """List all expense entries within an inclusive date range."""
    with sqlite3.connect(DB_PATH) as c:
        cur = c.execute(
            """SELECT id, date, amount, category, subcategory, note
            FROM expenses
            WHERE date BETWEEN ? AND ?
            ORDER BY id ASC
            """,
            (start_date, end_date)
        )
        cols=[d[0] for d in cur.description]
        return [dict(zip(cols, row)) for row in cur.fetchall()]

@mcp.tool()
def summarize_expenses(start_date: str, end_date: str, category: str = None):
    """Summarize total expenses grouped by category for a date range (YYYY-MM-DD).
    Optionally filter to a single category."""
    with sqlite3.connect(DB_PATH) as c:
        query = """SELECT category, SUM(amount) as total_amount
                   FROM expenses
                   WHERE date BETWEEN ? AND ?"""
        params = [start_date, end_date]

        if category:
            query += " AND LOWER(category) = LOWER(?)"
            params.append(category)

        query += " GROUP BY category ORDER BY category ASC"
        cur = c.execute(query, params)
        cols = [d[0] for d in cur.description]
        return [dict(zip(cols, row)) for row in cur.fetchall()]

@mcp.resource("expense://categories", mime_type="application/json")
def categories():
    #Read fresh each time so you can edit the file without restarting
    with open(CATEGORY_PATH, "r", encoding="utf-8") as f:
        return f.read()
    
@mcp.tool()
def edit_expenses(id, date=None, amount=None, category=None, subcategory=None, note=None):
    """Edit an existing expense entry by id. Only provided fields will be updated."""
    with sqlite3.connect(DB_PATH) as c:
        fields = []
        params = []
        if date is not None:
            fields.append("date = ?")
            params.append(date)
        if amount is not None:
            fields.append("amount = ?")
            params.append(amount)
        if category is not None:
            fields.append("category = ?")
            params.append(category.lower().strip())
        if subcategory is not None:
            fields.append("subcategory = ?")
            params.append(subcategory.lower().strip())
        if note is not None:
            fields.append("note = ?")
            params.append(note)

        if not fields:
            return {"status": "error", "message": "No fields to update"}

        params.append(id)
        query = f"UPDATE expenses SET {', '.join(fields)} WHERE id = ?"
        c.execute(query, params)
        if c.rowcount == 0:
            return {"status": "error", "message": f"No expense found with id {id}"}
        return {"status": "ok", "id": id}
    
if __name__ == "__main__":
    mcp.run()
