import sqlite3

DB_NAME = "safety.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    c.execute("""
    CREATE TABLE IF NOT EXISTS users (
        username TEXT PRIMARY KEY,
        password TEXT,
        role TEXT
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS incidents (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        terminal TEXT,
        incident_type TEXT,
        severity TEXT,
        description TEXT,
        action_taken TEXT,
        date TEXT
    )
    """)

    conn.commit()
    conn.close()

def insert_incident(data):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    c.execute("""
    INSERT INTO incidents (terminal, incident_type, severity, description, action_taken, date)
    VALUES (?, ?, ?, ?, ?, ?)
    """, data)

    conn.commit()
    conn.close()

def get_all_incidents():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    c.execute("SELECT * FROM incidents")
    rows = c.fetchall()
    conn.close()

    return rows
