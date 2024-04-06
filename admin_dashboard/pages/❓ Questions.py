import streamlit as st
import requests
from utils import get_questions, API_BASE_URL, HEADERS

st.set_page_config(layout="wide")

def add_question():
    content = st.session_state.question_content
    frequency_days = st.session_state.question_frequency_days
    if content and frequency_days:  # Check if content and frequency_days are not empty
        response = requests.post(f"{API_BASE_URL}/questions", headers=HEADERS, json={
            "content": content,
            "frequency_days": frequency_days
        })
        if response.status_code == 200:
            st.success("Question added successfully! Please refresh the page to see the updated list of questions.")
        else:
            st.error("Failed to add the question")
            
def remove_question():
    if question_id_to_remove:  # Check if content and frequency_days are not empty
        response = requests.delete(f"{API_BASE_URL}/questions/{question_id_to_remove}", headers=HEADERS)
        if response.status_code == 200:
            st.success("Question removed successfully! Please refresh the page to see the updated list of questions.")
        else:
            st.error("Failed to remove the question")

st.title('Questions Dashboard')

# Display existing questions
st.dataframe(get_questions())

# Input for new question content
content = st.text_area(
    "Add new question",
    placeholder="Write a new question here...",
    key="question_content"  # Use a unique key for session state
)

# Input for frequency in days
frequency_days = st.number_input('How frequently should this question be asked in terms of days?', min_value=1, max_value=365, key="question_frequency_days")

# Button to add a new question
if st.button("Add"):
    add_question()
    
st.write('Remove a question')
question_id_to_remove = st.text_input('Question ID To Remove')
if st.button("Remove"):
    remove_question()