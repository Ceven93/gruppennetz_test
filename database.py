import sqlite3

def get_connection():
    return sqlite3.connect("soziogramm.db", check_same_thread=False)

def init_db():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL
    );
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS classes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        teacher_id INTEGER,
        class_name TEXT,
        date TEXT,
        token TEXT,
        closed INTEGER DEFAULT 0
    );
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS students (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        class_id INTEGER,
        name TEXT
    );
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS responses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        class_id INTEGER,
        respondent TEXT,
        target TEXT,
        rating INTEGER,
        nominated INTEGER
    );
    """)

    conn.commit()
    conn.close()