
import streamlit as st
import requests

from utils import get_users


st.set_page_config(layout="wide")


st.title('Users Dashboard')

st.dataframe(get_users())

