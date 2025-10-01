import streamlit as st

pages = {
    "Your account": [
        st.Page("portfolio_view.py", title="portfolio"),
        st.Page("navi2.py", title="Manage your account"),
        st.Page("logout.py", title="Logout"),
    ],
}

pg = st.navigation(pages, position="top")
pg.run()	

#C:\VS_Code\Python_Works\Fetquest-OneView\pages\portfolio_view.py

# --- Intercept Logout ---
# if pg.title == "🚪 Logout":
#     st.session_state.clear()
#     st.switch_page("login.py")
# else:
#     pg.run()	