import sqlite3
from database import DB_NAME

def create_default_users():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    c.execute("INSERT OR IGNORE INTO users VALUES ('admin', 'admin123', 'Admin')")
    c.execute("INSERT OR IGNORE INTO users VALUES ('officer', 'officer123', 'Officer')")

    conn.commit()
    conn.close()

def login(username, password):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    c.execute("SELECT role FROM users WHERE username=? AND password=?", (username, password))
    user = c.fetchone()
    conn.close()

    return user[0] if user else None
