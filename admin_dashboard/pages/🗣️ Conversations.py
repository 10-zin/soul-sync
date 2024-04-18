import streamlit as st

from utils import get_conversation, get_user

st.set_page_config(layout="wide")

if "password_correct" not in st.session_state or not st.session_state["password_correct"]:
    st.title('Please Login First!')    
    st.stop()

st.title('Conversations Dashboard')

user_id = st.text_input('Enter User ID')
# Button to add a new question
if st.button("Look Up"):
    user = get_user(user_id)
    messages = get_conversation(user["ai_wingman"]["conversation_id_user_default"])
    for i, message in enumerate(messages):
        if message["sender_id"] == user["participant"]["id"]:
            chat_bubble = st.chat_message("user")
        else:
            chat_bubble = st.chat_message("ai")
        chat_bubble.write(message['content'])
