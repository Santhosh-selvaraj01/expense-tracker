import sqlite3
import os

DB = "expenses.db"

if not os.path.exists(DB):
    conn = sqlite3.connect(DB)
    c = conn.cursor()

    # Create income table
    c.execute('''
    CREATE TABLE IF NOT EXISTS income (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        source TEXT,
        amount REAL,
        month TEXT
    )
    ''')

    # Create expenses table
    c.execute('''
    CREATE TABLE IF NOT EXISTS expenses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        category TEXT,
        sub_category TEXT,
        amount REAL,
        date TEXT,
        is_recurring INTEGER,
        last_updated TEXT DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    conn.commit()
    conn.close()
    print("Database setup complete ✅")
else:
    print("Database already exists ✅ – your existing data is safe")
