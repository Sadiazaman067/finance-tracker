import sqlite3
import bcrypt
import os

DB_PATH = "data/pennybloom.db"

def init_db():
    os.makedirs("data", exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            date TEXT NOT NULL,
            description TEXT NOT NULL,
            amount REAL NOT NULL,
            category TEXT NOT NULL
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS budgets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            budget_json TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

def register_user(username, name, email, password):
    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("INSERT INTO users (username, name, email, password) VALUES (?, ?, ?, ?)",
                  (username, name, email, hashed))
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        return False

def login_user(username, password):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT name, password FROM users WHERE username = ?", (username,))
    result = c.fetchone()
    conn.close()
    if result and bcrypt.checkpw(password.encode(), result[1].encode()):
        return result[0]
    return None

def save_transaction(username, transaction):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("INSERT INTO transactions (username, date, description, amount, category) VALUES (?, ?, ?, ?, ?)",
              (username, transaction["date"], transaction["description"],
               transaction["amount"], transaction["category"]))
    conn.commit()
    conn.close()

def load_transactions(username):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT date, description, amount, category FROM transactions WHERE username = ?", (username,))
    rows = c.fetchall()
    conn.close()
    return [{"date": r[0], "description": r[1], "amount": r[2], "category": r[3]} for r in rows]

def save_budget(username, budget):
    import json
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("INSERT OR REPLACE INTO budgets (username, budget_json) VALUES (?, ?)",
              (username, json.dumps(budget)))
    conn.commit()
    conn.close()

def load_budget(username):
    import json
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT budget_json FROM budgets WHERE username = ?", (username,))
    result = c.fetchone()
    conn.close()
    if result:
        return json.loads(result[0])
    return {}