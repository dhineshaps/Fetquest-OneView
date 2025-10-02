import streamlit as st

st.set_page_config(page_title="Demo", layout="wide")

# Add CSS to move navbar to the top
st.markdown("""
<style>
/* Remove default Streamlit padding at the top */
div.block-container {
    padding-top: 3.5rem;  /* add space for the navbar height */
}

/* Fixed navbar */
.navbar-container {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    background-color: #1e1e2f;
    padding: 0.5rem 1rem;
    z-index: 1000; /* keep above content */
    border-bottom: 1px solid #333;
}
.navbar-inner {
    display: flex;
    justify-content: space-between;
    align-items: center;
}
.nav-links {
    display: flex;
    gap: 0.5rem;
}
.nav-links button {
    background-color: transparent;
    color: #ccc;
    border: none;
    font-weight: 500;
    padding: 0.5rem 0.8rem;
    border-radius: 6px;
    cursor: pointer;
    transition: all 0.2s ease;
}
.nav-links button:hover {
    background-color: #2b2b3d;
    color: white;
}
.nav-links button.active {
    background-color: #4e9af1;
    color: white;
}
.logout-btn {
    background-color: #f25c5c;
    color: white;
    padding: 0.5rem 0.8rem;
    border: none;
    border-radius: 6px;
    cursor: pointer;
}
.logout-btn:hover {
    background-color: #d84b4b;
}
</style>
""", unsafe_allow_html=True)

# Navbar structure (fixed at top)
st.markdown("""
<div class="navbar-container">
  <div class="navbar-inner">
    <div class="nav-links">
      <button onclick="window.location.href='/View_Portfolio'">View Portfolio</button>
      <button onclick="window.location.href='/Manage_Portfolio'">Manage Portfolio</button>
    </div>
    <div>
      <button class="logout-btn" onclick="window.location.href='/login_new'">Logout</button>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

navbar = st.container()
with navbar:
    # Use columns INSIDE the fixed navbar
    col1, col2, col3 = st.columns([2, 2, 1])

    with col1:
        if st.button("📊 View Portfolio", key="view_btn"):
            st.switch_page("pages/1_View_Portfolio.py")

    with col2:
        if st.button("🛠 Manage Portfolio", key="manage_btn"):
            st.switch_page("pages/2_Manage_Portfolio.py")

    with col3:
        if st.button("🚪 Logout", key="logout_btn"):
            st.session_state.clear()
            st.switch_page("login_new.py")

# === Main content ===
st.title("Main Content Area")
for i in range(30):
    st.write(f"Row {i+1}: Dashboard content...")