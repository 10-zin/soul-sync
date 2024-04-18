import streamlit as st
import pandas as pd
import numpy as np

from utils import get_questions, get_users, GLOBAL_PASSWORD

st.title('SoulSync Dashboard')

def check_password():
    """Returns `True` if the user had the correct password."""

    def password_entered():
        """Checks whether a password entered by the user is correct."""
        if st.session_state["password"] == GLOBAL_PASSWORD:
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # Don't store the password.
        else:
            st.session_state["password_correct"] = False

    # Return True if the password is validated.
    if st.session_state.get("password_correct", False):
        return True

    # Show input for password.
    st.text_input(
        "Password", type="password", on_change=password_entered, key="password"
    )
    if "password_correct" in st.session_state:
        st.error("😕 Password incorrect")
    return False


if not check_password():
    st.stop()  # Do not continue if check_password is not True.

col1, col2, col3 = st.columns(3)
col1.metric("Total Users", len(get_users()))
col2.metric("Total Questions", len(get_questions()))
# col3.metric("Humidity", "86%", "4%")