
import requests
import streamlit as st

from utils import API_BASE_URL, HEADERS, get_users


st.set_page_config(layout="wide")


st.title('Users Dashboard')

st.dataframe(get_users())


st.write('Remove a user')
user_id_to_remove = st.text_input('User ID To Remove')
if st.button("Remove"):
    if user_id_to_remove:  # Check if content and frequency_days are not empty
        response = requests.delete(f"{API_BASE_URL}/users/{user_id_to_remove}", headers=HEADERS)
        if response.status_code == 200:
            st.success("User removed successfully! Please refresh the page.")
        else:
            st.error("Failed to remove the user")
    