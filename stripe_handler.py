import stripe
import streamlit as st

stripe.api_key = st.secrets["stripe"]["secret_key"]

PRICE_SINGLE = st.secrets["stripe"]["price_single"]
PRICE_YEAR = st.secrets["stripe"]["price_year"]
DOMAIN = st.secrets["stripe"]["domain"]


def create_checkout_session(price_id, teacher_id):
    session = stripe.checkout.Session.create(
        payment_method_types=["card"],
        line_items=[{
            "price": price_id,
            "quantity": 1,
        }],
        mode="payment",
        success_url=f"{DOMAIN}/?success=true&session_id={{CHECKOUT_SESSION_ID}}",
        cancel_url=f"{DOMAIN}/?canceled=true",
        metadata={
            "teacher_id": teacher_id
        }
    )
    return session.url


def verify_session(session_id):
    session = stripe.checkout.Session.retrieve(session_id)
    return session