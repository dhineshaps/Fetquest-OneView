import streamlit as st
from utils import clear_user_id
import pandas as pd
from utils import load_user_id,load_user_name,init_session
from query import load_portfolio,load_mf_transactions


init_session()

if "data_version" not in st.session_state:
    st.session_state.data_version = 0

user_id = st.session_state.u_id

@st.cache_data
def show_holdings(user_id,version):
    df = load_portfolio(user_id).reset_index(drop=True)
    df.index = df.index + 1 
    df.index.name = "S.No"
    return df

@st.cache_data
def show_mf_transactions(user_id,version):  # user id needs to be passed
    df = load_mf_transactions(user_id).reset_index(drop=True)
    df.columns = df.columns.str.lower()
    df.index = df.index + 1 
    df.index.name = "S.No"
    return df

#print(st.session_state.data_version)


def top_navbar():
    left_col, middle_col, right_col = st.columns([2, 2, 1])

    st.session_state.portfolio_curd = show_holdings(st.session_state.u_id, st.session_state.data_version)
    st.session_state.mf_transactions = show_mf_transactions(st.session_state.u_id, st.session_state.data_version)

    # st.write(st.session_state.mf_transactions.columns)
    # st.write("end of nav bar print")

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
            if st.session_state.get("login_method") == "google":
                try:
                    st.logout()
                    st.session_state.clear()
                    st.stop()
                except Exception:
                    pass
            st.session_state.clear()
            st.session_state.mf_transactions = pd.DataFrame()
            clear_user_id()
            st.switch_page("login.py")
