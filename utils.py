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

def load_user_id() -> str | None:
    """Load user ID from cookie (if available)."""
    return cookies.get("u_id")

def clear_user_id():
    """Remove user ID (logout)."""
    if "u_id" in cookies:
        del cookies["u_id"]
        cookies.save()