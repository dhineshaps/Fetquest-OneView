import streamlit as st
import uuid
from utils import load_user_id

# pages = {
#     "Your account": [
#         #st.Page("portfolio_view.py", title="portfolio"),
#         st.Page("navi2.py", title="Manage your account"),
#         st.Page("logout.py", title="Logout"),
#     ],
# }

# pg = st.navigation(pages, position="top")
# #pg.run()	


# --- Initialize session state ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "u_id" not in st.session_state:
    st.session_state.u_id = None

# If no u_id in session, try loading from storage
if not st.session_state.u_id:
    st.session_state.u_id = load_user_id()
    st.session_state.logged_in = bool(st.session_state.u_id)


# --- Block access if not logged in ---
if not st.session_state.logged_in:
    st.error("Please login first!")
    st.stop()

st.title("📊 Portfolio Page")
st.write(f"Welcome! Your User ID: {st.session_state.u_id}")

# --- Dynamic row logic ---
if "rows" not in st.session_state:
    st.session_state["rows"] = []

rows_collection = []

def add_row():
    element_id = uuid.uuid4()
    st.session_state["rows"].append(str(element_id))

def remove_row(row_id):
    st.session_state["rows"].remove(str(row_id))

def generate_row(row_id):
    row_container = st.empty()
    row_columns = row_container.columns((3, 2, 1))
    row_name = row_columns[0].selectbox(
        "Stock_Name", 
        options=("ITC.NS","TCS.NS","RELIANCE.NS"), 
        key=f"txt_{row_id}"
    )
    row_columns[1].button("🗑️", key=f"del_{row_id}", on_click=remove_row, args=[row_id])
    return {"name": row_name}

def portfolio_curd():
    st.button("Add Stock", on_click=add_row)
    for row in st.session_state["rows"]:
        row_data = generate_row(row)
        rows_collection.append(row_data)
        st.write("here")
        st.write(rows_collection)

portfolio_curd()

# --- Logout ---
if st.button("Logout"):
    st.session_state.clear()
    st.switch_page("login.py")