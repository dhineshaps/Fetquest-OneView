import streamlit as st

st.set_page_config(page_title="Login", page_icon="🔐", layout="wide")

# Initialize session state
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

st.title("🔐 Login Page")

# Very simple login form
username = st.text_input("Username")
password = st.text_input("Password", type="password")

if st.button("Login"):
    if username == "admin" and password == "1234":
        st.session_state.authenticated = True
        st.session_state.username = username
        st.success("Login successful! Redirecting...")
        st.switch_page("pages/1_View_Portfolio.py")
    else:
        st.error("Invalid credentials")
