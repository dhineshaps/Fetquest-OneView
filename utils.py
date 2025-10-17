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