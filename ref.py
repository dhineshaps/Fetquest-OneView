import streamlit as st

def remove_row(row_id):
    st.session_state["rows"].remove(row_id)

if "rows" not in st.session_state:
    st.session_state["rows"] = ["row1"]  # just one row for demo

for row_id in st.session_state["rows"]:
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