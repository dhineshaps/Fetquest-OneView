from streamlit_cookies_manager import EncryptedCookieManager
import streamlit as st

# Initialize cookie manager (only ONCE globally)
cookies = EncryptedCookieManager(
    prefix="myapp_", 
    password="super-secret-key"   # ⚠️ use a strong secret in real apps
)

# Streamlit requires this check
if not cookies.ready():
    st.stop()

def save_user_id(user_id: str):
    """Save user_id into cookie"""
    cookies["u_id"] = str(user_id)
    cookies.save()   # 🔑 persist cookie

def save_user_cookies(user_id: str, user_name: str):
    """Save both user_id and user_name into cookies in a single call."""
    cookies["u_id"] = str(user_id)
    cookies["u_name"] = str(user_name)
    cookies.save()

def load_user_id() -> str | None:
    """Load user ID from cookie (if available)."""
    return cookies.get("u_id")

def load_user_name() -> str | None:
    """Load user ID from cookie (if available)."""
    return cookies.get("u_name")

# def clear_user_id():
#     """Remove user ID (logout)."""
#     if "u_id" in cookies:
#         del cookies["u_id"]
#         cookies.save()

def clear_user_id():
    """Remove user cookies (logout)."""
    for key in ["u_id", "u_name"]:
        if key in cookies:
            del cookies[key]
    cookies.save()

def init_session():
    # --- Initialize session state ---
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
    if "u_id" not in st.session_state:
        st.session_state.u_id = None
    if "u_name" not in st.session_state:
        st.session_state.u_name = None

    # If no u_id in session, try loading from storage
    if not st.session_state.u_id:
        st.session_state.u_id = load_user_id()
        st.session_state.logged_in = bool(st.session_state.u_id)

    if not st.session_state.u_name:
        st.session_state.u_name = load_user_name()
        st.session_state.logged_in = bool(st.session_state.u_name)


    # --- Block access if not logged in ---
    if not st.session_state.logged_in:
        st.error("Please login first!")
        st.stop()