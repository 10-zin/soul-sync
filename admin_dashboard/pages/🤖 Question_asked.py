import numpy as np
import streamlit as st
import requests

from utils import get_question_asked_instances

st.set_page_config(layout="wide")

if "password_correct" not in st.session_state or not st.session_state["password_correct"]:
    st.title('Please Login First!')    
    st.stop()

st.title('Question Metrics')

question_id = st.text_input('Enter Question ID')
# Button to add a new question
if st.button("Look Up"):
    instances = get_question_asked_instances(question_id)
    messages_count = [instance["messages_count"] for instance in instances]
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Times Asked", len(instances))
    col2.metric("Average Messages Exchanged", np.mean(messages_count))
    st.dataframe(instances)