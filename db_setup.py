import sqlite3

conn = sqlite3.connect("expenses.db")
c = conn.cursor()

# Create tables
c.execute('''
CREATE TABLE IF NOT EXISTS income (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source TEXT,
    amount REAL,
    month TEXT
)
''')

c.execute('''
CREATE TABLE IF NOT EXISTS expenses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    category TEXT,
    sub_category TEXT,
    amount REAL,
    date TEXT,
    is_recurring INTEGER
)
''')

conn.commit()
conn.close()

print("Database setup complete ✅")
