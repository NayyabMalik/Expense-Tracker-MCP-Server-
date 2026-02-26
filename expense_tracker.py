from fastmcp import FastMCP
import os 
import sqlite3

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(BASE_DIR, 'expenses.db')

mcp = FastMCP(name='ExpenseTracker')

def init_db():
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            amount REAL NOT NULL,
            category TEXT NOT NULL,
            subcategory TEXT NOT NULL,
            date TEXT NOT NULL,
            note TEXT DEFAULT ' ' 
        )
    ''')
    conn.commit()
    conn.close()

init_db()

@mcp.tool
def add_expense(amount: float, category: str, subcategory: str, date: str, note: str = ' '):
    """Add a new expense to the database."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO expenses (amount, category, subcategory, date, note)
        VALUES (?, ?, ?, ?, ?)
    ''', (amount, category, subcategory, date, note))
    conn.commit()
    last_id = cursor.lastrowid
    conn.close()
    return {"status": "success", "message": "Expense added successfully.", "id": last_id}

@mcp.tool
def list_expenses(start_date: str = None, end_date: str = None, category: str = None):
    """List all expenses in the database."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    query = 'SELECT * FROM expenses'
    params = []
    conditions = []
    if start_date is not None:
        conditions.append('date >= ?')
        params.append(start_date)
    if end_date is not None:
        conditions.append('date <= ?')
        params.append(end_date)
    if category is not None:
        conditions.append('category = ?')
        params.append(category)
    if conditions:
        query += ' WHERE ' + ' AND '.join(conditions)
    cursor.execute(query, params)
    expenses = cursor.fetchall()
    conn.close()
    return [{"id": row[0], "amount": row[1], "category": row[2], "subcategory": row[3], "date": row[4], "note": row[5]} for row in expenses]

@mcp.tool
def delete_expense(expense_id: int):
    """Delete an expense from the database by ID."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('DELETE FROM expenses WHERE id = ?', (expense_id,))
    conn.commit()
    deleted = cursor.rowcount
    conn.close()
    if deleted > 0:
        return {"status": "success", "message": "Expense deleted successfully."}
    else:
        return {"status": "error", "message": "Expense not found."}

@mcp.tool
def update_expense(expense_id: int, amount: float = None, category: str = None, subcategory: str = None, date: str = None, note: str = None):
    """Update an existing expense in the database by ID."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    fields = []
    params = []
    if amount is not None:
        fields.append('amount = ?')
        params.append(amount)
    if category is not None:
        fields.append('category = ?')
        params.append(category)
    if subcategory is not None:
        fields.append('subcategory = ?')
        params.append(subcategory)
    if date is not None:
        fields.append('date = ?')
        params.append(date)
    if note is not None:
        fields.append('note = ?')
        params.append(note)
    if not fields:
        conn.close()
        return {"status": "error", "message": "No fields to update."}
    params.append(expense_id)
    query = f'UPDATE expenses SET {", ".join(fields)} WHERE id = ?'
    cursor.execute(query, params)
    conn.commit()
    updated = cursor.rowcount
    conn.close()
    if updated > 0:
        return {"status": "success", "message": "Expense updated successfully."}
    else:
        return {"status": "error", "message": "Expense not found."}

@mcp.tool
def summarize_expenses_by_category(start_date: str = None, end_date: str = None):
    """Summarize total expenses by category."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    query = 'SELECT category, SUM(amount) FROM expenses'
    params = []
    conditions = []
    if start_date is not None:
        conditions.append('date >= ?')
        params.append(start_date)
    if end_date is not None:
        conditions.append('date <= ?')
        params.append(end_date)
    if conditions:
        query += ' WHERE ' + ' AND '.join(conditions)
    query += ' GROUP BY category'
    cursor.execute(query, params)
    summary = cursor.fetchall()
    conn.close()
    return [{"category": row[0], "total_amount": row[1]} for row in summary]

@mcp.resource(uri='file://categories.json', name='categories.json', mime_type='application/json')
def get_categories():
    """Get expense categories."""
    categories_path = os.path.join(BASE_DIR, 'categories.json')
    with open(categories_path, 'r') as f:
        return f.read()

if __name__ == "__main__":
    mcp.run()