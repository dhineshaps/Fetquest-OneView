# pages/2_Manage_Portfolio.py
import streamlit as st
import urllib
from navbar import top_navbar

st.set_page_config(page_title="Manage Portfolio", layout="wide")
# --- Auth check ---
if "authenticated" not in st.session_state or not st.session_state.authenticated:
    st.switch_page("login.py")
    st.stop()

# --- Mark this page as current (used by JS to highlight) ---
st.session_state.current_page = "Manage Portfolio"

top_navbar()

#st.title("fetquest")
#st.title("⚙️ Manage Portfolio")
st.write("Here you can manage your assets.")
st.write(f"Welcome, {st.session_state.get('username', 'User')}")