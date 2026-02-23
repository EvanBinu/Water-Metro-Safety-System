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

    # 1. ADDED 'evidence' COLUMN HERE
    c.execute("""
    CREATE TABLE IF NOT EXISTS incidents (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        terminal TEXT,
        incident_type TEXT,
        severity TEXT,
        description TEXT,
        action_taken TEXT,
        date TEXT,
        evidence TEXT  
    )
    """)

    # 2. MIGRATION LOGIC: In case the table already exists without the column
    try:
        c.execute("ALTER TABLE incidents ADD COLUMN evidence TEXT")
    except sqlite3.OperationalError:
        # This error means the column already exists, so we can ignore it
        pass

    conn.commit()
    conn.close()

def insert_incident(data):
    """
    Expects data as a tuple: 
    (terminal, incident_type, severity, description, action_taken, date, evidence_path)
    """
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    # 3. UPDATED TO HANDLE 7 INPUTS (terminal through evidence)
    c.execute("""
    INSERT INTO incidents (terminal, incident_type, severity, description, action_taken, date, evidence)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """, data)

    conn.commit()
    conn.close()

def get_all_incidents():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    # 4. SELECT * will now return 8 columns (id + the 7 above)
    c.execute("SELECT * FROM incidents")
    rows = c.fetchall()
    conn.close()

    return rows