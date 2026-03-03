import sqlite3
import bcrypt
import streamlit as st

DB_NAME = "soziogramm.db"

# Registrierung
def register(email, password):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt())

    try:
        c.execute(
            "INSERT INTO teachers (email, password_hash) VALUES (?, ?)",
            (email, hashed)
        )
        conn.commit()
        return True
    except:
        return False
    finally:
        conn.close()


# Login
def login(email, password):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    c.execute("SELECT id, password_hash, analyses_left FROM teachers WHERE email=?", (email,))
    user = c.fetchone()
    conn.close()

    if user:
        user_id, stored_hash, analyses_left = user

        if bcrypt.checkpw(password.encode(), stored_hash):
            return user_id, analyses_left

    return None