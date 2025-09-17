import streamlit as st
import pandas as pd
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode
import uuid

# Example holdings
if "data" not in st.session_state:
    st.session_state["data"] = pd.DataFrame([
        {"Asset": "Stock", "Name": "TCS.NS", "Qty": 5, "Avg Price": 3200},
        {"Asset": "Gold", "Name": "Gold ETF", "Qty": 10, "Avg Price": None}
    ])

st.title("FETQuest OneView – Manage Portfolio")

st.dataframe(st.session_state["data"])

rows_data = [] 

with st.expander("➕ Add Holding"):
    if "rows" not in st.session_state:
        st.session_state["rows"] = []

    print(st.session_state["rows"])

    def add_row():
        element_id = uuid.uuid4()
        st.session_state["rows"].append(str(element_id))

    rows_collection = []

    def remove_row(row_id):
        st.session_state["rows"].remove(str(row_id))
     
    def generate_row(row_id):
        col1, col2, col3, col4, col5 = st.columns([2,2,2,2,1])

        with col1:
            asset_type = st.selectbox(
                "Type", 
                options=("Stock", "Mutual Fund", "Gold"), 
                key=f"type_{row_id}"
            )

        with col2:
            if asset_type == "Stock":
                st.selectbox("Stock", options=("ITC.NS","TCS.NS","RELIANCE.NS"), key=f"stock_{row_id}")
            elif asset_type == "Mutual Fund":
                st.selectbox("MF", options=("Axis Bluechip","HDFC Midcap","SBI Smallcap"), key=f"mf_{row_id}")
            else:
                st.selectbox("Gold Type", options=("Gold ETF","SGB"), key=f"gold_{row_id}")

        with col3:
            st.number_input("Qty", min_value=1, key=f"qty_{row_id}")

        with col4:
            if asset_type in ("Stock", "Mutual Fund"):
                st.number_input("Avg Price", min_value=0.0, key=f"price_{row_id}")
            else:
                st.write("—")  # no price field for gold

        with col5:
            st.button("🗑️", key=f"del_{row_id}", on_click=remove_row, args=[row_id])

        #return {"name": row_name}

    for row in st.session_state["rows"]:
        row_data = generate_row(row)
        rows_collection.append(row_data)

        row_data = {
            "type": st.session_state.get(f"type_{row}"),
            "stock": st.session_state.get(f"stock_{row}"),
            "qty": st.session_state.get(f"qty_{row}"),
            "price": st.session_state.get(f"price_{row}"),
        }
    
        rows_data.append(row_data)
    
    menu = st.columns(2)

    with menu[0]:
        st.button("Add Stock", on_click=add_row)

    proceed = st.button("Submit", type="primary")

    if  proceed:
        st.write(rows_data)




    # st.text_input("Asset Name")
    # st.number_input("Qty", min_value=1)
    # st.number_input("Avg Price", min_value=0.0)
    # st.button("Save")

# 🔹 Expander for Update

with st.expander("✏️ Update Holding"):
        st.write("Update form here...")
# 🔹 Expander for Delete
with st.expander("🗑️ Delete Holding"):
    st.write("Delete form here...")

# with col1:
#     if st.button("➕ Add Holding"):
#         #st.session_state["show_add"] = True
#         st.session_state["show_add"] = not st.session_state.get("show_add", False)

# with col2:
#     if st.button("✏️ Update Holding"):
#         st.session_state["show_update"] = True

# with col3:
#     if st.button("🗑️ Delete Holding"):
#         st.session_state["show_delete"] = True

# # Show conditional form
# if st.session_state.get("show_add"):
#     st.subheader("Add Holding")
#     st.text_input("Asset Name")
#     st.number_input("Qty", min_value=1)
#     st.number_input("Avg Price", min_value=0.0)
#     st.button("Save")

# if st.session_state.get("show_update"):
#     st.write("hello")