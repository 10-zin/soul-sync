import streamlit as st
import pandas as pd
import numpy as np
import requests

from utils import get_questions, get_users

st.title('SoulSync Dashboard')

col1, col2, col3 = st.columns(3)
col1.metric("Total Users", len(get_users()))
col2.metric("Total Questions", len(get_questions()))
# col3.metric("Humidity", "86%", "4%")

