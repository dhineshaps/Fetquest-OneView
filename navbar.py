import streamlit as st

def top_navbar():
    left_col, middle_col, right_col = st.columns([2, 2, 1])

    with left_col:
        if st.session_state.current_page == "View Portfolio":
            st.button("View Portfolio", type="primary")
        else:
            if st.button("View Portfolio"):   
                st.session_state.current_page = "View Portfolio"
                st.switch_page("pages/portfolio_view.py")

    with middle_col:
        if st.session_state.current_page == "Manage Portfolio":
            st.button("Manage Portfolio", type="primary")
        else:
            if st.button("Manage Portfolio"): 
                st.session_state.current_page = "Manage Portfolio"
                st.switch_page("pages/manage_portfolio.py")

    with right_col:
        if st.button("Logout"):
            st.session_state.clear()
            st.switch_page("login.py")