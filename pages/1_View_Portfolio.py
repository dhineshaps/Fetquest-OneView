import streamlit as st
from navbar import top_navbar

# --- Page config ---
st.set_page_config(page_title="View Portfolio", layout="wide")

# --- Auth check ---
if "authenticated" not in st.session_state or not st.session_state.authenticated:
    st.switch_page("login_new")
    st.stop()

# --- Track current page for highlighting ---
st.session_state.current_page = "View Portfolio"  # update this for each page

top_navbar()

# --- Page content ---
st.title("📈 View Portfolio")
st.write(f"Welcome, {st.session_state.get('username', 'User')}")