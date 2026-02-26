from fastmcp import FastMCP
import os 
import sqlite3
db_path = os.path.join(os.path.dirname(__file__), 'expenses.db')## in project folder files of db store
mcp=FastMCP(name='ExpenseTracker')

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
    return {"status": "success", "message": "Expense added successfully.","id": cursor.lastrowid}

@mcp.tool
def list_expenses(start_date: str = None, end_date: str = None, category: str = None):
    """List all expenses in the database."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    query = 'SELECT * FROM expenses'
    params = []
    if start_date is not None:
        query += ' WHERE date >= ?'
        params.append(start_date)
    if end_date is not None:
        query += ' AND date <= ?' if start_date is not None else ' WHERE date <= ?'
        params.append(end_date)
    if category is not None:
        query += ' AND category = ?' if (start_date is not None or end_date is not None) else ' WHERE category = ?'
        params.append(category)
    cursor.execute(query, params)
    expenses = cursor.fetchall()
    return [{"id": row[0], "amount": row[1], "category": row[2], "subcategory": row[3], "date": row[4], "note": row[5]} for row in expenses]

@mcp.tool
def delete_expense(expense_id: int):
    """Delete an expense from the database by ID."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('DELETE FROM expenses WHERE id = ?', (expense_id,))
    conn.commit()
    if cursor.rowcount > 0:
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
    params.append(expense_id)
    query = f'UPDATE expenses SET {", ".join(fields)} WHERE id = ?'
    cursor.execute(query, params)
    conn.commit()
    if cursor.rowcount > 0:
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
    if start_date is not None:
        query += ' WHERE date >= ?'
        params.append(start_date)
    if end_date is not None:
        query += ' AND date <= ?' if start_date is not None else ' WHERE date <= ?'
        params.append(end_date)
    query += ' GROUP BY category'
    cursor.execute(query, params)
    summary = cursor.fetchall()
    return [{"category": row[0], "total_amount": row[1]} for row in summary]

@mcp.resource(name='categories.json', mime_type='application/json')
def get_categories():
    with open('categories.json', 'r') as f:
        return f.read()

if __name__ == "__main__":
    mcp.run()