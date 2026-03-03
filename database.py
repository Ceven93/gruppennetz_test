import sqlite3

DB_NAME = "soziogramm.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    # Lehrpersonen
    c.execute("""
    CREATE TABLE IF NOT EXISTS teachers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT UNIQUE,
        password_hash TEXT,
        analyses_left INTEGER DEFAULT 0
    )
    """)

    # Klassen
    c.execute("""
    CREATE TABLE IF NOT EXISTS classes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        teacher_id INTEGER,
        class_name TEXT,
        date TEXT,
        token TEXT,
        closed INTEGER DEFAULT 0
    )
    """)

    # Schülerinnen & Schüler
    c.execute("""
    CREATE TABLE IF NOT EXISTS students (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        class_id INTEGER,
        name TEXT
    )
    """)

    # Antworten
    c.execute("""
    CREATE TABLE IF NOT EXISTS responses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        class_id INTEGER,
        respondent TEXT,
        target TEXT,
        rating INTEGER,
        nominated INTEGER
    )
    """)

    conn.commit()
    conn.close()