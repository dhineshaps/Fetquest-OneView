import streamlit as st
import pandas as pd
import uuid

# Dummy lists
fund_list = ["Aditya Birla Sun Life Banking & PSU Fund", "HDFC Equity Fund", "SBI Small Cap Fund"]
cos_list = ["TCS", "Infosys", "Reliance"]
gold_list = ["24K", "22K"]

# Fake holdings for Update/Delete testing
holdings = {
    "MF001": {"type": "Mutual Fund", "name": "HDFC Equity Fund", "units": 100},
    "STK001": {"type": "Stock", "name": "Infosys", "qty": 10},
    "GLD001": {"type": "Gold", "name": "24K", "grams": 5}
}

st.title("💼 Portfolio Manager")

# Step 1: Choose Operation
operation = st.radio("Choose Operation", ["Add Holding", "Update Holding", "Delete Holding"])

# -------------------- ADD -------------------- #
if operation == "Add Holding":
    asset_type = st.selectbox("Type", ("Stock", "Mutual Fund", "Gold"))

    if asset_type == "Stock":
        stock = st.selectbox("Select Stock", cos_list)
        qty = st.number_input("Quantity", min_value=1)
        price = st.number_input("Average Price", min_value=0.0)

    elif asset_type == "Mutual Fund":
        mf = st.selectbox("Select Mutual Fund", fund_list)
        txn_date = st.date_input("Txn Date", pd.to_datetime("today"))
        txn_type = st.selectbox("Txn Type", ["Buy", "Sell"])
        amount = st.number_input("Amount (₹)", min_value=0.0)
        nav = st.number_input("NAV", min_value=0.0)
        units = amount / nav if nav > 0 else 0
        st.metric("Units", f"{units:.2f}")

    else:  # Gold
        gold_type = st.selectbox("Gold Type", gold_list)
        grams = st.number_input("Grams", min_value=1)

    if st.button("➕ Add Holding"):
        st.success("✅ Holding Added Successfully!")

# -------------------- UPDATE -------------------- #
elif operation == "Update Holding":
    holding_id = st.selectbox("Select Holding", holdings.keys())
    holding = holdings[holding_id]

    st.write(f"Selected: {holding['type']} - {holding['name']}")

    if holding["type"] == "Mutual Fund":
        new_units = st.number_input("Update Units", min_value=0.0, value=float(holding["units"]))
    elif holding["type"] == "Stock":
        new_qty = st.number_input("Update Quantity", min_value=1, value=holding["qty"])
    else:
        new_grams = st.number_input("Update Grams", min_value=1, value=holding["grams"])

    if st.button("✏️ Update Holding"):
        st.success("✅ Holding Updated Successfully!")

# -------------------- DELETE -------------------- #
else:  # Delete
    holding_id = st.selectbox("Select Holding", holdings.keys())
    holding = holdings[holding_id]

    st.warning(f"⚠️ Delete {holding['type']} - {holding['name']} ?")
    if st.button("🗑️ Delete Holding"):
        st.success("✅ Holding Deleted Successfully!")
