from database import get_connection

def register(email, password):
    conn = get_connection()
    cur = conn.cursor()

    try:
        cur.execute(
            "INSERT INTO users (email, password) VALUES (?, ?)",
            (email, password)
        )
        conn.commit()
        return True
    except:
        return False
    finally:
        conn.close()


def login(email, password):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        "SELECT id FROM users WHERE email=? AND password=?",
        (email, password)
    )

    user = cur.fetchone()
    conn.close()

    return user