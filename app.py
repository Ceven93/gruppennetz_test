import streamlit as st
import uuid
import pandas as pd
import qrcode
import io

from database import get_connection, init_db
from auth import register, login
from analysis import calculate_metrics, draw_sociogram

# --------------------------------------------------
# INIT
# --------------------------------------------------

st.set_page_config(page_title="GruppenNetz", layout="wide")
init_db()

# --------------------------------------------------
# TOKEN PRÜFEN – KINDERSEITE
# --------------------------------------------------

query_params = st.query_params
token = query_params.get("token")

if token:

    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        "SELECT id, closed FROM classes WHERE token=%s",
        (token,)
    )
    class_data = cur.fetchone()

    if not class_data:
        st.error("Ungültiger Zugang.")
        st.stop()

    class_id, closed = class_data

    if closed == 1:
        st.success("Die Befragung ist abgeschlossen.")
        st.stop()

    df_students = pd.read_sql_query(
        "SELECT name FROM students WHERE class_id=%s",
        conn,
        params=(class_id,)
    )

    students = df_students["name"].tolist()

    st.title("Fragebogen")

    respondent = st.radio("Wie heisst du?", students)

    existing = pd.read_sql_query(
        "SELECT * FROM responses WHERE class_id=%s AND respondent=%s",
        conn,
        params=(class_id, respondent)
    )

    if len(existing) > 0:
        st.success("Du hast bereits teilgenommen.")
        st.stop()

    st.subheader("Mit welchen Kindern spielst du oft?")
    nominations = []

    for s in students:
        if s != respondent:
            if st.checkbox(s, key=f"nom_{s}"):
                nominations.append(s)

    st.subheader("Wie gerne spielst du mit ...")
    ratings = {}

    for s in students:
        if s != respondent:
            ratings[s] = st.radio(
                s,
                [1, 2, 3, 4, 5, 6],
                horizontal=True,
                key=f"rate_{s}"
            )

    if st.button("Absenden"):

        for s in students:
            if s != respondent:
                nominated = 1 if s in nominations else 0

                cur.execute("""
                    INSERT INTO responses
                    (class_id, respondent, target, rating, nominated)
                    VALUES (%s, %s, %s, %s, %s)
                """, (class_id, respondent, s, ratings[s], nominated))

        conn.commit()
        conn.close()

        st.success("Vielen Dank! Das Fenster kann nun geschlossen werden.")
        st.stop()

    st.stop()

# --------------------------------------------------
# LOGIN SYSTEM
# --------------------------------------------------

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
                st.success("Login erfolgreich")
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

# --------------------------------------------------
# LEHRPERSONENBEREICH
# --------------------------------------------------

page = st.sidebar.selectbox(
    "Navigation",
    ["Dashboard", "Analyse"]
)

# --------------------------------------------------
# DASHBOARD
# --------------------------------------------------

if page == "Dashboard":

    st.title("Lehrpersonen-Dashboard")

    st.header("Neue Klasse erstellen")

    class_name = st.text_input("Klassenname")
    date = st.date_input("Datum")
    names = st.text_area("Namen der Kinder (eine pro Zeile)")

    if st.button("Klasse erstellen"):

        token = str(uuid.uuid4())

        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
            INSERT INTO classes 
            (teacher_id, class_name, date, token, closed)
            VALUES (%s, %s, %s, %s, 0)
            RETURNING id
        """, (st.session_state.user_id, class_name, str(date), token))

        class_id = cur.fetchone()[0]

        for name in names.split("\n"):
            if name.strip():
                cur.execute(
                    "INSERT INTO students (class_id, name) VALUES (%s, %s)",
                    (class_id, name.strip())
                )

        conn.commit()
        conn.close()

        st.success("Klasse erstellt!")

        base_url = st.secrets["APP_URL"]
        url = f"{base_url}/?token={token}"

        st.subheader("Link für Kinder")
        st.code(url)

        qr = qrcode.make(url)
        buf = io.BytesIO()
        qr.save(buf, format="PNG")
        buf.seek(0)

        st.image(buf)

    # Bestehende Klassen

    st.header("Bestehende Klassen")

    conn = get_connection()

    df_classes = pd.read_sql_query(
        "SELECT * FROM classes WHERE teacher_id=%s",
        conn,
        params=(st.session_state.user_id,)
    )

    if df_classes.empty:
        st.info("Noch keine Klassen vorhanden.")
        conn.close()
        st.stop()

    for _, row in df_classes.iterrows():

        st.subheader(row["class_name"])
        class_id = row["id"]

        df_students = pd.read_sql_query(
            "SELECT name FROM students WHERE class_id=%s",
            conn,
            params=(class_id,)
        )

        students = df_students["name"].tolist()

        df_responses = pd.read_sql_query(
            "SELECT DISTINCT respondent FROM responses WHERE class_id=%s",
            conn,
            params=(class_id,)
        )

        responded = df_responses["respondent"].tolist()
        missing = [s for s in students if s not in responded]

        st.write("Teilgenommen:", len(responded), "/", len(students))

        if missing:
            st.write("Noch offen:", ", ".join(missing))
        else:
            st.success("Alle Kinder haben teilgenommen!")

        if row["closed"] == 0 and len(missing) == 0:
            if st.button(f"Erhebung abschliessen {class_id}"):

                cur = conn.cursor()
                cur.execute(
                    "UPDATE classes SET closed=1 WHERE id=%s",
                    (class_id,)
                )
                conn.commit()
                st.success("Erhebung abgeschlossen.")

    conn.close()

# --------------------------------------------------
# ANALYSE
# --------------------------------------------------

if page == "Analyse":

    st.title("Analyse")

    conn = get_connection()

    df_classes = pd.read_sql_query(
        "SELECT * FROM classes WHERE closed=1 AND teacher_id=%s",
        conn,
        params=(st.session_state.user_id,)
    )

    if df_classes.empty:
        st.info("Keine abgeschlossenen Erhebungen vorhanden.")
        conn.close()
        st.stop()

    selected_class = st.selectbox(
        "Klasse auswählen",
        df_classes["class_name"]
    )

    class_id = df_classes[
        df_classes["class_name"] == selected_class
    ]["id"].values[0]

    df_students = pd.read_sql_query(
        "SELECT name FROM students WHERE class_id=%s",
        conn,
        params=(class_id,)
    )

    students = df_students["name"].tolist()

    df_responses = pd.read_sql_query(
        "SELECT * FROM responses WHERE class_id=%s",
        conn,
        params=(class_id,)
    )

    results = calculate_metrics(df_responses, students)

    st.subheader("Kennwerte")
    st.dataframe(pd.DataFrame(results).T)

    st.subheader("Soziogramm")
    fig = draw_sociogram(df_responses, students, results)
    st.pyplot(fig)

    conn.close()