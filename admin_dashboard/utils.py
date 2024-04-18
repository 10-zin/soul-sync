import os
import streamlit as st
from dotenv import load_dotenv
import requests

load_dotenv()

API_BASE_URL = os.getenv("API_BASE_URL")
ADMIN_API_TOKEN = os.getenv("ADMIN_API_TOKEN")
GLOBAL_PASSWORD = os.getenv("GLOBAL_PASSWORD")

HEADERS = {"Authorization": f"token {ADMIN_API_TOKEN}"}

def get_users():
    response = requests.get(f"{API_BASE_URL}/users", headers=HEADERS)
    return response.json()

def get_user(user_id: str):
    response = requests.get(f"{API_BASE_URL}/users/{user_id}", headers=HEADERS)
    return response.json()
    

def get_questions():
    response = requests.get(f"{API_BASE_URL}/questions", headers=HEADERS)
    return response.json()

@st.cache_data
def get_conversation(conversation_id: str):
    response = requests.get(f"{API_BASE_URL}/conversations/{conversation_id}/messages", headers=HEADERS)
    return response.json()

def get_question_asked_instances(question_id: str):
    response = requests.get(f"{API_BASE_URL}/questions/{question_id}/asked", headers=HEADERS)
    return response.json()