import streamlit as st
import uuid
import pandas as pd
import qrcode
import io

from database import get_connection, init_db
from auth import register, login

st.set_page_config(page_title="GruppenNetz", layout="wide")
init_db()

# --------------------------
# KINDERSEITE (Token)
# --------------------------

query_params = st.query_params
token = query_params.get("token")

if token:
    conn = get_connection()

    df_class = pd.read_sql_query(
        "SELECT id, closed FROM classes WHERE token=?",
        conn,
        params=(token,)
    )

    if df_class.empty:
        st.error("Ungültiger Zugang")
        st.stop()

    class_id = df_class.iloc[0]["id"]
    closed = df_class.iloc[0]["closed"]

    if closed == 1:
        st.success("Befragung abgeschlossen")
        st.stop()

    df_students = pd.read_sql_query(
        "SELECT name FROM students WHERE class_id=?",
        conn,
        params=(class_id,)
    )

    students = df_students["name"].tolist()

    st.title("Fragebogen")

    respondent = st.radio("Wie heisst du?", students)

    st.subheader("Mit wem spielst du gerne?")
    nominations = []

    for s in students:
        if s != respondent:
            if st.checkbox(s):
                nominations.append(s)

    if st.button("Absenden"):
        for target in nominations:
            conn.execute(
                "INSERT INTO responses (class_id, respondent, target, rating, nominated) VALUES (?, ?, ?, ?, ?)",
                (class_id, respondent, target, 1, 1)
            )
        conn.commit()
        conn.close()
        st.success("Danke für deine Teilnahme!")
        st.stop()

    conn.close()
    st.stop()

# --------------------------
# LOGIN
# --------------------------

if "user_id" not in st.session_state:
    st.session_state.user_id = None

if st.session_state.user_id is None:
    st.title("GruppenNetz Login")

    tab1, tab2 = st.tabs(["Login", "Registrieren"])

    with tab1:
        email = st.text_input("E-Mail")
        password = st.text_input("Passwort", type="password")

        if st.button("Login"):
            result = login(email, password)
            if result:
                st.session_state.user_id = result[0]
                st.rerun()
            else:
                st.error("Falsche Zugangsdaten")

    with tab2:
        email_reg = st.text_input("E-Mail (neu)")
        password_reg = st.text_input("Passwort (neu)", type="password")

        if st.button("Registrieren"):
            if register(email_reg, password_reg):
                st.success("Registrierung erfolgreich")
            else:
                st.error("E-Mail existiert bereits")

    st.stop()

# --------------------------
# NAVIGATION
# --------------------------

page = st.sidebar.selectbox("Navigation", ["Dashboard", "Analyse"])

# --------------------------
# DASHBOARD
# --------------------------

if page == "Dashboard":

    st.title("Dashboard")

    class_name = st.text_input("Klassenname")
    names = st.text_area("Namen (eine pro Zeile)")

    if st.button("Klasse erstellen"):
        token = str(uuid.uuid4())

        conn = get_connection()
        cur = conn.cursor()

        cur.execute(
            "INSERT INTO classes (teacher_id, class_name, date, token, closed) VALUES (?, ?, ?, ?, 0)",
            (st.session_state.user_id, class_name, "", token)
        )

        class_id = cur.lastrowid

        for name in names.split("\n"):
            if name.strip():
                cur.execute(
                    "INSERT INTO students (class_id, name) VALUES (?, ?)",
                    (class_id, name.strip())
                )

        conn.commit()
        conn.close()

        st.success("Klasse erstellt")

        base_url = "http://localhost:8501"
        link = f"{base_url}/?token={token}"

        st.subheader("Link für Kinder")
        st.code(link)

        qr = qrcode.make(link)
        buf = io.BytesIO()
        qr.save(buf, format="PNG")
        buf.seek(0)

        st.image(buf)

# --------------------------
# ANALYSE
# --------------------------

if page == "Analyse":

    st.title("Analyse")

    conn = get_connection()

    df_classes = pd.read_sql_query(
        "SELECT * FROM classes WHERE teacher_id=?",
        conn,
        params=(st.session_state.user_id,)
    )

    if df_classes.empty:
        st.info("Keine Klassen vorhanden")
        conn.close()
        st.stop()

    selected = st.selectbox("Klasse wählen", df_classes["class_name"])

    class_id = df_classes[
        df_classes["class_name"] == selected
    ]["id"].values[0]

    df_responses = pd.read_sql_query(
        "SELECT * FROM responses WHERE class_id=?",
        conn,
        params=(class_id,)
    )

    st.subheader("Antworten")
    st.dataframe(df_responses)

    conn.close()