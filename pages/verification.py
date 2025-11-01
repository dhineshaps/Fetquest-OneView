import streamlit as st
import time
from supabase import create_client, Client
st.set_page_config(page_title="Verification",page_icon="the-fet-quest.jpg")

st.markdown("<h1 style='text-align: center; color: #FFA500;font-size: 30px'>FETQuest OneView - Portfolio</h1>", unsafe_allow_html=True)

st.title("Email Verification")

st.success("✅ Your email has been verified successfully!")
st.info("Redirecting to login page...")
time.sleep(2)
st.switch_page("login.py")
