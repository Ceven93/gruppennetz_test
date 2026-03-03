import streamlit as st
import psycopg2


def get_connection():
    return psycopg2.connect(st.secrets["DATABASE_URL"])


def init_db():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id SERIAL PRIMARY KEY,
        email TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL
    );
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS classes (
        id SERIAL PRIMARY KEY,
        teacher_id INTEGER REFERENCES users(id),
        class_name TEXT,
        date TEXT,
        token TEXT,
        closed INTEGER DEFAULT 0
    );
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS students (
        id SERIAL PRIMARY KEY,
        class_id INTEGER REFERENCES classes(id),
        name TEXT
    );
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS responses (
        id SERIAL PRIMARY KEY,
        class_id INTEGER REFERENCES classes(id),
        respondent TEXT,
        target TEXT,
        rating INTEGER,
        nominated INTEGER
    );
    """)

    conn.commit()
    cur.close()
    conn.close()