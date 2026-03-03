import bcrypt
from database import get_connection


def register(email, password):
    conn = get_connection()
    cur = conn.cursor()

    # Prüfen ob E-Mail existiert
    cur.execute("SELECT id FROM users WHERE email = %s", (email,))
    existing = cur.fetchone()

    if existing:
        conn.close()
        return False

    # Passwort hashen
    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

    cur.execute(
        "INSERT INTO users (email, password) VALUES (%s, %s)",
        (email, hashed)
    )

    conn.commit()
    conn.close()
    return True


def login(email, password):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT id, password FROM users WHERE email = %s", (email,))
    user = cur.fetchone()

    conn.close()

    if user:
        user_id, hashed_pw = user
        if bcrypt.checkpw(password.encode(), hashed_pw.encode()):
            return (user_id,)
    
    return None